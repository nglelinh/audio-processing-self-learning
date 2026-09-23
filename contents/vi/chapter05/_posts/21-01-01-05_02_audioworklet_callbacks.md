---
layout: post
title: "05-02 AudioWorklet và audio callback"
chapter: "05"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter05
lesson_type: required
draft: false
---

Audio realtime trình duyệt chạy trong **AudioWorklet** (ScriptProcessorNode cũ—tránh production). Stack native dùng **audio callback** nghiêm ngặt tương tự. Bài này dạy hợp đồng callback: không block, CPU bị chặn, giao tiếp tường minh với main thread, và chỗ đặt processor họ DeepFilterNet trong `process(inputs, outputs, parameters)`.

## Mục tiêu học tập

Bạn mô tả vòng đời AudioWorklet (`addModule`, `AudioWorkletNode`, `process`), liệt kê thao tác cấm trên audio thread, thiết kế giao thức message-port điều khiển (bật NS, nạp state), và phác chỗ ring buffer đứng so với callback (05-03).

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao audio main-thread thất bại; lịch sử → Worklet.
- **10–25 phút** — Vòng đời và chữ ký `process`; render quantum.
- **25–40 phút** — Nên/không nên; trao PCM qua MessagePort / SharedArrayBuffer (mức cao).
- **40–50 phút** — Đặt NS neural: trong worklet vs worker+SAB.
- **50–60 phút** — Bẫy, bài tập, hệ quả Mezon web.

## Giải thích cốt lõi

### Vòng đời (trình duyệt)

1. Main: `audioContext.audioWorklet.addModule('ns-processor.js')`.
2. Tạo `AudioWorkletNode(...)`.
3. Nối `mic → nsNode → destination` (hoặc plumbing WebRTC—Ch. 07).
4. Trình duyệt gọi `process` lặp trên **luồng render audio**.

### Hợp đồng `process`

Chỉ việc bị chặn; `return true` để giữ processor sống (biết quirk trình duyệt). **Cấm:** `fetch`, parse JSON lớn, cấp phát mảng khổng lồ mỗi callback, khóa chờ main, GC nặng, compile WASM đồng bộ, `Atomics.wait` thiếu thiết kế realtime rõ. **Nên:** preallocate, tái sử dụng scratch, message điều khiển nhỏ, đo worst-case, fail mềm (bypass NS) khi trễ.

### Render quantum vs hop mô hình

Trình duyệt thường giao khối **128 mẫu**. Hop DeepFilterNet có thể **lớn hơn** (ví dụ 480 mẫu @ 48 kHz ≈ 10 ms—xác minh mô hình). Phải **gom** quantum thành hop và **phát** OLA qua ring buffer. Đừng giả định `input.length === hopSize`.

### Mặt phẳng điều khiển

`node.port.postMessage` cho bật/tắt, cường độ khử, thống kê RTF (throttled), tín hiệu mô hình sẵn/lỗi. Nạp weight trên main hoặc worker; chỉ chuyển module WASM / session ORT sẵn vào worklet theo pattern runtime hỗ trợ.

### Callback native (mô hình tinh thần song song)

CoreAudio / WASAPI / Android AudioTrack cùng triết lý: **xong trước chu kỳ kế**. Cùng quy tắc ring buffer và state; chỉ đổi tên API.

## Bẫy thường gặp

- Dùng ScriptProcessorNode (main-thread, latency cao).
- `new Float32Array` mỗi lần `process`.
- Giả định sampleRate luôn 48000—đọc `sampleRate` trong scope worklet.
- `postMessage` PCM lớn mỗi quantum (ưu tiên SAB / transferable ring).

## Bài tập

1. Worklet pass-through gain 0.5; kiểm bằng tone.
2. Đếm số mẫu mỗi `process` trên Chrome/Firefox; ghi ma trận.
3. Đặc tả message `{type:'setEnabled', value:boolean}` và state machine.
4. Mô tả UX nếu `process` thỉnh thoảng 15 ms khi quantum ~3 ms.

## Đọc thêm

- MDN AudioWorklet / AudioWorkletProcessor.
- Spec Web Audio API — ghi chú rendering thread.
- Điểm chèn WebRTC (xem trước Ch. 07).
- Hướng dẫn tích hợp ORT Web / WASM (mức cao).
