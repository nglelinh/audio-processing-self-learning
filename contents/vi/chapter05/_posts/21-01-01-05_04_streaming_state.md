---
layout: post
title: "05-04 Trạng thái mô hình streaming"
chapter: "05"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter05
lesson_type: required
draft: false
---

Mô hình SE streaming mang **state** qua các hop: phần dư overlap STFT, vector ẩn RNN/GRU, lịch sử tap deep filter, có thể cả tracker PSD nhiễu. Quản lý state sai gây click lúc bắt đầu, trôi chất lượng cuộc gọi dài, hoặc hỏng sau đổi sample rate. Bài này liệt kê loại state, chính sách reset, và kiểm thử ổn định stream dài.

## Mục tiêu học tập

Bạn liệt kê phần tử state trong đồ thị streaming họ DF, thiết kế chính sách reset / flush cho mute và đổi thiết bị, giải thích rủi ro trôi dài với RNN nhỏ, và đặc tả kế hoạch test cuộc gọi ≥ 30 phút.

## Kế hoạch 60 phút

- **0–10 phút** — Bug: bật NS giữa câu → click kim loại.
- **10–25 phút** — Kiểm kê state streaming (DSP + neural).
- **25–40 phút** — Chuyển reset / warm-start / bypass.
- **40–50 phút** — Trôi và giảm nhẹ (con trỏ văn liệu siêu nhẹ).
- **50–60 phút** — Bẫy, bài tập.

## Giải thích cốt lõi

### Kiểm kê state

| Loại | Ví dụ | Lỗi nếu sai |
|------|-------|-------------|
| STFT/OLA | ring vào, đuôi OLA | click, lọc răng lược |
| Recurrent neural | GRU/LSTM h, c | tembre sai, nổ |
| Tap deep filter | $$T-1$$ phổ trước | smear tạm thời |
| Tracker cổ điển | PSD nhiễu, $$\xi$$ | khử quá/thiếu |
| Điều khiển | bật, cường độ | nhảy gain đột ngột |

Đồ thị ONNX streaming thường lộ state thành **I/O tường minh** phải feedback mỗi khung. Quên nối khiến mô hình hành xử như mạng stateless sai.

### Chuyển tiếp

1. **Cold start:** zero hoặc state khởi tạo học; tùy chọn warm-up silence.
2. **Bật NS giữa cuộc gọi:** crossfade dry→wet 5–20 ms; reset OLA cẩn thận.
3. **Tắt:** crossfade wet→dry; giữ hoặc đóng băng state—ghi rõ.
4. **Đổi thiết bị / sample rate:** **reset đầy đủ** + khởi tạo lại hop.
5. **Phục hồi underrun:** ưu tiên reset đuôi OLA; cân nhắc decay mềm RNN về 0.

### Trôi stream dài

Mô hình siêu nhẹ (dòng Fast-ULCNet) ghi nhận **trôi state RNN**. Họ DF cũng có thể tích tụ dị thường số dưới lượng tử hóa (Ch. 06). Giảm nhẹ: reset/blend về 0 lúc silence dài (VAD), kiểm thử **≥ 30–45 phút**, so “giờ 0 vs giờ 1” bằng DNSMOS / nghe.

### Giả mã feedback

```text
state = zeros()
for hop in stream:
    y, state = model(hop, state)
    emit y
```

Unit-test shape `state` khớp binding ORT (bug tích hợp phổ biến).

## Bẫy thường gặp

- Tạo lại session ORT mỗi hop (phá state *và* RTF).
- Chia sẻ một object state cho hai cuộc gọi đồng thời.
- Không reset sau seek trong lab file offline.
- Coi bộ nhớ toàn cục WASM an toàn qua lần reload worklet.

## Bài tập

1. Liệt kê tensor state kỳ vọng kiểu DeepFilterNet; đối chiếu dump I/O ONNX đã pin.
2. Cố ý zero đuôi OLA giữa stream STFT giả; mô tả artifact.
3. Viết chính sách reset chính thức Mezon cho mute, unmute, đổi mic.
4. Job tự động chạy NS 45 phút; cờ RTF_p95 và trôi gain.

## Đọc thêm

- Ví dụ I/O binding / RNN stateful ONNX Runtime.
- Đường suy luận streaming DeepFilterNet.
- Thảo luận hành vi state dài Fast-ULCNet (con trỏ khảo sát).
- Ghi chú vòng đời AudioWorkletProcessor (MDN).
