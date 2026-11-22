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

Biến đổi Fourier thời gian ngắn (STFT) là biểu diễn cốt lõi của cả khử nhiễu cổ điển lẫn họ mô hình DeepFilterNet. Trong bài học này, phép biến đổi thuận dùng cửa sổ phân tích, còn phép biến đổi nghịch chỉ rõ cửa sổ tổng hợp riêng biệt để áp dụng chính xác điều kiện COLA từ bài 02-02 mà không bị ẩn đi bước nhân cửa sổ nào.

## Mục tiêu học tập

1. Hình dung rõ cấu trúc lưới STFT (thời gian × tần số).
2. Phân biệt mặt nạ biên độ, mặt nạ phức và ý tưởng của deep filtering.
3. Nêu các điều kiện tái tạo hoàn hảo (perfect reconstruction) trong thực hành.
4. Ánh xạ các tham số STFT (tần số lấy mẫu, \(N\), hop, hàm cửa sổ) sang độ trễ và độ phân giải.
5. Liên hệ thiết kế STFT đã công bố của DeepFilterNet với các thông số triển khai kỹ thuật.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Định nghĩa STFT; mối liên hệ giữa phổ đồ (spectrogram) và \(|\mathrm{STFT}|\) |
| 12–28 | ISTFT, cộng chồng lấp OLA và bài kiểm tra tái tạo |
| 28–42 | Xử lý biên độ so với xử lý phổ phức; trực giác về deep filtering |
| 42–52 | Thực hành trích xuất tham số từ bài báo DeepFilterNet |
| 52–60 | Bài tập nhỏ |

![Cùng bức tranh overlap-add: frame phân tích, cửa sổ Hann bước theo hop R, và tổng cửa sổ mà ISTFT dựa vào]({{ site.imgurl }}/generated/stft-ola.png)

*Hình. Mỗi khung màu tương ứng với một cột của lưới STFT; ISTFT cộng chồng các khung sau biến đổi nghịch, và tổng cửa sổ phía dưới phải là hằng số để sóng sin ban đầu được tái tạo mà không bị gợn biên độ theo nhịp hop.*

## Giải thích cốt lõi

### Biến đổi STFT

$$
X(\ell,k)=\sum_{n=0}^{L-1}x[n+\ell R]\,w[n]\,e^{-j2\pi kn/N}
$$

Trong công thức trên, \(w[n]\) là cửa sổ **phân tích** \(w_{\mathrm{ana}}\). Trên lưới thời gian–tần số, mỗi cột là một khung thời gian \(\ell\) và mỗi hàng là một bin tần số \(k\). Nhiệm vụ của tăng cường tiếng nói là ước lượng phổ sạch \(\hat{X}(\ell,k)\) từ phổ quan sát có nhiễu \(Y(\ell,k)\).

\(N\) là độ dài FFT: có thể chọn \(N > L\) khi đệm số 0, còn nếu \(N < L\) sẽ gây chồng chéo (aliasing) theo thời gian ngay trong khung. Khoảng cách giữa các bin bằng \(f_s/N\), nhưng độ phân giải tần số thực vẫn do hàm cửa sổ quyết định (xem bài 02-03). Với tín hiệu thực, chỉ có \(N/2+1\) bin không dư thừa và bin cuối cùng là tần số Nyquist.

### Biến đổi ISTFT

Quy trình tổng hợp gồm: tính FFT nghịch cho từng khung, nhân cửa sổ tổng hợp (nếu có), rồi cộng chồng lấp OLA. Mỗi khung sau biến đổi nghịch trước khi cộng chồng lấp có dạng:

$$
y_\ell[n]=\frac{1}{N}\sum_{k=0}^{N-1}\hat{X}(\ell,k)\,e^{j2\pi kn/N},\qquad n=0,\ldots,L-1
$$

(sử dụng biến đổi FFT thực `irfft` cho tín hiệu thực). Dạng sóng đầu ra được ghép theo:

$$
\hat{x}[n]=\sum_\ell w_{\mathrm{syn}}[n-\ell R]\,y_\ell[n-\ell R].
$$

Nếu bước phân tích đã nhân \(w\) và chọn \(w_{\mathrm{syn}}=1\), điều kiện tái tạo phổ chưa sửa quy về \(\sum_\ell w[n-\ell R]=C\) rồi chia cho \(C\). Nếu có nhân thêm cửa sổ tổng hợp \(w_{\mathrm{syn}}\), điều kiện COLA là tổng tích đã nêu ở bài 02-02:

$$
\sum_\ell w[n-\ell R]\,w_{\mathrm{syn}}[n-\ell R]=C.
$$

Khi phổ không bị chỉnh sửa và COLA được thỏa mãn, hệ thống sẽ tái tạo chính xác \(x\) (sai khác tối đa độ trễ và hằng số khuếch đại). Lưu ý rằng STFT ngoại tuyến căn giữa bị lệch khoảng \(L/2\) mẫu so với STFT streaming nhân quả; cả hai đều có thể thỏa COLA nhưng độ lệch thời gian đó đủ làm sụt giảm mạnh điểm SI-SDR nếu không căn chỉnh khi đánh giá.

### Các dạng biểu diễn phổ

| Biểu diễn | Thành phần lưu giữ | Ứng dụng điển hình |
|-----------|--------------------|--------------------|
| Phổ phức \(X\) | Phần thực/ảo hoặc biên độ/pha | Deep filtering, mặt nạ phức |
| Biên độ \(|X\|\) | Giá trị không âm | Lọc Wiener cổ điển, mặt nạ biên độ |
| Log-biên độ / dB | Nén dải động | Trích xuất đặc trưng, vẽ đồ thị |
| Dãy lọc ERB / Mel | Năng lượng theo băng tần | Tiền xử lý cảm thụ (DeepFilterNet dùng đặc trưng thang ERB) |

### Mặt nạ biên độ và deep filtering

- **Mặt nạ biên độ:** \(\hat{X}=M\odot|Y|e^{j\arg Y}\), tức giữ nguyên pha của tín hiệu nhiễu. Cách này nhẹ nhưng gây méo pha đáng kể khi SNR thấp.
- **Mặt nạ phức và lọc sâu (deep filtering):** dự đoán các hệ số lọc để kết hợp nhiều bin lân cận theo cả thời gian và tần số. Trong các bài báo DeepFilterNet, **deep filtering** áp bộ lọc học được trực tiếp lên phổ phức, nhờ đó khôi phục cấu trúc tín hiệu tốt hơn so với hệ số khuếch đại độc lập trên từng bin.

Chi tiết kiến trúc cụ thể sẽ được học qua các bài báo DeepFilterNet / 2 / 3 ở Chương 04. Ở bài này, điều cốt lõi cần nắm là: **mô hình đang chỉnh sửa một lưới STFT dưới ràng buộc nhân quả, sau đó biến đổi ISTFT để trả về dạng sóng.**

### Thực hành kiểm tra tái tạo hoàn hảo

Bài kiểm thử đơn vị bắt buộc trước khi bật mô hình: cho tín hiệu đi qua chuỗi STFT → ISTFT không qua khử nhiễu và kiểm tra đầu ra phải xấp xỉ tín hiệu gốc. Nếu phép biến đổi khứ hồi này chưa đúng thì phải dừng lại sửa ngay. Phần Mini-lab dưới đây thực hiện kiểm thử này trên sóng sin: sai số ở `float64` nằm quanh \(10^{-15}\) tại vùng giữa, còn sai số mức \(10^{-2}\) báo hiệu lỗi hàm cửa sổ hoặc bước nhảy hop và sẽ nghe rõ dưới dạng rung biên độ theo nhịp hop.

### Ánh xạ tham số từ bài báo sang hệ thống

Khi đọc tài liệu hoặc bài báo, hãy trích xuất đầy đủ: \(f_s\), dạng cửa sổ và độ dài \(L\) / kích thước FFT \(N\), bước nhảy hop \(R\), số khung nhìn trước nhân quả và giả định mono. Sau đó quy đổi sang mili giây và số hop/giây bằng các công thức của Chương 01–02 trước khi tích hợp `deepfilternet3-noise-filter` hay ONNX Runtime.

**Lưới STFT đã công bố của DeepFilterNet.** Framework hỗ trợ tần số lấy mẫu lên đến 48 kHz; cấu hình toàn băng công bố sử dụng \(N_{\mathrm{FFT}}=960\) (20 ms ở 48 kHz) với chồng lấp 50%, tức \(R=480\) (10 ms) — xem Schröter và cộng sự ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)) cùng cấu hình tham chiếu tại [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) (`sr=48000`, `fft_size=960`, `hop_size=480`). Hàm cửa sổ gắn liền với checkpoint đã huấn luyện nên hop và cửa sổ phải khớp tuyệt đối. Gói npm `deepfilternet3-noise-filter` 1.3.0 cũng tuân theo giao ước toàn băng 48 kHz này. Việc tự ý đổi sang hop 16 kHz, cửa sổ Blackman hay STFT ngoại tuyến căn giữa không hề "tăng chất lượng" mà sẽ cung cấp cho dãy lọc ERB một lưới khác hẳn lưới mà trọng số đã học.

Cấu hình công bố đó cũng ghi nhận độ trễ nhìn trước tích chập nhỏ (\(l_{\mathrm{DNN}}=2\) khung và \(l_{\mathrm{DF}}=1\) khung). Với hop 10 ms, các khung nhìn trước này cộng thêm vào độ trễ của cửa sổ 20 ms — hãy đối chiếu trực tiếp với cấu hình của checkpoint cụ thể.

## Ví dụ có số

Với 1 giây âm thanh ở 16 kHz, \(R=256\), \(N=512\) (FFT thực), lưới STFT có khoảng \(16000/256\approx 62\) khung (có thể lệch 1 tùy quy ước biên) và 257 bin không dư thừa. Tensor mặt nạ có thể có kích thước \([1,257,62]\) hoặc hoán đổi thứ tự trục tùy định nghĩa của mô hình.

Với 2 giây âm thanh ở 48 kHz, \(R=480\), \(N=960\), lưới STFT có khoảng \(96000/480=200\) khung và \(960/2+1=481\) bin thực — đây là kích thước mà tích hợp DeepFilterNet 48 kHz cần cấp phát, không phải 257 bin.

Ở các bin có SNR thấp, pha của hỗn hợp gần như trở thành pha ngẫu nhiên của nhiễu. Mặt nạ biên độ có thể hạ năng lượng nhiễu nhưng phần dư thường nghe bị méo "ướt"; phương pháp xử lý phổ phức cải thiện rõ rệt tình trạng này, dù vẫn có giới hạn trước nhiễu babble.

## Bẫy thường gặp

1. Bật chế độ căn giữa khung (center padding) khi chạy ngoại tuyến nhưng tắt khi chạy streaming.
2. Dùng bước nhảy hop lúc triển khai khác với lúc huấn luyện.
3. Đưa đặc trưng Mel vào mô hình được thiết kế cho thang ERB hoặc STFT tuyến tính.
4. Tính ISTFT hàng loạt trên toàn tệp trong môi trường thời gian thực, làm tăng vọt độ trễ.
5. Suy diễn các hằng số STFT nội bộ chưa được công bố của Mezon chỉ dựa vào nội dung khóa học.

## Mini-lab

**Mục tiêu.** Cho một sóng sin 440 Hz đi qua chuỗi STFT (có cửa sổ phân tích) và ISTFT cộng chồng lấp, sau đó in sai số tuyệt đối lớn nhất ở vùng giữa.

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

**Kết quả kỳ vọng.** `max abs error` cỡ \(10^{-15}\) (ngưỡng sai số `float64`), trong đó mảng tổng COLA `acc` bằng hằng số 1 trên toàn vùng giữa đúng như chứng minh ở bài 02-02.

**Lỗi thường gặp.** Quên chia cho `acc` sẽ làm đầu ra mất nửa biên độ hoặc bị gợn với sai số cỡ \(10^{-1}\); dùng Hann đối xứng hoặc nhân `w` thêm lần nữa ở khung nghịch sẽ tạo sai số tuần hoàn theo hop nghe rất rõ; đánh giá sai số ngay trên `L` mẫu đầu tiên (nơi `acc` chưa ổn định) sẽ làm sai số trông lớn bất thường dù vùng ổn định đã chính xác. Nếu đoạn mã này cho sai số lớn đáng kể, nguyên nhân là backend FFT không khứ hồi đúng chứ không phải vì COLA là tùy chọn.

## Bài tập nhỏ

1. Ước lượng kích thước lưới STFT cho đoạn âm thanh 2 giây ở 48 kHz với \(R=480\) và \(N=960\).
2. Giải thích vì sao việc tái sử dụng pha nhiễu trở nên kém hiệu quả khi SNR xuống sâu.
3. Liệt kê bốn tham số cần sao chép từ cấu hình DeepFilterNet vào danh mục kiểm tra tích hợp.
4. Khi điều kiện COLA bị vi phạm, âm thanh đầu ra sau ISTFT có biểu hiện như thế nào?
5. So với STFT tuyến tính, nêu một lý do khiến thang ERB được ưa chuộng trong phần tiền xử lý tăng cường tiếng nói.

### Gợi ý đáp án

1. Khoảng 200 khung thời gian và 481 bin tần số thực.
2. Ở SNR thấp, pha của tín hiệu hỗn hợp bị chi phối bởi pha ngẫu nhiên của nhiễu, nên ngay cả khi khôi phục hoàn hảo biên độ, tiếng nói vẫn bị điều biến méo.
3. Tần số lấy mẫu \(f_s\), kích thước FFT, bước nhảy hop và dạng hàm cửa sổ (kèm số khung nhìn trước nếu có tài liệu hóa; cấu hình công khai cần đối chiếu là 48 kHz, 960 và 480).
4. Xuất hiện rung biên độ (tremolo) ở tần số \(f_s/R\) (ví dụ 100 Hz với hop 10 ms).
5. Thang ERB tập trung mật độ dải tần cao hơn ở vùng tai người (và các formant tiếng nói) nhạy cảm, thay vì chia đều tuyến tính theo Hz.

## Đọc thêm

- Các bài báo DeepFilterNet, DeepFilterNet2, DeepFilterNet3 về STFT, đặc trưng ERB và deep filtering: bắt đầu tại [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) và kho mã [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Julius O. Smith, *Spectral Audio Signal Processing* — định nghĩa cặp STFT/ISTFT khớp hàm cửa sổ.
- Oppenheim & Schafer — mối liên hệ giữa dãy bộ lọc (filter bank) và STFT.

## Video tham khảo

- [Short-Time Fourier Transform Explained Easily](https://www.youtube.com/watch?v=-Yxj3yfvY-4) — Valerio Velardo - The Sound of AI, tiếng Anh. **Xem trước.** Trình bày khung phân tích và yêu cầu phép biến đổi nghịch phải hoàn tác chính xác bước phân tích — đúng giao ước STFT/ISTFT cho tiếng nói.
- [The Spectrogram and the Gabor Transform](https://www.youtube.com/watch?v=EfWnEldTyPA) — Steve Brunton, tiếng Anh. Minh họa cửa sổ trượt trên biến đổi Fourier tạo nên phổ đồ, giúp hình dung miền biểu diễn thời gian–tần số mà phần tiền xử lý DeepFilterNet giả định.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Quan sát luồng STFT đi vào dãy ERB và ISTFT đi ra — phần kết nối trực tiếp của bài học này với DeepFilterNet trước khi bàn đến hàm mất mát.
