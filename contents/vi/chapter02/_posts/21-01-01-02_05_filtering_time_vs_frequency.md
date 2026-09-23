---
layout: post
title: "02-05 Lọc miền thời gian và miền tần số"
chapter: "02"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Khử nhiễu là lọc trong điều kiện không chắc. Đôi khi bạn dùng FIR/IIR miền thời gian; đôi khi nhân từng bin STFT; đôi khi mạng dự đoán các phép nhân đó. Bài này so hai miền để chọn công cụ có chủ đích. Một đáp ứng xung cố định là tích chập. Gain khử nhiễu theo bin là một hệ số mới mỗi frame, và hình ở chương 03 chính là đối tượng thứ hai.

## Mục tiêu học tập

1. Đối chiếu lọc LTI miền thời gian với gain nhân trong miền STFT.
2. Giải thích tích chập vòng và tuyến tính, và vì sao có OLA/OLS.
3. Nối gain Wiener / spectral subtraction cổ điển với lọc STFT.
4. Nêu khi nào miền thời gian vẫn thắng (chặn DC, heuristic chặn click).
5. Tránh các phép “lọc” làm vỡ COLA streaming.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Ôn tích chập LTI; đáp ứng tần số |
| 12–28 | Gain miền STFT như lọc biến thiên theo thời gian |
| 28–42 | Tích chập qua FFT; OLA/OLS |
| 42–52 | Ví dụ NS: high-pass, gain Wiener, mask neural |
| 52–60 | Bài tập |

![Trái: spectral subtraction từng bin, mỗi bin một gain. Phải: gain Wiener trơn theo SNR, vẫn là một hệ số mỗi bin chứ không phải một đáp ứng xung cố định]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Hình. Cả hai panel là gain theo bin, không phải một tích chập: cột bên trái đổi theo phổ cục bộ, đường bên phải gán một hệ số khác cho mỗi SNR.*

## Giải thích cốt lõi

### Lọc LTI miền thời gian

$$
y[n]=(h*x)[n]=\sum_k h[k]x[n-k]
$$

Đáp ứng tần số \(H(e^{j\omega})\) nhân DTFT của \(x\) khi \(h\) cố định. Hợp cho chặn DC, EQ kệ nhẹ, low-pass chống alias. Một mình thì không đủ cho nhiễu không dừng, vì nhiễu đó cần hành vi đổi theo thời gian.

“Cố định” là từ chịu lực. Một \(h\) có một \(H(k)\) cho cả câu. Sai phân bậc một \(h=[1,-1]\) là high-pass viết trong một dòng, và \(|H|\) không quan tâm frame này là nguyên âm hay tiếng phím. Nó đứng *trước* suppressor như bước bỏ DC/rumble, không thay suppressor.

### Xử lý nhân trong miền STFT

Mỗi frame: \(\hat{X}(\ell,k)=G(\ell,k)Y(\ell,k)\). Nếu \(G\) đổi chậm, đây xấp xỉ một lọc biến thiên chậm. Nếu \(G\) nhảy từng hop, từng bin, bạn gặp musical noise và COLA bị căng.

**Spectral subtraction** và **Wiener** cổ điển (chương 03) là công thức cho \(G\). Mask neural học \(G\) (hoặc deep filter giàu hơn).

Cột xanh lá là phép trừ theo bin (mỗi bin một gain). Đường bên phải \(H=\xi/(1+\xi)\) bằng 0.5 khi công suất tiếng nói và nhiễu bằng nhau (\(-6\,\mathrm{dB}\)). Không panel nào là FFT của một \(h\) ngắn cố định.

### Tích chập qua FFT

Muốn áp FIR dài \(h\) cho rẻ: nhân FFT với \(H\), rồi iFFT — nhưng phải chia khối bằng **overlap-add** (OLA) hoặc **overlap-save** (OLS) thì mới ra tích chập *tuyến tính*. Nhân STFT từng frame với một \(H\) cố định mà không cẩn thận thì không luôn trùng FIR đó trong miền thời gian — cửa sổ gây rò.

Tích chập tuyến tính của một dốc 8 điểm với \(h=[1,-1]\) có đuôi; tích chập vòng 8 điểm quấn đuôi đó vào mẫu 0 (mini-lab lệch 8). **OLA** giữ đuôi và cộng vào khối sau. **OLS** bỏ mép bị alias thời gian và hop theo phần hợp lệ. \(G(\ell,k)\) đổi mỗi hop là một lọc biến thiên theo thời gian khác, không tự động là FIR đó.

### Chọn miền

| Nhu cầu | Nên dùng |
|---------|----------|
| EQ nhẹ / bỏ DC, cố định | IIR/FIR ngắn miền thời gian |
| NS không dừng | STFT + \(G\) thích nghi hoặc neural |
| Cổng click, CPU cực thấp | detector miền thời gian |
| FIR vang dài | tích chập FFT kiểu OLA/OLS |

### Nối DeepFilterNet

Deep filtering dự đoán bộ lọc trên các hệ số STFT phức, theo tần số và ngữ cảnh thời gian — vẫn là “lọc miền tần số”, nhưng giàu hơn đường chéo \(G(\ell,k)\). Gain đường chéo không dựng lại một hài mà nhiễu đã xóa; một lọc ngắn theo thời gian hoặc tần số có thể trộn các láng giềng còn cấu trúc pha. Khóa học này bám pipeline kiểu DeepFilterNet, STFT, 48 kHz, hop và cửa sổ khớp checkpoint (bài 02-02 và 02-04).

## Ví dụ có số

Bộ chặn DC \(y[n]=x[n]-x[n-1]\) (dạng rút gọn) thì high-pass, rẻ, đặt trước NS. Nó không xóa babble quán cà phê. Null ở DC, đỉnh ở Nyquist. Group delay chỉ một phần mẫu, không ăn ngân sách trễ hội thoại như FIR pha tuyến tính hàng trăm tap.

Hoạt hình Wiener:

$$
G(k)=\frac{P_x(k)}{P_x(k)+P_n(k)}
$$

Ước lượng công suất từ biên độ STFT, nhân gain, ISTFT. Phần khó là ước lượng \(P_n\) không dừng. Đây là đường bên phải của hình, một số mỗi bin mỗi frame. Chương 03 mới chứng minh và đưa bộ theo dõi decision-directed.

Xóa bin ngẫu nhiên mỗi hop, không làm mượt, thì ra birdies. Tương đương miền thời gian là một đáp ứng xung nhảy loạn. Cũng không hợp đường gọi: FIR pha tuyến tính group delay 30 ms. Đáp ứng biên độ có thể đẹp mà cuộc nói vẫn thấy trễ.

## Bẫy thường gặp

1. Coi nhân gain STFT ≡ một FIR tùy ý, chính xác.
2. FIR rất dài trên audio thread mà không tăng tốc bằng FFT.
3. Xếp high-pass + NS mà không đo phần tiếng nói bị mất.
4. FIR pha tuyến tính, group delay lớn, trên đường gọi.
5. Quên nhân quả realtime khi thiết kế lọc offline “hay”.

## Mini-lab

**Mục tiêu.** Đối chiếu một FIR cố định (tích chập) với gain Wiener theo bin, và thấy tích chập vòng không khớp tích chập tuyến tính.

```python
import numpy as np

h = np.array([1.0, -1.0])
H = np.abs(np.fft.rfft(h, n=8))
print("fixed |H|", np.round(H, 3))

xi = np.array([0.1, 0.3, 1.0, 3.0, 10.0])  # SNR tiên nghiệm, năm bin
G = xi / (xi + 1.0)
print("per-bin G", np.round(G, 3))

x = np.arange(1, 9, dtype=float)
y_lin = np.convolve(x, h)
h_pad = np.zeros(8)
h_pad[:2] = h
y_circ = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(h_pad), n=8)
print("linear   ", y_lin)
print("circular ", np.round(y_circ, 5))
print("max |linear[:8] - circular|", np.max(np.abs(y_lin[:8] - y_circ)))
```

**Kỳ vọng.** `fixed |H|` bắt đầu bằng 0 (null ở DC) và tăng về phía Nyquist. `per-bin G` khoảng `[0.091, 0.231, 0.5, 0.75, 0.909]` — một hình dạng khác, tính từ SNR, không phải từ `h`. Tích chập tuyến tính kết thúc bằng `-8`; tích chập vòng quấn đuôi đó vào mẫu đầu. Độ lệch tuyệt đối lớn nhất trên 8 mẫu đầu là `8.0`.

**Khi hỏng.** Nếu độ lệch in ra 0, bạn đã zero-pad cả `x` lẫn `h` và vô tình tính tích chập tuyến tính; bug mà OLA/OLS phải sửa bị giấu. Nếu `G` bằng `|H|`, vector SNR đã bị thay bằng FIR. Bộ chặn DC mà bin đầu của `|H|` không phải 0 thì không phải `h=[1,-1]`.

## Bài tập nhỏ

1. Một lọc nên làm miền thời gian trước NS.
2. Vì sao gain per-bin không làm mượt gây click/twitter?
3. OLA vs OLS: một câu phân biệt.
4. Group delay 30 ms từ FIR pha tuyến tính — an toàn cho gọi?
5. Phác neural mask vẫn là lọc \(G(\ell,k)\).

### Gợi ý đáp án

1. Bộ chặn DC một zero, hoặc low-pass chống alias trước khi hạ 48→16 kHz.
2. Biến đổi ngược của mỗi hop là một đáp ứng xung khác, nên biên OLA bị nhảy.
3. OLA giữ đuôi tích chập và cộng vào khối sau; OLS bỏ mép bị alias thời gian và hop theo phần hợp lệ.
4. Không an toàn cho cuộc gọi trực tiếp: 30 ms đã là độ trễ hội thoại, trước cả encoder và mạng.
5. \(\hat{X}(\ell,k)=G(\ell,k)Y(\ell,k)\), với \(G\) được dự đoán theo bin (hoặc một deep filter ngắn quanh bin đó).

## Đọc thêm

- Oppenheim & Schafer — lọc, tích chập FFT, xử lý STFT.
- Julius O. Smith, *Spectral Audio Signal Processing* — overlap-add và overlap-save.
- Tăng cường tiếng nói cổ điển (Wiener / spectral subtraction) là cầu sang chương 03. Boll, 1979, là bài kinh điển của phép trừ phổ; dạng Wiener cho tiếng nói là bài sau.
