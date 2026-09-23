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

Gói npm `deepfilternet3-noise-filter` **1.3.0** là phương tiện đưa DeepFilterNet3 vào app LiveKit và Web Audio. Nó không phải giáo trình. Bài này ánh xạ các method công khai sang frame, gain, WASM, CDN, và TrackProcessor của LiveKit, để capstone đổi một kỹ thuật bạn đo được. Bài khóa không sửa kho sản phẩm. Checkout tùy chọn của giảng viên là `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.

![API processor công khai đứng trước đường publish TrackProcessor của LiveKit]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. Bề mặt npm là một TrackProcessor cộng một core Web Audio, không phải một thuật toán khử nhiễu thứ hai.*

## Mục tiêu học tập

Bạn ánh xạ từng lời gọi công khai sang một ý của khóa, chọn cấu hình hay fork với lập luận bảo trì, và nêu việc mở rộng không cần sửa cây sản phẩm.

## Kế hoạch 60 phút

- **0–10 phút** — Core, TrackProcessor, asset.
- **10–25 phút** — Bảng API đối với Chương 02–06.
- **25–40 phút** — Các núm: mức, bypass, CDN, SIMD.
- **40–50 phút** — Cấu hình, bọc, hoặc fork.
- **50–60 phút** — Mini-lab và ràng buộc capstone.

## Bề mặt công khai

Cài bằng `npm install deepfilternet3-noise-filter`. Peer dependency: `livekit-client` ^2. Ghi chú bundler trong README vẫn đúng: mã worklet được inline thành blob URL, nên không cần plugin copy.

### `DeepFilterNoiseFilterProcessor`

Lớp triển khai TrackProcessor (móc biến đổi track của LiveKit). `name` là `deepfilternet3-noise-filter`.

- Option của constructor: `sampleRate`, `noiseReductionLevel`, `enabled`, `assetConfig.cdnUrl`.
- `static isSupported()` — có `AudioContext` và `WebAssembly`.
- `init` và `restart` — dựng hoặc dựng lại đồ thị 48 kHz trên một `MediaStreamTrack`.
- `setSuppressionLevel(level)` — chuyển 0–100 xuống core.
- `await setEnabled(boolean)` — bypass hoặc bật lại khử nhiễu; trả về cờ enabled.
- `suspend`, `resume` — trạng thái nguồn của `AudioContext`.
- `destroy` — gỡ đồ thị và core.
- Gắn bằng `await audioTrack.setProcessor(filter)`, rồi `publishTrack`.

`DeepFilterNoiseFilter(options)` là factory nhỏ trả về một processor. Trong snippet của khóa hãy ưu tiên class để vòng đời còn nhìn thấy.

### `DeepFilterNet3Core`

Core Web Audio mà processor dùng, và bạn cũng dùng riêng được:

```javascript
import { DeepFilterNet3Core, DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";

const proc = new DeepFilterNet3Core({ sampleRate: 48000, noiseReductionLevel: 0 });
await proc.initialize();
const node = await proc.createAudioWorkletNode(ctx);
proc.setSuppressionLevel(50); // 0–100
proc.setNoiseSuppressionEnabled(true);
proc.destroy();
```

`initialize` tải và biên dịch. `createAudioWorkletNode` ném lỗi nếu bạn bỏ qua bước đó. `setNoiseSuppressionEnabled(false)` là bypass của core; `setEnabled` của processor gọi nó. `destroy` thả worklet và asset đã biên dịch.

AudioWorklet (callback xử lý âm thanh trên luồng realtime) là node mà `createAudioWorkletNode` trả về.

### Asset

`df_bg.wasm` là bản WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) mà README mô tả (`wasm-pack`, cờ SIMD cho ≥ 1.2.0). `DeepFilterNet3_onnx.tar.gz` là kho upstream. Changelog 1.3.0 ghi lần nâng tract **0.23.3** cho đường WASM đó. Layout CDN (mạng phân phối nội dung) là bài 07-03. Kho: [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression).

SIMD (một lệnh xử lý nhiều số) là tính năng của file WASM, không phải một option constructor.

## API sang ý của khóa

| API hoặc artifact | Ý của khóa |
|-------------------|------------|
| `sampleRate` 48 kHz | Chương 02, PCM và tiếng nói full-band |
| Node AudioWorklet | Chương 05, callback realtime |
| Frame trong WASM | Chương 02 về hop; ERB và deep filter của DeepFilter, Chương 04 |
| `noiseReductionLevel` 0–100 | Mức mạnh của gain, không phải lời hứa về SI-SDR |
| `cdnUrl` trên CDN | Chương 06 về đóng gói và bài 07-03 |
| WASM SIMD ≥ 1.2.0 | Chương 06; khẳng định 20–30% của README |
| `setProcessor` | Bài 07-01, điểm chèn A |
| `await setEnabled(false)` | Bypass mà không publish lần thứ hai |
| Trọng số INT8, nếu bạn lượng tử offline | Bài 06-02, làm trước khi upload |

Không có method công khai để đặt tên input ONNX (định dạng trao đổi đồ thị), opset, hay một route máy chủ riêng. Nếu capstone cần đồ thị mới, đó là fork hoặc runtime riêng, không phải option giấu.

Gương native tùy chọn, chỉ là phần kéo dài: API frame Rust `df-core` ở kho anh em, Chương 09. Đừng chặn capstone trình duyệt vì nó.

## Các núm

| Núm | Vặn lên | Rủi ro |
|-----|---------|--------|
| Mức khử | Sàn nhiễu thấp hơn | Giọng mỏng, nhiễu nhạc ở gain gần 0 |
| Enabled | Khử nhiễu bật | CPU, nhiệt, độ trễ |
| CDN đối với byte đóng gói sẵn | Cache dùng chung, npm nhỏ hơn | Lần join đầu phụ thuộc mạng |
| Bản SIMD | Hệ số realtime thấp hơn ở nơi instantiate được | Safari trước 16.4 fail đóng |

Hãy cặp mọi lần đổi núm với Chương 08 (SI-SDR trên mix tổng hợp, DNSMOS hoặc bài nghe ngắn trên clip thật) và hệ số realtime trên một thiết bị gọi tên. Bump dependency mà không có bảng thì không phải kết quả.

## Mở rộng mà không sửa sản phẩm

1. Harness đánh giá: WAV vào, WAV ra, SI-SDR và DNSMOS.
2. Chính sách UX: tắt khử nhiễu ở chế độ nhạc hoặc khi hệ số realtime ở mức cao lâu.
3. Layout CDN và header cache của riêng bạn.
4. Telemetry thời gian init và lý do fallback, không upload audio.
5. Một kế hoạch fork viết ra giấy nếu loader không chứa được kho khác.
6. Phần kéo dài: parity API frame trong Rust `df-core`.

## Cấu hình đối với fork

| Tình huống | Ưu tiên |
|------------|---------|
| Base CDN, mức mặc định, UX bật/tắt | Cấu hình `assetConfig` và constructor |
| Lỗi vòng đời hoặc lệch phiên bản LiveKit | Báo upstream, hoặc một lớp bọc mỏng trong app của bạn |
| Kiến trúc mô hình mới | Fork hoặc gói mới; giữ Apache-2.0 OR MIT, khớp upstream |
| Bài tập khóa | Kho của bạn, ghi chú của bạn, hoặc kho Rust anh em. Không phải cây sản phẩm của giảng viên |

## Đường join đã chú thích

```javascript
// 07-01 điểm chèn A, local trước encode
// 07-03 CDN; client thêm v2 theo quy tắc >= 1.2.0 của README
// 05 AudioWorklet bên trong init
// 04 trọng số DeepFilterNet3 trong tar.gz
const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: { cdnUrl: MY_CDN },
});
await audioTrack.setProcessor(filter);
await room.localParticipant.publishTrack(audioTrack);
filter.setSuppressionLevel(60);
```

## Mini-lab

Chạy `python3 api_map.py`. Script gắn mỗi lời gọi với kiểu sở hữu nó trong 1.3.0.

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

**Expected**

```text
createAudioWorkletNode -> DeepFilterNet3Core
isSupported -> DeepFilterNoiseFilterProcessor
setEnabled -> DeepFilterNoiseFilterProcessor
setNoiseSuppressionEnabled -> DeepFilterNet3Core
setProcessor -> LiveKit LocalAudioTrack
```

**Failure modes**

- Gọi `setEnabled` trên core. Method của core là `setNoiseSuppressionEnabled`.
- Gọi `setNoiseSuppressionEnabled` trên processor. Method của processor là `setEnabled`, và nên được await.
- Coi `setProcessor` là method của class npm. Nó là `LocalAudioTrack.setProcessor`.
- Sửa `/Users/nguyenlelinh/ncc/mezon-noise-suppression` như một phần bài tập.

## Bẫy thường gặp

1. Capstone chỉ bump dependency.
2. Đổ lỗi cho mô hình khi 404 CDN là do tiền tố kép.
3. Phân phối lại trọng số mà chưa đọc giấy phép upstream.
4. Commit của khóa nằm trong cây sản phẩm.

## Bài tập

1. Mở rộng bảng mini-lab với `init`, `restart`, `destroy` và `setSuppressionLevel`.
2. Đề xuất một cải tiến capstone không cần sửa source gói, và nêu metric.
3. Đề xuất một cải tiến cần fork, và biện minh vì sao cấu hình không làm được.
4. So mức khử 40 và 80 trên một clip ồn. Bạn nghe gì ở các bin yên?
5. Vì sao `isSupported()` trả về đúng vẫn không cho phép bỏ qua kiểm Safari 16.4?

### Gợi ý đáp án

1. `init`, `restart` và `destroy` nằm trên processor (LiveKit gọi `init` / `restart`). `setSuppressionLevel` có trên cả hai; processor chuyển xuống core.
2. Một mirror CDN, một chính sách bypass, hoặc harness SI-SDR quanh file WAV. Metric: delta SI-SDR, DNSMOS, hoặc hệ số realtime p95.
3. Một bộ toán tử mới hoặc layout kho mà loader không diễn tả được. Cấu hình chỉ đặt sample rate, mức, enabled, và `cdnUrl`.
4. Mức 80 nên cắt nhiều nhiễu hơn và có thể làm mỏng phụ âm xát hoặc tạo nhiễu nhạc ở sàn. Mức 40 để lại nhiều nhiễu dư hơn. Dùng cùng một clip.
5. `isSupported()` chỉ kiểm `AudioContext` và `WebAssembly`. SIMD là bài 06-03; Safari trước 16.4 làm module ≥ 1.2.0 fail lúc compile.

## Đọc thêm

- npm [deepfilternet3-noise-filter](https://www.npmjs.com/package/deepfilternet3-noise-filter) và [GitHub](https://github.com/mezonai/mezon-noise-suppression).
- Upstream [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet), gồm Schröter và cộng sự, ICASSP 2022, arXiv:2110.05588.
- LiveKit [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/).
- [tract](https://github.com/sonos/tract) và [ONNX Runtime](https://onnxruntime.ai/docs/) cho phía runtime của Chương 06.
