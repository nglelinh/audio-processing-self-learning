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

Hãy thử nghĩ xem chuyện gì xảy ra nếu bạn có 10.000 người dùng vào họp trực tuyến mỗi ngày và mỗi lần mở trình duyệt, ứng dụng lại đi tải mới 3,4 MB mô hình từ một máy chủ gốc duy nhất đặt ở nửa bên kia địa cầu: vừa tốn hàng chục gigabyte băng thông mỗi ngày, vừa khiến người dùng chờ dài cổ, lại chỉ cần một dòng cấu hình thiếu header CORS hay sai tiền tố `v2/` là toàn bộ tính năng khử nhiễu biến mất không một dấu vết! Đó là lý do tầng **tải tài nguyên qua CDN** là mạch máu thầm lặng của mọi sản phẩm AI chạy trên trình duyệt.

Chạy DeepFilterNet3 trên trình duyệt đòi hỏi hai tệp nhị phân lớn: module **WASM** (WebAssembly — mã nhị phân chạy trong trình duyệt) và gói trọng số `DeepFilterNet3_onnx.tar.gz`. Nếu đóng gói cả hai vào tarball npm, kích thước cài đặt sẽ tăng vọt và mỗi lần cập nhật tệp mô hình đều buộc phải triển khai lại toàn bộ ứng dụng web. Do đó, các hệ thống thực tế tải chúng từ **CDN** (mạng phân phối nội dung) để tận dụng lớp lưu đệm gần người dùng. Gói `deepfilternet3-noise-filter` **1.3.0** tự động phân giải đường dẫn từ `assetConfig.cdnUrl`. Bài học này giúp bạn tính chính xác 4 URL cho hai thế hệ 1.1.2 và 1.3.0, đồng thời đảm bảo một lỗi mạng khi tải tệp không làm gián đoạn cuộc gọi.

**Mạch bài học:** Băng thông & độ trễ khi phân phối mô hình AI trên web → Kiến thức cần nhớ (Phân phối biên CDN & HTTP Caching bất biến, Hợp đồng CORS & MIME `application/wasm`, Tải song song `Promise.all` & Sẵn sàng tăng dần) → Cặp tệp tài nguyên & quy tắc đường dẫn `v2/` → Giải thích tính tay tiết kiệm băng thông từ cache 80% và so sánh tải song song vs. tuần tự → Bảng xử lý 6 lỗi tải một phần, Mini-lab và Bài tập.

![CDN tải WASM và kho ONNX trước khi AudioWorklet biên dịch]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Hình. Máy khách phân giải `cdnUrl` thành một URL cho tệp WASM và một URL cho gói mô hình, sau đó mới biên dịch WASM.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ viết chính xác các URL đã phân giải cho phiên bản ≤ 1.1.2 và phiên bản 1.3.0 theo quy tắc README, không đưa `v2` vào `cdnUrl`, thiết lập header cache HTTP an toàn khi nâng cấp phiên bản, và cài đặt cơ chế bypass khử nhiễu khi thao tác tải gặp lỗi.

## Kiến thức cần nhớ: Ba trụ cột của phân phối mô hình AI qua CDN

### 1. Mạng phân phối biên (CDN) và Lưu đệm bất biến (`immutable`)
- **Là gì:** Hệ thống máy chủ đặt gần người dùng cuối (edge PoP) phục vụ các tệp tĩnh `df_bg.wasm` và `DeepFilterNet3_onnx.tar.gz` kèm header `Cache-Control: public, max-age=31536000, immutable`.
- **Nghiên cứu gì:** Biến bài toán tải nhiều megabyte mỗi cuộc gọi thành chi phí một lần duy nhất (0 ms mạng ở mọi lần gọi sau), đồng thời bảo vệ quyền riêng tư tuyệt đối vì CDN chỉ gửi trọng số một chiều xuống máy khách.

### 2. Hợp đồng giao thức trình duyệt: CORS, MIME và Tính nguyên tử cặp tệp
- **Là gì:** Ba điều kiện hạ tầng bắt buộc khi `fetch` tài nguyên khác tên miền: `Access-Control-Allow-Origin` (CORS), `Content-Type: application/wasm` (MIME) và gom cặp WASM + trọng số vào cùng một thư mục phiên bản (`v2/`).
- **Nghiên cứu gì:** Chẩn đoán nhanh nguyên nhân thất bại lúc `initialize()` (404 do lặp `/v2/v2/`, chặn CORS, lệch thế hệ WASM–mô hình) mà không đổ lỗi oan cho thuật toán lọc nhiễu.

### 3. Sẵn sàng tăng dần (Progressive Readiness) với `Promise.all`
- **Là gì:** Tải song song cả hai tệp trên kết nối HTTP/2, tách biệt khỏi `room.connect()`, và chuyển êm về bypass/APM khi tải đứt đoạn thay vì treo giao diện.
- **Nghiên cứu gì:** Tối ưu hóa thời gian khởi động lạnh và độ tin cậy vận hành trên mạng di động chập chờn hoặc mạng doanh nghiệp có tường lửa (mirror nội bộ VPC).

## Kế hoạch 60 phút

- **0–10 phút** — Hai tệp tài nguyên cần tải và thời điểm `initialize()` thực hiện tải.
- **10–25 phút** — Cấu hình `cdnUrl` và quy tắc tiền tố phiên bản.
- **25–40 phút** — Chính sách cache, kiểu MIME và cấu hình CORS.
- **40–50 phút** — Trạng thái sẵn sàng tăng dần mà không chặn `connect()`.
- **50–60 phút** — Thực hành mini-lab: tính 4 URL chuẩn.

## Cặp tệp tài nguyên

Theo README của gói, có hai tệp chính:

| Tệp tài nguyên | Vai trò |
|-------|---------|
| `pkg/df_bg.wasm` (dưới base hoặc dưới `v2/`) | Module WASM (có bật SIMD ở các phiên bản hỗ trợ) |
| `models/DeepFilterNet3_onnx.tar.gz` | Gói mô hình DeepFilterNet3 từ kho nguồn gốc |

Đường dẫn kho nguồn gốc: [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz). Lưu ý rằng CDN chỉ phân phối **trọng số và mã nhị phân**, hoàn toàn không tiếp nhận âm thanh người dùng; mọi bước suy luận đều diễn ra cục bộ trên thiết bị, không bao giờ thêm tính năng tải PCM lên máy chủ “để gỡ lỗi” trên bản sản phẩm.

Trong cặp tệp này, đồ thị ONNX (định dạng trao đổi đồ thị) nằm trong tệp `.tar.gz`, còn tối ưu SIMD (một lệnh xử lý nhiều dữ liệu) nằm trong tệp WASM; AudioWorklet (callback xử lý âm thanh trên luồng thời gian thực) chỉ bắt đầu hoạt động sau khi cả hai tệp đã tải xong.

## Cấu hình đường dẫn gốc

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

Nếu bỏ qua `cdnUrl`, gói sẽ dùng mặc định chính đường dẫn gốc của Mezon như trên. Khi dựng máy chủ lưu trữ riêng (mirror), bạn chỉ cần thay tên miền gốc và tiền tố đường dẫn tương ứng.

### Quy tắc đường dẫn theo phiên bản

README quy định rõ cấu trúc đường dẫn phân giải cho từng dải phiên bản:

| Phiên bản gói | Đường dẫn đã phân giải |
|-----|------------------|
| ≤ 1.1.2 | `{cdnUrl}/pkg/df_bg.wasm` và `{cdnUrl}/models/DeepFilterNet3_onnx.tar.gz` |
| ≥ 1.2.0, gồm 1.3.0 | `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` |

Với phiên bản ≥ 1.2.0 (bao gồm 1.3.0), chính thư viện sẽ tự động nối thêm `v2/`; tuyệt đối không tự chèn `v2` vào `cdnUrl`. Đường dẫn gốc ví dụ công khai là `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`. Cũng theo README, bản dựng SIMD từ 1.2.0 trở lên nhanh hơn khoảng 20–30% (số liệu công bố từ README) và yêu cầu trình duyệt Chrome 91+, Firefox 89+ hoặc Safari 16.4+. Riêng bản 1.3.0 cập nhật `tract` lên 0.23.3 cho đường WASM, nhưng thay đổi này không làm đổi quy tắc tiền tố `v2/`.

## Giải thích: Tính tay lợi ích của tải song song `Promise.all` và Cache bất biến

### Phép tính 1: Tải song song vs. Tải tuần tự trên kết nối độ trễ cao
Giả sử cặp tệp nén có dung lượng minh họa `df_bg.wasm` = $$1{,}2\text{ MB}$$ ($$9{,}6\text{ Mb}$$) và `DeepFilterNet3_onnx.tar.gz` = $$2{,}2\text{ MB}$$ ($$17{,}6\text{ Mb}$$), tổng $$27{,}2\text{ Mb}$$, trên mạng 4G có băng thông $$10\text{ Mbps}$$ và độ trễ vòng (RTT) $$100\text{ ms}$$:
- **Tải tuần tự (`await fetch(wasm); await fetch(model)`):** Chịu 2 lần RTT nối tiếp cộng thời gian truyền:
  $$ T_{\text{seq}} = 2 \times 0{,}10 + \frac{9{,}6 + 17{,}6}{10} = 0{,}20 + 2{,}72 = \mathbf{2{,}92\text{ s}}. $$
- **Tải song song (`Promise.all` trên HTTP/2):** Chỉ chịu 1 lần RTT chung cho cả hai luồng ghép kênh:
  $$ T_{\text{par}} = 0{,}10 + \frac{27{,}2}{10} = \mathbf{2{,}82\text{ s}} $$
  (trên mạng vệ tinh hoặc kết nối xuyên lục địa có $$\text{RTT} = 300\text{ ms}$$, tải song song cắt ngay **300 ms** chờ rỗi!).

### Phép tính 2: Tác động tài chính của một dòng header `Cache-Control: immutable`
Giả sử hệ thống có **10.000 lượt gọi mỗi ngày**, trong đó **80%** là người dùng quay lại trong tuần:
- **Quên bật cache (hoặc gắn `?t=Date.now()` phá cache):**
  $$ 10\,000 \times 3{,}4\text{ MB} = \mathbf{34\,000\text{ MB} \approx 34\text{ GB/ngày}} \approx \mathbf{1{,}02\text{ TB/tháng}}. $$
- **Bật `Cache-Control: public, max-age=31536000, immutable` trên thư mục phiên bản:** Chỉ 20% lượt gọi đầu (2.000 lượt) cần tải từ CDN:
  $$ 2\,000 \times 3{,}4\text{ MB} = \mathbf{6{,}8\text{ GB/ngày}} \approx \mathbf{204\text{ GB/tháng}} $$
  — cắt thẳng **80% chi phí băng thông CDN**, đồng thời giúp 8.000 lượt gọi mỗi ngày khởi động khử nhiễu gần như tức thì!

## Sẵn sàng tăng dần

Phương thức `initialize()` tải song song cả hai tệp bằng `Promise.all` rồi biên dịch WASM trên luồng chính. `setProcessor` sẽ chờ `init`, và `init` chờ quá trình này hoàn tất; tuy nhiên luồng báo hiệu kết nối phòng (`connect()`) không được phép bị chặn theo.

```text
connect() ──► phòng đã lên, mic tắt hoặc NS đang bypass
                ├─► tải cặp ──► ok ──► setProcessor, rồi publish, rồi setEnabled(true)
                └─► tải cặp ──► lỗi ──► telemetry, ở lại bypass hoặc chỉ APM
```

Khi tài nguyên đã nằm sẵn trong cache, quy trình vẫn đi theo thứ tự chuẩn của README: khởi tạo, gọi `setProcessor`, rồi `publishTrack`. Sai lầm cần tránh là đặt `await` chờ tải CDN lạnh ngay **bên trong** `connect()` trước khi người dùng vào được phòng. Nếu đo được tiến độ tải theo byte, hãy hiển thị trạng thái nhẹ kiểu “đang chuẩn bị lọc nhiễu”, và chỉ hiện một thông báo toast duy nhất nếu tải thất bại.

Bản thân `TrackProcessor` (móc biến đổi track của LiveKit) không tự quản lý tầng cache; nó chỉ thực hiện yêu cầu `fetch` tới hai URL nói trên.

## Cấu hình cache HTTP

Các thư mục phiên bản bất biến nên trả về header `Cache-Control: public, max-age=31536000, immutable`. Khi nội dung nhị phân thay đổi, hãy đăng tải sang một thư mục mới để tiền tố phiên bản của gói trỏ tới, tuyệt đối không ghi đè tệp tại URL đã gắn `immutable`. Không thêm tham số truy vấn kiểu `?t=Date.now()` mỗi lần vào phòng vì sẽ phá hỏng hoàn toàn tỉ lệ trúng cache. Nếu ứng dụng dùng thêm Cache API, hãy lập khóa theo URL đầy đủ có phiên bản, giới hạn dung lượng lưu trữ và cung cấp tùy chọn hỗ trợ xóa cache lọc nhiễu.

Máy chủ cần phục vụ `df_bg.wasm` kèm header `Content-Type: application/wasm`. Thiếu header `Access-Control-Allow-Origin` thường chỉ hiện ra như một lỗi mạng chung chung, vì vậy cần ghi log rõ mã trạng thái HTTP và kiểu phản hồi. Cặp tệp WASM và gói mô hình phải được xem là một đơn vị nguyên tử: không ghép thử module SIMD của bản 1.3.0 với gói trọng số từ thời 1.1.2.

Trên mạng di động, độ trễ theo khu vực địa lý ảnh hưởng rõ rệt đến tốc độ tải lần đầu. Với khách hàng doanh nghiệp có tường lửa chặn tên miền công khai, hãy mirror cặp tệp vào hạ tầng VPC của họ (vẫn áp dụng đầy đủ CORS và TLS). API công khai của gói không hỗ trợ header xác thực riêng mà chỉ gọi `fetch` tiêu chuẩn.

## Bảng xử lý các lỗi tải một phần

| Loại lỗi | Tác động người dùng thấy | Hướng xử lý |
|-----|-----------------|--------------|
| 404 WASM hoặc mô hình | Không bật được khử nhiễu | Sửa cấu hình đường dẫn; phát hành âm thanh gốc |
| Lỗi CORS | Không bật được khử nhiễu | Bổ sung header CORS trên CDN |
| Tệp tải bị đứt đoạn | `initialize` ném ngoại lệ | Thử lại 1 lần, sau đó chuyển sang bypass |
| Mất mạng sau khi đã cache tốt | Có thể vẫn hoạt động bình thường | Kiểm chứng lại bằng disk cache hoặc Cache API |
| Lệch phiên bản giữa hai tệp | Âm thanh méo hoặc lỗi biên dịch | Khóa chặt hai tệp trong cùng một thư mục phiên bản |
| Sai kiểu MIME | Bộ nạp streaming báo lỗi | Cấu hình `Content-Type: application/wasm` |

## Ví dụ triển khai mirror riêng

Tải tệp `DeepFilterNet3_onnx.tar.gz` từ kho gốc cùng tệp `df_bg.wasm` tương ứng với phiên bản gói đang dùng. Đối với máy khách phiên bản ≥ 1.2.0 tuân theo README, đăng tải hai tệp vào `https://assets.example.com/ns/df3/v2/pkg/` và `.../v2/models/`, sau đó cấu hình `cdnUrl` là `https://assets.example.com/ns/df3`. Thực hiện kiểm thử nhanh (smoke-test) trên hồ sơ trình duyệt trắng có tắt cache, rồi kiểm tra lại lần hai khi bật cache.

## Mini-lab

Cho `cdnUrl = https://example.com/df3`, tính chính xác 4 URL phân giải cho phiên bản ≤ 1.1.2 và phiên bản ≥ 1.2.0 (gồm 1.3.0). Lưu đoạn mã sau thành `cdn_urls.py` và chạy `python3 cdn_urls.py`.

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

**Kết quả kỳ vọng**

```text
1.1.2
https://example.com/df3/pkg/df_bg.wasm
https://example.com/df3/models/DeepFilterNet3_onnx.tar.gz
1.3.0
https://example.com/df3/v2/pkg/df_bg.wasm
https://example.com/df3/v2/models/DeepFilterNet3_onnx.tar.gz
```

**Lỗi thường gặp**

- Đưa sẵn `v2` vào `cdnUrl`, tạo ra URL lỗi `https://example.com/df3/v2/v2/pkg/df_bg.wasm`.
- Đổi sai tên tệp so với chuẩn `df_bg.wasm` hoặc `DeepFilterNet3_onnx.tar.gz`.
- Chặn `connect()` chờ cả bốn URL phản hồi; thực tế mỗi máy khách chỉ tải đúng hai URL ứng với phiên bản gói đã cài, và bước này không được chặn signaling.
- Nhầm lẫn bản 1.3.0 dùng cấu trúc không tiền tố; từ 1.2.0 trở đi (gồm 1.3.0), máy khách luôn tự nối `v2/`.

## Bẫy thường gặp

1. Lỗi lặp tiền tố `/v2/v2/`.
2. Chặn giao diện tham gia phòng họp chờ lệnh `fetch`.
3. Tải âm thanh thô của người dùng lên máy chủ trong môi trường sản phẩm.
4. Dùng chung một thư mục tài nguyên cho cả máy khách ≤ 1.1.2 và ≥ 1.2.0 mà không tách cấu trúc đường dẫn.
5. Cấu hình sai kiểu MIME cho tệp `.wasm`.

## Bài tập

1. Tự viết lại cả 4 URL từ trí nhớ, sau đó đối chiếu với phần kết quả kỳ vọng của mini-lab.
2. Liệt kê các trạng thái giao diện `idle`, `downloading`, `ready`, `error` và chỉ rõ phương thức nào của processor sẽ được gọi khi chuyển sang `ready`.
3. Viết giá trị header `Cache-Control` cho cây thư mục `v2` bất biến cùng quy tắc phát hành cây thư mục mới khi cập nhật mô hình.
4. Phác thảo khoảng 10 dòng chính sách xử lý sự cố khi tải tài nguyên lỗi mà vẫn giữ cuộc họp hoạt động bình thường.
5. Giải thích vì sao tệp `.wasm` và tệp `.tar.gz` bắt buộc phải thuộc cùng một thế hệ thư mục phiên bản.

### Gợi ý đáp án

1. Có 2 tệp nhân với 2 thế hệ phiên bản; chỉ thế hệ ≥ 1.2.0 (gồm 1.3.0) có thêm tiền tố `v2/`, còn đường dẫn gốc vẫn giữ nguyên `https://example.com/df3`.
2. Trạng thái `ready` đạt được ngay sau khi `initialize()` hoàn tất; khi đó tiến hành gọi `setProcessor` (nếu chưa gọi) và `await setEnabled(true)` nếu người dùng đang bật khử nhiễu.
3. Dùng `public, max-age=31536000, immutable` trên thư mục đã gắn phiên bản; mỗi khi tệp nhị phân thay đổi thì xuất bản thư mục mới, không ghi đè thư mục cũ.
4. Bắt lỗi (rejection) từ `setProcessor` hoặc `initialize`, chuyển sang phát hành track âm thanh thô, gửi một sự kiện telemetry ghi rõ nguyên nhân lỗi và không lặp lại yêu cầu tải vô hạn.
5. Module WASM SIMD và gói trọng số là một cặp đồng bộ; tách rời hai thế hệ thư mục sẽ khiến module biên dịch đọc nhầm cấu trúc hoặc trọng số không tương thích.

## Đọc thêm

- README của gói, mục *Custom CDN*: [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- Tài liệu MDN về [HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching) và [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS).
- Gói mô hình nguồn gốc [DeepFilterNet3_onnx.tar.gz](https://github.com/Rikorose/DeepFilterNet/blob/main/models/DeepFilterNet3_onnx.tar.gz).
- Chương 06 về lượng tử hóa, SIMD và quy trình đóng gói cho đúng cặp tệp này.

## Video tham khảo

- [What is a CDN (Content Delivery Network) and How does a CDN Work?](https://www.youtube.com/watch?v=rIAIzf6utOc) — Cloudflare, tiếng Anh. **Xem trước.** Giải thích cơ chế phân phối từ máy chủ biên (edge cache) so với máy chủ gốc — lý do chính để tách tệp WASM và mô hình ra khỏi tarball npm.
- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, tiếng Anh. Phần suy luận phía máy khách giải thích vì sao trình duyệt phải tải đủ cả đồ thị mô hình lẫn engine thực thi trước hop đầu tiên.
- [Quantization explained with PyTorch - Post-Training Quantization, Quantization-Aware Training](https://www.youtube.com/watch?v=0VdNflU08yA) — Umar Jamil, tiếng Anh. Trọng số gọn nhẹ hơn giúp cải thiện tốc độ tải lần đầu qua CDN, nhưng cần cân nhắc kỹ đánh đổi về độ chính xác.
