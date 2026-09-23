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

SDK client của LiveKit mở một **TrackProcessor** (móc biến đổi track) để track audio local được biến đổi trước khi mã hóa và publish. `DeepFilterNoiseFilterProcessor` trong `deepfilternet3-noise-filter` **1.3.0** là móc đó cho DeepFilterNet3. Class còn có `init`, `restart`, `suspend`, `resume`, `destroy`, và `isSupported()` tĩnh. Bài này là vòng đời, thứ tự lời gọi lúc join, và các lỗi giúp cuộc gọi sống khi CDN hoặc worklet trục trặc.

![Vòng đời TrackProcessor từ lúc dựng tới lúc publish trên track audio local của LiveKit]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. TrackProcessor nằm trên track audio local: init dựng đồ thị worklet, publish gửi processedTrack.*

## Mục tiêu học tập

Bạn sắp `new DeepFilterNoiseFilterProcessor`, `setProcessor`, `publishTrack` và `setSuppressionLevel`, nêu các method của processor mà LiveKit gọi hộ, và giữ `connect()` độc lập với lượt tải mô hình.

## Kế hoạch 60 phút

- **0–10 phút** — Processor sở hữu gì, Room sở hữu gì.
- **10–25 phút** — Vòng đời và snippet công khai 1.3.0.
- **25–40 phút** — Bật, bypass, mức khử, backpressure.
- **40–50 phút** — Mobile, telemetry, dispose.
- **50–60 phút** — Mini-lab về thứ tự gọi.

## Trách nhiệm

Processor nên nhận track nguồn qua `LocalAudioTrack.setProcessor`, sinh `processedTrack`, tải WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) và kho mô hình một cách bất đồng bộ, đưa ra điều khiển lúc chạy mà không cần publish lại, rồi giải phóng worker, `AudioContext` và bộ nhớ WASM. Nó không nên giữ token phòng, và không nên upload PCM micro. Đường mặc định của Mezon là trên thiết bị. Nó cũng không nên đóng băng nút join hàng chục giây mà không có tiến trình.

`DeepFilterNoiseFilterProcessor.isSupported()` trả về đúng khi có `AudioContext` và `WebAssembly`. Đó là sàn, không phải kiểm SIMD (một lệnh xử lý nhiều số, bài 06-03).

## Tích hợp tham chiếu

Peer dependency: `livekit-client` ^2. Constructor công khai và thứ tự gọi:

```javascript
import { DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";

const filter = new DeepFilterNoiseFilterProcessor({
  sampleRate: 48000,
  noiseReductionLevel: 80,
  enabled: true,
  assetConfig: {
    cdnUrl: "https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3"
  }
});

await audioTrack.setProcessor(filter);
await room.localParticipant.publishTrack(audioTrack);
filter.setSuppressionLevel(60);
await filter.setEnabled(false); // bypass
```

`sampleRate: 48000` khớp đồ thị full-band mà gói dựng (`new AudioContext({ sampleRate: 48000 })`). `noiseReductionLevel` và `setSuppressionLevel` là núm sản phẩm 0–100, không phải đích SNR. Mức được kẹp rồi chuyển vào cổng worklet. `setEnabled` là bất đồng bộ. Sample README đôi khi bỏ `await`; method trả về promise và cập nhật `DeepFilterNet3Core.setNoiseSuppressionEnabled`, thứ gửi cờ bypass. Hãy await. Bypass để đồ thị ở lại, nên khe publish không đổi.

`setProcessor` là lời gọi của code bạn. LiveKit sau đó gọi `init({ track })`. `init` lưu track gốc và `ensureGraph`: resume context, `initialize()` core (tải song song WASM và mô hình, rồi `WebAssembly.compile`), tạo node AudioWorklet (callback xử lý âm thanh trên luồng realtime) một lần, nối source → worklet → destination, và gán `processedTrack`. `restart` là lần dựng lại đồ thị đó khi danh tính track micro đổi. `suspend` và `resume` ánh xạ sang `AudioContext`. `destroy` ngắt node, đóng context, và gọi `processor.destroy()`.

Người anh em không dùng LiveKit là `DeepFilterNet3Core`: `initialize`, `createAudioWorkletNode`, `setSuppressionLevel`, `setNoiseSuppressionEnabled`, `destroy`. Dùng nó khi bạn tự sở hữu `AudioContext`.

CDN (mạng phân phối nội dung) được chạm bên trong `initialize`, không phải bên trong signaling.

## Máy trạng thái

```text
Created
  → LoadingAssets   (trong init / initialize)
  → Ready
  → Active          (đang bật, frame đang chảy)
  → Bypassed        (await setEnabled(false))
  → Failed          (lỗi asset hoặc compile)
  → Disposed        (destroy)
```

Khi lỗi, hãy publish audio chưa xử lý hoặc chỉ APM và hiện toast không chặn. Đừng reject `connect()` chỉ vì kho 404. Hãy cổng “khử nhiễu sẵn sàng” tách khỏi “đã vào phòng”.

### Backpressure

Tôn trọng nhịp AudioWorklet. Frame trễ quantum nên đi passthrough hoặc bỏ, không nối vào hàng đợi PCM không giới hạn. Hệ số realtime cao kéo dài là lý do hạ mức khử hoặc bypass, không phải lý do đệm năm giây audio.

### Theo track đối với theo phòng

| Phạm vi | Ví dụ | Khi nào |
|---------|-------|---------|
| Theo track | `setProcessor` trên mic | Mặc định |
| Phòng / UX | “Bật NS” trong cài đặt | Lưu localStorage; áp lúc publish |
| Participant remote | Xử lý track đã subscribe | Hiếm; bot và ghi âm |

Hãy lưu preference ở tầng UX. Áp nó bằng cách dựng processor khi tạo track local.

## Thứ tự join và CDN

`await audioTrack.setProcessor(filter)` chờ `init`, và `init` chờ CDN. Điều đó đúng **trước publish**. Đặt nó trước `room.connect()` thì sai. Hãy nối signaling, publish khi sẵn sàng, và nếu asset còn đang tải thì giữ mic tắt hoặc bypass. Gọi `setProcessor` chỉ sau `publishTrack`, rồi không bao giờ `restart` khi track bên dưới bị thay, sẽ khiến LiveKit tiếp tục gửi mic gốc. Thứ tự an toàn là dựng, `setProcessor`, `publishTrack`, rồi `setSuppressionLevel`. Lần đổi thiết bị sau đó đi qua `restart`, không đi qua một `setProcessor` thứ hai bị quên.

## Mobile và telemetry

Tab nền làm chậm timer. Callback audio được ưu tiên hơn và vẫn không miễn phí. Safari trên iOS resume `AudioContext` từ cử chỉ người dùng; hãy khởi tạo sau thao tác chạm để vào phòng. Camera cộng mô hình này cộng Opus có thể làm điện thoại tầm trung nóng và giảm xung. Tốc độ Bluetooth SCO có thể không phải 48 kHz; hãy ở lại context 48 kHz đã được tài liệu hóa khi có thể.

Telemetry không kèm audio thô: `ns_init_ms`, số byte asset, cache hit, cờ bật, mức, phân vị hệ số realtime, lý do fallback. Đó là dữ liệu độ tin cậy. MOS nằm ở Chương 08.

## Mini-lab

Đọc snippet phía trên và điền thứ tự. Tự kiểm bằng `python3 join_order.py`.

```python
order = [
    "new DeepFilterNoiseFilterProcessor",
    "setProcessor",
    "publishTrack",
    "setSuppressionLevel",
]
print("\n".join(f"{i}. {step}" for i, step in enumerate(order, 1)))
```

**Expected**

```text
1. new DeepFilterNoiseFilterProcessor
2. setProcessor
3. publishTrack
4. setSuppressionLevel
```

**Failure modes**

- Gọi `setProcessor` sau `publishTrack` mà không `restart` khi track mic bị thay. Phòng giữ track chưa xử lý.
- Chặn `connect()` vì CDN. Việc tải asset thuộc `init` bên trong `setProcessor`, không thuộc bắt tay signaling.
- Quên `await` trên `setEnabled` rồi đọc `isEnabled()` trước khi bài post bypass xong.
- Gọi `setProcessor` hai lần trong khi `init` đầu vẫn đang tải.

## Bẫy thường gặp

1. `setProcessor` trước khi `LocalAudioTrack` tồn tại.
2. Điều hướng mà không `destroy`, để lại worklet ma.
3. Coi mảnh README là toàn bộ API. `init`, `restart`, `suspend`, `resume`, `destroy` và `isSupported` là thật.
4. Dùng tên class cũ không còn là export của 1.3.0. Hãy dựng `DeepFilterNoiseFilterProcessor` hoặc `DeepFilterNet3Core`.

## Bài tập

1. Đánh dấu trên máy trạng thái chỗ UI hiện spinner và chỗ hiện công tắc.
2. Phác `connectWithNS()` vẫn join được khi CDN lỗi.
3. Liệt kê sự kiện LiveKit nào trong app của bạn nên gọi `destroy`.
4. Khi nào chọn `DeepFilterNoiseFilterProcessor`, khi nào chọn `DeepFilterNet3Core`?
5. Người dùng bật bypass trong lúc `LoadingAssets`. Bạn lưu gì, và method nào áp dụng sau `init`?

### Gợi ý đáp án

1. Spinner trong `LoadingAssets`. Công tắc chỉ ở `Active` và `Bypassed`. `Failed` hiện toast, không phải spinner không bao giờ tắt.
2. `await room.connect(url, token)` và không đặt `await filter` phía trước. Trong `catch` của `setProcessor`, publish audio thô hoặc APM.
3. Disconnected, và lúc unmount route của bạn. Đổi thiết bị gọi `restart`, không phải rời phòng hẳn.
4. Processor khi publish `LocalAudioTrack` của LiveKit. Core khi bạn tự dựng đồ thị `AudioContext`.
5. Lưu boolean mong muốn. `ensureGraph` đã kết thúc bằng `setEnabled(this.enabled)`. Đừng gọi `setProcessor` lần thứ hai.

## Đọc thêm

- LiveKit: [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/), và trang chủ [https://docs.livekit.io/](https://docs.livekit.io/).
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) và [gói npm](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- Chương 05 về quantum của worklet và Chương 06 về lỗi biên dịch SIMD trong `init`.
