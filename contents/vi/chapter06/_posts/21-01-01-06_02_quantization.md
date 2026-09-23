---
layout: post
title: "06-02 Lượng tử hóa cho mô hình tiếng nói"
chapter: "06"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter06
lesson_type: required
draft: false
---

**Lượng tử hóa** thu nhỏ weight và thường tăng tốc suy luận SE—quan trọng cho kích thước tải WASM và RTF CPU—nhưng có thể làm hỏng chất lượng tiếng nói hoặc mất ổn định state RNN. Bài này phủ INT8 / weight-only ở mức kỹ sư, phương pháp hiệu chuẩn, và cổng xác nhận listening-first cho bộ khử nhiễu.

## Mục tiêu học tập

Bạn phân biệt lượng tử hóa INT8 động vs tĩnh, giải thích vì sao mô hình SE nhạy thang hiệu chuẩn, liệt kê lớp thường giữ FP32, và thiết kế cổng A/B nghe + SI-SDR trước khi ship weight đã lượng tử.

## Kế hoạch 60 phút

- **0–10 phút** — Động lực kích thước/RTF cho WASM họ DF.
- **10–25 phút** — Cartoon toán INT8; thang per-tensor vs per-channel.
- **25–40 phút** — Luồng công cụ lượng tử ORT; dữ liệu hiệu chuẩn tiếng nói.
- **40–50 phút** — Cái gì hỏng: nhiễu dư, over-attenuation, trôi state.
- **50–60 phút** — Bẫy, bài tập.

## Giải thích cốt lõi

### Cartoon toán

$$
w \approx s\,(q - z).
$$

Kernel GEMM nhân số nguyên rồi rescale. Thang **per-channel** cho convolution thường thắng per-tensor thô về chất lượng.

### Cách tiếp cận

| Chế độ | Ý | Ưu | Nhược |
|--------|---|-----|-------|
| Dynamic | Activation lượng tử lúc chạy | Dễ | Overhead; biến thiên |
| Static PTQ | Hiệu chuẩn khoảng activation offline | Suy luận nhanh | Cần audio đại diện |
| QAT | Train với nhiễu lượng tử | Chất lượng tốt nhất | Đắt |
| Weight-only | Weight INT8/INT4, act FP | Thắng kích thước đơn giản | Thắng tốc độ nhỏ hơn |

Với SE streaming, **static PTQ** hoặc toolchain quanh ORT là điểm khởi đầu phổ biến; QAT nếu chất lượng tụt.

### Hiệu chuẩn cho tiếng nói (không phải ImageNet)

Tập hiệu chuẩn phải gồm: silence / chỉ nhiễu, tiếng near-end to, mix quán SNR thấp, clip kiểu echo dư nếu trong phạm vi. Không thì thang lệch → **pumping** hoặc nhiễu dư gắt.

### Thường giữ FP32

Op elementwise / gating nhạy; đầu gain cuối; lớp rất nhỏ nơi overhead INT8 > lợi; heuristic lớp đầu/cuối—xác minh thực nghiệm.

### Cổng xác nhận

1. Khách quan: delta SI-SDR / DNSMOS vs FP32 trên eval đóng băng (Ch. 08).
2. Nghe: ≥ 10 cặp clip, buộc chọn.
3. Stream dài: ổn định 30 phút (05-04).
4. RTF: xác nhận tăng tốc trên thiết bị đích, không chỉ kích thước mô hình.

## Bẫy thường gặp

- Hiệu chuẩn chỉ white noise.
- Lượng tử trước khi xác minh parity STFT.
- Bỏ qua overflow tensor state.
- Ship INT8 không ghi delta chất lượng cho hỗ trợ.

## Bài tập

1. Weight trong $$[-0.8,0.8]$$: tính thang INT8 đối xứng.
2. Liệt kê 8 loại clip hiệu chuẩn PTQ Mezon.
3. Thiết kế phiếu nghe mù FP32 vs INT8.
4. Lướt docs lượng tử ORT; nêu tool/API sẽ gọi.

## Đọc thêm

- Tài liệu lượng tử hóa ONNX Runtime.
- Jacob et al. — paper lượng tử mobile kinh điển.
- Thảo luận runtime int8 SE FastEnhancer / faster-enhancer.c (con trỏ khảo sát).
- Ghi chú kích thước / realtime mô hình DeepFilterNet.
