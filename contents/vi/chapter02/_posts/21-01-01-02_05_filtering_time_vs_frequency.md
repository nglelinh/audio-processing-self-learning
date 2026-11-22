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

Khử nhiễu về bản chất là bài toán lọc trong điều kiện không chắc chắn. Đôi khi hệ thống dùng bộ lọc FIR/IIR ở miền thời gian, đôi khi nhân hệ số độ lợi trên từng bin STFT, và đôi khi mạng nơ-ron trực tiếp dự đoán các hệ số lọc đó. Bài học này đối chiếu hai miền xử lý để lựa chọn công cụ đúng mục đích: một đáp ứng xung cố định tương ứng với phép tích chập, còn độ lợi khử nhiễu theo bin là một hệ số thay đổi ở mỗi khung — như minh họa trong hình dưới đây.

## Mục tiêu học tập

1. Đối chiếu lọc LTI miền thời gian với phép nhân độ lợi trong miền STFT.
2. Phân biệt tích chập vòng với tích chập tuyến tính và giải thích vai trò của OLA/OLS.
3. Liên hệ độ lợi Wiener và trừ phổ cổ điển với bài toán lọc trên miền STFT.
4. Xác định các tác vụ mà xử lý miền thời gian vẫn vượt trội (chặn DC, phát hiện xung click).
5. Tránh các thao tác lọc làm phá vỡ điều kiện COLA trong chế độ streaming.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Ôn tập tích chập LTI và đáp ứng tần số |
| 12–28 | Độ lợi miền STFT dưới góc nhìn bộ lọc biến thiên theo thời gian |
| 28–42 | Tích chập nhanh qua FFT và kỹ thuật OLA/OLS |
| 42–52 | Ví dụ thực tế trong NS: lọc thông cao, độ lợi Wiener và mặt nạ mạng nơ-ron |
| 52–60 | Bài tập nhỏ |

![Trái: spectral subtraction từng bin, mỗi bin một gain. Phải: gain Wiener trơn theo SNR, vẫn là một hệ số mỗi bin chứ không phải một đáp ứng xung cố định]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Hình. Cả hai biểu đồ đều biểu diễn độ lợi theo từng bin chứ không phải một phép tích chập cố định: biểu đồ bên trái thay đổi theo phổ cục bộ, còn đường cong bên phải ánh xạ mỗi mức SNR sang một hệ số độ lợi tương ứng.*

## Giải thích cốt lõi

### Lọc LTI miền thời gian

$$
y[n]=(h*x)[n]=\sum_k h[k]x[n-k]
$$

Khi đáp ứng xung \(h\) cố định, phép lọc tương đương nhân DTFT của \(x\) với đáp ứng tần số \(H(e^{j\omega})\). Cách tiếp cận này phù hợp cho bộ chặn DC, cân bằng âm sắc (EQ) nhẹ hoặc lọc thông thấp chống aliasing. Tuy nhiên, riêng nó không đủ để xử lý nhiễu không dừng vì bài toán này đòi hỏi đặc tính lọc phải thích nghi theo thời gian.

Từ khóa then chốt ở đây là "cố định": một đáp ứng xung \(h\) chỉ cho ra duy nhất một đáp ứng \(H(k)\) cho toàn bộ câu nói. Bộ lọc sai phân bậc một \(h=[1,-1]\) là bộ lọc thông cao đơn giản, trong đó \(|H|\) không phân biệt khung hiện tại là nguyên âm hay tiếng gõ phím. Vì vậy, nó đứng *trước* bộ khử nhiễu để loại bỏ thành phần DC và tiếng ù tần số cực thấp chứ không thay thế bộ khử nhiễu.

### Xử lý nhân trong miền STFT

Ở mỗi khung, ta áp dụng \(\hat{X}(\ell,k)=G(\ell,k)Y(\ell,k)\). Nếu \(G\) biến thiên chậm, phép toán này xấp xỉ một bộ lọc biến thiên chậm theo thời gian. Ngược lại, nếu \(G\) nhảy đột ngột giữa các hop và các bin kề nhau, hệ thống sẽ sinh nhiễu nhạc và gây áp lực lên điều kiện COLA.

Các phương pháp **trừ phổ (spectral subtraction)** và **lọc Wiener** cổ điển (Chương 03) cung cấp công thức giải tích cho \(G\), còn mô hình mạng nơ-ron học cách dự đoán \(G\) (hoặc dự đoán bộ lọc sâu giàu biểu diễn hơn).

Trên hình minh họa, các cột xanh lá thể hiện phép trừ theo từng bin (mỗi bin nhận một hệ số riêng). Đường cong bên phải \(H=\xi/(1+\xi)\) đạt giá trị 0.5 (tương đương \(-6\,\mathrm{dB}\)) khi công suất tiếng nói và công suất nhiễu bằng nhau. Không biểu đồ nào trong hai hình là FFT của một bộ lọc FIR ngắn cố định.

### Tích chập qua FFT

Để thực hiện phép tích chập với một bộ lọc FIR dài \(h\) hiệu quả hơn, ta nhân phổ FFT với \(H\) rồi biến đổi iFFT — nhưng bắt buộc phải chia khối bằng **overlap-add (OLA)** hoặc **overlap-save (OLS)** để thu được tích chập *tuyến tính*. Nhân trực tiếp phổ STFT từng khung với một \(H\) cố định mà thiếu bước xử lý phù hợp không tự động tương đương với bộ lọc FIR đó ở miền thời gian do tác động rò phổ của hàm cửa sổ.

Xét ví dụ tích chập tuyến tính của một dãy tăng dần 8 điểm với \(h=[1,-1]\): kết quả tạo ra phần đuôi vượt quá 8 mẫu, trong khi tích chập vòng 8 điểm sẽ quấn phần đuôi này ngược về mẫu đầu tiên (lệch đúng 8 đơn vị trong Mini-lab). **OLA** giữ phần đuôi để cộng sang khối tiếp theo, còn **OLS** loại bỏ phần mép bị chồng chéo theo thời gian và chỉ giữ đoạn hợp lệ. Khi \(G(\ell,k)\) thay đổi theo từng hop, nó trở thành một bộ lọc biến thiên theo thời gian chứ không còn là bộ lọc FIR tĩnh.

### Lựa chọn miền xử lý

| Nhu cầu | Phương pháp phù hợp |
|---------|---------------------|
| EQ nhẹ hoặc chặn DC cố định | Bộ lọc IIR/FIR ngắn ở miền thời gian |
| Khử nhiễu không dừng | Miền STFT kèm \(G\) thích nghi hoặc mạng nơ-ron |
| Cổng chặn xung click, CPU rất thấp | Bộ phát hiện xung ở miền thời gian |
| Bộ lọc FIR dài (ví dụ mô phỏng vang) | Tích chập nhanh qua FFT bằng OLA/OLS |

### Liên hệ với DeepFilterNet

Kỹ thuật deep filtering dự đoán các hệ số lọc tác động trực tiếp lên các hệ số STFT phức theo cả lân cận tần số lẫn ngữ cảnh thời gian — vẫn là "lọc miền tần số", nhưng tổng quát hơn nhiều so với độ lợi đường chéo \(G(\ell,k)\). Độ lợi đường chéo không thể phục hồi một họa âm đã bị nhiễu che lấp, còn bộ lọc ngắn trải theo thời gian–tần số có thể khai thác thông tin pha từ các bin lân cận. Khóa học này bám sát pipeline kiểu DeepFilterNet trên miền STFT 48 kHz với kích thước hop và cửa sổ khớp checkpoint (bài 02-02 và 02-04).

## Ví dụ có số

Bộ chặn DC dạng rút gọn \(y[n]=x[n]-x[n-1]\) là bộ lọc thông cao có chi phí rất thấp, thường đặt trước khối khử nhiễu (dù tất nhiên không thể loại bỏ nhiễu babble quán cà phê). Đáp ứng của nó bằng 0 tại DC và đạt đỉnh tại Nyquist, với trễ nhóm (group delay) nhỏ hơn một mẫu nên không làm tiêu hao ngân sách độ trễ hội thoại như các bộ lọc FIR pha tuyến tính hàng trăm hệ số.

Mô hình giản lược của độ lợi Wiener:

$$
G(k)=\frac{P_x(k)}{P_x(k)+P_n(k)}
$$

Quy trình gồm ước lượng công suất từ biên độ STFT, nhân độ lợi rồi tính ISTFT. Phần khó nhất là ước lượng chính xác \(P_n\) trong môi trường nhiễu không dừng. Công thức trên tương ứng với đường cong bên phải trong hình (một hệ số cho mỗi bin ở mỗi khung); Chương 03 sẽ trình bày chi tiết chứng minh và bộ ước lượng decision-directed.

Nếu triệt tiêu ngẫu nhiên các bin ở từng hop mà không làm mượt, âm thanh sẽ sinh ra nhiễu nhạc kiểu "chim hót" (birdies), tương ứng ở miền thời gian với một đáp ứng xung biến đổi hỗn loạn. Tương tự, một bộ lọc FIR pha tuyến tính có trễ nhóm 30 ms cũng không phù hợp cho thoại trực tiếp: dù đáp ứng biên độ rất đẹp, độ trễ vẫn gây khó chịu trong hội thoại.

## Bẫy thường gặp

1. Đánh đồng phép nhân độ lợi trên STFT với một bộ lọc FIR tuyến tính chính xác.
2. Chạy bộ lọc FIR rất dài trực tiếp trên audio thread mà không tăng tốc bằng FFT.
3. Xếp chồng bộ lọc thông cao và bộ khử nhiễu mà không đo lượng thành phần tiếng nói bị suy hao.
4. Dùng bộ lọc FIR pha tuyến tính có trễ nhóm lớn trên đường thoại thời gian thực.
5. Thiết kế bộ lọc ngoại tuyến cho chất lượng cao nhưng quên ràng buộc nhân quả của thời gian thực.

## Mini-lab

**Mục tiêu.** Đối chiếu đáp ứng của một bộ lọc FIR cố định với độ lợi Wiener theo từng bin, đồng thời minh họa sự sai khác giữa tích chập vòng và tích chập tuyến tính.

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

**Kết quả kỳ vọng.** `fixed |H|` bắt đầu từ 0 (triệt tại DC) và tăng dần về phía Nyquist. `per-bin G` cho ra `[0.091, 0.231, 0.5, 0.75, 0.909]` — một đường đáp ứng hoàn toàn khác được tính từ SNR chứ không phải từ `h`. Tích chập tuyến tính kết thúc bằng `-8`, còn tích chập vòng quấn giá trị đuôi này vào mẫu đầu tiên, tạo độ lệch cực đại trên 8 mẫu đầu bằng `8.0`.

**Lỗi thường gặp.** Nếu độ lệch in ra bằng 0, nghĩa là bạn đã đệm số 0 cho cả `x` lẫn `h` nên vô tình tính tích chập tuyến tính và che mất lỗi mà OLA/OLS cần xử lý; nếu `G` trùng với `|H|`, vector SNR đã bị thay nhầm bằng bộ lọc FIR; và nếu bin đầu tiên của `|H|` khác 0 thì bộ lọc không phải bộ chặn DC `h=[1,-1]`.

## Bài tập nhỏ

1. Nêu một bộ lọc nên đặt ở miền thời gian trước khối khử nhiễu.
2. Vì sao độ lợi theo từng bin không được làm mượt dễ gây tiếng lách tách hoặc nhiễu nhạc?
3. Phân biệt OLA và OLS trong một câu.
4. Một bộ lọc FIR pha tuyến tính có trễ nhóm 30 ms có phù hợp cho đường gọi thoại thời gian thực không?
5. Viết biểu thức tổng quát cho thấy mặt nạ mạng nơ-ron vẫn đóng vai trò một phép lọc \(G(\ell,k)\).

### Gợi ý đáp án

1. Bộ chặn DC một điểm không, hoặc bộ lọc thông thấp chống aliasing trước khi giảm mẫu từ 48 kHz xuống 16 kHz.
2. Phép biến đổi nghịch ở mỗi hop tương ứng với một đáp ứng xung khác nhau, gây gián đoạn tại biên cộng chồng lấp OLA.
3. OLA giữ lại phần đuôi tích chập để cộng sang khối tiếp theo, trong khi OLS bỏ đi đoạn mép bị chồng chéo vòng và chỉ giữ phần hợp lệ.
4. Không phù hợp cho gọi thoại trực tiếp: riêng 30 ms đã chiếm phần lớn ngân sách độ trễ hội thoại trước cả khi tính đến bộ mã hóa và đường truyền mạng.
5. \(\hat{X}(\ell,k)=G(\ell,k)Y(\ell,k)\), trong đó \(G\) được dự đoán theo từng bin (hoặc mở rộng thành bộ lọc sâu ngắn trên vùng lân cận quanh bin đó).

## Đọc thêm

- Oppenheim & Schafer — thiết kế bộ lọc, tích chập qua FFT và xử lý STFT.
- Julius O. Smith, *Spectral Audio Signal Processing* — kỹ thuật overlap-add và overlap-save.
- Khử nhiễu tiếng nói cổ điển (Wiener / trừ phổ) làm cầu nối sang Chương 03: Boll (1979) là bài báo kinh điển về trừ phổ, còn bộ lọc Wiener cho tiếng nói sẽ được trình bày ở bài kế tiếp.

## Video tham khảo

- [But what is a convolution?](https://www.youtube.com/watch?v=KuXjwB4LzSA) — 3Blue1Brown, tiếng Anh. **Xem trước.** Trình bày trực quan định lý tích chập: lọc là phép trung bình có trọng số trượt ở miền thời gian và là phép nhân ở miền tần số — nền tảng cho việc chọn miền xử lý trong bài.
- [Spectral Subtraction In Python - Alexx Mitchell](https://www.youtube.com/watch?v=Xb--68NlxS0) — The Audio Programmer, tiếng Anh. Minh họa quy tắc chỉnh biên độ trên từng bin dựa theo ước lượng nhiễu, thể hiện rõ sự khác biệt với lọc FIR cố định.
- [Lec 22: Causal IIR Wiener Filter](https://www.youtube.com/watch?v=K_U0yeVdblU) — NPTEL IIT Guwahati, tiếng Anh. Trình bày dẫn xuất cổ điển của bộ lọc Wiener nhân quả (không riêng cho mặt nạ tiếng nói), cho thấy cách độ lợi suy giảm khi nhiễu tăng — nguyên lý trực tiếp đằng sau độ lợi theo bin trên STFT.
