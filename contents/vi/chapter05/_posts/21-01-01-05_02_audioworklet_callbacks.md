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

Audio trình duyệt được render trên một luồng thời gian thực. **AudioWorklet** (luồng render của Web Audio) là API đặt mã của bạn lên luồng đó: `audioWorklet.addModule`, rồi một `AudioWorkletNode`, rồi `process(inputs, outputs, parameters)` một lần mỗi render quantum. Quantum thường là **128 mẫu**. Ở 48 kHz đó là $$128/48000\approx 2{,}67$$ ms. Trong `process` bạn không được cấp phát, lấy khóa, hay chạm mạng. `console.log` phạm cả ba kiểu hại đó và không phải cách gỡ một dropout.

![Quantum AudioWorklet như ngân sách thời gian tường cạnh RTF]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Figure. Mỗi callback sở hữu một khối ngắn — thường 128 mẫu, khoảng 2,67 ms ở 48 kHz — và phải trả về trước khối kế. RTF (real-time factor, hệ số thời gian thực) đo trên khối bạn chọn để bấm giờ (một quantum, hoặc một hop mô hình 10 ms gom từ nhiều quantum). Hình là hạn, không phải giấy phép chạy một lượt forward của DeepFilterNet bên trong một lần `process`.*

## Mục tiêu học tập

Bạn lần vòng đời AudioWorklet, viết một `process` chép đầu vào sang đầu ra khi cờ bypass bật, giải thích vì sao `console.log` là bất hợp pháp trên luồng đó, và đặt hop DeepFilterNet 480 mẫu lên nhiều quantum 128 mẫu mà không giả định các số chia hết.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao luồng chính không được sở hữu callback micro.
- **10–25 phút** — Vòng đời, quantum 128 mẫu, `return true`.
- **25–40 phút** — Bản sao bypass, và lệnh cấm cấp phát / khóa / mạng.
- **40–50 phút** — Đồ thị ONNX DF3 được phép chạy ở đâu.
- **50–60 phút** — Mini-lab (mã giả là đủ), bài tập.

## Giải thích cốt lõi

### Vòng đời

1. Trên luồng chính, `audioContext.audioWorklet.addModule('ns-processor.js')` nạp script processor. Biên dịch thuộc về đây. Không thuộc về trong `process`.
2. `new AudioWorkletNode(audioContext, 'ns-processor', options)` tạo node. `options.processorOptions` truyền kích thước hop và số kênh một lần.
3. Nối `source → nsNode → destination`, hoặc vào đường track WebRTC (Chương 07).
4. Trình duyệt gọi `process` trên **luồng render audio**, một lần mỗi quantum, suốt đời node. Trang AudioWorklet của MDN là tham chiếu hướng spec: [developer.mozilla.org/en-US/docs/Web/API/AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet).

`registerProcessor('ns-processor', NsProcessor)` chạy khi module nạp, lúc dựng luồng audio, không phải mỗi buffer. Trả `true` từ `process` giữ node sống. Trả `false` cho phép trình duyệt thu hồi node — nghe như suppressor biến mất giữa cuộc gọi.

### Hợp đồng bypass

```js
class NsProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bypass = true; // model not ready: copy, do not block
    this.port.onmessage = (event) => {
      // Control messages are delivered between callbacks, not during them.
      if (event.data.type === "setBypass") this.bypass = event.data.value;
    };
  }

  process(inputs, outputs) {
    const input = inputs[0] && inputs[0][0];
    const output = outputs[0] && outputs[0][0];
    if (!input || !output) return true;
    if (this.bypass) {
      // output already exists. set() copies bytes; it does not allocate the buffer.
      output.set(input);
      return true;
    }
    // Enhancement would use only preallocated scratch and a ready model.
    output.set(input);
    return true;
  }
}
registerProcessor("ns-processor", NsProcessor);
```

Khi `bypass` bật, người nghe nghe micro, trễ bằng đồ thị, không có suppressor. Đó là hành vi đúng lúc WASM đang biên dịch hoặc hop trước trượt hạn (bài 05-03). `output.set(input)` đòi độ dài bằng nhau. Quantum 128 vào buffer dư có kích thước khác sẽ ném, và một ngoại lệ trong `process` giết node. Kiểm `input.length` trước khi chép.

`deepfilternet3-noise-filter` dùng cùng hình: ONNX/WASM trong AudioWorklet, `DeepFilterNoiseFilterProcessor`, `DeepFilterNet3Core`, suppression 0–100 qua `setSuppressionLevel`. Nó không khớp bit với CLI `deepFilter`, và đoạn bypass ở trên là mã giảng, không phải mã gói đó.

### Vì sao `console.log` bất hợp pháp trong `process`

Luồng render có hạn cứng khoảng 2,67 ms cho quantum 128 mẫu ở 48 kHz. Ba luật kéo theo, và `console.log` phá cả ba:

- **Không cấp phát.** Định dạng một dòng log dựng một chuỗi. Chuỗi là cấp phát heap. Cấp phát có thể kích hoạt thu gom rác, và một khoảng dừng GC vài mili giây đã lớn hơn quantum.
- **Không khóa.** Đưa dòng đó tới console hoặc DevTools sang luồng khác và có thể chờ mutex. `Atomics.wait` và mọi IPC đồng bộ cùng một lớp lỗi.
- **Không mạng.** Một nơi nhận log đăng lên debugger từ xa hoặc đầu telemetry thì chờ I/O. Thiết bị audio không chờ.

Cùng lệnh cấm phủ `fetch`, `JSON.parse` một file trọng số, `new Float32Array` mỗi callback, biên dịch WASM, và chặn trên mutex mà luồng chính đang giữ. Đổi điều khiển (bypass, suppression, bit “model sẵn sàng”) đến như thông điệp nhỏ trên `MessagePort`, áp giữa các quantum. Trọng số nạp trên luồng chính hoặc một worker trước khi node rời bypass.

Một script Node.js import `wrtc` hoặc một bản WASM là luyện tập tùy chọn. Không bắt buộc để qua lab này. Điều kiện đạt là mã giả và lời giải thích ở trên.

### Quantum và hop

Hop đã công bố là 10 ms, **480 mẫu** ở 48 kHz (04-02, 04-03). $$480/128=3{,}75$$. Ba callback giữ 384 mẫu, bốn giữ 512. Nối vào một ring (05-03) đến khi đủ 480, chạy một hop, rồi cắt đầu ra overlap-add trở lại các quantum 128 mẫu. Giả định `input.length === 480` sẽ làm rơi hoặc lặp audio.

`sampleRate` nằm trong scope của worklet. Hãy đọc nó. Ở 44,1 kHz cùng 128 mẫu kéo dài $$128/44100\approx 2{,}90$$ ms, và hop 480 mẫu là độ dài sai cho mô hình 48 kHz. CoreAudio, WASAPI và AAudio dùng cùng luật dưới tên khác: xong trước kỳ kế, và bypass khi mô hình trễ.

## Bẫy thường gặp

- Gỡ dropout bằng `console.log` rồi làm chúng nặng hơn.
- `new Float32Array(128)` bên trong `process`.
- Ghim cứng 48000 thay vì đọc `sampleRate`.
- Structured-clone cả buffer PCM sang luồng chính mỗi quantum. Nếu phải rời luồng, dùng ring SharedArrayBuffer, và đo các bản sao.
- Chạy ScriptProcessorNode, kéo audio về luồng chính.

## Mini-lab

**Mục tiêu.** Hiện thực bản sao bypass bằng mã giả Python để lab không cần trình duyệt và không phụ thuộc Node. Bản AudioWorklet là khối trong bài; harness Node là tùy chọn và không bắt buộc để đạt.

```bash
python3 - << 'PY'
def process(frame, bypass, output):
    """Copy input to the caller-provided output when bypass is set.
    console.log is illegal: it allocates a string, can lock against
    the console thread, and may touch the network. Do none of that here.
    """
    if bypass:
        for i, sample in enumerate(frame):
            output[i] = sample
        return True
    for i, sample in enumerate(frame):
        output[i] = sample  # enhancement would write here, still no allocation
    return True

frame = [0.1, -0.2, 0.3, -0.4]
out = [0.0] * 4
alive = process(frame, bypass=True, output=out)
print(alive, out)
PY
```

**Expected**. `True [0.1, -0.2, 0.3, -0.4]`. Đối tượng buffer đầu ra là cái bên gọi đã cấp phát. Không gì trong `process` dựng list, in, hay chờ.

**Failure modes**. Cấp phát `out = frame.copy()` bên trong hàm rồi gọi đó là an toàn thời gian thực. Nhét một lệnh in “chỉ cho lab” rồi để lại trong worklet. Đòi `npm install` hoặc trình duyệt đang chạy mới được đạt. Coi một bản sao thành công là bằng chứng đồ thị DF3 đạt ngân sách 2,67 ms — bản sao là vài load và store, đồ thị thì không.

## Bài tập

1. **Hạn.** Quantum 256 mẫu, 48 kHz. Bạn có bao nhiêu mili giây? Ở 44,1 kHz?
2. **Gom.** Bạn cần 480 mẫu và mỗi `process` cho 128. Sau bao nhiêu callback thì lần đầu giữ đủ một hop, và còn dư bao nhiêu mẫu?
3. **Thông điệp suppression.** Soạn payload `postMessage` đặt suppression bằng 40 trên processor có `setSuppressionLevel` trong khoảng 0–100. Chuyện gì xảy ra nếu áp nó giữa chừng `output.set`?
4. **Sự cố.** `process` thỉnh thoảng mất 15 ms trong khi quantum là 2,67 ms. Người dùng nghe gì, và callback kế nên làm gì?

### Gợi ý đáp án

1. $$256/48000\approx 5{,}33$$ ms. $$256/44100\approx 5{,}80$$ ms. Cả hai vẫn quá nhỏ cho một session ONNX lạnh, và 5,33 ms là nửa hop 10 ms, nên một quantum vẫn chưa phải một hop.
2. Bốn callback giữ $$4\times 128=512$$ mẫu. Hop tiêu 480 và **32** mẫu còn trong ring đầu vào. Ba callback chỉ giữ 384.
3. `{type: "setSuppressionLevel", value: 40}` xử lý trong `onmessage`, cất vào một trường, áp ở biên hop kế. Áp giữa chừng bản sao khiến hai nửa của một quantum dùng hai gain khác nhau và gây click.
4. Thiết bị underrun: một click, một lần lặp, hoặc một khoảng im ngắn, tùy trình duyệt. Callback hồi phục nên đi đường bypass (chép) hoặc phát mẫu đã có trong ring đầu ra, không chặn đến khi suy luận đuổi kịp.

## Đọc thêm

- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet) và tham chiếu `AudioWorkletProcessor.process`.
- Bài 05-01 cho RTF và ngân sách hop 10 ms; bài 05-03 cho ring hấp thụ 3,75 quantum.
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) cho `DeepFilterNoiseFilterProcessor` và `setSuppressionLevel` như bề mặt sản phẩm, không phải mã của bài này.
