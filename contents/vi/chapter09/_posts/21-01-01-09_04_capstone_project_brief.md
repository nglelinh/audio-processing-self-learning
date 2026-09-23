---
layout: post
title: "09-04 Đề bài capstone"
chapter: "09"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Nộp **thiết kế viết**, **demo có đo** trên tập clip nhỏ, và bằng chứng bạn hiểu kỹ thuật sau Mezon NS — không phải trivia wrapper. Đề bài định nghĩa mốc, artifact, và trọng tâm chấm.

## Kế hoạch giảng 60 phút

- 0–15 phút: Đọc đề + tiêu chí thành công.
- 15–30 phút: Chọn track (harness / UX policy / rust stretch).
- 30–45 phút: Lịch mốc baseline → đổi → eval → báo cáo.
- 45–55 phút: Checklist artifact.
- 55–60 phút: Hỏi đáp cắt scope.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Nộp thiết kế viết + demo đo được.
- Gồm RTF (hoặc ghi chú hệ thống trung thực) trên ít nhất một môi trường.
- Nộp reading log liên kết kỹ thuật với tài liệu Mezon.
- Lên kế hoạch mà không đụng product repo dùng chung.

## Track (chọn một chính)

**A. Eval & policy sản phẩm (khuyến nghị)** — harness + listening + mức mặc định / fallback.  
**B. Kỹ thuật tích hợp** — UX CDN, telemetry, checklist constraint có đo.  
**C. Rust stretch** — mốc `df-core` hướng backend thật + golden CLI.

## Mốc

| Mốc | Đầu ra |
|-----|--------|
| M0 | Phác kiến trúc (09-01) + giả thuyết (09-02) |
| M1 | Metric baseline trên clip đóng băng |
| M2 | Thay đổi *ngoài* product tree (hoặc fork cá nhân) |
| M3 | Bảng báo cáo đủ kiểu 08-04 |
| M4 | Script demo + checklist (09-05) |

## Artifact bắt buộc

1. Design note 2–4 trang  
2. Bảng metric + tóm tắt listening  
3. Ghi chú hệ thống (RTF/init trên thiết bị đặt tên)  
4. Reading log ≥5 bullet  
5. Diff config/patch *hoặc* link harness — không chỉ “npm bump”  
6. Mục giới hạn trung thực  

## Trọng tâm chấm (gợi ý)

Cao: hiểu kỹ thuật + eval trung thực; đo tái lập được.  
Trung bình: đường demo chạy.  
Thấp: slide đẹp.  
Không: sửa product repo không được phép.

## Phi mục tiêu

Train SOTA SE từ đầu; bảo đảm parity Rust bit-exact trong một kỳ; xử lý cloud audio khách không có thiết kế riêng tư.

## Bài tập

1. Chọn A/B/C và viết giả thuyết M0.  
2. Đóng băng danh sách 10 clip hôm nay.  
3. Phác reading log 5 dòng trống.  
4. Rủi ro lịch lớn nhất là gì?

## Đọc thêm

- `COURSE_OUTLINE.md`  
- README mezon-noise-suppression  
- Mẫu báo cáo 08-04
