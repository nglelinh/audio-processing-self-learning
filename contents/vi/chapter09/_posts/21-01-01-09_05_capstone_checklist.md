---
layout: post
title: "09-05 Checklist capstone & demo day"
chapter: "09"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Demo day thưởng **rõ ràng**: đường chạy được, con số bảo vệ được, và giới hạn đã biết. Dùng checklist này ngày trước và script 5 phút trên sân khấu.

## Kế hoạch giảng 60 phút

- 0–15 phút: Chạy checklist kỹ thuật theo cặp.
- 15–30 phút: Làm slide metric + listening.
- 30–45 phút: Diễn tập script 5 phút.
- 45–55 phút: Tiêm lỗi (tắt CDN / toggle NS).
- 55–60 phút: Nộp inventory artifact.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Chạy checklist cuối về đúng đắn, độ trễ, cờ UX.
- Chuẩn bị script demo 5 phút.
- Liệt kê giới hạn trung thực.
- Trình bày một ví dụ listening có ngữ cảnh.

## Checklist kỹ thuật

### Đường audio

- [ ] Quyền mic + đúng thiết bị  
- [ ] Bật/tắt NS (hoặc ghi rõ nếu phải restart)  
- [ ] Tương tác NS trình duyệt đã tài liệu hóa  
- [ ] Dispose không để AudioContext ma  

### Tải model

- [ ] Cold start: tải được hoặc lỗi rõ  
- [ ] Offline sau cache: hành vi đã ghi  
- [ ] Fallback: cuộc gọi vẫn chạy nếu CDN fail  

### Metric

- [ ] Bảng SI-SDR và/hoặc DNSMOS  
- [ ] Tóm tắt AB với N  
- [ ] RTF/timing trên thiết bị đặt tên  
- [ ] Pin phiên bản gói/commit/model  

### Demo

- [ ] Bản ghi dự phòng nếu mic live hỏng  
- [ ] Tai nghe  
- [ ] Một clip café + bàn phím + sạch  

## Script demo 5 phút

| Thời gian | Nội dung |
|-----------|----------|
| 0:00–0:40 | Bài toán nhiễu uplink; DF3 on-device |
| 0:40–1:30 | Một slide kiến trúc |
| 1:30–2:30 | AB live hoặc ghi |
| 2:30–3:30 | Bảng metric — cái gì tốt / không |
| 3:30–4:20 | Đóng góp kỹ thuật của bạn |
| 4:20–5:00 | Giới hạn + bước tiếp |

## Slide giới hạn (bắt buộc)

Ví dụ: mới test laptop EN/VI; cần SIMD cho path ≥1.2.0; chưa lab ITU chính thức; Rust vẫn stub (nếu đúng).

## Bài tập

1. Diễn tập bấm giờ; cắt cho ≤5:00.  
2. Chặn CDN; quay fallback.  
3. Peer review slide giới hạn.  
4. Inventory artifact theo 09-04.

## Đọc thêm

- Chương 07 và 08  
- Docs LiveKit / WebRTC track processing  
- README gói (asset, trình duyệt)
