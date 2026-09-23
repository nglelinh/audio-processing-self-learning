---
layout: post
title: "06-01 ONNX, tract và ORT"
chapter: "06"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter06
lesson_type: required
draft: false
---

NS on-device hầu như luôn **xuất** đồ thị đã train sang runtime suy luận. **ONNX** là định dạng trao đổi; **ONNX Runtime (ORT)** là engine đa nền thống trị (kể cả bản Web/WASM); **tract** là crate suy luận Rust-native khi muốn đường thuần Rust. Bài này so ở mức chọn lựa, phủ bẫy opset / dynamic axes, và giải thích vì sao sản phẩm kiểu Mezon thường chuẩn hóa ORT/WASM.

## Mục tiêu học tập

Bạn giải thích ONNX như định dạng trao đổi SE, so ORT vs tract về hệ sinh thái và đích, liệt kê bẫy xuất từ khung train kiểu PyTorch, và phác hợp đồng I/O streaming với dynamic axes và state RNN.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao không ship PyTorch trong AudioWorklet.
- **10–25 phút** — Khái niệm đồ thị ONNX: node, initializer, opset.
- **25–40 phút** — Ma trận chọn ORT vs tract.
- **40–50 phút** — Bẫy xuất; trục streaming.
- **50–60 phút** — Bẫy, bài tập, lý do mặc định Mezon.

## Giải thích cốt lõi

### ONNX một đoạn

ONNX tuần tự hóa đồ thị tính: tensor vào/ra, toán tử (`Conv`, `GRU`, `MatMul`…), weight dạng initializer. Khung train xuất; runtime tối ưu và chạy. Với SE, đồ thị có thể gồm biến đổi đặc trưng *hoặc* giả định bạn chạy STFT bên ngoài—**biết phía nào sở hữu STFT**.

### Tương thích opset

Toán tử đánh phiên bản theo **opset**. Xuất opset 17 có thể không nạp được ORT cũ. Pin: opset xuất, phiên bản ORT sản phẩm, CI nạp đúng `.onnx` trên runtime ship.

### ORT vs tract (mức chọn)

| Tiêu chí | ONNX Runtime | tract |
|----------|--------------|-------|
| Ngôn ngữ | C/C++, Python, Java, C#, JS/WASM… | ưu tiên Rust |
| Câu chuyện web | Mạnh (`onnxruntime-web`) | Không phải đường web chính |
| Tối ưu | Graph opts, EP (CPU, CUDA…) | Đồ thị Rust, thân thiện CLI |
| Khớp sản phẩm | Mezon web/native qua ORT phổ biến | Hấp dẫn thí nghiệm Rust-native `df-core` |
| Độ phủ op | Rộng, mặc định ngành | Kiểm tra op SE / lớp tùy biến |

**Rule of thumb:** chọn ORT khi cần WASM + parity đa nền; chọn tract khi binary Rust-native và đồ thị được hỗ trợ—luôn xác minh toán tử trên export DF thật.

### Dynamic axes cho streaming

Mô hình stream có thể khai báo `input_frame` với `time=1`, `state_in`/`state_out` kích thước ẩn cố định, `batch` động (thường 1 trong callback). Xuất với dynamic axes tường minh; test kỹ **batch=1 time=1**. Một số export vô tình nướng `time=100` cho chunk offline—không dùng được trong callback.

### Bẫy xuất

1. Op không hỗ trợ (lớp deep-filter tùy biến)—cần fuse về op thân thiện ONNX hoặc custom ORT op.
2. Lệch tracing in-place / control-flow.
3. Thiếu I/O state cho GRU—mô hình trông stateless.
4. Thừa float64—ép float32.
5. Lệch tiền xử lý — STFT numpy lúc train vs STFT Rust lúc prod.

### Vì sao Mezon thường chuẩn hóa ORT/WASM

Giao trình duyệt muốn một họ artifact; ORT Web có playbook hiệu năng đã biết (SIMD, threads khi cho phép). Native có thể chia sẻ cùng file ONNX. Tract vẫn là đường **Rust tùy chọn** giá trị (Ch. 09 stretch).

## Checklist trước khi đóng băng artifact

1. Nạp được trên phiên bản ORT ship.
2. Stream với feedback state khớp train.
3. Gần bit / SNR với tham chiếu Python trên clip vàng.
4. RTF_p95 trong ngân sách (05-01).
5. Giấy phép weight + op bên thứ ba đã rõ.

## Bẫy thường gặp

- Ship file ONNX khác nhau theo OS không có CI.
- Bật CUDA EP cho sản phẩm phải chạy laptop chỉ CPU.
- Giả định tract hỗ trợ mọi mô hình ORT.
- Đo RTF Python ORT rồi kỳ vọng số WASM giống hệt.

## Bài tập

1. Bảng tên/shape tensor cho SE GRU hop đồ chơi.
2. Cho ORT phiên bản X, tra opset hỗ trợ; chọn opset xuất (bài docs).
3. Memo 150 từ: ORT vs tract cho (a) Chrome extension (b) CLI enhancer Rust.
4. Thiết kế CI: chạy ONNX vs PyTorch; fail nếu delta SI-SDR > ngưỡng.

## Đọc thêm

- Tài liệu chính thức ONNX và ONNX Runtime.
- Docs `onnxruntime-web` (WASM).
- Tài liệu tract (suy luận Rust-native).
- Thảo luận export DeepFilterNet / ONNX cộng đồng (xác minh trước khi dựa).
