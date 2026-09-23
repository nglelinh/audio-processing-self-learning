---
layout: post
title: "07-02 Pattern TrackProcessor của LiveKit"
chapter: "07"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter07
lesson_type: required
draft: false
---

SDK client LiveKit cung cấp hook **TrackProcessor** để biến đổi track audio local trước khi encode và publish. Gói `deepfilternet3-noise-filter` của Mezon triển khai hook đó với DeepFilterNet3. Bài này dạy vòng đời, chế độ lỗi, và quan sát — kỹ thuật bạn tái sử dụng được cả khi đổi model sau này.

## Kế hoạch giảng 60 phút

- 0–10 phút: TrackProcessor sở hữu gì vs Room sở hữu gì.
- 10–25 phút: Vòng đời — tạo → tải asset → `setProcessor` → xử lý → dispose.
- 25–40 phút: Backpressure, bật/tắt, nút mức khử nhiễu.
- 40–50 phút: Lưu ý trình duyệt mobile và hook quan sát.
- 50–60 phút: Mini-lab: sequence diagram join / leave / toggle NS.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Giải thích trách nhiệm TrackProcessor trên đường publish LiveKit.
- Phác vòng đời processor DF3 (init, process, dispose).
- Nhận diện backpressure và xử lý lỗi để cuộc gọi vẫn sống.
- Nêu tradeoff cấu hình theo track vs theo room.

## Trách nhiệm của TrackProcessor

Processor nên:

1. Nhận track nguồn (hoặc gắn qua `LocalAudioTrack.setProcessor`).
2. Sinh track đã xử lý để LiveKit publish.
3. Tải asset nặng (WASM, model) **bất đồng bộ** với trạng thái ready/error rõ.
4. Expose điều khiển runtime (`setEnabled`, `setSuppressionLevel`) khi có thể không cần republish.
5. **Dispose** sạch: tắt worker, đóng AudioContext, giải phóng WASM.

Processor *không* nên: ôm signaling/token; upload PCM mic lên server trong thiết kế mặc định Mezon; chặn UI join hàng chục giây mà không có tiến trình.

## Tích hợp tham chiếu (từ README gói)

```javascript
import { DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";

const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: {
    cdnUrl:
      "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3",
  },
});

await audioTrack.setProcessor(filter);
await room.localParticipant.publishTrack(audioTrack);

filter.setSuppressionLevel(60);
filter.setEnabled(false);
```

- `sampleRate: 48000` khớp framing full-band phổ biến của DF3.
- Mức khử map sang UX sản phẩm, không phải SNR “ma thuật”.
- CDN quan trọng cho cache sản xuất (bài 07-03).

Lựa chọn thấp hơn trong cùng gói: `DeepFilterNet3Core` + `createAudioWorkletNode` cho đồ thị WebAudio không LiveKit.

## Máy trạng thái vòng đời

```text
Created → LoadingAssets → Ready → Active
  → Bypassed (enabled=false)
  → Failed → đường fallback
  → Disposed
```

**Hành vi khuyến nghị khi Failed:** vẫn publish audio chưa xử lý (hoặc chỉ APM) và toast không chặn — đừng làm fail toàn bộ `connect()`.

### Process và backpressure

Tôn trọng nhịp AudioWorklet; đừng làm JS nặng trên main thread mỗi quantum 10 ms. Nếu một frame vượt hạn, passthrough quantum đó thay vì xếp hàng PCM không giới hạn.

## Cấu hình theo track vs room

| Phạm vi | Ví dụ | Khi nào |
|---------|-------|---------|
| Theo track | `setProcessor` trên mic | Mặc định |
| Theo room/UX | toggle “NS on” trong settings | Lưu preference |
| Remote participant | xử lý track subscribe | Đắt; thường bot/ghi âm |

## Lưu ý mobile

- Tab nền có thể throttle; callback audio đặc quyền hơn nhưng không miễn phí.
- iOS Safari: resume AudioContext cần gesture người dùng.
- Nhiệt: DF3 + camera + encode có thể thermal-throttle.
- Bluetooth SCO có thể lệch sample rate — bám đường 48 kHz đã tài liệu hóa khi có thể.

## Quan sát (telemetry) tối thiểu

`ns_init_ms`, `ns_asset_cache_hit`, `ns_enabled`, `ns_level`, `ns_rtf_p95`, `ns_fallback_reason` — **không** gửi raw audio.

## Bẫy thường gặp

1. `setProcessor` trước khi track tồn tại.
2. Quên dispose → worklet “ma” sau điều hướng.
3. Chặn join vì tải model trên mạng chậm.
4. Coi snippet README là toàn bộ API — hãy đọc typings.

## Bài tập

1. Vẽ máy trạng thái và đánh dấu chỗ UI hiện spinner vs toggle.
2. Viết pseudocode `connectWithNS()` không reject chỉ vì CDN lỗi.
3. Liệt kê event LiveKit nào phải trigger dispose.
4. So `DeepFilterNoiseFilterProcessor` vs `DeepFilterNet3Core`.

## Đọc thêm

- Tài liệu LiveKit Track Processor (đúng phiên bản SDK bạn dùng)
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression)
- npm [`deepfilternet3-noise-filter`](https://www.npmjs.com/package/deepfilternet3-noise-filter)
- Chương 05 và 06
