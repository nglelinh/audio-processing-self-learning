---
layout: post
title: "07-01 Điểm chèn trong WebRTC"
chapter: "07"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter07
lesson_type: required
draft: false
---

Vị trí chèn bộ khử nhiễu trong một cuộc gọi WebRTC quyết định trực tiếp đến độ trễ, khả năng khử vọng (echo) và việc máy chủ SFU có nhận được tín hiệu giọng nói đã làm sạch hay không. Bài học này ánh xạ các điểm chèn tiềm năng với `getUserMedia`, bộ xử lý âm thanh tích hợp (Audio Processing Module — APM) của trình duyệt và `RTCPeerConnection`, đồng thời phân tích cách `DeepFilterNoiseFilterProcessor` trong gói `deepfilternet3-noise-filter` **1.3.0** can thiệp vào luồng phát (uplink) trước bước mã hóa thông qua TrackProcessor (cơ chế biến đổi track của LiveKit).

![Track audio local của LiveKit đi qua processor khử nhiễu trước khi publish]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Hình. Điểm chèn A là TrackProcessor đặt trên track micro cục bộ (local), ngay trước khi bộ gửi (sender) thực hiện mã hóa.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ biết cách đặt bộ khử nhiễu mạng nơ-ron trên đường phát trước bước mã hóa, giữ lại tính năng khử vọng của trình duyệt đồng thời tắt bộ khử nhiễu mặc định của trình duyệt, và mô tả chính xác những gì `setProcessor` thay đổi trên `MediaStreamTrack` được phát hành mà không cần đẩy bước suy luận ra khỏi thiết bị.

## Kế hoạch 60 phút

- **0–10 phút** — Toàn cảnh chuỗi truyền âm: micro, xử lý, mã hóa, SFU, giải mã và phát loa.
- **10–25 phút** — So sánh ba điểm chèn A, B và C.
- **25–40 phút** — Đối chiếu APM trình duyệt với processor bản 1.3.0.
- **40–50 phút** — Xử lý tình huống đổi thiết bị, tắt tiếng (mute) và vòng đời đồ thị worklet.
- **50–60 phút** — Thực hành mini-lab, bẫy thường gặp và làm bài tập.

## Đồ thị âm thanh hội nghị

Đường gửi cục bộ (uplink):

```text
Microphone
  → getUserMedia MediaStreamTrack
  → [tuỳ chọn: AudioContext / AudioWorklet NS]
  → [tuỳ chọn: APM trình duyệt: AEC / NS / AGC]
  → RTCPeerConnection sender (encode Opus)
  → SFU / peers
```

Đường nhận (downlink):

```text
RTP từ xa
  → decode phía receiver
  → MediaStreamTrack
  → phần tử audio hoặc AudioContext
```

Bộ khử nhiễu cho **luồng gửi của bạn** cần được chạy trên đường gửi cục bộ, trước khi mã hóa. Nếu đặt khử nhiễu sau bước giải mã trên track từ xa (remote), bạn chỉ làm sạch nhiễu của người khác cho riêng tai mình nghe; cách đó không làm giảm nhiễu trong tín hiệu bạn gửi đi và cũng không đúng vị trí để xử lý tiếng vọng phát sinh từ phía bạn.

AudioWorklet (callback xử lý âm thanh trên luồng thời gian thực) chỉ xuất hiện tường minh ở điểm A khi bạn tự dựng đồ thị Web Audio; còn khi dùng LiveKit, `TrackProcessor` sẽ bao bọc lớp worklet đó.

## Điểm chèn A, B và C

**A — Xử lý cục bộ, trước bước mã hóa.** Tín hiệu micro được lọc ngay trên máy khách trước khi phát hành track. Nhờ đó, SFU và mọi người tham gia khác đều nhận được giọng nói đã làm sạch. Đổi lại, bạn phải chịu độ trễ thuật toán trên đường găng và đảm bảo không làm lệch nhịp tham chiếu của bộ khử vọng. Đây chính là thiết kế của gói Mezon: `DeepFilterNoiseFilterProcessor` triển khai giao diện TrackProcessor của LiveKit. Quy trình gồm khởi tạo processor, gọi `await audioTrack.setProcessor(filter)`, rồi `await room.localParticipant.publishTrack(audioTrack)`. LiveKit sẽ tự gọi phương thức `init` của processor để dựng đồ thị xử lý, hoàn toàn không tải PCM lên một máy chủ tăng cường riêng.

**B — Chỉ sử dụng APM của trình duyệt.** Các ràng buộc `echoCancellation`, `noiseSuppression` và `autoGainControl` ủy thác toàn bộ xử lý cho Audio Processing Module sẵn có của Chromium. Cách này tốn rất ít tài nguyên, nhưng phần điều khiển chủ yếu chỉ ở mức bật/tắt (boolean), hiệu quả với nhiễu không dừng thường kém hơn DeepFilterNet3 và không có thanh điều chỉnh mức khử nhiễu 0–100.

**C — Xử lý trên SFU hoặc máy chủ đám mây.** Máy khách tiết kiệm CPU và chất lượng đồng đều giữa các thiết bị, nhưng phải đánh đổi bằng quyền riêng tư, chi phí máy chủ và độ trễ cộng thêm. Khử vọng trên máy chủ cũng khó khăn hơn nhiều vì máy chủ không nắm được tín hiệu tham chiếu đang phát ra loa của từng thiết bị. Hướng kiến trúc này thuộc một dòng sản phẩm khác với gói npm hiện tại.

## Kết hợp APM trình duyệt với bộ khử nhiễu mạng nơ-ron

| Khía cạnh | Khử nhiễu APM | DeepFilterNoiseFilterProcessor |
|-----------|---------------|--------------------------------|
| Điều khiển | Bật/tắt (boolean) theo mặc định trình duyệt | `noiseReductionLevel`, `setSuppressionLevel` (0–100), `setEnabled` |
| Độ trễ | Thường nhỏ | Độ trễ hop cộng mô hình; phải nằm trong ngân sách RTF |
| Khử vọng (Echo) | AEC tích hợp sẵn trong APM | Cần giữ nguyên nhịp tham chiếu cho AEC |
| Phân phối | Có sẵn trong trình duyệt | Tải WASM và mô hình từ CDN (bài 06-03, 07-03) |

Phần lớn ứng dụng giữ nguyên **khử vọng (AEC) và tự động cân bằng âm lượng (AGC)**, đồng thời đặt **khử nhiễu mặc định của trình duyệt về `false`** khi chạy processor mạng nơ-ron. Chạy nối tiếp hai bộ khử nhiễu sẽ khiến giọng nói bị đục và méo. Ví dụ cấu hình ràng buộc đầu vào:

```javascript
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: false,
    autoGainControl: true,
    channelCount: 1,
  },
});
```

Luôn ghi log kết quả từ `track.getSettings()` trên trình duyệt đích, vì Chrome và Safari không phải lúc nào cũng áp dụng đúng mọi ràng buộc bạn yêu cầu.

Các thành phần như WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) và CDN (mạng phân phối nội dung) thuộc phạm vi triển khai của điểm chèn A, không phải điểm B.

## Những gì processor thực sự chèn vào đồ thị

`DeepFilterNoiseFilterProcessor` là lớp tích hợp công khai dành cho LiveKit, hoạt động dựa trên lớp lõi Web Audio bên dưới là `DeepFilterNet3Core`. Khi `init` hoặc `restart` được gọi, processor khởi tạo `AudioContext` ở tần số 48 kHz, gọi `initialize()` để tải mô hình và biên dịch WASM, rồi gọi `createAudioWorkletNode`. Đồ thị tín hiệu có dạng `source → worklet → MediaStreamDestination`, trong đó `processedTrack` là track âm thanh của destination mà LiveKit sẽ phát hành. Phương thức `setSuppressionLevel` giới hạn tham số về số nguyên trong khoảng 0–100 rồi gửi qua cổng của worklet. Gọi `await filter.setEnabled(false)` sẽ chuyển sang chế độ bypass mà không phá hủy đồ thị. Cuối cùng, `destroy` sẽ đóng context và gọi `proc.destroy()` trên lớp core.

Với các ứng dụng WebRTC thuần không sử dụng LiveKit, bạn vẫn có thể dựng đồ thị tương tự bằng `DeepFilterNet3Core` rồi thay track gửi đi bằng `sender.replaceTrack(processedTrack)`. Dù gói khai báo peer dependency là `livekit-client` ^2, lớp core vẫn hoạt động độc lập tốt bên ngoài LiveKit Room.

### Đổi thiết bị và tắt tiếng (mute)

Khi người dùng đổi micro, cần dọn đồ thị cũ bằng `destroy` hoặc để LiveKit tự gọi `restart` với `MediaStreamTrack` mới, sau đó phát hành lại track đã xử lý mới. Khi tắt tiếng, hãy tắt track hoặc gọi `setEnabled(false)` và cập nhật giao diện trung thực với trạng thái thực tế, tránh để worklet bị treo mà người dùng không thấy cảnh báo. Chỉ yêu cầu cấp lại quyền micro khi trình duyệt thực sự đòi hỏi.

## Khử vọng, kích thước hop và SFU

Bộ khử vọng (AEC) cần tín hiệu tham chiếu đồng bộ thời gian chặt chẽ với tín hiệu micro. Nếu bộ khử nhiễu chèn thêm độ trễ bất thường hoặc chạy lệch thứ tự kỳ vọng của AEC trình duyệt, cuộc gọi sẽ xuất hiện tiếng vọng dư hoặc bị cắt giọng. Do đó, hãy tận dụng AEC sẵn có của nền tảng, duy trì kích thước hop DeepFilter gần 10 ms ở 48 kHz (480 mẫu) theo đúng thiết kế khung của mô hình, và không tự viết thêm một lớp AEC thứ hai bằng JavaScript nếu chưa đo đạc kỹ.

SFU chỉ chuyển tiếp các gói Opus mà không chia sẻ tín hiệu tham chiếu loa giữa các máy khách. Chi phí CPU cho khử nhiễu phát sinh theo từng người tham gia đang phát âm thanh (publisher), không phụ thuộc số lượng người nghe (subscriber). Nếu chỉ một nhóm máy khách nhất định được bật tính năng này, cần ghi rõ trong tài liệu hỗ trợ kỹ thuật.

## Cấu hình kiến trúc đề xuất

Đối với ứng dụng họp trực tuyến trên trình duyệt dùng SFU LiveKit: chọn điểm chèn **A**, sử dụng `DeepFilterNoiseFilterProcessor`, cấu hình trình duyệt `echoCancellation: true` và `noiseSuppression: false`, đồng thời tải tài nguyên từ CDN do đội ngũ tự kiểm soát (bài 07-03) để việc hỗ trợ mạng nội bộ/mạng cách ly chỉ là vấn đề cấu hình đóng gói chứ không phải fork mã nguồn.

## Mini-lab

Lưu đoạn mã sau thành `insertion_check.py` và chạy `python3 insertion_check.py`.

```python
steps = [
    "getUserMedia",
    "new DeepFilterNoiseFilterProcessor",
    "setProcessor",
    "publishTrack",
]
constraints = {
    "echoCancellation": True,
    "noiseSuppression": False,
    "autoGainControl": True,
}
print("order=" + " > ".join(steps))
print("browser_ns=" + str(constraints["noiseSuppression"]))
```

**Kết quả kỳ vọng**

```text
order=getUserMedia > new DeepFilterNoiseFilterProcessor > setProcessor > publishTrack
browser_ns=False
```

**Lỗi thường gặp**

- Bật đồng thời `noiseSuppression: true` cùng processor mạng nơ-ron, gây khử nhiễu hai lần liên tiếp.
- Gắn processor lên track **từ xa (remote)** rồi nhầm tưởng là đã làm sạch luồng gửi đi.
- Chặn hàm `room.connect()` chờ tải xong tệp từ CDN; vì `setProcessor` chờ `init`, cần để tiến trình kết nối phòng chạy độc lập (bài 07-02).
- Gọi `replaceTrack` bằng track micro thô sau khi đổi thiết bị, vô tình bỏ qua track đã xử lý.

## Bẫy thường gặp

1. Khử nhiễu hai lần khiến giọng nói bị đục và nghẹt.
2. Mặc định chạy khử nhiễu trên track từ xa, gây tốn CPU sai mục đích sản phẩm.
3. Vô tình lấy mẫu lại (resample) ra khỏi tần số 48 kHz trước khi đưa vào mô hình.
4. Quên đóng `AudioContext` khi rời phòng, gây rò rỉ tài nguyên, chiếm giữ micro và hao pin.
5. Mặc định mọi ràng buộc `getUserMedia` đều được áp dụng mà không kiểm tra lại bằng `getSettings()`.

## Bài tập

1. Vẽ sơ đồ luồng gửi và luồng nhận âm thanh của ứng dụng bạn đang phát triển, đồng thời đánh dấu điểm chèn bạn chọn để triển khai.
2. Trên Chrome, ghi lại kết quả `getSettings()` trong hai trường hợp yêu cầu bật và tắt `noiseSuppression` của trình duyệt.
3. Liệt kê ba tình huống thay đổi trạng thái thiết bị (chuyển tai nghe Bluetooth, cắm micro USB, chuyển tab sang nền) và xác định khi nào cần gọi `destroy` hay `restart`.
4. Trong khoảng 5 câu, giải thích vì sao khử nhiễu phía máy chủ SFU là một bài toán sản phẩm khác với gói npm này.
5. Lời gọi `await filter.setEnabled(false)` tác động ở vị trí nào so với bước mã hóa, và tín hiệu nào vẫn tiếp tục được gửi tới SFU?

### Gợi ý đáp án

1. Triển khai điểm A trên track micro cục bộ; điểm B chỉ đóng vai trò phương án dự phòng chứ không chạy song song làm tầng xử lý thứ hai.
2. Luôn ghi lại giá trị `noiseSuppression` thực tế trình duyệt cấp phát thay vì chỉ lưu đối tượng ràng buộc đầu vào.
3. Chuyển tai nghe Bluetooth hoặc micro USB đều cần gọi `restart` hoặc khởi tạo processor mới gắn với track mới. Khi tab chuyển sang nền, `AudioContext` có thể bị `suspend` và cần `resume` sau thao tác tương tác của người dùng. Luôn gọi `destroy` khi rời phòng.
4. Khử nhiễu trên đám mây xử lý âm thanh ở phía máy chủ, làm tăng chi phí hạ tầng, băng thông và đặt ra yêu cầu cao hơn về quyền riêng tư; đồng thời máy chủ không có tín hiệu tham chiếu loa của từng máy khách để phối hợp khử vọng. Gói npm giữ toàn bộ quá trình suy luận ngay trên trình duyệt.
5. Chế độ bypass vẫn nằm tại điểm chèn A: SFU tiếp tục nhận luồng micro trên cùng track đã phát hành nhưng không áp dụng bộ khử nhiễu, không cần mở khe phát hành mới.

## Đọc thêm

- Bộ ví dụ chuẩn [WebRTC samples](https://webrtc.github.io/samples/).
- Tài liệu [MDN: MediaStreamTrack](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack).
- Tài liệu phát hành media của LiveKit: [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/) và trang chủ tài liệu [https://docs.livekit.io/](https://docs.livekit.io/).
- Chương 03 về khử vọng (AEC) và Chương 05 về ngân sách xử lý của AudioWorklet.

## Video tham khảo

- [Revamping Audio Quality for RTC Part 1: Beryl Echo Cancellation | Sriram Srinivasan and Hoang Do](https://www.youtube.com/watch?v=lapq9zvUd-k) — @Scale, tiếng Anh. **Xem trước.** Video trình bày trọn chuỗi xử lý từ miệng người nói tới tai người nghe (thu âm, tăng cường, mã hóa, truyền mạng, giải mã, phát loa) — nền tảng để xác định đúng các điểm chèn.
- [Group calling architectures in WebRTC: MCU, SFU & P2P](https://www.youtube.com/watch?v=d2N0d6CKrbk) — Tsahi Levent-Levi, tiếng Anh. Phân tích sự khác biệt giữa Mesh, MCU và SFU trong việc xử lý luồng âm thanh trên máy chủ, làm rõ vì sao cần khử nhiễu trước bước mã hóa.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Phần tích hợp cho thấy cách bộ khử nhiễu mạng nơ-ron vận hành chung với khử vọng và mất gói trong một hệ thống gọi thực tế.
