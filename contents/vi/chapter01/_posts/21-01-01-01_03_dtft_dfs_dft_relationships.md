---
layout: post
title: "01-03 Hệ thống quan hệ DTFT, DFS và DFT"
chapter: "01"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Mã nguồn thực tế không bao giờ tính biến đổi DTFT vô hạn mà tính DFT hữu hạn (thông qua thuật toán FFT) trên từng cửa sổ nối tiếp nhau theo bước nhảy hop. Bài học này hệ thống hóa mối quan hệ DTFT ↔ DFS ↔ DFT để các siêu tham số STFT có ý nghĩa kỹ thuật rõ ràng.

![Các tone cơ sở DFT: lưới rời rạc mà FFT thực sự tính]({{ site.imgurl }}/generated/dft-basis.png)

*Hình. DFT không tính một đường cong phổ liên tục mà tính tích trong với các thành phần cơ sở phức rời rạc này, mỗi bin ứng với một tần số.*

## Mục tiêu học tập

1. Phân biệt DTFT (thời gian rời rạc, tần số liên tục) với DFT (lưới tần số hữu hạn).
2. Giải thích mối quan hệ tuần hoàn giữa miền thời gian và miền tần số ở mức trực giác kỹ thuật.
3. Đọc mỗi bin DFT như một mẫu rời rạc trên phổ của đoạn tín hiệu đã qua cửa sổ.
4. Phân biệt tác dụng của việc đệm số 0 (zero-padding) với độ phân giải tần số thực tế.
5. Vận dụng tính đối xứng liên hợp và hiểu đúng khái niệm "FFT N điểm" trong các hệ thống khử nhiễu.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Phân loại các phép biến đổi và vị trí của STFT |
| 12–28 | DTFT và góc nhìn cửa sổ hóa như phép tích chập trên miền tần số |
| 28–42 | Công thức DFT và thiết kế thí nghiệm kiểm chứng zero-padding |
| 42–52 | Tính đối xứng của tín hiệu thực và lưu ý về tích chập vòng |
| 52–60 | Bài tập gắn với cách chọn kích thước \(N\) theo hướng DeepFilterNet |

## Giải thích cốt lõi

| Tên | Miền thời gian | Miền tần số | Trong mã nguồn NS |
|-----|----------------|-------------|-------------------|
| CTFT | Liên tục | Liên tục | Lý thuyết |
| DTFT | Rời rạc vô hạn | Liên tục, chu kỳ \(2\pi\) | Lý thuyết |
| DFS | Rời rạc tuần hoàn | Rời rạc tuần hoàn | Ít gọi tên trực tiếp |
| DFT/FFT | Vector dài \(N\) | \(N\) bin | **Xuất hiện mọi nơi** |
| STFT | Các khung cửa sổ | DFT trên từng khung | **Xương sống của NS** |

$$
X[k]=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N}
$$

DFT thực chất là phép lấy mẫu DTFT của một dãy hữu hạn tại các điểm tần số \(\omega_k=2\pi k/N\). Thay trực tiếp vào tổng DTFT, ta thu được:

$$
X(e^{j\omega})\Big|_{\omega=2\pi k/N}
=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N}
=X[k].
$$

Phép lấy mẫu này không tạo thêm thông tin mới giữa các bin. Phép nhân từng phần tử giữa hai DFT tương ứng với **tích chập vòng (circular convolution)** độ dài \(N\) trong miền thời gian — vì vậy để thực hiện tích chập tuyến tính trên tín hiệu dài, hệ thống cần các sơ đồ như OLA hoặc OLS.

Cắt đoạn tín hiệu bằng cửa sổ chữ nhật dài \(L\) gây hiện tượng nhòe phổ (spectral smearing) với độ rộng búp chính (main lobe) tỷ lệ khoảng \(1/L\). Đệm số 0 (zero-padding) chỉ làm dày thêm các điểm lấy mẫu của DTFT chứ **không** cải thiện độ phân giải tần số thực của đoạn quan sát.

Với tín hiệu đầu vào thực, phổ thỏa mãn tính đối xứng liên hợp \(X[k]=X^*[N-k]\), nên phần thông tin không dư thừa chỉ nằm trong các bin \(0..N/2\). Việc thay đổi kích thước \(N\) giữa giai đoạn huấn luyện và giai đoạn suy luận trên một mô hình tạo mặt nạ mạng nơ-ron là lỗi cấu hình nghiêm trọng.

Ví dụ: ở \(f_s=48\,\mathrm{kHz}\) với \(N=960\) (20 ms), khoảng cách giữa hai bin là \(\Delta f=50\,\mathrm{Hz}\); ở 16 kHz với \(N=512\), ta có \(\Delta f=31.25\,\mathrm{Hz}\).

## Ví dụ có số

Ở tần số lấy mẫu 16 kHz với \(N=512\), thành phần 1 kHz rơi đúng vào bin 32 vì \(1000/31.25=32\); tuy nhiên năng lượng vẫn có thể lan sang các bin kế cận do búp phổ của cửa sổ, nên mặt nạ khử nhiễu cần có độ mượt theo tần số. Xét 64 mẫu của âm đơn 1 kHz ở 16 kHz: tín hiệu đi hết \(1000\times 64/16000=4\) chu kỳ, nên DFT 64 điểm đạt đỉnh tại bin 4. Khi đệm số 0 lên 512 điểm, chính 64 mẫu đó sẽ đạt đỉnh tại bin 32. Bước nhảy tần số giữa các bin giảm từ 250 Hz xuống 31.25 Hz, nhưng độ rộng búp chính tính theo Hz vẫn bị giới hạn bởi 64 mẫu quan sát ban đầu (cỡ 250 Hz). Ở tần số mặc định 48 kHz, bẫy tương tự xảy ra khi đệm số 0 một khung 10 ms rồi cho rằng bước bin mịn hơn mang lại "độ phân giải pitch tốt hơn" trong khi thời lượng quan sát thực tế từ micro không hề tăng.

## Bẫy thường gặp

1. Hiểu nhầm zero-padding là kỹ thuật siêu phân giải tần số.
2. Quên sự khác biệt giữa tích chập vòng và tích chập tuyến tính.
3. So sánh biên độ \(|X[k]|\) ở các kích thước \(N\) khác nhau mà không chuẩn hóa.
4. Làm phá vỡ tính đối xứng liên hợp của phổ rồi gọi iFFT và chỉ giữ lại phần thực.
5. Dùng hai giá trị \(N\) khác nhau giữa lúc huấn luyện và lúc triển khai.

## Mini-lab

**Mục tiêu.** So sánh kết quả DFT 64 điểm của âm đơn 1 kHz ở 16 kHz với chính 64 mẫu đó sau khi đệm số 0 lên 512 điểm.

```python
import numpy as np

fs, n_win = 16_000, 64
n = np.arange(n_win)
tone = np.cos(2 * np.pi * 1000 * n / fs)
peak64 = int(np.argmax(np.abs(np.fft.rfft(tone))))
peak512 = int(np.argmax(np.abs(np.fft.rfft(tone, n=512))))
print(peak64, peak512, fs / n_win, fs / 512)
```

**Kết quả kỳ vọng.** `4 32 250.0 31.25`. Chỉ số đỉnh thay đổi do lưới tần số dày hơn, nhưng độ dài đoạn quan sát thực tế không đổi.

**Lỗi thường gặp.** Diễn giải đỉnh tại bin 32 ở \(N=512\) là "tín hiệu sắc nét hơn"; so sánh trực tiếp chiều cao đỉnh `|rfft|` giữa hai kích thước mà không thống nhất chuẩn hóa; hoặc quên rằng sóng cosine đúng bin vẫn có một thành phần đối xứng ở tần số âm mà `rfft` không hiển thị riêng.

## Bài tập nhỏ

1. Tìm chỉ số bin gần 1 kHz nhất ở \(f_s=16\,\mathrm{kHz}\) với \(N=512\).
2. Tóm tắt trong một câu sự khác nhau giữa zero-padding và tăng độ dài cửa sổ.
3. Giữa một âm đơn rơi đúng bin và một âm đơn nằm giữa hai bin, trường hợp nào gây rò phổ nhiều hơn khi dùng cửa sổ chữ nhật?
4. Vì sao STFT cần bước nhảy hop \(R<N\) thay vì chỉ tính các khối DFT rời nhau không chồng lấp?
5. Nếu trọng số mô hình yêu cầu đầu vào gồm 513 bin biên độ, kích thước \(N\) của real-FFT là bao nhiêu?

### Gợi ý đáp án

1. Khoảng cách bin là \(\Delta f=16000/512=31.25\,\mathrm{Hz}\), nên 1 kHz rơi chính xác vào bin \(32\).
2. Zero-padding chỉ nội suy dày thêm các điểm mẫu trên cùng một DTFT, còn kéo dài cửa sổ mới thực sự thu hẹp búp chính của phổ.
3. Âm đơn rơi đúng bin trùng khớp với một vector cơ sở nên dưới cửa sổ chữ nhật chỉ tập trung vào một bin duy nhất; âm nằm giữa hai bin bị gián đoạn khi nối tuần hoàn nên sinh ra rò phổ.
4. Bước nhảy \(R<N\) tạo vùng chồng lấp giúp phép ISTFT thỏa điều kiện cộng chồng lấp không đổi (COLA); các khối DFT nối tiếp với \(R=N\) sẽ để lại vết gián đoạn ở biên khung.
5. Phép real-FFT lưu giữ \(N/2+1\) bin không dư thừa, do đó 513 bin tương ứng với \(N=1024\).

## Đọc thêm

- Oppenheim & Schafer — mối quan hệ giữa DTFT, DFS và DFT.
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — trình bày chi tiết về DFT, DTFT và zero-padding.
- DeepFilterNet (arXiv:2110.05588) và kho mã nguồn https://github.com/Rikorose/DeepFilterNet cho cấu hình độ dài khung thực tế; tài liệu công khai của RNNoise là mốc đối chiếu cho cấu hình FFT ngắn hơn.

## Video tham khảo

- [Chương 3.1: Biến đổi Fourier rời rạc (DFT)](https://www.youtube.com/watch?v=bC5umvKV8bE) — Tín hiệu và hệ thống UEt, tiếng Việt. **Xem trước.** Bài giảng tiếng Việt về tổng DFT, hữu ích khi đối chiếu song song với tài liệu tiếng Anh trong khóa.
- [The Discrete Fourier Transform (DFT)](https://www.youtube.com/watch?v=nl9TZanwbBk) — Steve Brunton, tiếng Anh. Trình bày DFT như chuỗi Fourier hữu hạn thay vì tích phân vô hạn, làm rõ bản đồ quan hệ DTFT–DFS–DFT trong bài.
- [Computing the DFT Matrix](https://www.youtube.com/watch?v=Xw4voABxU5c) — Steve Brunton, tiếng Anh. Minh họa ma trận lấy mẫu các thành phần tần số trong định nghĩa DFT, chuyển tổng hữu hạn thành phép tích trong trên từng bin.
