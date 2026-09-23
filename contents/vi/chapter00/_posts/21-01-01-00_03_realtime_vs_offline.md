---
layout: post
title: "00-03 Khử nhiễu thời gian thực và offline"
chapter: "00"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter00
lesson_type: required
draft: false
---

Ship NS ít phụ thuộc đỉnh MOS trên bảng xếp hạng hơn là sống sót trên audio thread. Bài này định nghĩa độ trễ và RTF chặt, giải thích ràng buộc streaming, và liệt kê chế độ hỏng bạn sẽ debug trong tích hợp kiểu Mezon.

## Mục tiêu học tập

1. Định nghĩa độ trễ thuật toán, độ trễ đệm, và RTF.
2. Giải thích ràng buộc nhân quả / streaming so với look-ahead offline.
3. Liên hệ kích thước frame, hop, và ngân sách trễ đầu–cuối cho cuộc gọi.
4. Liệt kê underrun, audio cắt khúc, drift đồng hồ, gián đoạn state.
5. Áp dụng tư duy “RTF worst-case trên thiết bị đích” khi chọn mô hình.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Định nghĩa latency + RTF kèm bài tập số |
| 12–28 | Pipeline STFT nhân quả; vì sao SOTA offline thất bại trên WebRTC/LiveKit |
| 28–42 | State streaming: OLA, ẩn RNN/DF |
| 42–52 | Chế độ hỏng và checklist SLA |
| 52–60 | Bài tập nhỏ |

## Giải thích cốt lõi

### Ba khái niệm độ trễ

1. **Đệm** — thời gian gom mẫu trước khi xử lý frame.
2. **Thuật toán** — look-ahead, group delay bộ lọc, trễ OLA.
3. **Hệ thống** — quantum OS/callback, cầu JS/Wasm, jitter mạng.

### Real-time factor

$$
\mathrm{RTF} = \frac{T_{\mathrm{proc}}}{T_{\mathrm{audio}}}
$$

Streaming cần **dư địa**: RTF trung bình 0.9 vẫn chết khi GC/thermal đẩy một frame lên RTF 2.0.

**Ví dụ:** hop \(R=480\) tại \(48\,\mathrm{kHz}\) → \(10\,\mathrm{ms}\). Ngân sách RTF \(\le 0.5\) ⇒ \(T_{\mathrm{proc}}\le 5\,\mathrm{ms}\) cho đường STFT+model+ISTFT (đã khấu hao).

### Nhân quả và offline

DeepFilterNet2/3 nhấn thiết kế **real-time / causal** — lý do khóa học neo vào họ này thay vì chỉ mô hình diffusion offline.

### Frame, hop, trễ

$$
T_{\mathrm{hop}}=\frac{R}{f_s},\qquad T_{\mathrm{win}}=\frac{L}{f_s}
$$

Giảm \(L\) giảm trễ nhưng hại độ phân giải tần số — Chương 02 đào sâu.

### State streaming

OLA, ước lượng nhiễu/VAD, state hồi tiếp neural. Cold-start mỗi callback gây click; đổi sample rate không reset gây “bùn”.

### Chế độ hỏng

Underrun/glitch; tiếng nói cắt/ướt; drift ring buffer; artifact đuôi; cliff nhiệt.

## Ví dụ — mô hình này ship được không?

Offline: look-ahead 300 ms, RTF GPU 0.15, RTF CPU laptop 1.2 @ 48 kHz mono. Ngân sách gọi \(\le 40\,\mathrm{ms}\) look-ahead → **fail**. RTF 1.2 → **fail** nếu không downsample/quantize/mô hình nhỏ hơn.

## Bẫy thường gặp

1. Trích RTF paper đo offline batch lớn.
2. Bỏ qua latency đuôi p95/p99.
3. Dùng checkpoint non-causal “cho demo”.
4. Đo trễ bằng `Date.now()` xuyên nhiều tầng đệm ẩn.
5. Nhầm quantum AudioWorklet (ví dụ 128 mẫu ≈ 2.67 ms @ 48 kHz) với hop STFT.

## Bài tập nhỏ

1. Hop 256 mẫu @ 16 kHz: hop ms? \(T_{\mathrm{proc}}\) max cho RTF 0.25?
2. Liệt kê ba state buffer hệ STFT-NS phải giữ giữa các hop.
3. Vì sao RTF trung bình 0.4 vẫn glitch trên Chrome khi tải cao?
4. Đề xuất checklist go/no-go 5 phép đo trước khi bật NS mặc định.

## Đọc thêm

- DeepFilterNet2/3 — mục thiết kế real-time / causal.
- Tổng quan đồ thị xử lý WebRTC APM.
- Tài liệu MDN AudioWorklet (ràng buộc thời gian callback).
