---
layout: post
title: "07-03 Tải mô hình qua CDN"
chapter: "07"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter07
lesson_type: required
draft: false
---

DeepFilterNet3 trên trình duyệt cần **WASM** và **kho model** (`DeepFilterNet3_onnx.tar.gz`). Nhét hết vào tarball npm làm nặng cài đặt; app sản xuất thường tải từ **CDN** có cache và đường dẫn có phiên bản. Bài này thiết kế tải dần, an toàn cache, và chế độ lỗi giữ cuộc gọi sống.

## Kế hoạch giảng 60 phút

- 0–10 phút: Phải fetch gì (WASM vs model).
- 10–25 phút: `assetConfig.cdnUrl` và quy tắc `v2/` (≥1.2.0).
- 25–40 phút: HTTP caching, hash nội dung, cache busting.
- 40–50 phút: UX sẵn sàng — không chặn connect.
- 50–60 phút: Ma trận lỗi (404, CORS, offline, cache cũ).

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Thiết kế tải dần với trạng thái sẵn sàng hiện cho user.
- Cache model an toàn giữa các phiên.
- Xử lý lỗi một phần mà không giết cuộc gọi.
- Giải thích vì sao ≥1.2.0 tự thêm `v2/` dưới base CDN.

## Asset liên quan

| Asset | Vai trò |
|-------|---------|
| `pkg/df_bg.wasm` (base hoặc `v2/`) | Lớp DSP/suy luận tốc độ native |
| `models/DeepFilterNet3_onnx.tar.gz` | Trọng số / đồ thị từ upstream DeepFilterNet |

Con trỏ upstream: [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).

**Riêng tư:** thiết kế mặc định Mezon suy luận **trên thiết bị**. CDN phục vụ *weights*, không phải audio người dùng.

## Cấu hình CDN

```javascript
const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  assetConfig: {
    cdnUrl:
      "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3",
  },
});
```

| Phiên bản gói | Đường dẫn resolve |
|---------------|-------------------|
| ≤ 1.1.2 | `{cdnUrl}/pkg/...`, `{cdnUrl}/models/...` |
| ≥ 1.2.0 | `{cdnUrl}/v2/pkg/...`, `{cdnUrl}/v2/models/...` |

Tiền tố `v2/` do **gói** thêm — đừng tự ghi `v2` trong `cdnUrl` kẻo thành `.../v2/v2/...`.

## UX tải dần

1. `connect` phòng vẫn chạy (mic mute hoặc NS bypass).
2. Fetch WASM + model nền; hiện tiến trình nếu đo được bytes.
3. Thành công → bật processor.
4. Thất bại → giữ APM/raw; toast một lần.

Đừng để `await fetch(model)` chặn join WebSocket trên mạng mobile.

## Cache HTTP

- URL bất biến theo phiên bản + `Cache-Control: public, max-age=31536000, immutable` là tốt nhất.
- Đổi weights → publish path mới (`v3`) hoặc major gói mới.
- Tránh `?t=Date.now()` mỗi lần tải.

WASM + model là **một cặp** phát hành cùng thư mục phiên bản.

## Ma trận lỗi một phần

| Lỗi | Hiện cho user | Hành động |
|-----|---------------|-----------|
| 404 wasm/model | NS không khả dụng | Sửa deploy; fallback audio |
| CORS | NS không khả dụng | Sửa header CDN |
| Tải cụt | lỗi init | retry một lần rồi fallback |
| Offline sau khi đã cache | có thể vẫn chạy | kiểm tra Cache API / HTTP cache |
| Lệch cặp wasm/model | crash / audio xấu | khóa phiên bản cùng tree |

## Bẫy thường gặp

1. Ghi đôi `v2`.
2. Chặn UI vì fetch model.
3. Upload raw audio “để debug” từ client production.
4. Trộn layout ≤1.1.2 với client ≥1.2.0 trên một folder CDN.
5. Sai MIME `.wasm`.

## Bài tập

1. Với `cdnUrl = https://example.com/df3`, viết đủ URL cho gói 1.1.2 và 1.3.0.
2. Thiết kế state UI: `idle | downloading | ready | error`.
3. Đề xuất header Cache-Control cho tree `v2` bất biến.
4. Viết policy fallback ~10 dòng khi tải asset lỗi.

## Đọc thêm

- README gói — mục Custom CDN
- MDN: HTTP caching, CORS
- Upstream DeepFilterNet3_onnx.tar.gz
- Chương 06
