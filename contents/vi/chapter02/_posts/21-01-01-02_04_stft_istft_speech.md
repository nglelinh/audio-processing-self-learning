---
layout: post
title: "02-04 STFT / ISTFT cho tiếng nói (nối DeepFilterNet)"
chapter: "02"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Biến đổi Fourier thời gian ngắn (STFT) là biểu diễn chủ lực của NS cổ điển và của họ mô hình DeepFilterNet. Biến đổi thuận dưới đây dùng một cửa sổ phân tích; biến đổi ngược gọi tên cửa sổ tổng hợp riêng, để điều kiện COLA của bài 02-02 áp được mà không có lần nhân cửa sổ bị giấu.

## Mục tiêu học tập

1. Có mô hình tinh thần của lưới STFT (thời gian × tần số).
2. Đối chiếu mask biên độ, mask phức, và ý deep filtering.
3. Nêu điều kiện tái dựng hoàn hảo trong thực hành.
4. Ánh xạ tham số STFT (rate, \(N\), hop, cửa sổ) sang độ trễ và phân giải.
5. Nối thiết kế STFT đã công bố của DeepFilterNet với tham số kỹ thuật.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Định nghĩa STFT; spectrogram là \(|STFT|\) |
| 12–28 | ISTFT / OLA; bài tái dựng |
| 28–42 | Xử lý mag và phức; trực giác deep filtering |
| 42–52 | Bài rút tham số từ paper DeepFilterNet |
| 52–60 | Bài tập |

![Cùng bức tranh overlap-add: frame phân tích, cửa sổ Hann bước theo hop R, và tổng cửa sổ mà ISTFT dựa vào]({{ site.imgurl }}/generated/stft-ola.png)

*Hình. Mỗi frame màu là một cột STFT; ISTFT cộng chồng các frame ngược, và tổng ở dưới phải là hằng, nếu không sine phía trên sẽ trở lại kèm bao biên theo hop.*

## Giải thích cốt lõi

### STFT

$$
X(\ell,k)=\sum_{n=0}^{L-1}x[n+\ell R]\,w[n]\,e^{-j2\pi kn/N}
$$

\(w[n]\) ở đây là cửa sổ **phân tích** \(w_{\mathrm{ana}}\). Lưới: cột là frame thời gian \(\ell\), hàng là bin tần số \(k\). Tăng cường tiếng nói ước lượng \(\hat{X}(\ell,k)\) sạch từ \(Y(\ell,k)\) nhiễu.

\(N\) là độ dài FFT. Có thể lớn hơn \(L\) khi zero-pad; nhỏ hơn \(L\) thì alias theo thời gian trong frame. Khoảng cách bin là \(f_s/N\), nhưng phân giải vẫn do cửa sổ (bài 02-03). Tín hiệu thực có \(N/2+1\) bin độc nhất, Nyquist ở bin cuối.

### ISTFT

FFT ngược từng frame, cửa sổ tổng hợp nếu có, rồi OLA. Một frame ngược, trước overlap-add:

$$
y_\ell[n]=\frac{1}{N}\sum_{k=0}^{N-1}\hat{X}(\ell,k)\,e^{j2\pi kn/N},\qquad n=0,\ldots,L-1
$$

(đóng gói FFT thực khi gọi `irfft`). Dạng sóng:

$$
\hat{x}[n]=\sum_\ell w_{\mathrm{syn}}[n-\ell R]\,y_\ell[n-\ell R].
$$

Nếu biến đổi thuận đã nhân \(w\) và \(w_{\mathrm{syn}}=1\), tái dựng phổ chưa sửa rút về \(\sum_\ell w[n-\ell R]=C\) rồi chia cho \(C\). Nếu còn nhân cửa sổ tổng hợp, COLA là tổng tích ở bài 02-02:

$$
\sum_\ell w[n-\ell R]\,w_{\mathrm{syn}}[n-\ell R]=C.
$$

Không sửa phổ và COLA đúng thì dựng lại \(x\) (trừ trễ/gain). STFT offline căn giữa lệch khoảng \(L/2\) so với stream nhân quả; cả hai có thể COLA mà vẫn lệch đủ để làm hỏng SI-SDR.

### Các biểu diễn

| Biểu diễn | Chứa | Dùng điển hình |
|-----------|------|----------------|
| Phức \(X\) | thực/ảo hoặc mag/pha | deep filtering, mask phức |
| Biên độ \(|X\|\) | không âm | Wiener cổ điển, mask mag |
| Log-mag / dB | nén | đặc trưng, đồ thị |
| Filterbank ERB / Mel | năng lượng băng | front-end tri giác (paper DeepFilterNet dùng đặc trưng thang ERB) |

### Mask biên độ và deep filtering

**Mask biên độ:** \(\hat{X}=M\odot|Y|e^{j\arg Y}\) (dùng lại pha nhiễu). Rẻ; sai pha khi SNR thấp.

**Mask phức / lọc:** dự đoán bộ lọc trộn các bin thời gian–tần số lân cận. **Deep filtering** trong tài liệu DeepFilterNet áp bộ lọc học được lên phổ phức, khôi phục cấu trúc tốt hơn gain từng bin độc lập.

Đọc paper DeepFilterNet / 2 / 3 cho kiến trúc chính xác. Bài này chỉ cần kết luận kỹ thuật: **bạn đang sửa một lưới STFT dưới ràng buộc nhân quả**, rồi ISTFT trở lại.

### Thực hành tái dựng hoàn hảo

Unit test: STFT→ISTFT không có mô hình phải xấp xỉ đồng nhất. Rồi mới bật mô hình. Nếu đồng nhất đã hỏng thì dừng. Mini-lab là test đó trên một sine: sai số float64 khoảng \(10^{-15}\) ở vùng trong. Sai số \(10^{-2}\) là lỗi cửa sổ hoặc hop, và sẽ thành tremolo theo hop.

### Ánh xạ tham số

Rút từ docs/paper: \(f_s\), loại cửa sổ và \(L\) / FFT \(N\), hop \(R\), look-ahead nhân quả, giả định mono. Đổi ra ms và hops/s bằng công thức chương 01–02 trước khi tích hợp `deepfilternet3-noise-filter` hoặc ORT.

**Lưới DeepFilterNet đã công bố.** Framework dành cho tốc độ tới 48 kHz. Thiết lập full-band được báo cáo dùng \(N_{\mathrm{FFT}}=960\) (20 ms ở 48 kHz) với overlap 50%, nên \(R=480\) (10 ms). Xem Schröter và cộng sự, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), và cấu hình tham chiếu [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) (`sr=48000`, `fft_size=960`, `hop_size=480`). Cửa sổ thuộc checkpoint đó: hop và cửa sổ phải khớp mô hình. Gói npm `deepfilternet3-noise-filter` 1.3.0 theo cùng hợp đồng full-band 48 kHz. Đổi hop 16 kHz, cửa sổ Blackman, hoặc STFT offline căn giữa không “tăng chất lượng”; nó đưa cho filterbank ERB một lưới khác với lưới của trọng số.

Thiết lập đó còn báo cáo look-ahead tích chập nhỏ (\(l_{\mathrm{DNN}}=2\) frame và \(l_{\mathrm{DF}}=1\) frame). Với hop 10 ms, các frame này nằm trên cửa sổ 20 ms. Hãy chép từ checkpoint.

## Ví dụ có số

1 giây @ 16 kHz, \(R=256\), \(N=512\), FFT thực → khoảng \(16000/256\approx 62\) frame (chính sách biên có thể lệch một), 257 bin độc nhất. Tensor mask có thể là \([1,257,62]\) hoặc đảo thứ tự trục — khớp mô hình.

2 giây @ 48 kHz, \(R=480\), \(N=960\): khoảng \(96000/480=200\) frame, \(960/2+1=481\) bin thực. Đó là họ kích thước mà tích hợp DeepFilterNet 48 kHz phải cấp phát, không phải 257 bin.

Bin SNR thấp: pha nhiễu gần như ngẫu nhiên. Mask biên độ dọn năng lượng nhưng phần dư nghe “ướt”. Phương pháp phức cố hơn — vẫn không phải phép màu với babble.

## Bẫy thường gặp

1. Căn giữa frame khi offline nhưng không làm vậy khi streaming.
2. Hop lúc train khác hop lúc serve.
3. Đưa Mel vào mô hình đang kỳ vọng ERB hoặc STFT tuyến tính.
4. ISTFT cả file theo batch trong production (độ trễ).
5. Khẳng định hằng số STFT Mezon chưa được tài liệu hóa, chỉ dựa vào khóa học này.

## Mini-lab

**Mục tiêu.** Đưa một sine 440 Hz qua STFT (cửa sổ phân tích) và ISTFT overlap-add, in sai số tuyệt đối lớn nhất ở vùng trong.

```python
import numpy as np

fs, L, R = 16000, 256, 128
w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(L) / L)
t = np.arange(fs) / fs
x = 0.5 * np.sin(2 * np.pi * 440 * t)
starts = range(0, len(x) - L + 1, R)
specs = [np.fft.rfft(x[s:s + L] * w) for s in starts]
y = np.zeros_like(x)
acc = np.zeros_like(x)
for s, spec in zip(starts, specs):
    y[s:s + L] += np.fft.irfft(spec, n=L)  # cửa sổ phân tích đã nằm trong frame
    acc[s:s + L] += w
mid = slice(L, len(x) - L)
err = np.max(np.abs(y[mid] / acc[mid] - x[mid]))
print("max abs error", err)
```

**Kỳ vọng.** `max abs error` cỡ \(10^{-15}\) (sai số float64). Ước COLA `acc` bằng hằng 1 ở vùng trong, như bài 02-02.

**Khi hỏng.** Quên chia cho `acc` để lại ngõ ra nửa biên độ hoặc gợn, sai số khoảng \(10^{-1}\). Hann đối xứng, hoặc nhân `w` lần nữa trên frame ngược, tạo sai số tuần hoàn theo hop, đủ để nghe. Chấm điểm `L` mẫu đầu, nơi `acc` chưa tới hằng, làm phồng sai số dù vùng ổn định đã đúng. Script này mà sai khác 0 thì backend FFT không khứ hồi, không phải vì COLA là tùy chọn.

## Bài tập nhỏ

1. Shape STFT xấp xỉ cho 2 s @ 48 kHz, \(R=480\), \(N=960\).
2. Vì sao tái sử dụng pha nhiễu thất bại khi nhiễu sâu?
3. Bốn tham số copy từ config DeepFilterNet vào checklist tích hợp.
4. COLA hỏng nghe thế nào sau ISTFT?
5. ERB vs STFT tuyến tính: một lý do dùng ERB ở front-end tăng cường tiếng nói?

### Gợi ý đáp án

1. Khoảng 200 frame và 481 bin thực.
2. SNR thấp thì pha nhiễu gần pha của nhiễu, nên biên độ hoàn hảo vẫn điều chế tiếng nói.
3. \(f_s\), độ dài FFT, hop, cửa sổ (và look-ahead nếu có ghi). Mặc định công khai cần đối chiếu: 48 kHz, 960, 480.
4. Tremolo biên độ ở \(f_s/R\) (100 Hz với hop 10 ms).
5. ERB dồn bin vào chỗ tai (và formant) có phân giải, thay vì chia đều theo hertz.

## Đọc thêm

- Paper DeepFilterNet, DeepFilterNet2, DeepFilterNet3 — STFT, ERB, deep filtering. Bắt đầu ở [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) và mã [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Julius O. Smith, *Spectral Audio Signal Processing* — định nghĩa STFT/ISTFT khớp cửa sổ.
- Oppenheim & Schafer — nối filter bank với STFT.
