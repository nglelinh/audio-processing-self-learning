---
layout: post
title: "02-06 Spectrogram: đọc tiếng nói và nhiễu"
chapter: "02"
order: 6
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Spectrogram là ngôn ngữ chung của kỹ sư tiếng nói. Bài này luyện đọc cấu trúc tiếng nói, loại nhiễu, và artifact của NS trên hình — và tránh thang dB nói dối. Spectrogram không phải “bức ảnh của audio”. Nó là \(|X(\ell,k)|\) của một STFT cụ thể, theo decibel, có sàn. Đổi cửa sổ hoặc thang màu là đổi câu chuyện.

## Mục tiêu học tập

1. Đọc các trục spectrogram (thời gian, tần số, màu dB).
2. Nhận nguyên âm hữu thanh, formant, phụ âm xát, và khoảng lặng.
3. Nhận sàn nhiễu dừng, burst, babble, và nhạc.
4. Nhận artifact NS thường gặp (musical noise, over-suppression, warble).
5. Dùng spectrogram có chừng mực, cùng với nghe và metric.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Giải phẫu một đồ thị spectrogram |
| 10–28 | Bộ mẫu tiếng nói (mô tả không cần audio) |
| 28–42 | Bộ mẫu nhiễu và cách đọc hỗn hợp |
| 42–52 | Đọc artifact trước/sau NS |
| 52–60 | Bài tập |

![Spectrogram tiếng nói: các vạch hài nằm ngang xếp chồng, rồi một burst nhiễu dọc phủ mọi băng]({{ site.imgurl }}/generated/spectrogram-reading.png)

*Hình. Hài hữu thanh là một chồng gờ ngang; burst nhiễu là một thanh dọc đổ đầy mọi băng cùng lúc.*

## Giải thích cốt lõi

### Trục và thang

- **X:** thời gian (giây) hoặc chỉ số frame.
- **Y:** Hz (tuyến tính) hoặc Mel/ERB (tri giác).
- **Màu:** thường \(20\log_{10}|X(\ell,k)|\) kèm sàn.

Luôn ghi: \(f_s\), cửa sổ, hop, kích thước FFT, dải dB (ví dụ −80..0 dB). Thiếu các mục này thì ảnh chụp màn hình không phải số liệu.

$$
S(\ell,k)=20\log_{10}\bigl(\max(|X(\ell,k)|,\,\varepsilon)\bigr).
$$

\(\varepsilon\) là sàn. Không có nó, bin im (đúng 0 sau mask cứng) thành \(-\infty\), thang màu bị kéo quanh một lỗ, phần còn lại của câu thành một vệt be. Sàn khoảng −80 dB so với sine full-scale thì khoảng lặng tối và hài của nguyên âm vẫn thấy. Hai ảnh chỉ so được khi \(\varepsilon\), cửa sổ và hop khớp. Trục Mel không thẳng hàng với bug bin tuyến tính: bin \(k\) ứng với \(k f_s/N\) hertz, và filterbank Mel đã cộng các bin đó lại.

### Quy trình đọc

Dùng hình như ca đã giải, rồi cùng thứ tự ấy cho mọi ảnh trong ticket.

1. **Đóng dấu STFT.** Đọc \(f_s\), cửa sổ, hop, \(N\) và dải dB trên chú thích trước khi diễn giải màu. Các gờ trên hình nằm gần 1.2, 2.4, 3.6, 4.8, 6.0 và 7.2 kHz: cơ bản 1.2 kHz và các hài, trên trục hertz tuyến tính.
2. **Tìm khoảng lặng hoặc sàn nhiễu.** Vùng tối trước 0.2 s và sau burst là sàn. Sàn đã sáng thì hoặc mic có hiss, hoặc thang màu đang zoom vào 20 dB dưới cùng. Đừng kết luận mô hình “khử thiếu” khi chưa biết cái nào.
3. **Tìm chồng hài.** Các gờ ngang, cách đều, là tiếng hữu thanh (hoặc nhạc). Khoảng cách là \(f_0\). Trên hình khoảng cách khoảng 1.2 kHz — giọng rất cao hoặc một nốt hát, không phải giọng nói điển hình 100–200 Hz. Hình học giống nhau, khoảng cách chính là cao độ.
4. **Tìm sự kiện dọc.** Plosive hoặc burst nhiễu thắp nhiều bin trong một hai frame. Thanh cam khoảng 0.85–1.0 s là kiểu đó: năng lượng mọi tần số, không phải một hài mới. Tiếng phím và tiếng ho giống vậy và hẹp hơn.
5. **Rồi mới so trước và sau NS**, cùng thang. Mất các gờ trên cao là over-suppression hài. Đốm ở vùng tối là musical noise. Sọc sáng/tối khóa đúng hop là COLA hoặc bơm gain, không phải “thêm nhiễu”.

Lỗi pha không hiện trên \(S(\ell,k)\). Phần dư nghe ướt mà spectrogram biên độ sạch là lỗi dùng lại pha (bài 02-04); hình sẽ không thú nhận.

### Mốc tiếng nói

| Mẫu | Nhìn thấy |
|-----|-----------|
| Nguyên âm hữu thanh | Vạch hài; băng formant tối hơn giữa các vạch |
| Đổi cao độ | Vạch nghiêng / khoảng cách đổi |
| Tắc | Burst băng rộng theo phương dọc + khoảng đóng |
| Xát | Mây nhiễu ở tần số cao |
| Lặng | Sát sàn (còn nhiễu mic) |

### Mốc nhiễu

| Nhiễu | Nhìn thấy |
|-------|-----------|
| HVAC | Gờ thấp, kéo dài |
| Hiss quạt | Sàn băng rộng bị nâng |
| Bàn phím | Kim dọc mỏng |
| Babble | Giống tiếng nói nhưng cấu trúc tranh chấp lộn xộn |
| Nhạc | Chồng hài ổn định, không chuyển formant như tiếng nói |

### Artifact sau NS

| Artifact | Nhìn / nghe |
|----------|-------------|
| Musical noise | Đốm bin lẻ theo thời gian |
| Over-suppression | Mất mây xát; tiếng bị bít |
| Warble hop | Sọc biên độ tuần hoàn đúng chu kỳ hop |
| Vang dư | Nhòe dọc còn lại sau tiếng nói |

Spectrogram **hỗ trợ** việc nghe và SI-SDR/DNSMOS (chương 08); không thay chúng. Spectrogram đẹp vẫn có thể nghe xấu vì lỗi pha không hiện trên đồ thị biên độ.

## Ví dụ có số

Tem tham số: “48 kHz, Hann 20 ms, hop 10 ms, N=1024, dB −70..0”. \(N=1024\) ở 48 kHz khoảng 21.3 ms nếu cửa sổ bằng FFT, *không* phải lưới 960 điểm của DeepFilterNet. Ghi rõ trong ticket, kẻo sửa nhầm bin.

Tần số tâm bin là \(k f_s/N\). Hài 200 Hz với \(f_s=8\,\mathrm{kHz}\), \(N=256\), rơi ở

$$
k=\frac{200}{8000/256}=6.4,
$$

nên năng lượng nằm giữa bin 6 và 7. Hài hai và ba nằm giữa 12–13 và gần 19. Mini-lab in các bin đó. Ticket viết “tone ở bin 200” là đang trộn hertz với chỉ số bin.

Thanh sáng tần số thấp có thể là lệch DC, không phải “mô hình thất bại”. High-pass trước khi vẽ nếu đang chẩn đoán NS. Babble và mục tiêu đều có hài; mục tiêu thường to hơn, gần hơn. NS một kênh thì chật — spectrogram để chỉnh kỳ vọng.

## Bẫy thường gặp

1. So đồ thị khác dải màu dB.
2. Dùng đồ Mel để debug bug bin STFT tuyến tính.
3. Tuyên bố thắng chỉ vì nền im hơn (tiếng nói có thể đã tổn).
4. Quên artifact pha vô hình trên mag.
5. Cửa sổ cực dài làm mọi thứ trông “dừng”.

## Mini-lab

**Mục tiêu.** Dựng một spectrogram nhỏ từ các frame `rfft` của sine ba hài, và in bin nào sáng.

```python
import numpy as np

fs, L, R = 8000, 256, 128
t = np.arange(int(0.4 * fs)) / fs
f0 = 200.0
x = (np.sin(2 * np.pi * f0 * t)
     + 0.5 * np.sin(2 * np.pi * 2 * f0 * t)
     + 0.25 * np.sin(2 * np.pi * 3 * f0 * t))
w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(L) / L)
frame = x[L:L + L] * w
mag = np.abs(np.fft.rfft(frame))
top = np.argsort(mag)[-6:][::-1]
print("top bins", top.tolist())
for h in (1, 2, 3):
    print(f"harmonic {h} expected k", h * f0 * L / fs)
```

**Kỳ vọng.** Tâm kỳ vọng là **6.4, 12.8, 19.2**. Các bin mạnh là láng giềng của các tâm đó (thường 6 và 7 cho 200 Hz, 12 và 13 cho 400 Hz, và 19 cho 600 Hz). Cặp bin ấy là rò của hài lệch lưới qua búp chính Hann, không phải nhiễu.

**Khi hỏng.** Chỉ `np.argmax` thì ra bin 6 và giấu các hài kia. `fft` thay `rfft` nhân đôi phổ và làm lệch câu chuyện chỉ số. Quên cửa sổ thì sidelobe (bài 02-03) đẩy bin không liên quan vào top sáu. Đọc bin 6 thành 6 Hz thay vì \(6\cdot8000/256=187.5\,\mathrm{Hz}\) là bug ticket quen thuộc.

## Bài tập nhỏ

1. Phác spectrogram hoạt hình của “hello” trong nhiễu.
2. COLA hỏng với hop 10 ms hiện thế nào?
3. Vì sao phải kẹp sàn log?
4. Hai cue phân biệt nhiễu nhạc và tiếng nói hữu thanh.
5. Metadata bắt buộc kèm spectrogram trong ticket bug?

### Gợi ý đáp án

1. Chồng hài tần số thấp cho nguyên âm, mây tần số cao cho phụ âm xát, burst dọc cho /h/ hoặc âm tắc, nằm trên một sàn ổn định.
2. Sọc sáng/tối dọc mỗi 10 ms, khóa theo hop, kể cả xuyên nguyên âm đều.
3. Nếu không, số 0 đúng trở thành \(-\infty\) và thang màu sụp.
4. Nhạc giữ khoảng cách hài cứng và partial dài, ổn định; tiếng nói di chuyển formant và đổi \(f_0\) theo ngữ điệu.
5. \(f_s\), cửa sổ, hop, kích thước FFT, và dải dB.

## Đọc thêm

- Oppenheim & Schafer, và ghi chú phổ của Julius O. Smith — biên độ thời gian ngắn thực sự đo cái gì.
- Chương spectrogram trong giáo trình xử lý tiếng nói / DSP.
- Ảnh minh họa DNS Challenge và hình trong paper DeepFilterNet; đọc trục trước khi so với STFT tuyến tính 48 kHz.
