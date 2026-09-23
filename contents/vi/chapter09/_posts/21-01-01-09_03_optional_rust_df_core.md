---
layout: post
title: "09-03 Lộ trình Rust native (df-core) tùy chọn"
chapter: "09"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Gói TypeScript/WASM vẫn là phân phối trình duyệt được hỗ trợ. **Workspace Rust sibling** (`df-core`, `df-audio`, `df-cli`) khám phá DeepFilterNet3 native desktop/server với frame API gương WASM. Đây là **stretch tùy chọn** — dạy mốc và kỷ luật parity, không phải bắt buộc viết lại.

## Kế hoạch giảng 60 phút

- 0–10 phút: Vì sao native (nhúng, CLI, shared lib).
- 10–25 phút: Bản đồ frame API TS → Rust.
- 25–40 phút: Backend (stub → tract / libDF).
- 40–50 phút: Golden test và license/weights.
- 50–60 phút: Kế hoạch mốc 1–2 tuần.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Nêu mục tiêu thí nghiệm Rust `df-core` (ORT/tract/libDF).
- Liệt kê lựa chọn FFI / nhúng ở mức cao.
- Đánh dấu đây là stretch tùy chọn.
- Viết kế hoạch parity với đường JS/WASM.

## Layout tham chiếu

```text
mezon-noise-suppression-rust/
  crates/df-core | df-audio | df-cli
  models/   # đặt DeepFilterNet3_onnx.tar.gz (KHÔNG commit)
```

Stub mặc định trong tree: **480** mẫu @ **48 kHz** (10 ms) cho đến khi golden xác nhận parity WASM.

## Bản đồ API

| TypeScript | Rust `df-core` |
|------------|----------------|
| `df_create` | `DfState::create` / `create_from_path` / `create_stub` |
| `df_get_frame_length` | `frame_length` |
| `df_process_frame` | `process_frame` → `(Vec<f32>, snr)` |
| `df_set_atten_lim` / `post_filter_beta` | `set_atten_lim` / `set_post_filter_beta` |

## Checklist mốc kỹ thuật

1. Stub passthrough — build được mọi nơi.  
2. Validate đường model — lỗi rõ khi thiếu tar/onnx.  
3. Load ONNX bằng **tract** *hoặc* link **libDF**.  
4. Khớp frame/hop/sr với WASM.  
5. Trả SNR local khi model thật có.  
6. Golden WAV vs WASM (dung sai mẫu).  
7. `df-cli` cho harness Ch 08.  
8. `df-audio` đo latency callback.  
9. Optional `cdylib` FFI.

## License và weights

Theo dual license upstream (**Apache-2.0 OR MIT**). **Không commit** binary model lớn; ghi URL tải. Asset CDN npm ≥1.2.0 dưới `v2/models/` cùng họ weights.

## Parity tối thiểu

Chạy WASM và `df-cli` trên cùng fixture; so SI-SDR / MAE; kiểm `frame_length` và atten. Khi vẫn stub — đánh dấu golden **pending**, đừng tuyên bố bit-exact giả.

## Bài tập

1. Kế hoạch 5 mốc kèm ước lượng thời gian.  
2. Test contract `process_frame` không cần model.  
3. Tradeoff tract vs libDF bằng lời của bạn.  
4. Go/no-go: Rust có nằm trong capstone của bạn?

## Đọc thêm

- README Rust in-tree  
- tract / ONNX Runtime Rust  
- Upstream DeepFilterNet `libDF` / models  
- Chương 06
