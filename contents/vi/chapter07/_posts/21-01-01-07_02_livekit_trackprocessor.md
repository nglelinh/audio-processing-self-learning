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

SDK máy khách của LiveKit cung cấp giao diện **TrackProcessor** (móc biến đổi track) cho phép xử lý track âm thanh cục bộ trước khi mã hóa và phát hành (publish). Lớp `DeepFilterNoiseFilterProcessor` trong gói `deepfilternet3-noise-filter` **1.3.0** chính là cài đặt của giao diện đó cho DeepFilterNet3, đi kèm các phương thức `init`, `restart`, `suspend`, `resume`, `destroy` và phương thức tĩnh `isSupported()`. Bài học này trình bày vòng đời hoạt động, thứ tự gọi hàm khi tham gia phòng họp và cơ chế xử lý lỗi giúp cuộc gọi vẫn duy trì ổn định khi CDN hoặc worklet gặp sự cố.

![Vòng đời TrackProcessor từ lúc dựng tới lúc publish trên track audio local của LiveKit]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Hình. TrackProcessor gắn trực tiếp lên track âm thanh cục bộ: `init` dựng đồ thị worklet, còn bước publish gửi đi `processedTrack`.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ sắp xếp chính xác thứ tự gọi `new DeepFilterNoiseFilterProcessor`, `setProcessor`, `publishTrack` và `setSuppressionLevel`, chỉ ra được các phương thức vòng đời mà LiveKit tự động kích hoạt, và thiết kế luồng kết nối giữ `connect()` độc lập hoàn toàn với quá trình tải mô hình.

## Kế hoạch 60 phút

- **0–10 phút** — Phân định trách nhiệm giữa Processor và Room.
- **10–25 phút** — Vòng đời hoạt động và đoạn mã tích hợp chuẩn bản 1.3.0.
- **25–40 phút** — Bật/tắt, chế độ bypass, điều chỉnh mức khử nhiễu và xử lý nghẽn (backpressure).
- **40–50 phút** — Lưu ý trên thiết bị di động, telemetry và dọn dẹp tài nguyên (dispose).
- **50–60 phút** — Thực hành mini-lab về thứ tự gọi hàm.

## Phân định trách nhiệm

Processor có nhiệm vụ tiếp nhận track nguồn qua `LocalAudioTrack.setProcessor`, tạo ra `processedTrack`, tải bất đồng bộ module WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) cùng gói mô hình, cung cấp các hàm điều khiển trong lúc chạy mà không phải phát hành lại track, và giải phóng worker, `AudioContext` cùng bộ nhớ WASM khi kết thúc. Ngược lại, processor không quản lý token phòng họp, không tải dữ liệu PCM micro lên máy chủ (kiến trúc mặc định của Mezon xử lý hoàn toàn trên thiết bị), và không được làm treo nút tham gia cuộc gọi hàng chục giây mà thiếu phản hồi trạng thái.

Phương thức `DeepFilterNoiseFilterProcessor.isSupported()` trả về `true` khi trình duyệt có `AudioContext` và `WebAssembly`. Đây chỉ là điều kiện nền tảng, không phải phép kiểm tra hỗ trợ SIMD (một lệnh xử lý nhiều dữ liệu, xem bài 06-03).

## Mã tích hợp tham chiếu

Phụ thuộc ngang hàng (peer dependency): `livekit-client` ^2. Cách khởi tạo và thứ tự gọi các phương thức công khai:

```javascript
import { DeepFilterNoiseFilter, DeepFilterNoiseFilterProcessor } from "deepfilternet3-noise-filter";
// DeepFilterNoiseFilter(options) trả về DeepFilterNoiseFilterProcessor.

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

Tham số `sampleRate: 48000` tương ứng với đồ thị toàn dải (full-band) mà gói khởi tạo (`new AudioContext({ sampleRate: 48000 })`). Hai tham số `noiseReductionLevel` và `setSuppressionLevel` là thang điều chỉnh sản phẩm từ 0 đến 100 (không phải giá trị SNR mục tiêu); giá trị truyền vào được giới hạn trong khoảng hợp lệ rồi gửi sang cổng worklet. Lưu ý rằng `setEnabled` là hàm bất đồng bộ trả về một Promise và cập nhật cờ bypass qua `DeepFilterNet3Core.setNoiseSuppressionEnabled`. Dù một số ví dụ ngắn trên README bỏ qua từ khóa `await`, bạn vẫn nên `await` lời gọi này. Chế độ bypass giữ nguyên đồ thị âm thanh đang hoạt động nên không làm thay đổi khe phát hành track.

Trong chuỗi trên, mã ứng dụng gọi `setProcessor`, còn LiveKit sẽ tự động gọi `init({ track })`. Hàm `init` lưu lại track gốc và gọi `ensureGraph` để khôi phục `AudioContext`, chạy `initialize()` trên lớp core (tải song song WASM và gói mô hình rồi biên dịch bằng `WebAssembly.compile`), khởi tạo `AudioWorkletNode` một lần duy nhất, nối chuỗi `source → worklet → destination` và gán kết quả cho `processedTrack`. Phương thức `restart` dựng lại đồ thị khi nguồn track micro thay đổi; `suspend` và `resume` điều khiển trực tiếp trạng thái của `AudioContext`; còn `destroy` ngắt kết nối các node, đóng context và gọi `processor.destroy()`.

Nếu không dùng LiveKit và tự quản lý `AudioContext`, bạn có thể sử dụng trực tiếp lớp lõi `DeepFilterNet3Core` với các phương thức `initialize`, `createAudioWorkletNode`, `setSuppressionLevel`, `setNoiseSuppressionEnabled` và `destroy`.

Việc truy cập CDN (mạng phân phối nội dung) chỉ diễn ra bên trong `initialize`, hoàn toàn tách biệt với quá trình truyền báo hiệu (signaling) của phòng họp.

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

Khi rơi vào trạng thái `Failed`, ứng dụng vẫn cần phát hành âm thanh gốc (hoặc chỉ dùng APM trình duyệt) và hiển thị một thông báo dạng toast không chặn thao tác. Tuyệt đối không từ chối `connect()` chỉ vì gói mô hình bị lỗi 404; hãy tách bạch trạng thái “khử nhiễu sẵn sàng” khỏi trạng thái “đã kết nối phòng”.

### Xử lý nghẽn (backpressure)

Luôn tuân thủ nhịp thời gian thực của AudioWorklet: các khung trễ hạn quantum phải chuyển sang đi thẳng (passthrough) hoặc loại bỏ, không bao giờ đẩy dồn vào hàng đợi PCM không giới hạn. Khi hệ số thời gian thực liên tục vượt ngưỡng, giải pháp đúng là hạ mức khử nhiễu hoặc bật bypass chứ không phải đệm thêm vài giây âm thanh.

### Phạm vi áp dụng: theo track so với theo phòng

| Phạm vi | Ví dụ | Khi nào áp dụng |
|---------|-------|---------|
| Theo track | Gắn `setProcessor` trên track micro | Cấu hình mặc định |
| Phòng / Giao diện (UX) | Tùy chọn “Bật khử nhiễu” trong cài đặt | Lưu vào `localStorage` và áp dụng khi phát hành track |
| Người tham gia từ xa | Xử lý track đã đăng ký nhận (subscribe) | Hiếm gặp; chủ yếu dùng cho bot hoặc hệ thống ghi âm |

Hãy lưu tùy chọn bật/tắt của người dùng ở tầng giao diện, sau đó áp dụng bằng cách khởi tạo processor tương ứng ngay khi tạo track cục bộ.

## Thứ tự tham gia phòng và tải tài nguyên CDN

Lời gọi `await audioTrack.setProcessor(filter)` sẽ chờ `init`, mà `init` lại chờ tải tài nguyên từ CDN. Đặt bước này **trước `publishTrack`** là chính xác, nhưng đặt trước `room.connect()` là sai lầm. Quy trình chuẩn là kết nối signaling trước, sau đó phát hành track khi sẵn sàng (hoặc giữ micro ở trạng thái tắt/bypass trong lúc tài nguyên đang tải). Ngược lại, nếu gọi `setProcessor` sau `publishTrack` mà không gọi `restart` khi thay đổi track micro bên dưới, LiveKit sẽ tiếp tục phát đi tín hiệu micro thô. Thứ tự an toàn luôn là: khởi tạo processor, gọi `setProcessor`, gọi `publishTrack`, rồi mới điều chỉnh `setSuppressionLevel`; các lần đổi thiết bị về sau đi qua `restart` thay vì gọi lại `setProcessor`.

## Lưu ý trên thiết bị di động và telemetry

Khi tab chuyển sang chạy nền, trình duyệt sẽ bóp tốc độ các bộ định thời; callback âm thanh tuy được ưu tiên hơn nhưng vẫn tiêu tốn tài nguyên đáng kể. Trên Safari iOS, `AudioContext` chỉ có thể `resume` từ một thao tác chạm trực tiếp của người dùng, vì vậy hãy gắn bước khởi tạo vào nút tham gia phòng. Ngoài ra, chạy đồng thời camera, mô hình khử nhiễu và bộ mã hóa Opus có thể làm nóng và hạ xung CPU trên điện thoại tầm trung. Tốc độ lấy mẫu của thiết bị Bluetooth SCO đôi khi không đạt 48 kHz, nhưng vẫn nên giữ `AudioContext` ở 48 kHz theo tài liệu hướng dẫn bất cứ khi nào có thể.

Dữ liệu telemetry cần thu thập (tuyệt đối không đính kèm âm thanh thô) gồm: `ns_init_ms`, dung lượng tải về, tỉ lệ trúng cache, trạng thái bật/tắt, mức khử nhiễu, các phân vị hệ số thời gian thực và lý do chuyển sang fallback. Đây là các chỉ số độ tin cậy vận hành; còn đánh giá chất lượng nghe như MOS sẽ được học ở Chương 08.

## Mini-lab

Đọc lại đoạn mã tích hợp tham chiếu ở trên và kiểm tra thứ tự thực thi chuẩn bằng cách chạy `python3 join_order.py`.

```python
order = [
    "new DeepFilterNoiseFilterProcessor",
    "setProcessor",
    "publishTrack",
    "setSuppressionLevel",
]
print("\n".join(f"{i}. {step}" for i, step in enumerate(order, 1)))
```

**Kết quả kỳ vọng**

```text
1. new DeepFilterNoiseFilterProcessor
2. setProcessor
3. publishTrack
4. setSuppressionLevel
```

**Lỗi thường gặp**

- Gọi `setProcessor` sau `publishTrack` mà không xử lý `restart` khi đổi micro, khiến phòng họp vẫn phát track chưa lọc.
- Chặn `connect()` chờ tải tài nguyên CDN; bước tải nằm trong `init` bên trong `setProcessor`, không thuộc bắt tay signaling.
- Quên `await` trước `setEnabled` rồi đọc `isEnabled()` ngay lập tức trước khi thông điệp bypass kịp áp dụng.
- Gọi `setProcessor` lần thứ hai trong khi quá trình `init` đầu tiên vẫn đang tải.

## Bẫy thường gặp

1. Gọi `setProcessor` trước khi đối tượng `LocalAudioTrack` được tạo.
2. Chuyển trang hoặc rời phòng mà không gọi `destroy`, để lại các worklet chạy ngầm.
3. Nghĩ rằng đoạn ví dụ ngắn trên README là toàn bộ API, trong khi `init`, `restart`, `suspend`, `resume`, `destroy` và `isSupported` đều là các phương thức công khai quan trọng.
4. Dùng tên lớp cũ không còn tồn tại trong bản 1.3.0; luôn dùng `DeepFilterNoiseFilterProcessor` hoặc `DeepFilterNet3Core`.

## Bài tập

1. Đánh dấu trên sơ đồ máy trạng thái các vị trí giao diện nên hiển thị biểu tượng đang tải (spinner) và vị trí nên hiển thị công tắc bật/tắt.
2. Viết phác thảo hàm `connectWithNS()` đảm bảo người dùng vẫn vào được phòng họp kể cả khi CDN gặp lỗi.
3. Liệt kê các sự kiện của LiveKit (hoặc vòng đời trang web) nơi ứng dụng cần gọi `destroy`.
4. Khi nào nên dùng `DeepFilterNoiseFilterProcessor` và khi nào nên dùng `DeepFilterNet3Core`?
5. Nếu người dùng bật chế độ bypass ngay trong lúc processor đang ở trạng thái `LoadingAssets`, bạn cần lưu lại thông tin gì và phương thức nào sẽ áp dụng trạng thái đó sau khi `init` hoàn tất?

### Gợi ý đáp án

1. Hiển thị spinner trong trạng thái `LoadingAssets`; chỉ hiển thị công tắc bật/tắt khi ở `Active` hoặc `Bypassed`; khi ở `Failed` cần hiện thông báo toast và tắt hẳn spinner.
2. Gọi `await room.connect(url, token)` độc lập mà không đặt `await filter` chặn phía trước; trong nhánh `catch` của `setProcessor`, thực hiện phát hành track âm thanh gốc hoặc APM.
3. Gọi `destroy` khi nhận sự kiện `Disconnected` hoặc khi component/route bị gỡ bỏ (unmount); trường hợp đổi thiết bị chỉ cần gọi `restart` chứ không cần rời phòng.
4. Dùng `DeepFilterNoiseFilterProcessor` khi phát hành `LocalAudioTrack` trong LiveKit; dùng `DeepFilterNet3Core` khi tự quản lý đồ thị `AudioContext` thuần.
5. Lưu cờ boolean thể hiện mong muốn của người dùng; hàm `ensureGraph` ở cuối quá trình `init` đã tự gọi `setEnabled(this.enabled)`, không cần gọi `setProcessor` lần thứ hai.

## Đọc thêm

- Tài liệu LiveKit: [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/) và trang chủ [https://docs.livekit.io/](https://docs.livekit.io/).
- Kho mã nguồn [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) và trang [gói npm](https://www.npmjs.com/package/deepfilternet3-noise-filter).
- Chương 05 về nhịp quantum của AudioWorklet và Chương 06 về lỗi biên dịch SIMD trong `init`.

## Video tham khảo

- [Group calling architectures in WebRTC: MCU, SFU & P2P](https://www.youtube.com/watch?v=d2N0d6CKrbk) — Tsahi Levent-Levi, tiếng Anh. **Xem trước.** LiveKit hoạt động theo mô hình SFU (chuyển tiếp track mà không trộn âm); video này giải thích nền tảng kiến trúc SFU thay vì hướng dẫn chi tiết từng API của TrackProcessor.
- [Revamping Audio Quality for RTC Part 1: Beryl Echo Cancellation | Sriram Srinivasan and Hoang Do](https://www.youtube.com/watch?v=lapq9zvUd-k) — @Scale, tiếng Anh. Minh họa vị trí xử lý tăng cường cục bộ trước bước mã hóa — đúng khoảng thời gian mà TrackProcessor phải hoàn tất công việc.
- [AudioWorklet :: What, Why, and How - Hongchan Choi](https://www.youtube.com/watch?v=g1L4O1smMC0) — WebAudio PDX, tiếng Anh. Trình bày các ràng buộc của luồng callback processor mà bộ xử lý âm thanh của LiveKit vẫn phải tuân thủ.
