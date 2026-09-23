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

Chỗ bạn chèn khử nhiễu (NS) trong cuộc gọi WebRTC quyết định độ trễ, hành vi echo, và liệu SFU có nhận được tiếng nói đã làm sạch hay không. Bài này ánh xạ các điểm chèn so với `getUserMedia`, Audio Processing Module (APM) của trình duyệt, và `RTCPeerConnection`, rồi đối chiếu NS APM tích hợp với đường neural tùy chỉnh kiểu DeepFilterNet3.

## Kế hoạch giảng 60 phút

- 0–10 phút: Đồ thị cuộc gọi — mic → xử lý → encode → SFU → decode → phát.
- 10–25 phút: Điểm chèn A/B/C (local trước encode, remote sau decode, phía SFU).
- 25–40 phút: NS APM trình duyệt vs NS neural (ràng buộc, khi nào tắt NS APM).
- 40–50 phút: Pattern thay track và bẫy khi đổi thiết bị.
- 50–60 phút: Mini-lab: phác thay `MediaStreamTrack` local sau NS neural.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Xác định chỗ NS chạy so với `getUserMedia` và `PeerConnection`.
- So sánh NS APM trình duyệt với NS neural cho hội nghị.
- Liệt kê ràng buộc riêng của cuộc gọi kiểu SFU.
- Phác luồng thay track an toàn khi mute và đổi thiết bị.

## Đồ thị âm thanh hội nghị

Đường gửi local đơn giản:

```text
Microphone
  → getUserMedia MediaStreamTrack
  → [tuỳ chọn: AudioContext / AudioWorklet NS]
  → [tuỳ chọn: APM trình duyệt: AEC / NS / AGC]
  → RTCPeerConnection sender (encode Opus/…)
  → SFU / peers
```

Đường nhận:

```text
Remote RTP
  → PeerConnection receiver (decode)
  → MediaStreamTrack
  → <audio> / AudioContext render
  → [hiếm: NS sau decode trên remote — thường sai chỗ nếu mục tiêu là echo của chính bạn]
```

**Quy tắc sản phẩm:** chạy NS uplink của *bạn* trên **đường gửi local**, trước encode. NS sau decode trên audio remote chỉ làm sạch nhiễu *người khác* cho tai *bạn*; không giảm những gì bạn upload.

## Điểm chèn (A / B / C)

### A — Local trước encode (khuyến nghị cho NS sản phẩm)

Xử lý track mic, tạo `MediaStreamTrack` mới, publish track đó.

Ưu: SFU và peer nhận tiếng đã enhance; một chỗ chỉnh mức khử nhiễu.  
Nhược: thêm độ trễ thuật toán; phải sống chung cẩn thận với AEC.

### B — Chỉ APM trình duyệt

Dùng ràng buộc `getUserMedia` / APM Chromium (`echoCancellation`, `noiseSuppression`, `autoGainControl`).

Ưu: sẵn có, ít công sức.  
Nhược: thường yếu hơn mô hình kiểu DeepFilterNet với nhiễu không dừng; ít nút UX sản phẩm.

### C — NS phía SFU / cloud

Ưu: client nhẹ.  
Nhược: riêng tư, chi phí, độ trễ; AEC khó — không phải thiết kế gói Mezon trên trình duyệt.

`deepfilternet3-noise-filter` của Mezon hướng tới **A** qua LiveKit `TrackProcessor` (bài 07-02).

## NS APM vs NS neural tùy chỉnh

| Khía cạnh | APM NS | Neural (ví dụ DF3 WASM) |
|-----------|--------|-------------------------|
| Điều khiển | boolean / mặc định trình duyệt | mức khử, bật/tắt, phiên bản model |
| Độ trễ | thường nhỏ | frame hop + model (phải trong ngân sách realtime) |
| Echo | AEC trong APM | **Bạn** không được phá timing tham chiếu AEC |

**Kết hợp thực tế:** nhiều sản phẩm giữ **AEC + AGC** của trình duyệt và **tắt NS trình duyệt** khi NS neural đang chạy, tránh khử kép (giọng bị đục).

```javascript
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: false, // neural NS đảm nhận
    autoGainControl: true,
    channelCount: 1,
  },
});
```

Luôn kiểm tra trên trình duyệt đích: ràng buộc và `getSettings()` khác nhau (Chrome vs Safari).

## Pattern thay track

1. Lấy track mic từ `getUserMedia`.
2. Đưa qua `AudioContext` → worklet/WASM NS → `MediaStreamDestination`.
3. Lấy track publish từ `destination.stream`.
4. LiveKit: `audioTrack.setProcessor(filter)` (bài 07-02).
5. WebRTC thô: `sender.replaceTrack(processedTrack)` khi đổi thiết bị / bật tắt NS.

### Đổi thiết bị và mute

- **Đổi thiết bị:** phá đồ thị cũ (destroy processor), dựng lại, rồi `replaceTrack`.
- **Mute:** ưu tiên disable track; đừng để worklet treo mà UX không rõ.
- **Quyền:** chỉ hỏi lại khi cần; gán nhãn thiết bị sau khi đã cấp quyền.

## Tương tác đường echo (ôn chương 03)

AEC cần **tham chiếu** (những gì phát ra loa) căn chỉnh với mic. Nếu NS thêm trễ lớn không được tính, hoặc làm biến dạng mic trước AEC theo thứ tự trình duyệt không mong đợi, bạn có thể gặp echo dư hoặc cắt tiếng.

Gợi ý: giữ AEC trình duyệt theo tài liệu stack (LiveKit / browser); căn frame ~10 ms @ 48 kHz (480 mẫu) khi khớp WASM DeepFilterNet3; đừng chồng thêm một AEC JS “cho chắc” mà không đo.

## Ràng buộc kiểu SFU

- SFU thường **chuyển tiếp** Opus; không chia sẻ tham chiếu loa từng client cho AEC.
- CPU NS là theo participant local, không theo mỗi subscriber.
- Nếu chỉ một số client bật NS, ghi rõ cho đội hỗ trợ.

## Bẫy thường gặp

1. **NS kép** — APM + neural → giọng đục.
2. Xử lý track remote theo mặc định — sai câu chuyện sản phẩm “nhiễu của tôi”.
3. Bỏ qua sample rate — resample lung tung trước DF3.
4. Rò `AudioContext` khi rời phòng.
5. Giả định constraint luôn được tôn trọng — hãy log `track.getSettings()`.

## Bài tập

1. Vẽ đồ thị send/receive của app và đánh dấu đúng một điểm chèn NS sẽ ship.
2. Trên Chrome, so `getSettings()` khi NS on vs off.
3. Liệt kê ba edge case đổi thiết bị và cách dispose processor.
4. Giải thích ngắn vì sao NS phía SFU khác gói npm Mezon.

## Đọc thêm

- [WebRTC samples](https://webrtc.github.io/samples/)
- [MDN: MediaStreamTrack](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack)
- Tài liệu thiết kế WebRTC AudioProcessing (Chromium)
- Chương 03-04 và 05 của khóa học
