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

DeepFilterNet3 trong trình duyệt cần một module **WASM** (WebAssembly — mã nhị phân chạy trong trình duyệt) và một kho mô hình, `DeepFilterNet3_onnx.tar.gz`. Nhét cả hai chỉ trong tarball npm làm nặng lúc cài và buộc mọi lần đổi asset phải deploy lại ứng dụng. Trang sản xuất tải chúng từ **CDN** (mạng phân phối nội dung): một tầng cache đứng trước hai file đó. `deepfilternet3-noise-filter` **1.3.0** resolve URL từ `assetConfig.cdnUrl`. Bài này làm bốn URL của 1.1.2 và 1.3.0 tự chấm được, và giữ một lần fetch lỗi không kéo đổ cuộc gọi.

![CDN tải WASM và kho ONNX trước khi AudioWorklet biên dịch]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. Client biến cdnUrl thành một URL WASM và một URL mô hình, rồi biên dịch WASM.*

## Mục tiêu học tập

Bạn viết URL đã resolve cho gói ≤ 1.1.2 và cho quy tắc README của 1.3.0, giữ `v2` ngoài `cdnUrl`, đặt header cache sống sót qua lần đổi phiên bản, và bypass khử nhiễu khi fetch lỗi.

## Kế hoạch 60 phút

- **0–10 phút** — Hai thân nào di chuyển, và `initialize()` tải chúng lúc nào.
- **10–25 phút** — `cdnUrl` và tiền tố phiên bản.
- **25–40 phút** — Cache, MIME, CORS.
- **40–50 phút** — Sẵn sàng mà không chặn `connect()`.
- **50–60 phút** — Mini-lab: bốn URL.

## Asset

Theo README gói:

| Asset | Vai trò |
|-------|---------|
| `pkg/df_bg.wasm` dưới base hoặc dưới `v2/` | Keo WASM SIMD cho các bản bật tính năng đó |
| `models/DeepFilterNet3_onnx.tar.gz` | Kho DeepFilterNet3 từ upstream |

Con trỏ upstream: [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz). CDN phục vụ **trọng số và mã**, không phục vụ audio người dùng. Suy luận ở trên thiết bị. Đừng thêm upload PCM “để debug” trên client production.

ONNX (định dạng trao đổi đồ thị) nằm trong kho `.tar.gz`. SIMD (một lệnh xử lý nhiều số) nằm trong file WASM. AudioWorklet (callback xử lý âm thanh trên luồng realtime) chỉ chạy sau khi cả hai đã về.

## Cấu hình base

```javascript
const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: {
    cdnUrl: "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3"
  }
});
```

Nếu bỏ `cdnUrl`, mặc định của gói là đúng base Mezon đó. Mirror riêng chỉ thay origin và tiền tố đường dẫn.

### Đường dẫn theo phiên bản

README nêu:

| Gói | Đường đã resolve |
|-----|------------------|
| ≤ 1.1.2 | `{cdnUrl}/pkg/df_bg.wasm` và `{cdnUrl}/models/DeepFilterNet3_onnx.tar.gz` |
| ≥ 1.2.0, gồm 1.3.0 | `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` |

Gói thêm `v2/`. Bạn không thêm. README cũng nói bản SIMD nhanh hơn khoảng 20–30% với ≥ 1.2.0; hãy trích đó như con số của README. Trình duyệt cho bản đó, lại theo README: Chrome 91+, Firefox 89+, Safari 16.4+.

Gói ≥ 1.2.0, gồm 1.3.0, tự thêm `v2/`. Bạn không thêm. Đừng bao giờ đặt `v2` trong `cdnUrl`. Base ví dụ công khai là `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`. Changelog 1.3.0 cũng ghi lần nâng tract 0.23.3 cho bản WASM; ghim đó không đổi đường `v2/`.

## Sẵn sàng dần

`initialize()` tải cả hai thân bằng `Promise.all` và biên dịch WASM trên luồng chính. `setProcessor` chờ `init`, và `init` chờ việc đó. Signaling của phòng thì không được chờ.

```text
connect() ──► phòng đã lên, mic tắt hoặc NS đang bypass
                ├─► tải cặp ──► ok ──► setProcessor, rồi publish, rồi setEnabled(true)
                └─► tải cặp ──► lỗi ──► telemetry, ở lại bypass hoặc chỉ APM
```

Chính sách thực tế vẫn là thứ tự README khi asset đã nóng: dựng, `setProcessor`, `publishTrack`. Lỗi cần tránh là await CDN lạnh **bên trong** `connect()` trước khi người dùng vào phòng. Hiện “đang tăng cường audio” từ tiến trình byte nếu bạn đo được. Toast một lần khi lỗi.

TrackProcessor (móc biến đổi track của LiveKit) không tự biết cache. Nó chỉ fetch hai URL.

## Cache HTTP

Thư mục phiên bản bất biến có thể dùng `Cache-Control: public, max-age=31536000, immutable`. Khi byte đổi, hãy đăng thư mục mới và để tiền tố của gói trỏ tới đó. Đừng sửa byte tại URL bạn đã đánh dấu bất biến. `?t=Date.now()` mỗi lần join phá tỷ lệ trúng cache. Nếu bạn còn dùng Cache API, hãy khóa theo URL đầy đủ có phiên bản, giới hạn dung lượng, và có thao tác hỗ trợ xóa cache khử nhiễu.

Hãy phục vụ `df_bg.wasm` với `Content-Type: application/wasm`. Thiếu `Access-Control-Allow-Origin` trông như lỗi mạng chung chung; hãy log status và kiểu phản hồi. WASM và kho là một cặp nguyên tử. Module SIMD 1.3.0 đứng cạnh kho thời 1.1.2 không phải cấu hình trộn mà bạn nên “thử”.

Độ trễ vùng miền quan trọng trên mạng mobile. Hãy mirror vào VPC của khách khi host công khai bị chặn. CORS và TLS vẫn áp dụng. API công khai này không có header xác thực chưa công bố: client chỉ `fetch` bình thường.

## Lỗi một phần

| Lỗi | Người dùng thấy | Việc cần làm |
|-----|-----------------|--------------|
| 404 WASM hoặc mô hình | Không khử nhiễu được | Sửa đường; publish audio thô |
| Lỗi CORS | Như trên | Sửa header CDN |
| Thân bị cụt | `initialize` ném lỗi | Thử lại một lần, rồi bypass |
| Offline sau một lần cache tốt | Có thể vẫn chạy | Xác nhận cache đĩa hoặc Cache API |
| Lệch cặp | Audio xấu hoặc lỗi compile | Khóa cả hai file vào một thư mục |
| Sai MIME | Loader streaming fail | `application/wasm` |

## Mirror đã làm

Tải `DeepFilterNet3_onnx.tar.gz` từ upstream và `df_bg.wasm` khớp thế hệ gói của bạn. Với client đi theo quy tắc ≥ 1.2.0 của README, upload lên `https://assets.example.com/ns/df3/v2/pkg/` và `.../v2/models/`, rồi đặt `cdnUrl` là `https://assets.example.com/ns/df3`. Smoke-test một profile lạnh với cache tắt, rồi làm lại với cache bật.

## Mini-lab

Cho `cdnUrl = https://example.com/df3`, tính đường của bản ≤ 1.1.2 và của bản ≥ 1.2.0 gồm 1.3.0. Chạy `python3 cdn_urls.py`.

```python
cdn = "https://example.com/df3"
pairs = {
    "1.1.2": ("pkg/df_bg.wasm", "models/DeepFilterNet3_onnx.tar.gz"),
    "1.3.0": ("v2/pkg/df_bg.wasm", "v2/models/DeepFilterNet3_onnx.tar.gz"),
}
for ver, (wasm, model) in pairs.items():
    print(ver)
    print(f"{cdn}/{wasm}")
    print(f"{cdn}/{model}")
```

**Expected**

```text
1.1.2
https://example.com/df3/pkg/df_bg.wasm
https://example.com/df3/models/DeepFilterNet3_onnx.tar.gz
1.3.0
https://example.com/df3/v2/pkg/df_bg.wasm
https://example.com/df3/v2/models/DeepFilterNet3_onnx.tar.gz
```

**Failure modes**

- Nhúng `v2` vào `cdnUrl`, ra `https://example.com/df3/v2/v2/pkg/df_bg.wasm`.
- Dùng tên file không phải `df_bg.wasm` hoặc `DeepFilterNet3_onnx.tar.gz`.
- Chặn `connect()` cho tới khi cả bốn URL giả định đều trả lời. Chỉ hai URL của phiên bản đã cài được fetch, và không phải cổng của signaling.
- Coi 1.3.0 là layout không tiền tố. Từ 1.2.0 trở đi, gồm 1.3.0, client tự thêm `v2/`.

## Bẫy thường gặp

1. Tiền tố kép.
2. UI join bị cổng bởi `fetch`.
3. Upload audio thô từ production.
4. Một thư mục dùng chung một cách mù cho client ≤ 1.1.2 và ≥ 1.2.0.
5. Sai MIME của WASM.

## Bài tập

1. Nhắc lại bốn URL từ trí nhớ, rồi diff với khối expected.
2. Liệt kê trạng thái UI `idle`, `downloading`, `ready`, `error` và method nào của processor chạy khi `ready`.
3. Viết `Cache-Control` cho cây `v2` bất biến và quy tắc đăng cây mới.
4. Mười dòng chính sách khi tải asset lỗi mà phòng vẫn dùng được.
5. Vì sao file WASM và tar.gz phải cùng một thế hệ thư mục?

### Gợi ý đáp án

1. Hai file nhân hai thế hệ. Chỉ bản ≥ 1.2.0 / README 1.3.0 có tiền tố. Base vẫn là `https://example.com/df3`.
2. `ready` là lúc `initialize()` đã xong. Sau đó `setProcessor` (nếu chưa gọi) và `await setEnabled(true)` nếu người dùng muốn khử nhiễu.
3. `public, max-age=31536000, immutable` trên cây có phiên bản. Byte mới được thư mục mới, không ghi đè.
4. Bắt rejection của `setProcessor` hoặc `initialize`, publish track thô, phát một lý do telemetry, đừng thử lại mãi.
5. WASM SIMD và kho là một cặp khớp. Tách thế hệ qua hai thư mục là biên dịch module với sai trọng số.

## Đọc thêm

- README gói, mục Custom CDN: [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- MDN [HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching) và [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS).
- Upstream [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).
- Chương 06 về lượng tử hóa, SIMD, và đóng gói cùng cặp file đó.
