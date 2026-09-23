---
layout: post
title: "08-03 Kiểm thử lắng nghe"
chapter: "08"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter08
lesson_type: required
draft: false
---

Metric khách quan bỏ sót artifact quan trọng với sản phẩm: giọng “dưới nước”, cắt phụ âm, pumping, tiếng bàn phím còn sót. **Listening test** vẫn là trọng tài khi ship. Bài này hướng dẫn AB hoặc MUSHRA-like *nhỏ, trung thực* trong đội kỹ sư — không phải lab ITU đầy đủ — và cách ghi nhận cho stakeholder.

## Kế hoạch giảng 60 phút

- 0–10 phút: Khi nào dogfood đủ vs cần test có cấu trúc.
- 10–25 phút: AB vs MUSHRA-like; kiểm soát loudness và thứ tự.
- 25–40 phút: Hướng dẫn rater và tuyển mẫu.
- 40–50 phút: Phân tích — tỉ lệ thắng, hòa, bất đồng.
- 50–60 phút: Viết protocol 1 trang cho thay đổi mức khử.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Thiết kế AB hoặc MUSHRA-like nhỏ cho đội.
- Kiểm soát loudness và hiệu ứng thứ tự.
- Ghi nhận kết quả cho stakeholder.
- Biết khi nào dogfood nội bộ là đủ.

## Chọn protocol

| Protocol | Rater làm gì | Phù hợp |
|----------|--------------|---------|
| Dogfood | Dùng NS họp thật một ngày | Crash / CPU / UX |
| **AB** | Chọn A hoặc B (hoặc hòa) | Hai phiên bản / hai mức |
| MUSHRA-like | Chấm nhiều hệ trên thang có neo | Nhiều hệ; cần cẩn hơn |

ITU-T **P.808** / MUSHRA (ITU-R BS.1534) là tham chiếu chính thức — đội khóa học thường chạy biến thể **nhẹ**.

## Loudness và thứ tự

1. Chuẩn hóa loudness để không thiên vị file to hơn.  
2. Random hóa vị trí A/B; đừng luôn để “mới” bên phải.  
3. Nhãn mù “Hệ 1 / Hệ 2”.  
4. Cùng tai nghe nếu có thể.  
5. Clip ngắn 5–10 s có đoạn nhiễu + thoại quan trọng.

## Tuyển mẫu theo lưới

| Loại nhiễu | Độ khó | Thiết bị |
|------------|--------|----------|
| Babble quán | khó | laptop |
| Bàn phím | trung bình | laptop |
| Quạt / điều hòa | dễ | phone |
| Đường | khó | phone |
| Phòng im | đối chứng | laptop |

Gồm clip **sạch** — NS không được phá tiếng sạch. Quy mô nhỏ điển hình: 8–15 clip × 5–10 rater.

## Mẫu hướng dẫn rater

```text
Bạn sẽ nghe hai phiên bản cùng một take (thứ tự ngẫu nhiên).
Chọn bản tốt hơn cho họp việc, hoặc "hòa".
Ưu tiên: phụ âm rõ, giọng tự nhiên, ít bị nhiễu phân tâm.
Phạt: giọng đục, artifact robot, cắt chữ.
Bỏ qua: lệch loudness rất nhỏ.
```

## Báo cáo stakeholder

| Điều kiện | New thắng | Old thắng | Hòa |
|-----------|-----------|-----------|-----|
| Bàn phím | … | … | … |
| Café | … | … | … |

Kèm **một** ví dụ audio (có phép) trong demo — Chương 09-05.

## Khi nào dogfood đủ

Đổi độ tin cậy (fallback CDN) không đổi DSP; bật flag nội bộ; tối ưu RTF với parity waveform.

Cần listening có cấu trúc khi đổi mặc định mức khử, model/WASM mới, hoặc có complaint “giọng nghe lạ”.

## Bài tập

1. Viết hướng dẫn AB bằng EN và VI.  
2. Tuyển lưới 9 clip (3 nhiễu × 3 thiết bị).  
3. Café thua nhưng bàn phím thắng — bạn ship gì?  
4. Thiết kế attention check (clip trùng).

## Đọc thêm

- ITU-T P.808, ITU-R BS.1534 (tổng quan)  
- Ghi chú đánh giá người của DNS Challenge  
- Bài 08-01 / 08-02
