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

Hầu hết lập trình viên web đều quen với một phản xạ gỡ lỗi quen thuộc: thấy chương trình có vấn đề là chèn ngay một dòng `console.log(...)` vào bên trong hàm đang chạy. Thế nhưng trên luồng xử lý âm thanh thời gian thực của trình duyệt, chính dòng `console.log` vô hại đó lại là **thủ phạm** biến một cuộc gọi đang mượt mà thành một chuỗi tiếng tách và mất tiếng liên tục! Tại sao một dòng lệnh in ra màn hình lại nguy hiểm đến thế?

Âm thanh trên trình duyệt được xử lý trên một luồng thời gian thực chuyên biệt. **AudioWorklet** (luồng render của Web Audio API) là giao diện cho phép đưa mã xử lý của bạn chạy trực tiếp trên luồng đó theo trình tự: gọi `audioWorklet.addModule`, khởi tạo `AudioWorkletNode`, và nhận lệnh gọi `process(inputs, outputs, parameters)` một lần cho mỗi render quantum. Mỗi quantum thường dài **128 mẫu**, tương ứng $$128/48000\approx 2{,}67$$ ms ở tần số lấy mẫu 48 kHz. Bên trong `process`, bạn tuyệt đối không được cấp phát bộ nhớ, chờ khóa (lock) hay gọi mạng. Một lệnh `console.log` vi phạm cả ba nguyên tắc này và không thể dùng để gỡ lỗi mất tiếng (dropout).

**Mạch bài học:** Cú sốc `console.log` trên luồng âm thanh → Bản đồ kiến thức nền (Tách luồng Main vs. Audio Render, Ba lệnh cấm thời gian thực, Độ lệch nhịp 128 vs. 480 mẫu) → Vòng đời AudioWorklet & hợp đồng bypass → Vì sao `console.log` bị cấm → Khung giải thích theo dõi từng callback trong chu kỳ 15 quantum = 4 hop (40 ms) → Mini-lab và Bài tập.

![Quantum AudioWorklet như ngân sách thời gian tường cạnh RTF]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Hình. Mỗi callback chỉ quản lý một khối dữ liệu ngắn — thường là 128 mẫu, xấp xỉ 2,67 ms ở 48 kHz — và phải trả về trước khi khối kế tiếp đến hạn. Hệ số thời gian thực (real-time factor, RTF) được đo trên đơn vị khối mà bạn chọn bấm giờ (một quantum hoặc một hop 10 ms gom từ nhiều quantum). Biểu đồ này thể hiện giới hạn thời gian, không phải sự cho phép để chạy trọn một lượt suy luận của DeepFilterNet ngay trong một lần gọi `process`.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ nắm được vòng đời của AudioWorklet, viết được hàm `process` sao chép thẳng tín hiệu đầu vào sang đầu ra khi bật cờ bypass, giải thích được vì sao `console.log` bị cấm trên luồng render âm thanh, và biết cách ghép hop 480 mẫu của DeepFilterNet lên chuỗi quantum 128 mẫu mà không giả định chúng chia hết cho nhau.

## Bản đồ kiến thức nền: Kiến trúc luồng âm thanh thời gian thực trong trình duyệt

### 1. Tách biệt Luồng chính (Main Thread) và Luồng Render âm thanh (AudioWorklet Thread)
- **Là gì:** Trong trình duyệt, luồng chính bận vẽ giao diện (DOM layout, cuộn trang, phân tích JSON) và có thể bị treo hàng chục mili giây. `AudioWorklet` đẩy toàn bộ hàm `process()` sang một luồng ưu tiên thời gian thực riêng biệt, giao tiếp với luồng chính bất đồng bộ qua `MessagePort` (hoặc `SharedArrayBuffer`).
- **Nghiên cứu gì:** Bảo vệ nhịp phát/thu âm thanh khỏi những cú giật của giao diện người dùng (điều mà API cũ `ScriptProcessorNode` không làm được).

### 2. Tính an toàn thời gian thực (Real-Time Safety: No-Alloc, No-Lock, No-I/O)
- **Là gì:** Quy tắc thép chung cho mọi hệ thống âm thanh từ CoreAudio, WASAPI, AAudio đến AudioWorklet: thời gian chạy xấu nhất (worst-case execution time) bên trong callback phải bị chặn chặt.
- **Nghiên cứu gì:** Mọi thao tác có thời gian thực thi không xác định — cấp phát heap (có thể kích hoạt GC), chờ mutex (gây đảo ưu tiên), hay gọi mạng/ổ đĩa — đều bị cấm tuyệt đối; toàn bộ bộ đệm nháp (scratch buffer) phải cấp phát sẵn một lần duy nhất trong `constructor`.

### 3. Hợp đồng Bypass và Độ lệch pha kích thước khối (Block-Size Mismatch)
- **Là gì:** Trình duyệt cấp dữ liệu theo quantum $$Q = 128$$ mẫu, còn mạng DeepFilterNet xử lý theo hop $$H = 480$$ mẫu; đồng thời trong lúc WASM đang tải hoặc khi hop bị trễ, luồng âm thanh vẫn phải trả về đúng 128 mẫu mà không được đứng chờ.
- **Nghiên cứu gì:** Thiết kế đường dự phòng `bypass` sao chép không cấp phát (`output.set(input)`) kết hợp bộ đệm gom mẫu ở ranh giới giữa hai nhịp đồng hồ không chia hết cho nhau.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao luồng chính (main thread) không được đảm nhận callback micro.
- **10–25 phút** — Vòng đời AudioWorklet, quantum 128 mẫu và giá trị trả về `return true`.
- **25–40 phút** — Cơ chế sao chép bypass cùng lệnh cấm cấp phát bộ nhớ, khóa đồng bộ và gọi mạng.
- **40–50 phút** — Đồ thị ONNX của DF3 được phép thực thi ở đâu.
- **50–60 phút** — Thực hành mini-lab (chỉ cần mã giả) và làm bài tập.

## Giải thích cốt lõi

### Vòng đời

1. Trên luồng chính, gọi `audioContext.audioWorklet.addModule('ns-processor.js')` để nạp tệp script của processor. Quá trình biên dịch diễn ra tại bước này, không phải bên trong `process`.
2. Gọi `new AudioWorkletNode(audioContext, 'ns-processor', options)` để khởi tạo node. Tham số `options.processorOptions` dùng để truyền kích thước hop và số kênh một lần duy nhất lúc khởi tạo.
3. Kết nối đường tín hiệu `source → nsNode → destination`, hoặc nối vào luồng track của WebRTC (Chương 07).
4. Trình duyệt sẽ gọi hàm `process` trên **luồng render âm thanh**, một lần cho mỗi quantum trong suốt vòng đời của node. Bạn có thể xem thêm tài liệu tham chiếu chuẩn về AudioWorklet trên MDN tại [developer.mozilla.org/en-US/docs/Web/API/AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet).

Hàm `registerProcessor('ns-processor', NsProcessor)` chỉ chạy một lần khi module được nạp lúc dựng đường dẫn âm thanh, không chạy lặp lại ở từng buffer. Việc trả về `true` từ `process` giữ cho node tiếp tục hoạt động; nếu trả về `false`, trình duyệt có thể thu hồi node, khiến bộ khử nhiễu đột ngột ngừng hoạt động giữa cuộc gọi.

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

Khi `bypass` được bật, người nghe vẫn nhận được tín hiệu micro với độ trễ đúng bằng độ trễ của đồ thị âm thanh, chỉ không qua bộ khử nhiễu. Đây là hành vi chuẩn mực trong thời gian WASM đang biên dịch hoặc khi hop trước đó bị trễ hạn (bài 05-03). Lưu ý rằng `output.set(input)` yêu cầu hai mảng có độ dài tương thích; nếu ghi một quantum 128 mẫu vào bộ đệm đích có kích thước nhỏ hơn, trình duyệt sẽ ném ngoại lệ và chấm dứt hoạt động của node. Vì vậy, cần kiểm tra `input.length` trước khi sao chép.

Gói `deepfilternet3-noise-filter` áp dụng kiến trúc tương tự: chạy ONNX/WASM trong AudioWorklet với `DeepFilterNoiseFilterProcessor`, `DeepFilterNet3Core` và mức khử nhiễu từ 0 đến 100 qua `setSuppressionLevel`. Gói này không khớp từng bit với công cụ dòng lệnh `deepFilter`, và đoạn mã bypass ở trên chỉ là mã minh họa giảng dạy, không phải mã nguồn của gói đó.

### Vì sao `console.log` bị cấm trong `process`

Luồng render âm thanh chịu giới hạn thời gian cứng khoảng 2,67 ms cho mỗi quantum 128 mẫu ở 48 kHz. Ba nguyên tắc bắt buộc được suy ra từ giới hạn này, và `console.log` phá vỡ cả ba:

- **Không cấp phát bộ nhớ.** Việc định dạng một dòng log sẽ tạo ra chuỗi mới trên heap. Cấp phát bộ nhớ có thể kích hoạt bộ thu gom rác (GC), mà chỉ một khoảng dừng GC kéo dài vài mili giây đã vượt quá thời lượng một quantum.
- **Không chờ khóa (lock).** Việc chuyển dòng log sang giao diện console hoặc DevTools phải đi qua một luồng khác và có thể phải chờ mutex. `Atomics.wait` cũng như mọi cơ chế giao tiếp liên tiến trình (IPC) đồng bộ khác đều thuộc cùng nhóm lỗi này.
- **Không gọi mạng.** Nếu đầu ra log được gửi tới trình gỡ lỗi từ xa hoặc hệ thống thu thập telemetry, luồng sẽ phải chờ thao tác I/O, trong khi thiết bị âm thanh không bao giờ dừng lại chờ.

Lệnh cấm này cũng áp dụng cho `fetch`, `JSON.parse` tệp trọng số, tạo `new Float32Array` trong mỗi callback, biên dịch WASM hay bị chặn trên một mutex do luồng chính nắm giữ. Các thay đổi điều khiển (như bật/tắt bypass, chỉnh mức khử nhiễu, báo hiệu mô hình đã sẵn sàng) phải đi qua thông điệp nhỏ trên `MessagePort` và chỉ được áp dụng ở ranh giới giữa các quantum. Toàn bộ trọng số phải được nạp sẵn trên luồng chính hoặc một worker riêng trước khi node tắt chế độ bypass.

Việc viết một script Node.js import `wrtc` hoặc chạy bản dựng WASM là phần thực hành mở rộng, không bắt buộc để hoàn thành bài lab này. Tiêu chuẩn đạt yêu cầu chỉ cần phần mã giả và giải thích đúng như trên.

### Quan hệ giữa quantum và hop

Bước nhảy đã công bố của DeepFilterNet là 10 ms, tương đương **480 mẫu** ở tần số lấy mẫu 48 kHz (bài 04-02, 04-03). Tỉ số $$480/128=3{,}75$$ cho thấy hai kích thước này không chia hết cho nhau: 3 callback chỉ tích lũy được 384 mẫu, còn 4 callback tích lũy được 512 mẫu. Do đó, cần đưa dữ liệu vào một ring buffer (bài 05-03) cho đến khi đủ 480 mẫu để chạy một hop, sau đó cắt phần đầu ra overlap-add trở lại thành từng quantum 128 mẫu. Giả định cứng `input.length === 480` sẽ dẫn đến mất mẫu hoặc lặp âm thanh.

Biến `sampleRate` luôn có sẵn trong phạm vi toàn cục của worklet, vì vậy hãy đọc trực tiếp giá trị này. Ở tần số 44,1 kHz, cùng khối 128 mẫu kéo dài $$128/44100\approx 2{,}90$$ ms, đồng thời hop 480 mẫu sẽ không còn tương ứng 10 ms cho một mô hình huấn luyện ở 48 kHz. Các API âm thanh native như CoreAudio, WASAPI và AAudio đều tuân theo nguyên tắc tương tự dưới những tên gọi khác: phải hoàn thành trước kỳ kế tiếp và chuyển sang bypass nếu mô hình xử lý bị trễ.

## Khung giải thích: Dò tay chu kỳ ghép 128 mẫu và 480 mẫu (nên đọc chậm)

Tại sao ta nói không bao giờ được giả định "cứ đúng 4 callback là chạy 1 hop"? Hãy tính **bội chung nhỏ nhất** của $$Q = 128 = 2^7$$ và $$H = 480 = 2^5 \cdot 3 \cdot 5$$:
$$ \operatorname{LCM}(128, 480) = 2^7 \cdot 3 \cdot 5 = \mathbf{1920\text{ mẫu}}. $$
Ở 48 kHz, $$1920$$ mẫu đúng bằng $$40\text{ ms}$$, tương ứng **15 callback** ($$15 \times 128 = 1920$$) và **4 hop** ($$4 \times 480 = 1920$$). Bây giờ hãy dò từng callback để thấy số dư mẫu trong bộ đệm biến thiên tuần hoàn ra sao:

| Callback thứ | Mẫu tích lũy trước khi chạy hop | Chạy hop 480? | Mẫu còn dư trong ring A |
| :--- | :--- | :--- | :--- |
| 1, 2, 3 | $$128 \to 256 \to 384$$ | Chưa | $$384$$ |
| **4** | $$384 + 128 = 512$$ | **Có (Hop #1)** | $$512 - 480 = \mathbf{32}$$ |
| 5, 6, 7 | $$160 \to 288 \to 416$$ | Chưa | $$416$$ |
| **8** | $$416 + 128 = 544$$ | **Có (Hop #2)** | $$544 - 480 = \mathbf{64}$$ |
| 9, 10, 11 | $$192 \to 320 \to 448$$ | Chưa | $$448$$ |
| **12** | $$448 + 128 = 576$$ | **Có (Hop #3)** | $$576 - 480 = \mathbf{96}$$ |
| 13, 14 | $$224 \to 352$$ | Chưa | $$352$$ |
| **15** | $$352 + 128 = 480$$ | **Có (Hop #4)** | $$480 - 480 = \mathbf{0}$$ |

**Bài học rút ra từ bảng trên:** Hop #1, #2, #3 chạy sau mỗi **4 callback**, nhưng Hop #4 lại rơi vào đúng **3 callback** sau Hop #3 (tại callback 15)! Nếu một lập trình viên ngây thơ viết `if (callbackCount % 4 === 0) runHop()`, mỗi chu kỳ 40 ms sẽ bị rò rỉ đúng 128 mẫu — chỉ sau 1 giây đã trượt mất 3.200 mẫu (66,7 ms âm thanh)! Ring buffer ở bài 05-03 chính là cấu trúc loại bỏ hoàn toàn kiểu đếm tay sai lầm này.

## Bẫy thường gặp

- Gỡ lỗi mất tiếng bằng `console.log`, vô tình làm tình trạng mất tiếng nghiêm trọng hơn.
- Khởi tạo `new Float32Array(128)` ngay bên trong hàm `process`.
- Ghi cứng tần số 48000 thay vì đọc biến `sampleRate` thực tế của worklet.
- Dùng `postMessage` (structured clone) sao chép toàn bộ buffer PCM sang luồng chính ở mỗi quantum; nếu bắt buộc phải chuyển dữ liệu sang luồng khác, hãy dùng ring buffer trên `SharedArrayBuffer` và đo chi phí sao chép.
- Dùng `ScriptProcessorNode`, kéo toàn bộ quá trình xử lý âm thanh về luồng chính.

## Mini-lab

**Mục tiêu.** Hiện thực thao tác sao chép bypass bằng mã giả Python để bài lab không phụ thuộc vào trình duyệt hay Node.js. Phần triển khai bằng AudioWorklet đã được trình bày trong khối mã phía trên; bộ chạy thử trên Node là phần tùy chọn, không bắt buộc để đạt yêu cầu.

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

**Kết quả kỳ vọng.** `True [0.1, -0.2, 0.3, -0.4]`. Đối tượng `output` là bộ đệm do bên gọi cấp phát sẵn từ trước; hàm `process` không tạo thêm danh sách mới, không in ra màn hình và không thực hiện thao tác chờ nào.

**Lỗi thường gặp.** Cấp phát mới `out = frame.copy()` bên trong hàm rồi coi đó là an toàn thời gian thực; chèn lệnh in “tạm cho bài lab” rồi quên xóa khi đưa vào worklet; yêu cầu phải chạy `npm install` hoặc mở trình duyệt mới công nhận đạt; hoặc coi việc sao chép thành công là bằng chứng cho thấy đồ thị DF3 đáp ứng được ngân sách 2,67 ms — sao chép bộ nhớ chỉ tốn vài lệnh đọc ghi, còn suy luận đồ thị thì nặng hơn rất nhiều.

## Bài tập

1. **Giới hạn thời gian.** Với quantum 256 mẫu ở tần số 48 kHz, bạn có bao nhiêu mili giây để xử lý? Nếu tần số lấy mẫu là 44,1 kHz thì con số đó là bao nhiêu?
2. **Tích lũy mẫu.** Mô hình cần hop 480 mẫu trong khi mỗi lần gọi `process` chỉ cung cấp 128 mẫu. Sau bao nhiêu callback thì lần đầu tiên bạn có đủ một hop, và còn dư lại bao nhiêu mẫu?
3. **Thông điệp điều khiển mức khử nhiễu.** Hãy viết payload cho `postMessage` để đặt mức khử nhiễu bằng 40 trên một processor có hàm `setSuppressionLevel` trong dải 0–100. Điều gì xảy ra nếu áp dụng thay đổi này ngay giữa quá trình chạy `output.set`?
4. **Phân tích sự cố.** Hàm `process` thỉnh thoảng mất 15 ms trong khi thời lượng quantum chỉ là 2,67 ms. Người dùng sẽ nghe thấy hiện tượng gì, và các callback kế tiếp nên xử lý ra sao?

### Gợi ý đáp án

1. Ở 48 kHz: $$256/48000\approx 5{,}33$$ ms. Ở 44,1 kHz: $$256/44100\approx 5{,}80$$ ms. Cả hai khoảng thời gian đều vẫn quá nhỏ cho một session ONNX khởi động lạnh, và 5,33 ms mới chỉ bằng một nửa hop 10 ms nên một quantum vẫn chưa thể tương đương một hop.
2. Sau 4 callback, tổng số mẫu tích lũy là $$4\times 128=512$$ mẫu. Một hop tiêu thụ 480 mẫu và còn dư **32** mẫu nằm lại trong ring buffer đầu vào (3 callback chỉ mới có 384 mẫu).
3. Payload là `{type: "setSuppressionLevel", value: 40}`, được tiếp nhận trong `onmessage`, lưu tạm vào một thuộc tính của processor và chỉ áp dụng ở ranh giới hop kế tiếp. Nếu thay đổi hệ số khuếch đại ngay giữa quá trình sao chép, hai nửa của cùng một quantum sẽ có mức khuếch đại khác nhau và gây ra tiếng tách.
4. Thiết bị âm thanh sẽ bị underrun: người dùng nghe thấy tiếng tách, một đoạn âm bị lặp lại hoặc khoảng lặng ngắn tùy cách xử lý của từng trình duyệt. Callback phục hồi cần chuyển sang đường bypass (sao chép tín hiệu gốc) hoặc phát tiếp các mẫu sẵn có trong ring buffer đầu ra, tuyệt đối không chặn luồng để chờ suy luận đuổi kịp.

## Đọc thêm

- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet) và tài liệu tham chiếu `AudioWorkletProcessor.process`.
- Bài 05-01 về RTF và ngân sách hop 10 ms; bài 05-03 về ring buffer dùng để hấp thụ độ lệch 3,75 quantum mỗi hop.
- Kho mã [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) tham khảo giao diện sản phẩm với `DeepFilterNoiseFilterProcessor` và `setSuppressionLevel` (không phải mã nguồn của bài học này).

## Video tham khảo

- [AudioWorklet :: What, Why, and How - Hongchan Choi](https://www.youtube.com/watch?v=g1L4O1smMC0) — WebAudio PDX, tiếng Anh. **Xem trước.** Hongchan Choi giải thích vì sao luồng âm thanh không được phụ thuộc vào luồng chính, đồng thời trình bày rõ `addModule`, processor và callback.
- [Sonic Boom! Audio Programming on Android and Chrome (Google I/O'19)](https://www.youtube.com/watch?v=EeQr0zfvF04) — Google for Developers, tiếng Anh. Phần trình bày về Chrome minh họa sự kết hợp giữa AudioWorklet và WebAssembly ngay trên cùng callback, kèm các số liệu độ trễ khứ hồi đo được.
