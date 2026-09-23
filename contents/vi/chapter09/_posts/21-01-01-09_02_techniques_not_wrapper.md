---
layout: post
title: "09-02 Kỹ thuật vượt qua npm wrapper"
chapter: "09"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Điểm capstone đến từ **kỹ thuật**: framing, buffering, chọn model, tư duy lượng tử hóa, kỷ luật eval — không phải đổi tên dependency. Bài này giúp chọn một cải tiến bám Chương 02–05 (và 06–08), định nghĩa metric, và giữ phạm vi ship được trong khóa.

## Kế hoạch giảng 60 phút

- 0–10 phút: Trivia wrapper vs bằng chứng kỹ thuật.
- 10–25 phút: Thực đơn ý tưởng theo chương.
- 25–40 phút: Vòng giả thuyết → thí nghiệm → đo.
- 40–50 phút: Cắt scope theo lịch khóa.
- 50–60 phút: Chọn câu giả thuyết capstone của bạn.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Đề xuất một cải tiến bám Chương 02–05 (hoặc 06–08).
- Định nghĩa metric thành công (RTF, SI-SDR/DNSMOS, listening).
- Giữ scope ship được.
- Ghi tradeoff cho maintainer.

## Thực đơn ý tưởng

| Ý tưởng | Nhiên liệu chương | Artifact |
|---------|-------------------|----------|
| UX sẵn sàng / fallback CDN | 07-03 | policy + telemetry |
| Mức khử mặc định từ listening | 08-03 | kết quả AB + config |
| Harness SI-SDR + DNSMOS | 08 | script + bảng |
| Log RTF / hạ cấp tự động | 05, 07 | metric + policy |
| Tắt NS trình duyệt khi DF bật | 03, 07 | checklist constraint |
| Vector test CLI offline | 09-03 | wav golden |
| Stretch: backend tract trong df-core | 06, 09-03 | mốc Rust |

Tránh: refactor lang quangk; chỉ CSS; “bump latest” không đo.

## Mẫu giả thuyết

```text
Giả thuyết: Hạ mặc định 80→60 giảm complaint giọng đục
            mà không để lọt nhiễu bàn phím không chấp nhận được.
Thí nghiệm: 12 clip; AB ≥6 rater; DNSMOS; ΔSI-SDR tùy chọn.
Thành công / thất bại: nêu tiêu chí rõ trước khi chạy.
```

## Metric bắt buộc nêu tên

Chất lượng (SI-SDR và/hoặc DNSMOS + listening); hệ thống (RTF / CPU / init); UX (time-to-ready, fallback).

## ADR ngắn cho maintainer

Ngữ cảnh → quyết định → metric → phương án bị loại → việc tiếp theo.

## Bài tập

1. Viết giả thuyết một câu; peer review độ cụ thể.  
2. Liệt kê số baseline thu *trước* khi đổi gì.  
3. Cắt MVP vs stretch.  
4. Phác outline ADR trống.

## Đọc thêm

- Paper DeepFilterNet2/3 — protocol thực nghiệm  
- Tài liệu hiệu năng ORT / WASM (mức cao)  
- Mẫu suite Chương 08
