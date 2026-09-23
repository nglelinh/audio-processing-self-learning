---
layout: post
title: "04-06 RNNoise như cầu nối giảng dạy"
chapter: "04"
order: 6
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

**RNNoise** vẫn là artifact dạy học tốt nhất trong NS realtime: **front-end DSP cổ điển** (đặc trưng band nhận pitch) cộng **GRU nhỏ** dự đoán gain theo band, ship C di động với hành vi latency rõ. Nó không sánh DeepFilterNet3 về chất lượng cảm nhận full-band, nhưng dạy thiết kế hybrid, làm mượt gain, và thói quen nhúng chuyển được sang WASM và mô hình siêu nhẹ.

## Mục tiêu học tập

Bạn tóm tắt triết lý hybrid của RNNoise, đối chiếu pipeline đặc trưng/gain với ERB+deep-filter của DeepFilterNet, rút bài học tái sử dụng cho suy luận WASM/nhúng, và liệt kê giới hạn thúc đẩy mô hình họ DF trong Mezon.

## Kế hoạch 60 phút

- **0–10 phút** — Nghe: RNNoise vs NS full-band hiện đại.
- **10–25 phút** — Cartoon kiến trúc pitch / band / dự đoán gain.
- **25–40 phút** — Vì sao bản C là món quà cho kỹ sư hệ thống.
- **40–50 phút** — Bài học chuyển vs đường sản phẩm DF3.
- **50–60 phút** — Bài tập; khi nào giữ RNNoise trong lab.

## Giải thích cốt lõi

### Triết lý hybrid

RNNoise **không** đổ thô mọi bin STFT vào mạng khổng lồ. Nó:

1. Tính **đặc trưng thiết kế tay** (năng lượng band, cue liên quan pitch),
2. Chạy **mạng nhỏ** (GRU) dự đoán **gain theo band**,
3. Áp gain với làm mượt DSP / heuristic pitch để giảm artifact.

Đó là tiền thân tinh thần của “gain ERB + tinh chỉnh học”, với phong bì tính toán nhỏ hơn và gốc lịch sử thiên telephony.

### Tư duy độ phức tạp vận hành

| Chủ đề | RNNoise | DeepFilterNet |
|--------|---------|---------------|
| Đặc trưng | DSP pitch + band | ERB học + deep filter STFT |
| Kích thước net | GRU nhỏ | Mạng nhân quả lớn hơn |
| Băng thông | Gốc wideband telephony | Mục tiêu full-band 48 kHz |
| Code | C tự chứa | Train Rust/Python + đồ thị xuất |
| Giá trị dạy | Hệ thống + hybrid rõ | Baseline chất lượng hiện đại |

### Vì sao RNNoise là bạn lab tuyệt

- Đọc hết nguồn C trong một buổi.
- Dễ gắn log gain, vẽ SNR band.
- Cổng tự nhiên tới **SIMD**, tư duy fixed-point, API `process_frame` thân thiện callback (Ch. 05–06).
- Đặt kỳ vọng cảm xúc: **mô hình nhỏ vẫn chạy** nếu đặc trưng tốt.

### Giới hạn (thành thật)

- Nhiễu kiểu nhạc full-band và quán cà phê laptop hiện đại thường cần mô hình mạnh hơn.
- Đặc trưng tay có thể bỏ lỡ cue mà deep filter phức bắt được.
- Trần chất lượng dưới DF2/DF3 trên nhiều test full-band kiểu DNS (tự nghe kiểm—đừng bịa số).

**Tư thế Mezon:** ship họ DF3 cho chất lượng sản phẩm; giữ RNNoise (hoặc SpeexDSP) làm **baseline lab** và oracle hồi quy (“pipeline ta còn thắng cổ điển chứ?”).

### Bài học tái sử dụng WASM / nhúng

1. API theo khung—đúng một hop mỗi lần gọi; không ẩn heap churn.
2. Precompute bảng cửa sổ / filterbank.
3. Làm mượt gain—tránh musical noise (Ch. 03).
4. Biên dịch SIMD khi có (Ch. 06).
5. Khiêm tốn hybrid—đặc trưng cổ điển vẫn giúp mạng nhỏ.

## Bẫy thường gặp

- Coi RNNoise “lỗi thời” rồi bỏ bài học hệ thống.
- Kỳ vọng mặc định RNNoise khớp MOS DF3.
- Port chỉ GRU, bỏ logic pitch/DSP.
- Dùng RNNoise làm baseline duy nhất trong đánh giá sản phẩm 48 kHz full-band.

## Bài tập

1. Vẽ chuỗi đặc trưng → GRU → gain band → tổng hợp; chú thích kích thước khung từ docs repo chính thức.
2. Lab A/B RNNoise vs demo DF3 cùng clip; báo cáo nghe 10 dòng.
3. Phác API Rust/C `process_frame(&mut state, in, out)` lấy cảm hứng RNNoise cho dự án DF-lite.
4. Đề xuất (trên giấy) một đặc trưng cổ điển thêm trước mạng GTCRN-class nhỏ cho nhiễu gõ phím.

## Đọc thêm

- Paper RNNoise và repo chính thức Xiph / JM Valin.
- SpeexDSP preprocessor — baseline cổ điển đồng hành.
- Paper mở đầu DeepFilterNet — đọc đối chiếu.
- WebRTC APM NS — tham chiếu production cổ điển/hybrid khác.
