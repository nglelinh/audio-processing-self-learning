---
layout: post
title: "01-01 Trực giác biến đổi Fourier liên tục"
chapter: "01"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Các kỹ thuật tăng cường tiếng nói chủ yếu hoạt động trên miền tần số hơn là trên dạng sóng thô. Bài học này xây dựng trực giác về biến đổi Fourier thời gian liên tục (CTFT) để các tham số STFT trong mã nguồn ở những chương sau trở nên minh bạch thay vì là những con số khó hiểu.

![Một sóng được tách thành vài sinusoid; cộng lại thì ra sóng ban đầu]({{ site.imgurl }}/generated/fourier-intuition.png)

*Hình. Tần số là một hệ tọa độ: mỗi hình sin là một thành phần cơ sở, và phép biến đổi đo lượng đóng góp của từng thành phần đó trong tín hiệu.*

## Mục tiêu học tập

1. Hiểu tần số như tốc độ dao động và như một tọa độ trong hệ cơ sở tín hiệu.
2. Trình bày cặp biến đổi CTFT thuận/nghịch cùng cơ chế phân tích–tổng hợp.
3. Vận dụng các tính chất tuyến tính và dịch thời gian trong phân tích kỹ thuật.
4. Liên hệ phổ biên độ và phổ pha với cảm nhận thính giác ở mức tổng quan.
5. Giải thích vì sao tiếng nói và nhiễu thường tách biệt rõ hơn ở miền tần số, đồng thời chỉ ra các trường hợp trực giác này không còn đúng.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–8 | Dẫn nhập: so sánh cùng một dạng sóng ở miền thời gian và miền tần số; lý giải vì sao các hệ thống VoIP ưu tiên xử lý phổ |
| 8–20 | Tín hiệu hình sin, công thức Euler và trực giác hàm riêng của hệ LTI |
| 20–35 | Cặp biến đổi CTFT, biên độ và pha, cùng ví dụ về tính tuyến tính và dịch thời gian |
| 35–48 | Formant tiếng nói so với nền nhiễu, ngộ nhận về pha và định hướng sang DeepFilterNet |
| 48–60 | Các bẫy thường gặp, bài tập nhỏ và giới thiệu bài lấy mẫu |

## Giải thích cốt lõi

### Tần số là một hệ tọa độ

Tín hiệu hàm mũ phức \(e^{j\Omega t}\) dao động với tần số góc \(\Omega\) rad/s (\(f=\Omega/(2\pi)\) Hz). Các hàm này là **hàm riêng của hệ tuyến tính bất biến theo thời gian (LTI)**: một bộ lọc LTI chỉ nhân mỗi hàm mũ phức với đáp ứng tần số \(H(j\Omega)\) mà không sinh ra tần số mới. Đây là lý do khử nhiễu miền tần số rất hiệu quả: dưới giả định nhiễu cộng tính và gần LTI trong thời gian ngắn, ta có thể làm suy hao các bin nhiễu và giữ lại các bin tiếng nói. Dù thực tế phức tạp hơn (nhiễu không dừng, sai số mặt nạ, lệch pha), bức tranh hàm riêng vẫn là nền tảng cho phần lớn bộ khử nhiễu cổ điển lẫn mạng nơ-ron miền STFT.

### Biến đổi Fourier thời gian liên tục

$$
X(j\Omega)=\int_{-\infty}^{\infty}x(t)e^{-j\Omega t}\,\mathrm{d}t
$$

$$
x(t)=\frac{1}{2\pi}\int_{-\infty}^{\infty}X(j\Omega)e^{j\Omega t}\,\mathrm{d}\Omega
$$

Phép **phân tích** đo mức đóng góp của từng tần số, còn phép **tổng hợp** tái tạo lại dạng sóng ban đầu. Viết \(X=|X|e^{j\phi}\), trong đó biên độ phản ánh phân bố năng lượng (formant, tiếng rít), còn pha mã hóa cấu trúc thời gian (đoạn khởi âm, cấu trúc cao độ pitch). Vì giao diện phổ đồ (spectrogram) thường chỉ hiển thị biên độ, người mới dễ hình thành thói quen sai lầm rằng "pha không quan trọng". Khi áp dụng mặt nạ khử nhiễu mạnh, việc xử lý pha hoặc phổ phức trở thành yếu tố thiết kế then chốt — cơ chế lọc sâu (deep filtering) trên phổ phức của DeepFilterNet ra đời một phần để khắc phục giới hạn của mặt nạ biên độ đơn thuần.

### Các tính chất thường dùng trong thực tế

- **Tuyến tính:** phổ của tổng tín hiệu cộng theo thang **tuyến tính**, không cộng trực tiếp theo dB.
- **Dịch thời gian:** một độ trễ theo thời gian tương ứng với một độ dốc tuyến tính của pha theo tần số.
- **Định lý Parseval:** việc loại bỏ một vùng phổ lớn *bắt buộc* làm giảm năng lượng của dạng sóng tương ứng.
- **Điều chế (modulation):** tương ứng với phép dịch phổ, giải thích cấu trúc các dãy hài của âm có cao độ tuần hoàn.

### Tiếng nói và nhiễu (mô hình giản lược)

Tiếng nói hữu thanh có kích thích gần tuần hoàn tại tần số cơ bản \(f_0\), kéo theo chuỗi họa âm \(kf_0\) được định hình bởi các đỉnh formant. Âm vô thanh phân bố năng lượng rộng ở tần số cao — nếu cắt tần số cao quá mạnh sẽ làm giảm độ rõ. Nhiễu dừng như hệ thống HVAC tập trung ở tần số thấp hoặc phẳng như tiếng quạt. Với nhiễu babble, phổ chồng lấn trực tiếp với tiếng nói nên cần mô hình hóa ngữ cảnh theo thời gian (RNN, TCN...) như trong các hệ thống tăng cường tiếng nói hiện đại.

### Cầu nối sang phần còn lại của Chương 01

Micro không cung cấp hàm liên tục mà cung cấp chuỗi mẫu rời rạc. Do đó, tích phân liên tục sẽ chuyển thành DTFT, DFT và FFT trên từng cửa sổ. Điều cốt lõi cần ghi nhớ là: **tần số đóng vai trò hệ số trong một cơ sở tín hiệu, còn mỗi bin STFT là ước lượng cục bộ, có cửa sổ hóa của hệ số đó.**

## Ví dụ có số

Xét tín hiệu gồm hai thành phần tần số \(x(t)=\cos(2\pi\cdot 440\,t)+0.3\cos(2\pi\cdot 880\,t)\). Công thức Euler cho thấy rõ cấu trúc phổ của tín hiệu này:

$$
\cos\theta=\frac{e^{j\theta}+e^{-j\theta}}{2}.
$$

Thành phần cosine 440 Hz tạo ra một cặp vạch phổ tại \(\pm 440\,\mathrm{Hz}\), mỗi vạch có biên độ phức \(1/2\); thành phần cosine 880 Hz tạo cặp vạch tại \(\pm 880\,\mathrm{Hz}\) với biên độ \(0.15\). Một bộ lọc thông thấp (LPF) cắt tại 600 Hz sẽ loại bỏ họa âm quãng tám 880 Hz và làm tối âm sắc (timbre) — các bộ khử nhiễu kiểu "lọc thông thấp để hết tiếng rít" mắc đúng lỗi này với phụ âm. Trên đường xử lý 48 kHz toàn băng (mặc định của `deepfilternet3-noise-filter`), các phụ âm cao tần vẫn được bảo toàn trên 8 kHz. Một độ trễ 5 ms tại 1 kHz tạo ra độ dịch pha \(-2\pi f t_0\). Ngoài ra, cần tránh sai lầm khi cộng theo thang dB: không thể viết "−20 dB + −20 dB = −40 dB" cho một phép trộn tuyến tính.

## Bẫy thường gặp

1. Coi phổ đồ biên độ là toàn bộ thông tin của tín hiệu.
2. Cộng trực tiếp các giá trị dB như cộng biên độ tuyến tính.
3. Nhầm lẫn giữa tần số góc \(\Omega\) (rad/s) và tần số \(f\) (Hz).
4. Cho rằng độ phân giải tần số càng cao càng tốt mà bỏ qua cái giá phải trả về độ trễ.
5. Kỳ vọng công thức tích phân CTFT xuất hiện nguyên dạng trong mã nguồn thực tế.

## Mini-lab

**Mục tiêu.** Tổng hợp tín hiệu dài 1 giây gồm ba sóng sin 200 Hz, 600 Hz và 1000 Hz ở tần số lấy mẫu 8 kHz, sau đó đọc chỉ số các bin đỉnh từ `rfft`. Khi chọn \(N=f_s\), chỉ số bin trùng khớp trực tiếp với tần số tính bằng Hz.

```python
import numpy as np

fs = 8000
t = np.arange(fs) / fs
x = (
    np.sin(2 * np.pi * 200 * t)
    + np.sin(2 * np.pi * 600 * t)
    + np.sin(2 * np.pi * 1000 * t)
)
mag = np.abs(np.fft.rfft(x))
order = np.sort(np.argsort(mag)[-3:])
print(order.tolist())
print(np.round(mag[order], 1).tolist())
```

**Kết quả kỳ vọng.** `[200, 600, 1000]` và `[4000.0, 4000.0, 4000.0]`. Mỗi sóng sin có biên độ 1 và chứa đúng một số nguyên chu kỳ trong cửa sổ nên năng lượng tập trung vào đúng một bin dương với biên độ \(N/2=4000\).

**Lỗi thường gặp.** Dùng `np.fft.fft` rồi báo cáo thêm chỉ số tần số âm như một đỉnh riêng biệt; chọn \(N\) không chứa số nguyên chu kỳ khiến đỉnh bị nhòe sang các bin xung quanh; hoặc nhầm lẫn giá trị 4000 với hệ số \(1/2\) của cosine trong ví dụ liên tục (tỷ lệ quy đổi của `rfft` cho sóng sin là \(N/2\)).

## Bài tập nhỏ

1. Biểu diễn \(\sin(\Omega t)\) bằng hàm mũ phức theo công thức Euler.
2. Với độ trễ 2 ms, hãy tính độ dịch pha tại 500 Hz và 2 kHz (trước khi gập pha về \([-\pi, \pi]\)).
3. Phác họa dạng phổ giản lược cho bốn loại tín hiệu: nguyên âm hữu thanh, nhiễu trắng, tiếng gõ bàn phím và nhiễu babble.
4. Viết một đoạn ngắn giải thích vì sao hàm mũ phức đặc biệt thuận tiện khi phân tích hệ LTI.
5. Nêu một tình huống mà xử lý ở miền thời gian có thể hiệu quả hơn trừ phổ cơ bản (gợi ý: xung click).

### Gợi ý đáp án

1. \(\sin\theta=(e^{j\theta}-e^{-j\theta})/(2j)\): gồm hai vạch phổ trái dấu với hệ số \(1/(2j)\).
2. Áp dụng \(\Delta\phi=-2\pi f t_0\): tại 500 Hz và 2 ms, độ dịch pha là \(-2\pi\) rad (đúng một vòng); tại 2 kHz là \(-8\pi\) rad (bốn vòng), trong khi biên độ không đổi.
3. Nguyên âm hữu thanh có chuỗi hài xếp theo đường bao formant; nhiễu trắng có phổ phẳng; xung click trải rộng trên toàn băng tần; babble giống như một chuỗi hài thứ hai chồng lấn phức tạp.
4. Bộ lọc LTI chỉ nhân \(e^{j\Omega t}\) với một hằng số phức \(H(j\Omega)\) và không sinh ra tần số mới; mọi sóng cosine đều có thể tách thành tổng của hai hàm riêng như vậy.
5. Một xung click kéo dài một mẫu sẽ trải năng lượng đều trên mọi bin tần số. Một cổng triệt xung ngắn ở miền thời gian có thể phát hiện và chặn nó ngay lập tức, trong khi bộ theo dõi nền nhiễu cập nhật chậm ở miền tần số sẽ bỏ lọt.

## Đọc thêm

- Oppenheim & Schafer, *Discrete-Time Signal Processing* — các chương tổng quan về biến đổi Fourier.
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — góc nhìn xem sóng sin là hệ cơ sở trước khi đi vào STFT.
- DeepFilterNet (arXiv:2110.05588) — khử nhiễu trên miền STFT kết hợp deep filtering (bài này cung cấp nền tảng động lực cho phương pháp đó).

## Video tham khảo

- [But what is the Fourier Transform?  A visual introduction.](https://www.youtube.com/watch?v=spUNpyF58BY) — 3Blue1Brown, tiếng Anh. **Xem trước.** Minh họa trực quan phép quấn tín hiệu trước khi đi vào tích phân: mỗi tần số là một tọa độ, đúng với trực giác của bài học này.
- [The more general uncertainty principle, regarding Fourier transforms](https://www.youtube.com/watch?v=MBnnXbOM5S4) — 3Blue1Brown, tiếng Anh. Phần phân tích sóng âm minh họa sự đánh đổi giữa thời gian và tần số trước khi chọn độ dài cửa sổ.
