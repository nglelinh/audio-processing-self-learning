---
layout: post
title: "02-02 Frame, hop và overlap-add"
chapter: "02"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Pipeline STFT cắt audio thành khung chồng lấn, xử lý từng khung, rồi dán lại bằng overlap-add (OLA: cộng chồng các khung đã xử lý). Sai hop hoặc sai OLA tạo warble mà cập nhật trọng số neural không chữa được. Bài này chứng minh điều kiện COLA (constant overlap-add: tổng cửa sổ chồng là hằng) cho cửa sổ Hann tuần hoàn, và đổi \(L\), \(R\) ra mili giây — “overlap 50%” chưa phải độ trễ cho đến khi chia cho \(f_s\).

## Mục tiêu học tập

1. Định nghĩa độ dài frame \(L\), hop \(R\), tỷ lệ overlap.
2. Giải thích tái dựng OLA và điều kiện COLA.
3. Tính hệ quả độ trễ thuật toán của \(L\) và \(R\).
4. Chọn hop cho NS tiếng nói với trực giác trễ/chất lượng.
5. Có mô hình tinh thần buffer OLA streaming.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Sơ đồ frame/hop trên bảng |
| 12–28 | Toán OLA; COLA với ví dụ Hann |
| 28–42 | Cơ chế buffer streaming; hiệu ứng biên |
| 42–52 | Số liệu @ 16/48 kHz cho tiếng nói |
| 52–60 | Bài tập |

![Các frame phân tích chồng nhau, cửa sổ Hann trượt với hop R, và tổng overlap-add của chúng]({{ site.imgurl }}/generated/stft-ola.png)

*Hình. Frame dài \(L\) tiến từng hop \(R\); overlap-add dựng lại sóng chỉ ở chỗ tổng các cửa sổ dịch là hằng số.*

## Giải thích cốt lõi

### Cắt frame

Độ dài cửa sổ \(L\) mẫu; hop \(R\) mẫu (\(1\le R\le L\)). Tỷ lệ chồng:

$$
\rho = 1-\frac{R}{L}
$$

Overlap 50% nghĩa là \(R=L/2\); 75% nghĩa là \(R=L/4\). Hop cũng là số mẫu mới phải gom trước FFT kế tiếp:

$$
T_R=\frac{R}{f_s},\qquad \text{hops/s}=\frac{f_s}{R},\qquad T_L=\frac{L}{f_s}.
$$

\(T_L\) là lượng audio nằm trong một frame phân tích. \(T_R\) là chu kỳ ra một frame mới. Cửa sổ 20 ms với hop 10 ms vẫn nhìn 20 ms ngữ cảnh mỗi lần chạy.

### Overlap-add

Với frame đã sửa \(y_m[n]=w_{\mathrm{syn}}[n]\cdot \mathrm{iFFT}(\hat{X}_m)\), ngõ ra:

$$
\hat{x}[n]=\sum_m y_m[n-mR]
$$

Nếu \(\hat{X}_m\) đúng là STFT phân tích của \(x\) và cửa sổ thỏa **COLA**, \(\hat{x}\) dựng lại \(x\) (trừ trễ và gain). Bước phân tích đã nhân \(w_{\mathrm{ana}}\). Thứ nhân thêm sau iFFT mới là \(w_{\mathrm{syn}}\). Viết cả hai ra là cách tránh nhân cửa sổ hai lần.

### COLA

Với hop \(R\), tích cửa sổ phân tích và tổng hợp phải cộng thành hằng:

$$
\sum_m w_{\mathrm{ana}}[n-mR]\,w_{\mathrm{syn}}[n-mR] = C
$$

(Câu này phụ thuộc bạn nhân cửa sổ một lần hay hai lần; phải khớp định nghĩa STFT của pipeline.) Hann với overlap 50% là lựa chọn COLA kinh điển khi dùng đúng.

**Chứng minh cho Hann tuần hoàn.** Đặt

$$
w[n]=\frac12-\frac12\cos\frac{2\pi n}{L},\qquad n=0,\ldots,L-1.
$$

Mẫu số là \(L\), không phải \(L-1\). Đó là Hann *tuần hoàn* (`sym=False` trong NumPy). Hann đối xứng ép \(w[0]=w[L-1]=0\) **không** cộng thành hằng, và là lý do test “Hann 50%” lệch vài phần nghìn.

Lấy \(R=L/2\), xét mẫu nằm trong vùng hai cửa sổ phủ. Đặt \(\theta=2\pi n/L\):

$$
w[n]=\frac12(1-\cos\theta),\qquad
w[n+R]=\frac12(1+\cos\theta).
$$

$$
w[n]+w[n+R]=1.
$$

Vậy nếu \(w_{\mathrm{ana}}=w\) và \(w_{\mathrm{syn}}=1\) trên frame (không nhân cửa sổ lần hai), tổng COLA ở vùng ổn định là hằng \(C=1\). Mini-lab in ra hằng đó.

**Cái không hằng.** Tổng bình phương cùng cửa sổ là \(\tfrac12(1+\cos^2\theta)\), dao động giữa \(1/2\) và \(1\). Nhân Hann đầy đủ cả lúc vào lẫn lúc ra thì biên độ bơm theo \(f_s/R\) hertz. Cách sửa thường gặp: \(w_{\mathrm{ana}}=w_{\mathrm{syn}}=\sqrt{w}\). Tích hai cửa sổ là \(w\), và tổng các tích là hằng vừa chứng minh. Đó là lý do \(\sqrt{\mathrm{Hann}}\) xuất hiện trong code STFT.

### Độ trễ

\(L\) lớn → chi tiết tần số tốt hơn, trễ đệm lớn hơn. \(R\) nhỏ → cập nhật dày, CPU cao hơn (nhiều hop mỗi giây), mask thường mượt hơn. NS sản phẩm thường hop khoảng 5–20 ms, nhưng **phải khớp mô hình**.

Với cửa sổ phân tích nhân quả, trễ thuật toán cỡ cả cửa sổ, không phải hop:

$$
D_{\mathrm{alg}}\approx T_L=\frac{L}{f_s}.
$$

Chưa đủ mẫu cuối thì chưa lập được frame. Giảm \(R\) từ \(L/2\) xuống \(L/4\) làm đôi số hop/s nhưng không cắt \(D_{\mathrm{alg}}\) một nửa. STFT căn giữa cần khoảng \(T_L/2\) look-ahead. Bài 02-07 tách độ trễ này khỏi real-time factor (RTF: tỉ lệ thời gian CPU trên thời lượng audio).

### Buffer OLA streaming

Giữ accumulator dài \(\ge L\). Mỗi hop cộng frame mới, phát \(R\) mẫu mà frame tương lai không còn chạm, mang đuôi overlap sang. \(L-R\) mẫu đầu chỉ là tổng chưa đủ, chưa phải hằng \(C\); hãy fade. Xóa accumulator mỗi callback sẽ khởi động lại tổng dở và chính là tremolo.

## Ví dụ có số

\(f_s=48\,\mathrm{kHz}\), \(L=960\) (20 ms), \(R=480\) (10 ms): \(\rho=0.5\), hops/s \(=100\), \(D_{\mathrm{alg}}\approx 20\,\mathrm{ms}\). Đây là lưới phân tích DeepFilterNet công bố: \(N_{\mathrm{FFT}}=960\) ở 48 kHz, overlap 50% ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)).

\(f_s=16\,\mathrm{kHz}\), \(L=512\), \(R=256\): \(T_L=512/16000=32\,\mathrm{ms}\), \(T_R=16\,\mathrm{ms}\), hops/s \(=62.5\). 512 mẫu ở 16 kHz không phải 16 ms. Hop 10 ms ở 16 kHz là \(R=160\), không phải 256.

### Triệu chứng COLA hỏng

Tremolo biên độ ở \(f_s/R\) Hz (ví dụ 100 Hz với hop 10 ms). Người nghe bảo “robot” hoặc “pha”. Lỗi gain của mạng không khóa đúng \(f_s/R\); lỗi COLA thì có.

### Khởi động

\(L-R\) mẫu đầu có thể chưa đủ — bỏ hoặc fade trước khi chấm SI-SDR.

## Bẫy thường gặp

1. Analysis Hann + synthesis chữ nhật mà không kiểm COLA.
2. Đổi hop nhưng giữ cửa sổ của hop khác.
3. Phát đủ \(L\) mẫu mỗi hop (lệch đồng bộ).
4. Xóa nhớ OLA mỗi callback.
5. STFT offline (pad giữa) lệch STFT streaming khi eval.

## Mini-lab

**Mục tiêu.** Overlap-add cửa sổ Hann tuần hoàn, hop 50%, và kiểm tra tổng phẳng ở giữa.

```python
import numpy as np

L, R = 256, 128
n = np.arange(L)
w = 0.5 - 0.5 * np.cos(2 * np.pi * n / L)  # Hann tuần hoàn, không phải np.hann mặc định
N = L + 8 * R
acc = np.zeros(N)
for m in range(0, N - L + 1, R):
    acc[m:m + L] += w
mid = acc[L:N - L]
print("COLA constant", float(mid[0]))
print("peak deviation", float(np.max(np.abs(mid - mid[0]))))
```

**Kỳ vọng.** Hằng in ra là `1.0`. Độ lệch đỉnh cỡ \(10^{-15}\).

**Khi hỏng.** `np.hann(L)` (đối xứng) đẩy độ lệch lên khoảng \(10^{-2}\): hai đầu cửa sổ đều bằng 0, tổng từng cặp không còn là 1. Cộng `w**2` thay vì `w` thì “hằng” chạy giữa 0.5 và 1 — đó là gợn khi nhân cửa sổ hai lần, assert phải fail. Hop `L/4` với cùng `w` cũng không phẳng; đồng nhất thức dùng hop 50%.

## Bài tập nhỏ

1. Overlap \(L=1024\), \(R=256\)?
2. Hop ms @ 16 kHz với \(R=160\)?
3. Vì sao hop nhỏ hơn tăng CPU?
4. Phác buffer OLA sau 3 hop \(L=8\), \(R=4\).
5. Một tín hiệu test COLA (impulse hoặc chirp).

### Gợi ý đáp án

1. \(\rho=1-256/1024=0.75\).
2. \(160/16000=10\,\mathrm{ms}\).
3. hops/s \(=f_s/R\) tăng, và mỗi hop có một FFT.
4. Sau ba hop, accumulator có một đoạn trong dài \(R\) nơi hai cửa sổ chồng, cộng đuôi dài \(L-R\).
5. Xung (hoặc hằng số) làm tổng COLA không phẳng hiện thành bao biên độ tuần hoàn; chirp còn lộ nhòe thời gian.

## Đọc thêm

- Oppenheim & Schafer — STFT / filterbank / OLA.
- Julius O. Smith, *Spectral Audio Signal Processing* — COLA và đồng nhất thức Hann.
- Framing DeepFilterNet: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
