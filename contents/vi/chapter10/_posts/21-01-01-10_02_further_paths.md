---
layout: post
title: "10-02 Hướng học tiếp"
chapter: "10"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter10
lesson_type: required
draft: false
---

Sau capstone, hãy chọn một **lộ trình** thay vì bookmark lung tung. Ba hướng hữu ích: sâu DSP cổ điển, nghiên cứu SE neural, hoặc productization (WebRTC/LiveKit/on-device). Bài cũng gợi ý lịch 30 ngày và artifact portfolio.

## Kế hoạch giảng 60 phút

- 0–10 phút: Chương nào bạn mạnh nhất?
- 10–30 phút: Đường A/B/C.
- 30–45 phút: Chủ đề liền kề (AEC, multi-mic, SE cá nhân hóa).
- 45–55 phút: Nháp lịch 30 ngày.
- 55–60 phút: Checklist portfolio.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Chọn đường: DSP cổ điển, nghiên cứu SE, hoặc productization.
- Đề xuất chủ đề liền kề cho mini-project.
- Lên lịch luyện 30 ngày.
- Biến artifact capstone thành portfolio.

## Đường A — Sâu DSP cổ điển

Tái dựng STFT/OLA cẩn thận; đọc SpeexDSP / APM và đo AEC trên máy bạn; trực giác beamforming trên stereo.  
**Vé ra:** note kiểu blog “Khi NS cổ điển thắng model neural nhỏ”.

## Đường B — Nghiên cứu SE neural

Reading group 1 paper/tuần từ danh sách tùy chọn; reproduce RTF baseline trên ORT CPU; so DF3 với một ultra-light trên *clip set của bạn*.  
**Vé ra:** bảng eval công khai + caveat (không cosplay leaderboard).

## Đường C — Productization

Pattern LiveKit production; telemetry lỗi; ngân sách CDN/perf mạng mobile SEA; mốc Rust `df-core` hoặc nhúng mobile.  
**Vé ra:** design doc + đo init/RTF trên hai thiết bị.

## Chủ đề liền kề

| Chủ đề | Vì sao |
|--------|--------|
| AEC sâu | Echo thống trị chất lượng họp |
| Multi-mic | Laptop ngày càng nhiều mic |
| SE cá nhân hóa | Target speaker trong babble |
| Tương tác codec | Opus × artifact NS |
| Caption / ASR | WER sau NS |

## Lịch 30 ngày (mẫu)

| Ngày | Tập trung |
|------|-----------|
| 1–3 | Đọc lại Ch 02 + notebook SI-SDR |
| 4–7 | Đóng băng 20 clip cá nhân |
| 8–14 | MVP dự án theo đường đã chọn |
| 15–21 | Metric + listening với một peer |
| 22–26 | Viết + polish demo |
| 27–30 | Đóng góp docs/eval OSS *hoặc* ADR tại chỗ làm |

## Ý tưởng đóng góp mã nguồn mở

Cải thiện docs harness (repo của bạn); reproduce RTF và mở issue cẩn thận kèm phiên bản; ví dụ LiveKit processor (không refactor lang quangk).

## Artifact portfolio

Sơ đồ kiến trúc; bảng metric CSV+md; protocol AB (EN/VI); video demo ≤3 phút; reading log.

## Bài tập

1. Chọn A/B/C; viết lịch 30 ngày.  
2. Một chủ đề liền kề + thí nghiệm cuối tuần.  
3. Một lỗ hổng docs upstream bạn có thể vá.  
4. Nháp mục README portfolio.

## Đọc thêm

- Kỳ DNS Challenge / workshop SE (INTERSPEECH, ICASSP)  
- Cộng đồng docs LiveKit & WebRTC  
- Discussions/issues DeepFilterNet về đau triển khai thật
