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

Một đồ thị ONNX (định dạng trao đổi đồ thị) chuẩn xác vẫn có thể thất bại khi đưa vào sản phẩm nếu khâu **đóng gói** sai sót: dung lượng tải lần đầu quá lớn, URL không được lưu đệm (cache), tệp WASM và gói mô hình lệch phiên bản, hoặc vướng rào cản giấy phép phân phối. Gói `deepfilternet3-noise-filter` **1.3.0** tách bạch hai lớp này: gói npm chỉ chứa mã kết nối JavaScript, AudioWorklet (callback xử lý âm thanh trên luồng thời gian thực) được nhúng nội tuyến và bộ nạp; còn hai tệp dung lượng lớn là `df_bg.wasm` và `DeepFilterNet3_onnx.tar.gz` được tải từ CDN (mạng phân phối nội dung) thông qua `assetConfig.cdnUrl`. Bài học này trình bày bố cục tệp, quy tắc tiền tố phiên bản, kiểm tra tính toàn vẹn và phương án khôi phục (rollback). Chi tiết ghép nối URL đầy đủ sẽ được trình bày ở bài 07-03.

![WASM và kho ONNX đã đóng gói ở phía CDN của đường vào trình duyệt]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Hình. Khâu đóng gói quyết định chính xác những tệp nhị phân nào sẽ đi tới bước biên dịch WASM trên trình duyệt.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ tách bạch được gói npm khỏi các tệp tài nguyên trên CDN, áp dụng đúng quy tắc đường dẫn cho các phiên bản ≤ 1.1.2 và ≥ 1.2.0 (bao gồm bản 1.3.0 vốn tự động nối tiền tố `v2/`), phát hiện và loại bỏ các `cdnUrl` đã chứa sẵn `v2`, đồng thời liệt kê đầy đủ các hạng mục kiểm tra giấy phép và cache trước khi phát hành.

## Kế hoạch 60 phút

- **0–10 phút** — Lượt tải lần đầu chặn cuộc gọi, và vì sao dung lượng gói npm không phản ánh đúng tải trọng thực tế.
- **10–25 phút** — Cặp tệp tài nguyên, tệp cấu hình đi kèm và quy ước phiên bản (semver).
- **25–40 phút** — Quy tắc tiền tố đường dẫn, nén dữ liệu và chính sách cache bất biến.
- **40–50 phút** — Kiểm tra toàn vẹn, tuân thủ giấy phép và phát hành theo từng giai đoạn (staged rollout).
- **50–60 phút** — Thực hành mini-lab, bẫy thường gặp và làm bài tập.

## Giải thích cốt lõi

### Hai thành phần, một sản phẩm thống nhất

Lệnh `npm install deepfilternet3-noise-filter` cài đặt thư viện kèm phụ thuộc ngang hàng (peer dependency) `livekit-client` ^2. Theo README, mã nguồn worker và worklet đã được nhúng sẵn dưới dạng blob URL, nên các công cụ đóng gói như Webpack, Vite, Rollup, esbuild hay Parcel không cần cài thêm plugin sao chép tệp. Tuy nhiên, phần cài qua npm mới chỉ là lớp giao diện JavaScript gọn nhẹ, chưa bao gồm mô hình. Khi chạy, `DeepFilterNet3Core.initialize()` tải song song hai tệp trọng yếu là module WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) và gói nén mô hình — đây mới là phần quyết định thời gian khởi động lạnh. Lượng tử hóa (bài 06-02) và tối ưu SIMD (bài 06-03) giúp cải thiện dung lượng và tốc độ của hai tệp này, nhưng chỉ phát huy tác dụng khi cặp tệp được đăng tải lên đúng đường dẫn mà client gọi tới.

### Tệp siêu dữ liệu đi kèm (sidecar) nên duy trì

Kho lưu trữ tài nguyên của đội ngũ nên chứa đầy đủ siêu dữ liệu đi kèm để tránh việc wrapper và mô hình lệch nhau âm thầm. Một bố cục thư mục chuẩn cho quá trình quản lý có dạng như sau:

```text
models/df3-mono-48k/
  df_bg.wasm
  DeepFilterNet3_onnx.tar.gz
  config.json             # hop, sample_rate, shape state
  LICENSE_WEIGHTS.txt
  SHA256SUMS
  CHANGELOG.md
```

Tệp `config.json` đóng vai trò bảng kê kỹ thuật (manifest) ghi rõ tần số lấy mẫu (48000 Hz với gói này), độ dài hop, tên tensor đầu vào và kích thước trạng thái. API công khai của gói npm không yêu cầu bạn phải tải tệp này lên CDN — bản thân client chỉ yêu cầu đúng hai đường dẫn dưới `cdnUrl` — nhưng việc lưu manifest song song giúp kỹ sư và hệ thống CI dễ dàng đối chiếu.

### Quy tắc đường dẫn trong README

README của gói quy định cấu trúc đường dẫn theo phiên bản như sau:

| Phiên bản gói | Đường dẫn WASM | Đường dẫn gói mô hình |
|-----|------|-------------|
| ≤ 1.1.2 | `{cdnUrl}/pkg/df_bg.wasm` | `{cdnUrl}/models/DeepFilterNet3_onnx.tar.gz` |
| ≥ 1.2.0, gồm 1.3.0 | `{cdnUrl}/v2/pkg/df_bg.wasm` | `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` |

Với các phiên bản từ 1.2.0 trở lên, client sẽ tự động thêm tiền tố `v2/`; người cấu hình không được tự thêm vào `cdnUrl`. Nếu đường dẫn gốc đã kết thúc bằng `/v2`, URL sinh ra sẽ trở thành `.../v2/v2/...` và gặp lỗi 404. Đường dẫn gốc minh họa trong README là `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`. Tên gói mô hình là `DeepFilterNet3_onnx.tar.gz` (từ kho DeepFilterNet gốc của Rikorose), còn tên tệp WASM là `df_bg.wasm`.

### Cache, nén dữ liệu và kiểm tra toàn vẹn

Cặp tệp tài nguyên cần được phục vụ kèm nén Brotli hoặc gzip (gói ONNX thường nén giảm dung lượng rất tốt; tệp WASM nén ít hơn nhưng vẫn đáng kể). Nên đặt tên tệp theo mã băm nội dung hoặc đặt trong thư mục phiên bản cố định kèm header `Cache-Control: public, max-age=31536000, immutable`. Công bố mã băm SHA-256 và tự động đối chiếu sau khi tải về trong quy trình CI; chặn bản thử nghiệm canary nếu mã băm của WASM và mô hình không thuộc cùng một đợt phát hành. Một module SIMD mới chạy chung với gói mô hình từ tháng trước là lỗi đóng gói, không phải lỗi chất lượng mô hình.

Tuyệt đối không ghi đè trực tiếp lên một URL đã gắn chính sách cache một năm vì điều đó sẽ gây xung đột dữ liệu ở máy khách. Khi nâng cấp, hãy xuất bản sang thư mục phiên bản mới và giữ nguyên thư mục cũ để có thể chuyển `cdnUrl` ngược về hoặc hạ phiên bản gói ngay lập tức khi cần rollback mà không phải biên dịch lại toàn bộ hệ thống. Phiên bản gói JavaScript và thư mục tài nguyên phải luôn được quản lý theo cặp trong ma trận tương thích (gồm opset, phiên bản `tract` hoặc ORT, tập tính năng SIMD và phiên bản trình duyệt tối thiểu).

### Dung lượng là quyết định theo từng kênh triển khai

Về mặt ngân sách kỹ thuật (mức định hướng thiết kế, không phải số đo cố định của khóa học): nền tảng web di động cần cặp tệp nén nhỏ gọn cho lượt tải đầu tiên, nền tảng máy tính để bàn có thể chấp nhận tải trễ bản đầy đủ hơn, còn ứng dụng native chịu giới hạn kích thước riêng của kho ứng dụng. Trọng số INT8 và các mô hình siêu nhẹ (bài 04-05) là công cụ chính để đáp ứng ngân sách di động; quyết định này phải được chốt trước bước tải lên CDN, đúng như vị trí của khâu lượng tử hóa nằm trước bước biên dịch WASM trong hình minh họa.

### Đóng gói và tuân thủ giấy phép

Gói npm áp dụng giấy phép kép Apache-2.0 hoặc MIT, kế thừa từ dự án DeepFilterNet gốc. Khi phân phối lại tệp trọng số, bạn cần tuân thủ đúng điều khoản giấy phép của kho nguồn gốc và đính kèm đầy đủ thông báo bản quyền của các thư viện runtime bên thứ ba. Tuyệt đối không đưa tệp âm thanh của khách hàng vào gói phát hành; dù tệp mô hình không chứa bản ghi, dữ liệu telemetry ghi nhận chỉ số giọng nói vẫn có thể bị xếp vào nhóm dữ liệu cá nhân cần bảo vệ.

### Phát hành theo từng giai đoạn (staged rollout)

Hãy bắt đầu triển khai thử nghiệm (canary) trên một nhóm nhỏ người dùng máy tính để bàn, theo dõi sát tỉ lệ underrun và lỗi khởi tạo rồi mới mở rộng phạm vi. Cần tách bạch hai nhóm lỗi trong hệ thống log: các lỗi xảy ra lúc khởi động lạnh (như 404, CORS, sai kiểu MIME, lặp tiền tố đường dẫn) thuộc về khâu đóng gói, còn lỗi underrun trong trạng thái chạy ổn định thuộc về ngân sách hệ số thời gian thực.

## Mini-lab

Lưu đoạn mã sau thành `prefix_check.py` và chạy `python3 prefix_check.py`. Hàm này kiểm tra đúng quy tắc từ README: `cdnUrl` dùng cho bản 1.3.0 không được kết thúc sẵn bằng `/v2`.

```python
def prefix_ok(url):
    if url.rstrip("/").endswith("/v2"):
        return "double-prefix risk"
    return "base-ok"

print(prefix_ok("https://example.com/df3"))
print(prefix_ok("https://example.com/df3/v2"))
```

**Kết quả kỳ vọng**

```text
base-ok
double-prefix risk
```

**Lỗi thường gặp**

- Tự thêm `/v2` vào `cdnUrl` vì nhìn thấy `v2` trong cột đường dẫn đã phân giải của bảng README, khiến client bản ≥ 1.2.0 nối thêm một lần nữa và gửi yêu cầu lỗi 404 tới `.../v2/v2/...`.
- Chỉ tải `df_bg.wasm` lên đường dẫn `v2/pkg/` nhưng lại để tệp `.tar.gz` ở đường dẫn cũ của bản 1.1.2, làm lệch thế hệ giữa hai tệp.
- Tính mã băm SHA-256 trên máy cá nhân nhưng lại tải một bản biên dịch khác lên CDN.

## Bẫy thường gặp

- Đánh giá tải trọng mạng của sản phẩm chỉ dựa vào dung lượng lệnh `npm install`.
- Thiếu tệp manifest, khiến việc thay đổi độ dài hop vẫn nạp thành công về mặt kỹ thuật nhưng làm hỏng bước overlap-add.
- Phát hành tệp WASM bản debug lên môi trường sản phẩm.
- Gắn chuỗi truy vấn phá cache ở mỗi lần tải trang (ví dụ `?t=Date.now()`), làm vô hiệu hóa hoàn toàn lợi ích của CDN.
- Phục vụ lẫn lộn client bản ≤ 1.1.2 và ≥ 1.2.0 trên cùng một thư mục khi chưa bố trí đủ cả hai cấu trúc đường dẫn.

## Bài tập

1. Liệt kê các trường bắt buộc cần có trong tệp `config.json` để đảm bảo cấu hình hop 48 kHz của DeepFilter không bị lệch giữa các phiên bản.
2. Đề xuất ngân sách dung lượng nén phù hợp cho web di động và web máy tính để bàn, đồng thời nêu rõ biện pháp tương ứng (INT8, mô hình siêu nhẹ, tải trễ) để đạt từng ngân sách.
3. Mô tả quy trình rollback khôi phục lại cặp tệp tài nguyên phiên bản trước mà không cần chỉnh sửa mã nguồn kho sản phẩm.
4. Liệt kê các câu hỏi pháp lý về giấy phép cần làm rõ trước khi phân phối lại tệp `DeepFilterNet3_onnx.tar.gz` cho mục đích thương mại.
5. Một đồng nghiệp cấu hình `cdnUrl` là `https://cdn.example.com/df3/v2`. Client phiên bản ≥ 1.2.0 tuân theo README sẽ gửi yêu cầu tới những URL nào?

### Gợi ý đáp án

1. Cần ghi rõ tần số lấy mẫu (sample rate), độ dài hop, kích thước cửa sổ, tên các tensor đầu vào, kích thước tensor trạng thái và phiên bản gói đã dùng để kiểm chứng các kích thước đó.
2. Trên di động: ưu tiên lượng tử hóa hoặc chọn mô hình nhỏ hơn, đặt cặp tệp trên CDN thay vì gộp vào npm. Trên máy tính để bàn: có thể chấp nhận tải trễ miễn là không chặn thao tác tham gia cuộc gọi (bài 07-02).
3. Giữ nguyên thư mục tài nguyên cũ trên CDN; khi cần rollback chỉ cần trỏ `cdnUrl` về đường dẫn gốc của phiên bản trước hoặc ghim lại phiên bản gói cũ, tuyệt đối không ghi đè lên URL đã gắn `immutable`.
4. Cần kiểm tra điều khoản giấy phép của kho nguồn gốc, giấy phép kép Apache-2.0/MIT của gói, quy định về nhãn hiệu và quyền tự lưu trữ lại (mirror) tệp trọng số; luôn đọc kỹ model card gốc thay vì tự suy đoán là “phi thương mại”.
5. Client sẽ yêu cầu `https://cdn.example.com/df3/v2/v2/pkg/df_bg.wasm` và `.../v2/v2/models/DeepFilterNet3_onnx.tar.gz` — đây chính là lỗi lặp tiền tố.

## Đọc thêm

- README của gói, mục *Custom CDN Configuration*: [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- [Tài liệu ONNX Runtime](https://onnxruntime.ai/docs/) về định dạng tệp mô hình đã tối ưu hóa.
- Tệp trọng số gốc [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).
- Chương 07 về quy trình nạp mô hình qua `TrackProcessor` của LiveKit và chính sách xử lý khi CDN gặp sự cố.

## Video tham khảo

- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, tiếng Anh. **Xem trước.** Video minh họa chặng đường chuyển đổi từ đồ thị huấn luyện sang tệp triển khai gọn nhẹ cho máy khách — nền tảng của bước đóng gói kết hợp WASM và cache.
- [What is a CDN (Content Delivery Network) and How does a CDN Work?](https://www.youtube.com/watch?v=rIAIzf6utOc) — Cloudflare, tiếng Anh. Giải thích cơ chế cache tại biên so với máy chủ gốc, giúp hình dung rõ cách phân phối các tệp mô hình tĩnh có dung lượng lớn.
- [Quantization explained with PyTorch - Post-Training Quantization, Quantization-Aware Training](https://www.youtube.com/watch?v=0VdNflU08yA) — Umar Jamil, tiếng Anh. Trình bày vai trò của lượng tử hóa trong việc giảm kích thước gói tải và cái giá phải đánh đổi về độ chính xác.
