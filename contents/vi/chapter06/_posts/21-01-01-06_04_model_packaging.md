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

Đồ thị ONNX (định dạng trao đổi đồ thị) đúng vẫn thất bại trong sản phẩm khi **đóng gói** sai: lượt tải đầu quá nặng, URL không cache, file WASM và kho mô hình thuộc hai thế hệ, hoặc giấy phép bạn không đưa được cho khách. `deepfilternet3-noise-filter` **1.3.0** tách bài toán đó. Gói npm ship phần keo JavaScript, AudioWorklet (callback xử lý âm thanh trên luồng realtime) đã inline, và bộ tải. Phần byte nặng, `df_bg.wasm` và `DeepFilterNet3_onnx.tar.gz`, được lấy từ CDN (mạng phân phối nội dung) qua `assetConfig.cdnUrl`. Bài này thiết kế layout, quy tắc tiền tố phiên bản, toàn vẹn, và đường rollback. Bài 07-03 tính đủ URL.

![WASM và kho ONNX đã đóng gói ở phía CDN của đường vào trình duyệt]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. Đóng gói quyết định byte nào được phép đi vào bước biên dịch WASM trong trình duyệt.*

## Mục tiêu học tập

Bạn tách tarball npm khỏi artifact trên CDN, áp quy tắc README cho gói ≤ 1.1.2 và ≥ 1.2.0, cùng đường `v3/` mà bản 1.3.0 đã cài thực sự xin, từ chối `cdnUrl` đã chứa tiền tố phiên bản, và liệt kê kiểm tra giấy phép cùng cache thuộc cổng ship.

## Kế hoạch 60 phút

- **0–10 phút** — Một lượt tải lần đầu chặn cuộc gọi, và vì sao dung lượng npm là con số sai.
- **10–25 phút** — Cặp artifact, config gợi ý, semver.
- **25–40 phút** — Quy tắc tiền tố, nén, cache bất biến.
- **40–50 phút** — Toàn vẹn, giấy phép, rollout theo giai đoạn.
- **50–60 phút** — Mini-lab, bẫy, bài tập.

## Giải thích cốt lõi

### Hai gói, một sản phẩm

`npm install deepfilternet3-noise-filter` cài một thư viện có peer dependency `livekit-client` ^2. README nói mã worker và worklet được inline thành blob URL, nên Webpack, Vite, Rollup, esbuild và Parcel không cần plugin copy. Đó là bề mặt JavaScript nhỏ, có phiên bản. Nó không phải mô hình. `DeepFilterNet3Core.initialize()` tải song song hai thân: module WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) và kho mô hình. Hai thân đó chiếm thời gian khởi động lạnh. Lượng tử hóa (bài 06-02) và bản SIMD (một lệnh xử lý nhiều số, bài 06-03) đổi dung lượng và tốc độ của chúng, nhưng chỉ sau khi bạn đăng cặp file lên đúng URL mà client sẽ gọi.

### Sidecar gợi ý, không phải API riêng

Mirror của sản phẩm nên mang đủ metadata để wrapper không trôi im lặng. Layout để học, do bạn sở hữu, trông như sau:

```text
models/df3-mono-48k/
  df_bg.wasm
  DeepFilterNet3_onnx.tar.gz
  config.json             # hop, sample_rate, shape state
  LICENSE_WEIGHTS.txt
  SHA256SUMS
  CHANGELOG.md
```

`config.json` là manifest của bạn: sample rate (48000 với gói này), hop, tên input, và shape state. API công khai của npm không bắt bạn upload một file mang đúng tên đó. Client chỉ xin đúng hai đường dưới `cdnUrl`. Hãy để manifest cạnh chúng cho người và cho CI.

### Quy tắc đường dẫn trong README

README gói nêu:

| Gói | WASM | Kho mô hình |
|-----|------|-------------|
| ≤ 1.1.2 | `{cdnUrl}/pkg/df_bg.wasm` | `{cdnUrl}/models/DeepFilterNet3_onnx.tar.gz` |
| 1.2.x, như README vẫn ghi cho mọi bản ≥ 1.2.0 | `{cdnUrl}/v2/pkg/df_bg.wasm` | `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` |
| `getAssetUrls()` của bản 1.3.0 đã cài | `{cdnUrl}/v3/pkg/df_bg.wasm` | `{cdnUrl}/v3/models/DeepFilterNet3_onnx.tar.gz` |

Client tự thêm `v2/` với bản ≥ 1.2.0. Bạn không thêm. Base đã kết thúc bằng `/v2` sẽ thành `.../v2/v2/...` và 404. Mã nguồn 1.3.0 của `AssetLoader.getAssetUrls()` trên kho công khai lại thêm tiền tố `v3/` thay vì chuỗi `v2/` mà README vẫn in. Bảng trên là hợp đồng README mà khóa này dùng để tự chấm. Trước khi upload mirror sản xuất, hãy in URL từ gói đã cài và đăng đúng thư mục đó. Đừng bịa tên file thứ ba. Tên kho trong cả hai layout là `DeepFilterNet3_onnx.tar.gz`, từ kho DeepFilterNet upstream. Tên file WASM là `df_bg.wasm`.

### Cache, nén, toàn vẹn

Phục vụ cặp file với Brotli hoặc gzip. Kho ONNX thường nén tốt; WASM kém hơn nhưng vẫn có lợi. Ưu tiên tên đánh địa chỉ theo nội dung, hoặc một thư mục phiên bản bất biến, với `Cache-Control: public, max-age=31536000, immutable`. Công bố tổng SHA-256 và kiểm sau khi tải trong CI. Từ chối canary nếu hash WASM và hash mô hình không cùng một lần phát hành. Module SIMD mới đứng cạnh kho tháng trước là lỗi đóng gói, không phải lỗi chất lượng mô hình.

Ghi đè tại chỗ một URL mà bạn đã bảo cache giữ một năm là cách đầu độc client. Đi tiếp bằng cách đăng thư mục mới. Giữ thư mục cũ để trỏ `cdnUrl` ngược lại, hoặc hạ phiên bản gói, mà không phải dựng lại cả thế giới. Phiên bản gói JavaScript và phiên bản thư mục asset đi cùng nhau trong ma trận tương thích: opset, bản tract hoặc ORT, bộ tính năng SIMD, sàn trình duyệt.

### Dung lượng là quyết định theo kênh

Ngân sách để học, không phải số đo kho này: web mobile ở lượt tải đầu muốn cặp file nén nhỏ, desktop có thể tải trễ một bản lớn hơn, và app native có hạn mức cửa hàng riêng. Trọng số INT8 và mô hình siêu nhẹ (bài 04-05) là cách chạm con số mobile. Chúng được chọn trước lúc upload CDN, nên hình vẽ đặt lượng tử hóa bên trái bước biên dịch WASM.

### Đóng gói và giấy phép

Gói npm cấp phép kép Apache-2.0 OR MIT, theo upstream DeepFilterNet. Trọng số bạn phân phối lại cần cùng cách đọc giấy phép upstream, cộng thông báo bên thứ ba cho runtime. Đừng nhét audio khách hàng vào artifact. File mô hình không phải bản ghi, nhưng telemetry lưu metric giọng có thể là dữ liệu cá nhân. Cây `/Users/nguyenlelinh/ncc/mezon-noise-suppression` là checkout cục bộ tùy chọn của giảng viên. Bài khóa không sửa cây đó.

### Rollout theo giai đoạn

Canary một nhóm desktop nhỏ, theo dõi underrun và lỗi init, rồi mở rộng. Lỗi khởi động lạnh là lỗi đóng gói: 404, CORS, sai MIME, tiền tố kép. Underrun ở trạng thái ổn định là lỗi hệ số realtime. Hãy log tách hai loại.

## Mini-lab

Chạy `python3 prefix_check.py`. Hàm mã hóa quy tắc README: `cdnUrl` của 1.3.0 không được kết thúc sẵn bằng `/v2`.

```python
def prefix_ok(url):
    if url.rstrip("/").endswith("/v2"):
        return "double-prefix risk"
    return "base-ok"

print(prefix_ok("https://example.com/df3"))
print(prefix_ok("https://example.com/df3/v2"))
```

**Expected**

```text
base-ok
double-prefix risk
```

**Failure modes**

- Nhét `v2` vào `cdnUrl` vì bảng README có `v2` trong đường đã resolve. Tiền tố là việc của client.
- Chỉ upload `df_bg.wasm` dưới `v2/pkg/` và để tar.gz ở đường 1.1.2. Cặp file phải cùng thế hệ gói.
- Tin chuỗi `v2` của README khi `getAssetUrls()` của bản đã cài in `v3`. Lab kiểm quy tắc “đừng nhúng tiền tố”; tên thư mục lấy từ gói bạn thực sự ship.
- Băm file trên laptop rồi đăng byte khác lên CDN.

## Bẫy thường gặp

- Đánh giá sản phẩm bằng dung lượng `npm install`.
- Không có manifest, nên đổi hop vẫn “thành công” và làm gãy overlap-add.
- Ship WASM bản debug.
- Phá cache bằng query mỗi lần tải trang (`?t=Date.now()`), vô hiệu CDN.
- Trộn client ≤ 1.1.2 và ≥ 1.2.0 trong một thư mục khi chưa có đủ cả hai layout.

## Bài tập

1. Viết các trường `config.json` của bạn phải có để hop DeepFilter 48 kHz không trôi.
2. Đề xuất ngân sách dung lượng nén cho web mobile và desktop, và nêu núm nào (INT8, mô hình siêu nhẹ, tải trễ) chạm từng ngân sách.
3. Tài liệu hóa một lần rollback khôi phục cặp artifact trước mà không sửa kho sản phẩm.
4. Liệt kê câu hỏi giấy phép phải trả lời trước khi phân phối lại `DeepFilterNet3_onnx.tar.gz` cho mục đích thương mại.
5. Một đồng đội đặt `cdnUrl` thành `https://cdn.example.com/df3/v2`. Client ≥ 1.2.0 sẽ xin URL nào nếu nó theo README và lại thêm `v2`?

### Gợi ý đáp án

1. Sample rate, hop, cửa sổ, tên input của mô hình, shape state, và phiên bản gói mà các shape đã được kiểm.
2. Mobile: lượng tử hóa hoặc đổi mô hình nhỏ hơn, giữ cặp file trên CDN, không nhét vào npm. Desktop: tải trễ chấp nhận được nếu join không bị chặn (bài 07-02).
3. Giữ thư mục trước. Trỏ `cdnUrl` vào base resolve tới thư mục đó, hoặc ghim gói cũ. Đừng ghi đè URL bất biến.
4. Giấy phép upstream, giấy phép kép Apache-2.0 OR MIT của gói, thương hiệu, và mirror của bạn có được host lại kho hay không. Đọc model card upstream. Đừng đoán “phi thương mại” khi chưa có chữ.
5. `https://cdn.example.com/df3/v2/v2/pkg/df_bg.wasm` và `.../v2/v2/models/DeepFilterNet3_onnx.tar.gz`. Đó là lỗi tiền tố kép.

## Đọc thêm

- README gói, mục Custom CDN Configuration: [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- [Tài liệu ONNX Runtime](https://onnxruntime.ai/docs/) về artifact mô hình đã tối ưu.
- Kho upstream [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).
- Chương 07 về tải bằng TrackProcessor của LiveKit và chính sách khi CDN lỗi.
