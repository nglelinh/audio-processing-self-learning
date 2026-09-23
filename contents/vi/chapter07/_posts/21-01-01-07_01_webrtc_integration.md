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

Chỗ bạn chèn khử nhiễu trong cuộc gọi WebRTC quyết định độ trễ, echo, và việc SFU có chuyển tiếp tiếng đã sạch hay không. Bài này ánh xạ các điểm chèn với `getUserMedia`, Audio Processing Module của trình duyệt, và `RTCPeerConnection`, rồi chỉ cách `DeepFilterNoiseFilterProcessor` của `deepfilternet3-noise-filter` **1.3.0** chiếm chỗ trước encode trên uplink thông qua TrackProcessor (móc biến đổi track của LiveKit).

![Track audio local của LiveKit đi qua processor khử nhiễu trước khi publish]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. Điểm chèn A là TrackProcessor trên track mic local, trước khi sender mã hóa.*

## Mục tiêu học tập

Bạn đặt khử nhiễu neural trên uplink trước encode, giữ khử echo của trình duyệt trong khi tắt khử nhiễu của trình duyệt, và mô tả `setProcessor` đổi gì ở `MediaStreamTrack` được publish mà không đưa suy luận ra khỏi thiết bị.

## Kế hoạch 60 phút

- **0–10 phút** — Mic, xử lý, encode, SFU, decode, phát.
- **10–25 phút** — Điểm chèn A, B và C.
- **25–40 phút** — APM trình duyệt đối với processor 1.3.0.
- **40–50 phút** — Đổi thiết bị, mute, và đồ thị worklet.
- **50–60 phút** — Mini-lab, bẫy, bài tập.

## Đồ thị âm thanh hội nghị

Đường gửi local:

```text
Microphone
  → getUserMedia MediaStreamTrack
  → [tuỳ chọn: AudioContext / AudioWorklet NS]
  → [tuỳ chọn: APM trình duyệt: AEC / NS / AGC]
  → RTCPeerConnection sender (encode Opus)
  → SFU / peers
```

Đường nhận:

```text
RTP từ xa
  → decode phía receiver
  → MediaStreamTrack
  → phần tử audio hoặc AudioContext
```

Hãy chạy khử nhiễu uplink **của bạn** trên đường gửi local, trước encode. Khử nhiễu sau decode trên track remote chỉ làm sạch nhiễu của người khác cho tai bạn. Nó không giảm những gì bạn upload, và là chỗ sai để đuổi echo của chính bạn.

AudioWorklet (callback xử lý âm thanh trên luồng realtime) chỉ xuất hiện ở điểm A khi bạn tự dựng đồ thị. Với LiveKit, TrackProcessor bọc worklet đó.

## Điểm chèn A, B và C

**A — local, trước encode.** Xử lý mic và publish track đã xử lý. SFU và peer nhận tiếng đã tăng cường. Bạn trả độ trễ thuật toán trên đường găng, và không được phá nhịp của bộ khử echo. Đây là đích của gói Mezon. `DeepFilterNoiseFilterProcessor` triển khai TrackProcessor của LiveKit. Bạn dựng nó, rồi `await audioTrack.setProcessor(filter)`, rồi `await room.localParticipant.publishTrack(audioTrack)`. LiveKit gọi `init` của processor, và `init` dựng đồ thị. Thiết kế này không upload PCM lên một máy chủ tăng cường riêng.

**B — chỉ APM trình duyệt.** Các ràng buộc như `echoCancellation`, `noiseSuppression` và `autoGainControl` nhờ Audio Processing Module của Chromium làm việc. Chi phí thấp. Điều khiển chủ yếu là boolean, và nhiễu không dừng thường yếu hơn mô hình DeepFilterNet3. Không có thanh mức từ 0 đến 100.

**C — SFU hoặc cloud.** CPU client nhàn và chất lượng đồng đều, đổi lại quyền riêng tư, chi phí và độ trễ thêm. Khử echo cũng khó hơn vì máy chủ không giữ tham chiếu loa của từng client. Đó là sản phẩm khác gói npm này.

## APM trình duyệt đứng cạnh đường neural

| Khía cạnh | Khử nhiễu APM | DeepFilterNoiseFilterProcessor |
|-----------|---------------|--------------------------------|
| Điều khiển | Boolean / mặc định trình duyệt | `noiseReductionLevel`, `setSuppressionLevel` (0–100), `setEnabled` |
| Độ trễ | Thường nhỏ | Hop cộng mô hình; phải vào ngân sách hệ số realtime |
| Echo | AEC nằm trong APM | Bạn giữ nhịp tham chiếu AEC |
| Phân phối | Có sẵn | WASM cộng mô hình trên CDN (bài 06-03, 07-03) |

Nhiều sản phẩm giữ **khử echo và auto gain**, đặt **khử nhiễu của trình duyệt thành false** khi processor neural đang chạy. Hai bộ khử nối tiếp làm giọng đục. Phác ràng buộc:

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

Hãy log `track.getSettings()` trên trình duyệt đích. Chrome và Safari không tôn trọng mọi ràng buộc bạn xin.

WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) và CDN (mạng phân phối nội dung) thuộc điểm A, không thuộc điểm B.

## Processor chèn những gì

`DeepFilterNoiseFilterProcessor` là adapter LiveKit công khai. `DeepFilterNet3Core` là adapter Web Audio bên dưới. Khi `init` hoặc `restart`, processor bảo đảm `AudioContext` 48 kHz, gọi `initialize()` (biên dịch WASM và tải mô hình), rồi `createAudioWorkletNode`. Đồ thị là source → worklet → `MediaStreamDestination`. `processedTrack` là track audio của destination, và đó là track LiveKit nên publish. `setSuppressionLevel` kẹp về số nguyên từ 0 đến 100 rồi gửi vào cổng worklet. `await filter.setEnabled(false)` bỏ qua khử nhiễu mà không phá đồ thị. `destroy` đóng context và gọi `proc.destroy()` trên core.

Trang WebRTC thô không dùng LiveKit có thể dựng cùng đồ thị bằng `DeepFilterNet3Core` rồi `sender.replaceTrack(processedTrack)`. Peer dependency của gói là `livekit-client` ^2; class core vẫn là công cụ đúng khi bạn không ở trong Room.

### Đổi thiết bị và mute

Khi đổi thiết bị, phá đồ thị cũ bằng `destroy`, hoặc để LiveKit gọi `restart` với `MediaStreamTrack` mới. Sau đó publish track đã xử lý mới. Mute bằng cách tắt track hoặc `setEnabled(false)`, và giữ UX thành thật. Đừng để worklet treo mà màn hình không có trạng thái. Chỉ xin lại quyền khi trình duyệt đòi.

## Echo, hop, và SFU

Bộ khử echo cần tham chiếu căn với micro. Bộ khử nhiễu thêm một độ trễ không được tính, hoặc chạy theo thứ tự AEC trình duyệt không chờ, sẽ để echo dư hoặc cắt tiếng. Hãy ưu tiên AEC mà stack đã ghi tài liệu, giữ hop DeepFilter gần 10 ms ở 48 kHz (480 mẫu) khi đó là frame của mô hình, và đừng thêm AEC thứ hai bằng JavaScript nếu chưa đo.

SFU chuyển tiếp Opus. Nó không chia sẻ tham chiếu loa của từng client. CPU khử nhiễu tính theo participant đang publish, không theo người subscribe. Nếu chỉ một số client bật, hãy ghi vào tài liệu hỗ trợ.

## Lựa chọn đã làm

Cuộc họp trên trình duyệt với SFU LiveKit: điểm chèn **A**, `DeepFilterNoiseFilterProcessor`, `echoCancellation: true`, `noiseSuppression: false` của trình duyệt, asset từ CDN bạn kiểm soát (bài 07-03) để mạng cách ly là quyết định đóng gói chứ không phải một lần fork.

## Mini-lab

Chạy `python3 insertion_check.py`.

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

**Expected**

```text
order=getUserMedia > new DeepFilterNoiseFilterProcessor > setProcessor > publishTrack
browser_ns=False
```

**Failure modes**

- `noiseSuppression: true` cùng lúc với processor neural (khử hai lần).
- Chạy processor trên track **remote** rồi gọi đó là làm sạch uplink.
- Chặn `room.connect()` vì lần fetch CDN. `setProcessor` chờ `init`, nên hãy để kết nối phòng đi trên timeline riêng (bài 07-02).
- `replaceTrack` bằng mic thô sau khi đổi thiết bị, làm rơi track đã xử lý.

## Bẫy thường gặp

1. Khử nhiễu hai lần làm giọng đục.
2. Xử lý track remote theo mặc định tốn CPU cho một câu chuyện sản phẩm sai.
3. Resample bất ngờ ra khỏi 48 kHz trước mô hình này.
4. Rò `AudioContext` khi rời phòng, giữ micro và pin.
5. Giả định ràng buộc được tôn trọng chỉ vì bạn đã xin.

## Bài tập

1. Vẽ đồ thị gửi và nhận của app rồi đánh dấu một điểm chèn bạn sẽ ship.
2. Trên Chrome, chụp `getSettings()` khi xin khử nhiễu trình duyệt bật và tắt.
3. Liệt kê ba ca đổi thiết bị (tai nghe Bluetooth, mic USB, tab nền) và nêu `destroy` hoặc `restart` cho từng ca.
4. Trong năm câu, giải thích vì sao khử nhiễu phía SFU là sản phẩm khác gói này.
5. `await filter.setEnabled(false)` nằm ở đâu so với encode, và cái gì vẫn chảy tới SFU?

### Gợi ý đáp án

1. Ship điểm A trên mic local. Điểm B là đường lùi, không phải tầng thứ hai.
2. Ghi giá trị `noiseSuppression` có hiệu lực, không chỉ ràng buộc bạn truyền.
3. Bluetooth và USB đều cần `restart` hoặc processor mới với track mới. Tab nền có thể `suspend` `AudioContext`; `resume` sau cử chỉ người dùng. Luôn `destroy` khi rời phòng.
4. Khử nhiễu trên cloud nhìn audio đã mã hóa hoặc audio phía máy chủ, tốn băng thông và niềm tin, và không có tham chiếu loa của client. Processor npm ở lại trong trình duyệt.
5. Bypass vẫn là điểm chèn A. SFU nhận đường mic với khử nhiễu tắt, không phải một khe publish khác.

## Đọc thêm

- [WebRTC samples](https://webrtc.github.io/samples/).
- [MDN: MediaStreamTrack](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack).
- Tài liệu LiveKit về publish: [TrackProcessor / setProcessor on LocalAudioTrack](https://docs.livekit.io/transport/media/publish/). Trang chủ tài liệu: [https://docs.livekit.io/](https://docs.livekit.io/).
- Chương 03 về AEC và Chương 05 về ngân sách AudioWorklet.
