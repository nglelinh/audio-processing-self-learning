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

Spectrogram là ngôn ngữ chung của kỹ sư tiếng nói. Bài này luyện đọc cấu trúc tiếng nói, loại nhiễu và artifact NS trên hình — và tránh thang dB nói dối.

## Mục tiêu học tập

1. Đọc trục spectrogram (thời gian, tần số, màu dB).
2. Nhận hài hữu thanh, formant, xát âm, khoảng lặng.
3. Nhận nền nhiễu dừng, burst, babble, nhạc.
4. Phát hiện artifact NS (musical noise, over-suppression, warble).
5. Dùng spectrogram có trách nhiệm cùng listening và metric.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Giải phẫu một đồ thị spectrogram |
| 10–28 | Thư viện pattern tiếng nói (mô tả không audio) |
| 28–42 | Thư viện nhiễu + đọc hỗn hợp |
| 42–52 | Đọc artifact trước/sau NS |
| 52–60 | Bài tập |

## Giải thích cốt lõi

Trục X thời gian; Y Hz (tuyến tính) hoặc Mel/ERB; màu thường \(20\log_{10}|X|\) có clamp sàn. Luôn ghi: \(f_s\), cửa sổ, hop, FFT, dải dB.

| Pattern | Trông như |
|---------|-----------|
| Nguyên âm hữu thanh | Sọc hài; dải formant tối |
| Đổi pitch | Khoảng cách sọc đổi |
| Plosive | Burst thẳng đứng + khoảng đóng |
| Xát âm | Mây cao tần |
| HVAC | Sống thấp bền |
| Bàn phím | Gai thẳng đứng mỏng |
| Babble | Giống tiếng nói nhưng hỗn loạn |
| Musical noise | Đốm bin cô lập theo thời gian |
| Over-suppression | Mất mây xát; nghẹt |
| Warble hop | Sọc biên độ tuần hoàn theo hop |

Spectrogram **hỗ trợ** listening và SI-SDR/DNSMOS (Ch. 08); không thay thế. Spectrogram đẹp vẫn có thể nghe xấu (lỗi pha không hiện trên mag).

## Ví dụ có số

Tem tham số: “48 kHz, Hann 20 ms, hop 10 ms, N=1024, dB −70..0”. Thanh thấp sáng có thể là DC bias — high-pass trước khi kết tội mô hình.

## Bẫy thường gặp

1. So đồ thị khác dải màu dB.
2. Dùng Mel để debug bug bin STFT tuyến tính.
3. Tuyên bố thắng chỉ vì nền im hơn (tiếng nói có thể đã tổn).
4. Quên artifact pha vô hình trên mag.
5. Cửa sổ cực dài làm mọi thứ trông “dừng”.

## Bài tập nhỏ

1. Phác spectrogram hoạt hình “hello” trong nhiễu.
2. COLA hỏng hop 10 ms hiện thế nào?
3. Vì sao clamp sàn log?
4. Hai cue phân biệt nhiễu nhạc và tiếng nói hữu thanh.
5. Metadata bắt buộc kèm spectrogram trong ticket bug?

## Đọc thêm

- Chương spectrogram sách xử lý tiếng nói / giáo trình DSP.
- Ví dụ trực quan DNS Challenge.
- Hình trong paper DeepFilterNet (đọc kỹ trục).
