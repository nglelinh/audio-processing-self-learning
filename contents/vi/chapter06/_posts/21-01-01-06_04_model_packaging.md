---
layout: post
title: "06-04 Đóng gói mô hình cho sản phẩm"
chapter: "06"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter06
lesson_type: required
draft: false
---

Đồ thị ONNX tuyệt vẫn thất bại sản phẩm hóa nếu **đóng gói** sai: tải nhiều megabyte trên 3G, đường CDN không cache, lệch phiên bản, hoặc giấy phép. Bài này phủ bố cục artifact, nén, versioning, kiểm tra toàn vẹn, và ràng buộc định hình giao npm/CDN của Mezon (mở rộng Ch. 07).

## Mục tiêu học tập

Bạn thiết kế layout thư mục gói mô hình có semver, chọn nén và header cache ở mức cao, đặc tả hash toàn vẹn và ma trận tương thích (opset ↔ runtime), và liệt kê ràng buộc pháp lý/riêng tư khi phân phối lại weight.

## Kế hoạch 60 phút

- **0–10 phút** — Horror: cập nhật app ship FP32 80 MB, spike uninstall.
- **10–25 phút** — Nội dung artifact: onnx, config, license, changelog.
- **25–40 phút** — Ngân sách kích thước, nén, tương tác lượng tử hóa.
- **40–50 phút** — Versioning & toàn vẹn; rollout theo giai đoạn.
- **50–60 phút** — Bẫy, bài tập, checklist.

## Giải thích cốt lõi

### Layout gợi ý

```text
models/df3-mono-48k/
  model.onnx
  config.json             # hop, sample_rate, shape state
  LICENSE_WEIGHTS.txt
  SHA256SUMS
  CHANGELOG.md
```

`config.json` phải gồm sample rate, hop/cửa sổ, tên input, shape tensor state để wrapper không lệch im lặng.

### Ngân sách kích thước (mặc định dạy — chỉnh theo sản phẩm)

| Kênh | Ngân sách mạnh | Ghi chú |
|------|----------------|---------|
| Web mobile tải lần đầu | ≤ 5–10 MB nén | Ưu INT8 / biến thể nhỏ |
| Desktop Electron | ≤ 20–40 MB | Có thể lazy-download |
| App mobile native | ship trong binary hoặc on-demand | Coi kích thước store |

Lượng tử hóa (06-02) và phương án siêu nhẹ (04-05) là quyết định đóng gói không kém quyết định ML.

### Nén & cache

Phục vụ Brotli/gzip; tên file hash nội dung cho CDN bất biến; `Cache-Control: immutable` cho asset đã hash; cache ngắn cho con trỏ `latest`.

### Toàn vẹn & tương thích

1. Công bố SHA-256;verify sau tải.
2. Matrix-test: ORT 1.x + opset mô hình + ma trận trình duyệt trong CI.
3. Từ chối chạy nếu major semver `config.json` ≠ major wrapper.

### Pháp lý / đạo đức đóng gói

Tôn trọng giấy phép weight; ghi notice bên thứ ba (ORT, tác giả mô hình); không gói audio khách hàng; telemetry metric giọng có thể là dữ liệu nhạy cảm.

### Rollout theo giai đoạn

Canary 5% client desktop → theo dõi underrun → mở rộng. Giữ phiên bản mô hình trước trên CDN để rollback.

## Checklist cổng ship

- [ ] `config.json` đủ và đã test
- [ ] SHA256 đã công bố
- [ ] File license có mặt
- [ ] RTF_p95 đạt trên hạng đích
- [ ] Cổng nghe vs phiên bản trước
- [ ] Cache CDN đã xác minh
- [ ] Đường rollback đã tài liệu hóa

## Bẫy thường gặp

- Ghi đè `model.onnx` tại chỗ (địa ngục đầu độc cache).
- Quên kích thước npm ≠ kích thước mô hình CDN (tách chúng).
- Không có `config` → lệch hop im lặng sau “nạp thành công”.
- Ship bản debug ORT lên production.

## Bài tập

1. Viết schema config (JSON Schema hoặc struct typed) cho mô hình Mezon.
2. Bảng ngân sách web vs native cho DF3 FP32 vs INT8.
3. Drill rollback: các bước hoàn tác phiên bản mô hình < 15 phút.
4. Audit giấy phép: câu hỏi phải trả lời trước khi phân phối lại weight DeepFilterNet thương mại.

## Đọc thêm

- Docs đóng gói / tối ưu mô hình ONNX Runtime (định dạng `ORT`).
- Best practice kích thước npm; hướng dẫn cache CDN.
- Mục license model card DeepFilterNet (nguồn sơ cấp).
- Bài Chương 07 về tải CDN và bề mặt npm Mezon.
