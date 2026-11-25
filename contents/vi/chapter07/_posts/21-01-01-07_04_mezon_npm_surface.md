---
layout: post
title: "07-04 Bề mặt npm Mezon (kỹ thuật, không chỉ wrapper)"
chapter: "07"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter07
lesson_type: required
draft: false
---

Nếu chỉ nhìn qua đoạn code 10 dòng trên README — `npm install deepfilternet3-noise-filter`, tạo `new DeepFilterNoiseFilterProcessor(...)`, gọi `setProcessor` — rất dễ nảy sinh cảm giác rằng toàn bộ công việc khử nhiễu chỉ gói gọn trong việc "gọi một thư viện npm". Nhưng khi có sự cố ngoài đời thực — tiếng vọng dội ngược, giọng nói mỏng đi ở mức 80, hay lỗi biên dịch trên Safari 16.3 — người chỉ biết gọi wrapper sẽ bó tay, còn người nhìn thấu từng phương thức công khai xuống tới đúng khái niệm DSP, AudioWorklet, WASM SIMD và CDN bên dưới sẽ biết ngay cần đo cái gì và sửa ở đâu.

Gói npm `deepfilternet3-noise-filter` **1.3.0** là công cụ đưa DeepFilterNet3 vào các ứng dụng LiveKit và Web Audio, chứ không phải toàn bộ nội dung cốt lõi của khóa học. Bài học này ánh xạ từng phương thức công khai của gói về đúng các khái niệm nền tảng như khung xử lý (frame), hệ số khuếch đại (gain), WASM, CDN và TrackProcessor của LiveKit, để dự án cuối khóa (capstone) tập trung cải tiến một kỹ thuật đo đạc được mà không cần can thiệp sửa đổi kho mã nguồn sản phẩm.

**Mạch bài học:** Nhìn xuyên qua lớp wrapper npm → Kiến thức cần nhớ (Kiến trúc 3 tầng Core/Processor/Assets, Phân biệt Tham số sản phẩm vs. Đại lượng DSP, Quyết định Cấu hình vs. Bọc ngoài vs. Fork) → Giao diện API công khai & bảng ánh xạ kiến thức Chương 02–06 → Giải thích theo dõi luồng gọi hàm qua 4 thao tác người dùng và phân tích thang `noiseReductionLevel` 0–100 → Hướng mở rộng capstone, Mini-lab và Bài tập.

![API processor công khai đứng trước đường publish TrackProcessor của LiveKit]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Hình. Giao diện npm cung cấp một TrackProcessor và một lớp core Web Audio, không phải một thuật toán khử nhiễu thứ hai.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ ánh xạ được từng lời gọi API công khai với kiến thức tương ứng trong khóa học, quyết định được khi nào chỉ cần cấu hình và khi nào bắt buộc phải fork kèm lập luận bảo trì rõ ràng, đồng thời xác định được các hướng mở rộng mà không cần chỉnh sửa mã nguồn gốc của gói.

## Kiến thức cần nhớ: Giải phẫu kiến trúc ba tầng của một gói khử nhiễu web

### 1. Kiến trúc phân tầng: Core (`DeepFilterNet3Core`) vs. Adapter (`DeepFilterNoiseFilterProcessor`) vs. Assets
- **Là gì:** Tầng lõi `DeepFilterNet3Core` quản lý trực tiếp `AudioContext`, `WebAssembly.compile` và `AudioWorkletNode`; tầng adapter `DeepFilterNoiseFilterProcessor` bọc lớp lõi đó theo đúng giao diện `TrackProcessor` của LiveKit; còn tầng tài nguyên (`df_bg.wasm`, `DeepFilterNet3_onnx.tar.gz`) nằm tách biệt trên CDN.
- **Nghiên cứu gì:** Tách bạch quyền sở hữu từng phương thức (ví dụ `setEnabled` thuộc Processor, `setNoiseSuppressionEnabled` thuộc Core, `setProcessor` thuộc LiveKit `LocalAudioTrack`), giúp bạn dùng lại lớp lõi ngay cả trong ứng dụng WebRTC thuần không có LiveKit.

### 2. Tham số sản phẩm (`noiseReductionLevel` 0–100) vs. Đại lượng DSP đo đạc được
- **Là gì:** Con số `0–100` trên giao diện là thanh trượt điều khiển độ sâu giới hạn suy giảm (attenuation limit / pha trộn wet-dry), **không phải** chỉ số SI-SDR hay dB SNR mục tiêu.
- **Nghiên cứu gì:** Luôn đánh giá mọi thay đổi tham số bằng thước đo khách quan và chủ quan (SI-SDR, DNSMOS, nghe mù A/B ở Chương 08) kết hợp phân vị p95 RTF trên thiết bị thật.

### 3. Kỷ luật kỹ thuật: Khi nào Cấu hình, khi nào Bọc ngoài (Wrap), khi nào Fork
- **Là gì:** Khung ra quyết định kiến trúc cân nhắc giữa chi phí bảo trì dài hạn (tự gánh bản vá WASM/LiveKit khi fork) và nhu cầu thay đổi đồ thị mô hình.
- **Nghiên cứu gì:** Tập trung dự án capstone vào các cải tiến đo đạc được mà không sửa kho sản phẩm (bộ đo tự động, chính sách bypass theo RTF, mirror CDN, đối chiếu Rust `df-core`), và chỉ fork khi thật sự cần đổi cấu trúc đồ thị ONNX.

## Kế hoạch 60 phút

- **0–10 phút** — Tổng quan ba lớp: Core, TrackProcessor và tài nguyên (asset).
- **10–25 phút** — Bảng ánh xạ API sang kiến thức Chương 02–06.
- **25–40 phút** — Các tham số điều chỉnh: mức khử, bypass, CDN và SIMD.
- **40–50 phút** — Chiến lược cấu hình, bọc lớp trung gian hay fork.
- **50–60 phút** — Thực hành mini-lab và ràng buộc cho dự án cuối khóa.

## Giao diện API công khai

Cài đặt thư viện bằng `npm install deepfilternet3-noise-filter` (với peer dependency `livekit-client` ^2). Theo ghi chú trên README, mã nguồn worklet đã được nhúng nội tuyến dưới dạng blob URL nên các trình đóng gói hiện đại không cần cấu hình thêm plugin sao chép tệp.

### `DeepFilterNoiseFilterProcessor`

Lớp triển khai giao diện TrackProcessor (móc biến đổi track của LiveKit) với thuộc tính `name` là `deepfilternet3-noise-filter`:

- Tham số khởi tạo (constructor options): `sampleRate`, `noiseReductionLevel`, `enabled`, `assetConfig.cdnUrl`.
- `static isSupported()` — kiểm tra trình duyệt có hỗ trợ `AudioContext` và `WebAssembly` hay không.
- `init` và `restart` — khởi tạo hoặc dựng lại đồ thị xử lý 48 kHz trên một `MediaStreamTrack`.
- `setSuppressionLevel(level)` — truyền mức khử nhiễu trong khoảng 0–100 xuống lớp core.
- `await setEnabled(boolean)` — bật khử nhiễu hoặc chuyển sang bypass; trả về trạng thái `enabled` sau khi cập nhật.
- `suspend`, `resume` — điều khiển trạng thái hoạt động của `AudioContext`.
- `destroy` — giải phóng đồ thị xử lý và lớp core.
- Cách gắn vào LiveKit: gọi `await audioTrack.setProcessor(filter)`, sau đó gọi `publishTrack`.

Hàm `DeepFilterNoiseFilter(options)` là hàm factory gọn nhẹ trả về một thể hiện của processor. Trong các đoạn mã học tập, nên ưu tiên dùng trực tiếp lớp `DeepFilterNoiseFilterProcessor` để dễ theo dõi vòng đời đối tượng.

### `DeepFilterNet3Core`

Đây là lớp lõi Web Audio được processor gọi bên dưới và cũng có thể sử dụng độc lập:

```javascript
import { DeepFilterNet3Core, DeepFilterNoiseFilter, DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";
// LiveKit: new DeepFilterNoiseFilterProcessor(opts) hoặc DeepFilterNoiseFilter(opts)

const proc = new DeepFilterNet3Core({ sampleRate: 48000, noiseReductionLevel: 0 });
await proc.initialize();
const node = await proc.createAudioWorkletNode(ctx);
proc.setSuppressionLevel(50); // 0–100
proc.setNoiseSuppressionEnabled(true);
proc.destroy();
```

Phương thức `initialize` tải và biên dịch tài nguyên; `createAudioWorkletNode` sẽ ném lỗi nếu bạn bỏ qua bước khởi tạo này. `setNoiseSuppressionEnabled(false)` kích hoạt chế độ bypass ở tầng core (và `setEnabled` của processor chính là lớp gọi lên phương thức này). `destroy` giải phóng node worklet cùng tài nguyên đã biên dịch.

AudioWorklet (callback xử lý âm thanh trên luồng thời gian thực) chính là đối tượng node do `createAudioWorkletNode` trả về.

### Tệp tài nguyên

Tệp `df_bg.wasm` là bản dựng WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) được biên dịch bằng `wasm-pack` (có bật cờ SIMD từ bản ≥ 1.2.0), đi kèm gói mô hình nguồn gốc `DeepFilterNet3_onnx.tar.gz`. Ghi chú phát hành bản 1.3.0 nêu việc nâng cấp `tract` lên **0.23.3** cho đường WASM này. Cấu trúc đường dẫn CDN (mạng phân phối nội dung) được trình bày chi tiết ở bài 07-03. Kho mã nguồn: [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression).

Lưu ý rằng SIMD (một lệnh xử lý nhiều dữ liệu) là thuộc tính của tệp nhị phân WASM khi biên dịch, không phải một tham số truyền vào constructor.

## Ánh xạ API về kiến thức của khóa học

| API hoặc tệp tài nguyên | Kiến thức tương ứng trong khóa học |
|-------------------|------------|
| `sampleRate` 48 kHz | Chương 02: PCM và âm thanh giọng nói toàn dải |
| Node AudioWorklet | Chương 05: ràng buộc callback thời gian thực |
| Khung xử lý trong WASM | Chương 02 về hop; Chương 04 về băng ERB và deep filter |
| `noiseReductionLevel` 0–100 | Độ mạnh của hệ số suy giảm gain, không phải cam kết chỉ số SI-SDR |
| `cdnUrl` trên CDN | Chương 06 về đóng gói và bài 07-03 |
| WASM SIMD ≥ 1.2.0 | Chương 06; mức tăng tốc 20–30% nêu trong README |
| `setProcessor` | Bài 07-01: điểm chèn A trên luồng gửi |
| `await setEnabled(false)` | Chuyển sang bypass mà không cần phát hành lại track |
| Trọng số INT8 (nếu lượng tử hóa offline) | Bài 06-02: thực hiện trước khi đăng tải lên CDN |

Gói không cung cấp phương thức công khai để đổi tên tensor đầu vào ONNX (định dạng trao đổi đồ thị), đổi phiên bản opset hay định tuyến sang máy chủ xử lý riêng. Nếu dự án cuối khóa yêu cầu đồ thị mô hình hoàn toàn mới, bạn cần fork hoặc dựng runtime riêng thay vì tìm một tùy chọn ẩn.

Ngoài ra, phần mở rộng tùy chọn phía native sử dụng API xử lý khung bằng Rust (`df-core`) sẽ được giới thiệu ở Chương 09; không để phần mở rộng này cản trở tiến độ dự án cuối khóa trên trình duyệt.

## Giải thích: Dò luồng gọi hàm qua 4 thao tác người dùng và ý nghĩa toán học của mức khử 0–100

### Phép dò 1: Ai gọi ai trong 4 sự kiện phòng họp?
Hãy theo dõi chính xác chuỗi cuộc gọi đi qua ba lớp (`LiveKit` → `Processor` → `Core` → `AudioWorklet`) để thấy vì sao không cần phát hành lại track khi điều chỉnh thông số:

| Thao tác người dùng | Lời gọi ứng dụng | Chuỗi thực thi bên dưới | Có cần thương lượng lại WebRTC? |
| :--- | :--- | :--- | :--- |
| 1. Bật lọc lúc vào phòng | `audioTrack.setProcessor(filter)` | LiveKit gọi `filter.init` → `core.initialize` (CDN + WASM) → `core.createAudioWorkletNode` | Không (gắn trước `publishTrack`) |
| 2. Kéo thanh trượt 80 → 40 | `filter.setSuppressionLevel(40)` | `core.setSuppressionLevel(40)` → gửi thông điệp nhỏ qua `MessagePort` tới worklet | **Không** (áp dụng ở ranh giới hop kế tiếp) |
| 3. Bấm tắt lọc tạm thời | `await filter.setEnabled(false)` | `core.setNoiseSuppressionEnabled(false)` → bật cờ `bypass` trong worklet | **Không** (đồ thị vẫn sống) |
| 4. Cắm tai nghe USB mới | LiveKit đổi nguồn thiết bị | LiveKit gọi `filter.restart({ track })` → nối lại `source` mới vào đồ thị | Chỉ thay track nguồn cục bộ |

### Phép dò 2: Đừng nhầm `noiseReductionLevel = 80` với "cắt 80% nhiễu" hay "+80 dB SNR"!
Nếu mô hình gốc ước lượng một hệ số suy giảm gain $$g_{\text{model}} \in [0, 1]$$ và sản phẩm áp đặt một ngưỡng sàn suy giảm (attenuation floor) $$g_{\min}$$ tương ứng với mức `level` $$L \in [0, 100]$$ — ví dụ mô phỏng đơn giản theo thang giới hạn dB từ $$0\text{ dB}$$ đến $$-30\text{ dB}$$:
$$ \text{Atten}_{\max}(L) = -0{,}3\,L\text{ dB}, \qquad g_{\min}(L) = 10^{\text{Atten}_{\max}(L)/20}. $$
- Ở $$L = 40$$: giới hạn cắt tối đa $$-12\text{ dB}$$ ($$g_{\min} = 10^{-12/20} \approx 0{,}251$$) — giữ lại một phần nền âm êm để giọng nói tự nhiên.
- Ở $$L = 80$$: giới hạn cắt sâu xuống $$-24\text{ dB}$$ ($$g_{\min} = 10^{-24/20} \approx 0{,}063$$) — nền rất sạch nhưng dễ làm lộ lỗi ước lượng ở vùng gain nhỏ (như bài 06-02).
(Công thức ánh xạ chính xác bên trong `libDF` có thể dùng tham số `atten_lim_db` riêng; ví dụ số này minh họa rõ vì sao tăng `L` luôn là sự đánh đổi giữa độ sạch nền và độ tự nhiên của giọng nói!)

## Phân tích các tham số điều chỉnh

| Tham số | Tác động khi tăng/bật | Rủi ro đi kèm |
|-----|---------|--------|
| Mức khử nhiễu | Hạ thấp nền nhiễu sâu hơn | Giọng nghe mỏng, phát sinh nhiễu nhạc ở vùng gain gần 0 |
| Trạng thái bật (`enabled`) | Kích hoạt bộ khử nhiễu | Tăng tải CPU, tỏa nhiệt và thêm độ trễ |
| CDN so với nhúng sẵn | Tận dụng cache chung, gói npm gọn hơn | Lượt tham gia đầu tiên phụ thuộc vào mạng |
| Bản dựng SIMD | Giảm hệ số thời gian thực trên máy hỗ trợ | Trình duyệt Safari trước 16.4 báo lỗi không khởi tạo được |

Mọi thay đổi tham số cần được đánh giá cùng hệ thống đo lường của Chương 08 (SI-SDR trên bản trộn tổng hợp, DNSMOS hoặc bài nghe thử trên đoạn âm thực tế) kết hợp đo hệ số thời gian thực trên thiết bị cụ thể. Việc chỉ nâng phiên bản thư viện mà không có bảng số liệu đối chiếu không được tính là kết quả nghiên cứu.

## Các hướng mở rộng không cần sửa mã nguồn sản phẩm

1. Xây dựng bộ công cụ đánh giá tự động: đầu vào WAV, đầu ra WAV, tính toán SI-SDR và DNSMOS.
2. Thiết kế chính sách UX thông minh: tự động tắt khử nhiễu khi chuyển sang chế độ nhạc hoặc khi hệ số thời gian thực duy trì ở mức cao kéo dài.
3. Tự triển khai cấu trúc CDN và tối ưu hóa chính sách header cache.
4. Thu thập telemetry cho thời gian khởi tạo và nguyên nhân fallback (không tải âm thanh người dùng).
5. Lập bản thiết kế kế hoạch fork khi bộ nạp mặc định không đáp ứng được định dạng gói mô hình mới.
6. Phần mở rộng tùy chọn: đối chiếu tương đương API xử lý từng khung trên Rust `df-core`.

## Khi nào nên cấu hình và khi nào nên fork

| Tình huống | Phương án ưu tiên |
|------------|---------|
| Đổi đường dẫn CDN, mức khử mặc định, giao diện bật/tắt | Cấu hình qua `assetConfig` và tham số constructor |
| Lỗi vòng đời hoặc sai khác phiên bản LiveKit | Báo lỗi lên kho gốc, hoặc viết một lớp bọc (wrapper) mỏng trong ứng dụng |
| Đưa vào kiến trúc mô hình mới | Fork hoặc tạo gói mới; giữ đúng giấy phép Apache-2.0 hoặc MIT theo kho gốc |
| Bài tập và dự án khóa học | Thực hiện trên kho cá nhân hoặc kho Rust thử nghiệm, không sửa trực tiếp kho sản phẩm |

## Đoạn mã tích hợp có chú thích liên kết bài học

```javascript
// 07-01 điểm chèn A, local trước encode
// 07-03 CDN; >= 1.2.0 gồm 1.3.0 tự thêm v2/
// 05 AudioWorklet bên trong init
// 04 trọng số DeepFilterNet3 trong tar.gz
const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: {
    cdnUrl: "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3",
  },
});
await audioTrack.setProcessor(filter);
await room.localParticipant.publishTrack(audioTrack);
filter.setSuppressionLevel(60);
```

## Mini-lab

Lưu đoạn mã sau thành `api_map.py` và chạy `python3 api_map.py`. Chương trình ánh xạ từng phương thức công khai về đúng lớp sở hữu nó trong phiên bản 1.3.0.

```python
calls = {
    "createAudioWorkletNode": "DeepFilterNet3Core",
    "setProcessor": "LiveKit LocalAudioTrack",
    "setEnabled": "DeepFilterNoiseFilterProcessor",
    "setNoiseSuppressionEnabled": "DeepFilterNet3Core",
    "isSupported": "DeepFilterNoiseFilterProcessor",
}
for name in sorted(calls):
    print(f"{name} -> {calls[name]}")
```

**Kết quả kỳ vọng**

```text
createAudioWorkletNode -> DeepFilterNet3Core
isSupported -> DeepFilterNoiseFilterProcessor
setEnabled -> DeepFilterNoiseFilterProcessor
setNoiseSuppressionEnabled -> DeepFilterNet3Core
setProcessor -> LiveKit LocalAudioTrack
```

**Lỗi thường gặp**

- Gọi `setEnabled` trên lớp core (phương thức đúng của core là `setNoiseSuppressionEnabled`).
- Gọi `setNoiseSuppressionEnabled` trên processor (phương thức đúng của processor là `setEnabled`, và nên dùng `await`).
- Nhầm `setProcessor` là phương thức thuộc gói npm (thực tế đây là phương thức `LocalAudioTrack.setProcessor` của LiveKit).
- Chỉnh sửa trực tiếp kho mã nguồn sản phẩm khi làm bài tập khóa học.

## Bẫy thường gặp

1. Làm dự án cuối khóa chỉ dừng ở mức nâng cấp phiên bản dependency.
2. Quy lỗi cho mô hình khi nguyên nhân thực sự của lỗi 404 CDN là lặp tiền tố đường dẫn.
3. Phân phối lại tệp trọng số mà chưa đọc kỹ điều khoản giấy phép nguồn gốc.
4. Đưa các commit thử nghiệm của khóa học vào thẳng kho mã nguồn sản phẩm.

## Bài tập

1. Mở rộng bảng ánh xạ trong mini-lab với thêm 4 phương thức: `init`, `restart`, `destroy` và `setSuppressionLevel`.
2. Đề xuất một cải tiến cho dự án cuối khóa không cần chỉnh sửa mã nguồn của gói, kèm chỉ số đánh giá cụ thể.
3. Đề xuất một cải tiến bắt buộc phải fork mã nguồn và giải thích vì sao tham số cấu hình không thể đáp ứng được.
4. So sánh mức khử nhiễu 40 và 80 trên cùng một đoạn ghi âm nhiều tạp âm; mô tả sự khác biệt nghe thấy ở các đoạn nền yên lặng.
5. Giải thích vì sao dù `isSupported()` trả về `true`, bạn vẫn không được bỏ qua bước kiểm tra mốc trình duyệt Safari 16.4.

### Gợi ý đáp án

1. Ba phương thức `init`, `restart` và `destroy` thuộc về `DeepFilterNoiseFilterProcessor` (trong đó LiveKit gọi `init`/`restart`); `setSuppressionLevel` có mặt trên cả hai lớp, với processor chuyển tiếp giá trị xuống core.
2. Ví dụ: xây dựng mirror CDN, thiết lập chính sách bypass tự động theo RTF hoặc viết công cụ đo SI-SDR trên tập WAV; các chỉ số đánh giá tương ứng là độ chênh lệch SI-SDR, DNSMOS hoặc RTF p95.
3. Ví dụ: thay đổi tập toán tử hoặc cấu trúc gói mô hình mà bộ nạp hiện tại không hỗ trợ, bởi cấu hình công khai chỉ cho phép chỉnh `sampleRate`, mức khử, trạng thái `enabled` và `cdnUrl`.
4. Mức 80 cắt nhiễu mạnh hơn nhưng dễ làm mỏng các phụ âm xát hoặc tạo nhiễu nhạc ở nền âm; mức 40 giữ giọng tự nhiên hơn nhưng để lọt nhiều nhiễu dư hơn.
5. `isSupported()` chỉ kiểm tra sự hiện diện của `AudioContext` và `WebAssembly`, không kiểm tra hỗ trợ `simd128` (bài 06-03); do đó Safari trước bản 16.4 vẫn báo lỗi biên dịch đối với bản dựng ≥ 1.2.0.

## Đọc thêm

- Trang npm [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter) và kho [GitHub](https://github.com/mezonai/mezon-noise-suppression).
- Dự án gốc [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet), bao gồm bài báo Schröter và cộng sự (ICASSP 2022, arXiv:2110.05588).
- Tài liệu LiveKit về [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/).
- [tract](https://github.com/sonos/tract) và [ONNX Runtime](https://onnxruntime.ai/docs/) cho tầng runtime ở Chương 06.

## Video tham khảo

- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, tiếng Anh. **Xem trước.** Nghe trực tiếp hiệu quả xử lý của bộ khử nhiễu mà gói npm này tích hợp, giúp gắn kết các phương thức công khai với hành vi âm thanh thực tế.
- [Group calling architectures in WebRTC: MCU, SFU & P2P](https://www.youtube.com/watch?v=d2N0d6CKrbk) — Tsahi Levent-Levi, tiếng Anh. Giải thích cơ chế chuyển tiếp track của SFU — bối cảnh phía LiveKit của bề mặt API.
- [AudioWorklet :: What, Why, and How - Hongchan Choi](https://www.youtube.com/watch?v=g1L4O1smMC0) — WebAudio PDX, tiếng Anh. Làm rõ giới hạn thời gian của luồng callback nơi processor phải trả về đúng hạn.
