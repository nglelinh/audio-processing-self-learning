---
layout: post
title: "01-04 DFT như ma trận / cơ sở trực chuẩn"
chapter: "01"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Gỡ lỗi các hệ thống khử nhiễu đòi hỏi nhìn nhận DFT như một phép đổi cơ sở bảo toàn năng lượng (theo định lý Parseval), thay vì chỉ là một biểu đồ màu trực quan. Bài học này kết nối tính trực giao, dạng ma trận, cách đánh chỉ số bin và hiện tượng rò phổ.

![Tám tone cơ sở DFT: hệ tọa độ của biến đổi dài N]({{ site.imgurl }}/generated/dft-basis.png)

*Hình. Mỗi hàng của ma trận DFT là một thành phần tần số phức như minh họa; mỗi bin phổ là tích trong giữa khung tín hiệu và hàng tương ứng.*

## Mục tiêu học tập

1. Hiểu DFT dưới góc nhìn phép chiếu lên hệ cơ sở hàm mũ phức.
2. Viết DFT ở dạng ma trận và phân biệt quy ước chuẩn hóa unitary với quy ước không chuẩn hóa.
3. Sử dụng phép kiểm tra năng lượng theo Parseval để xác thực pipeline STFT/ISTFT.
4. Chuyển đổi thành thạo giữa chỉ số bin, tần số Hz và tần số chuẩn hóa.
5. Dự đoán và nhận diện hiện tượng rò phổ khi tín hiệu hình sin rơi lệch bin.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Tính trực giao của hàm mũ phức và góc nhìn tích trong |
| 12–28 | Ma trận \(\mathbf{F}\), hệ số chuẩn hóa unitary và quy ước giữa các thư viện |
| 28–42 | Quy đổi bin ↔ Hz, thành phần DC/Nyquist và tần số âm |
| 42–52 | Rò phổ khi lệch bin và thiết kế bài thực hành âm đơn + nhiễu |
| 52–60 | Bài tập và danh mục kiểm tra |

## Giải thích cốt lõi

Các vector cơ sở \(w_k[n]=e^{j2\pi kn/N}\) trực giao với nhau theo quan hệ \(\langle w_k,w_\ell\rangle=N\delta_{k\ell}\). Tổng cấp số nhân \(\sum_{n=0}^{N-1}e^{j2\pi(k-\ell)n/N}\) bằng \(N\) khi \(k\equiv\ell\pmod N\) và bằng 0 trong các trường hợp còn lại — đó chính là giá trị tích trong. Nhờ vậy, phép phân tích là \(X[k]=\langle x,w_k\rangle\), còn phép tổng hợp cần chia cho \(N\).

$$
\mathbf{X}=\mathbf{F}\mathbf{x},\quad F_{kn}=e^{-j2\pi kn/N}
$$

Nhiều thư viện FFT áp dụng quy ước: biến đổi thuận không chia, còn biến đổi nghịch chia cho \(1/N\) (hoặc ngược lại) — **lỗi hệ số tỷ lệ trong ISTFT** là một trong những lỗi âm thầm dễ làm hỏng chất lượng âm thanh nhất. Đặt \(\mathbf{U}=\mathbf{F}/\sqrt{N}\); do \(\mathbf{U}\) là ma trận trực chuẩn nên \(\|\mathbf{Ux}\|=\|\mathbf{x}\|\). Phép DFT không chuẩn hóa của NumPy thỏa \(\mathbf{X}=\sqrt{N}\,\mathbf{Ux}\), suy ra đẳng thức Parseval:

$$
\sum_n|x[n]|^2=\frac{1}{N}\sum_k|X[k]|^2.
$$

Nếu bước biến đổi nghịch đã chia \(N\) mà khâu cộng chồng lấp OLA lại chia thêm \(N\) lần nữa, biên độ sóng 48 kHz toàn băng sẽ suy giảm sai lệch ở mỗi hop. Lưu ý rằng `setSuppressionLevel` trên `DeepFilterNoiseFilterProcessor` không kiểm tra lỗi này: tham số đó chỉ điều chỉnh mức khử nhiễu, không tự kiểm định định lý Parseval cho đoạn STFT mà bạn tự cài đặt bên ngoài.

$$
f_k=\frac{k}{N}f_s
$$

Trong đó, \(k=0\) là thành phần một chiều (DC), \(k=N/2\) (với \(N\) chẵn) là tần số Nyquist, và \(k>N/2\) là vùng tần số âm của tín hiệu thực. Nếu một sóng sin không chứa đúng số nguyên chu kỳ trong khung, phép nối tuần hoàn sẽ tạo điểm gián đoạn ở biên, sinh ra các búp phụ (sidelobe) gây hiện tượng rò phổ (spectral leakage); việc áp dụng hàm cửa sổ sẽ giúp hạ búp phụ nhưng đánh đổi bằng việc nới rộng búp chính (xem Chương 02).

## Ví dụ có số

Ở tần số 48 kHz với \(N=1024\), khoảng cách giữa hai bin là \(\Delta f\approx46.875\,\mathrm{Hz}\). Nhiễu hệ thống HVAC quanh 100 Hz nằm gần các bin 2–3. Nếu mặt nạ chỉ triệt tiêu bin 2 mà giữ nguyên các bin 3–10 thì gần như không mang lại hiệu quả; hệ số độ lợi cần biến thiên mượt sang các bin lân cận.

Với một đoạn nhiễu trắng phương sai đơn vị dài 256 mẫu, năng lượng miền thời gian xấp xỉ 256; tổng \(\sum|X|^2\approx 65536\) khi dùng DFT không chuẩn hóa, và sau khi chia cho \(N=256\) sẽ khớp với đẳng thức Parseval.

Xét vector \(x=[1,0,-1,0]\), tương ứng với \(\cos(2\pi n/4)\): tín hiệu hoàn thành đúng một chu kỳ trong 4 mẫu, tức rơi vào bin \(k=1\). Phép DFT không chuẩn hóa cho \(X[1]=X[3]=2\) và hai bin còn lại bằng 0. Năng lượng miền thời gian bằng 2, còn năng lượng miền tần số là \((4+4)/4=2\). Bài tập 1 vẫn yêu cầu viết đầy đủ ma trận \(\mathbf{F}\); ví dụ này chỉ minh họa nhanh hai đỉnh phổ và định lý Parseval.

## Bẫy thường gặp

1. Chia hệ số chuẩn hóa \(1/N\) hai lần liên tiếp.
2. Coi nửa phổ đối xứng gương như chứa thêm thông tin độc lập gấp đôi.
3. Chỉnh sửa một nửa phổ nhưng không cập nhật phần đối xứng liên hợp tương ứng.
4. So sánh trực tiếp kết quả FFT giữa các thư viện hoặc ngôn ngữ khác nhau (NumPy, FFTW...) mà không đối chiếu quy ước chuẩn hóa.
5. Dùng trực tiếp `|X|**2` để ước lượng mật độ phổ công suất (PSD) mà quên chuẩn hóa theo công suất của hàm cửa sổ.

## Mini-lab

**Mục tiêu.** Xây dựng trực tiếp ma trận DFT dài 8 và kiểm chứng tính đối xứng liên hợp cùng đẳng thức Parseval trên một vector thực.

```python
import numpy as np

N = 8
n = np.arange(N)
F = np.exp(-2j * np.pi * np.outer(n, n) / N)
x = np.array([1.0, -0.5, 0.25, 0.0, 0.1, -0.2, 0.3, -0.1])
X = F @ x
sym = np.max(np.abs(X - np.conj(X[(N - n) % N])))
energy_time = np.sum(np.abs(x) ** 2)
energy_freq = np.sum(np.abs(X) ** 2) / N
print(f"sym={sym:.3e}")
print(f"time={energy_time:.6f} freq={energy_freq:.6f}")
```

**Kết quả kỳ vọng.** `sym` nhỏ hơn `1e-12` (khoảng `1.200e-15`), và cả hai giá trị năng lượng đều in ra `1.462500`.

**Lỗi thường gặp.** Dùng dấu mũ dương \(e^{+j2\pi kn/N}\) rồi đem so sánh với `numpy.fft.fft` mà không để ý quy ước dấu (trong bài thực hành này ta không gọi FFT của NumPy; tính đối xứng và Parseval vẫn đúng với ma trận \(F\) đã định nghĩa); quên chia `/ N` trong công thức Parseval rồi "sửa chắp vá" bằng cách chia năng lượng miền thời gian; hoặc chỉnh sửa `X[1]` mà không cập nhật cặp liên hợp `X[7]` rồi kỳ vọng biến đổi nghịch cho ra tín hiệu thực.

## Bài tập nhỏ

1. Với \(N=4\), hãy viết tường minh ma trận \(\mathbf{F}\).
2. Với \(k=32\), \(f_s=16\,\mathrm{kHz}\) và \(N=256\), bin này tương ứng với tần số bao nhiêu Hz?
3. Vì sao một âm đơn rơi lệch bin lại trải rộng trên nhiều bin khi dùng cửa sổ chữ nhật?
4. Thiết kế một bài kiểm thử đơn vị (unit test) khoảng 5 dòng dựa trên định lý Parseval cho hàm bọc FFT.
5. Nếu bin DC có giá trị rất lớn, triệu chứng tương ứng ở miền thời gian là gì?

### Gợi ý đáp án

1. Phần tử ở hàng \(k\), cột \(n\) là \(e^{-j2\pi kn/4}\); cụ thể hàng 0 gồm toàn số 1, hàng 2 là \([1,-1,1,-1]\).
2. Tần số tương ứng là \(f=32\times 16000/256=2000\,\mathrm{Hz}\).
3. Khi nối tuần hoàn sẽ xuất hiện bước nhảy tại biên khối nên sóng sin không trùng với một vector cơ sở duy nhất; đáp ứng dạng hàm sinc của cửa sổ chữ nhật làm năng lượng trải rộng ra nhiều bin.
4. Tạo một vector thực, so sánh \(\sum|x|^2\) với \((\sum|X|^2)/N\), và khẳng định độ lệch tuyệt đối nhỏ hơn `1e-6` theo đúng quy ước chuẩn hóa của thư viện.
5. Bin DC lớn đồng nghĩa với giá trị trung bình của tín hiệu khác 0 đáng kể (dạng sóng bị dịch khỏi trục 0); cần kiểm tra bộ chặn DC (DC blocker) hoặc độ lệch tĩnh (bias) của micro trước tiên.

## Đọc thêm

- Oppenheim & Schafer — các tính chất của DFT và định lý Parseval.
- Tài liệu hướng dẫn các thư viện FFT (phần cờ chuẩn hóa).
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — ma trận DFT, tính trực giao và định lý Parseval.

## Video tham khảo

- [Computing the DFT Matrix](https://www.youtube.com/watch?v=Xw4voABxU5c) — Steve Brunton, tiếng Anh. **Xem trước.** Trình bày trực quan ma trận DFT có các hàng là thành phần tần số phức, xem mỗi bin là một tích trong đúng với góc nhìn đổi cơ sở của bài.
- [The Discrete Fourier Transform (DFT)](https://www.youtube.com/watch?v=nl9TZanwbBk) — Steve Brunton, tiếng Anh. Phần mở đầu xây dựng phép nhân ma trận trước khi nói đến thuật toán tăng tốc FFT — đúng đối tượng bạn cần nắm vững khi gỡ lỗi.
- [Chương 3.1: Biến đổi Fourier rời rạc (DFT)](https://www.youtube.com/watch?v=bC5umvKV8bE) — Tín hiệu và hệ thống UEt, tiếng Việt. Bài giảng tiếng Việt về tổng DFT, thích hợp để kết hợp cùng video ma trận khi cần kiểm tra cách đánh chỉ số bin.
