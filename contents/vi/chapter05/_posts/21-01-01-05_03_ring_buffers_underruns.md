---
layout: post
title: "05-03 Ring buffer và underrun"
chapter: "05"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter05
lesson_type: required
draft: false
---

Audio realtime là bài toán **producer–consumer**. Capture sinh mẫu; NS cần khối kích thước hop; phía phát cần output liên tục. **Ring buffer** hấp thụ jitter; khi cạn hoặc tràn bạn nghe **underrun** / overrun. Bài này xây trực giác cấu trúc dữ liệu, lập kế hoạch dung lượng, và triage glitch cho pipeline kiểu Mezon.

## Mục tiêu học tập

Bạn nắm ring buffer SPSC (chỉ số, capacity lũy thừa 2), tính kích thước từ hop và ngân sách jitter, phân biệt triệu chứng underrun vs overrun, và viết checklist triage tiếng nứt dưới tải.

## Kế hoạch 60 phút

- **0–10 phút** — Nghe underrun vs clipping vs méo NS.
- **10–25 phút** — Cơ chế ring; quy tắc SPSC.
- **25–40 phút** — Toán dung lượng; ống nhiều tầng.
- **40–50 phút** — Bộ đếm underrun; bypass thích nghi.
- **50–60 phút** — Bẫy, bài tập.

## Giải thích cốt lõi

### Cơ chế

Mảng vòng với `write_pos` / `read_pos`. SPSC không khóa (hoặc atomics trên SAB): producer ghi nếu còn chỗ ≥ $$n$$; consumer đọc nếu sẵn ≥ $$n$$. Capacity thường $$2^m$$ để mask index.

### Các tầng pipeline

```text
quantum mic → [ring A] → gom hop → mô hình NS → [ring B] → quantum ra
```

Ring A hấp thụ kích thước callback ≠ hop. Ring B hấp thụ NS phát theo burst hop vào quantum nhỏ hơn. Quá nhỏ → underrun; quá lớn → latency.

### Phác hoạch dung lượng

$$
C \gtrsim H + J\cdot H + Q
$$

với $$H$$ = hop, $$Q$$ = quantum, $$J$$ = số hop jitter muốn hấp thụ. Ví dụ $$H=480$$, $$Q=128$$, $$J=2$$ → cỡ ~1200+ mẫu/tầng, làm tròn lũy thừa 2 (2048). Chỉnh bằng đo.

### Underrun vs overrun

| Sự kiện | Nguyên nhân | Âm thanh |
|---------|-------------|----------|
| Underrun (output) | Consumer đói | click, dropout, lỗ silence |
| Overrun (input) | Producer nhanh / consumer kẹt | trễ rồi nhảy nếu drop |
| NS overtime | Spike RTF | như underrun nếu ring ra cạn |

### Chiến lược fail mềm

1. **Bypass** NS $$N$$ khung khi trễ.
2. **Drop** input cũ nhất nếu ring capture tràn.
3. **Không block** audio thread chờ warm-up mô hình—pass-through đến khi sẵn.

### Chẩn đoán

Giữ `underrun_count`, `overrun_count`, `max_fill`, `min_fill`. Vẽ mức đầy. Tương quan RTF_p95 từ 05-01.

## Bẫy thường gặp

- Cùng một ring từ hai producer không có thiết kế đồng thời.
- Nhầm interleaved vs planar.
- “Sửa” underrun bằng phóng buffer đến latency vệ tinh.
- Xóa ring mỗi lần bật NS (gây glitch)—xả thanh lịch.

## Bài tập

1. Cài ring float SPSC (Python/Rust) với unit test wrap-around.
2. Tính capacity lũy thừa 2 cho $$H=480$$, $$Q=128$$, $$J=3$$.
3. Cố tình sleep quá hạn trong callback giả; quan sát đếm underrun.
4. Design note: dung lượng ring A/B cho đường DF3 web Mezon.

## Đọc thêm

- Tài liệu kỹ thuật circular buffer / SPSC trong audio.
- Thảo luận underrun Web Audio / game-audio (MDN + bug tracker).
- Docs latency JACK / PipeWire — mô hình sâu buffer vs latency.
