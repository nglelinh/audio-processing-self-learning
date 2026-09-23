---
layout: post
title: "00-03 Khử nhiễu thời gian thực và offline"
chapter: "00"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter00
lesson_type: required
draft: false
---

Ship NS ít phụ thuộc đỉnh MOS trên bảng xếp hạng hơn là sống sót trên audio thread. Bài này định nghĩa độ trễ và RTF chặt, giải thích ràng buộc streaming, và liệt kê chế độ hỏng bạn sẽ debug trong tích hợp kiểu Mezon.

![Cùng một bộ khử nhiễu, vẽ một lần là batch offline và một lần là khối streaming nhân quả]({{ site.imgurl }}/generated/realtime-vs-offline.png)

*Figure. Look-ahead offline và hop streaming là hai khoản trễ khác nhau; hình chỉ để lập ngân sách, không phải thuật toán thứ hai.*

## Mục tiêu học tập

1. Định nghĩa độ trễ thuật toán, độ trễ đệm, và RTF.
2. Giải thích ràng buộc nhân quả / streaming so với look-ahead offline.
3. Liên hệ kích thước frame, hop, và ngân sách trễ đầu–cuối cho cuộc gọi.
4. Liệt kê underrun, audio cắt khúc, drift đồng hồ, gián đoạn state.
5. Áp dụng tư duy “RTF worst-case trên thiết bị đích” khi chọn mô hình.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Định nghĩa latency + RTF kèm bài tập số |
| 12–28 | Pipeline STFT nhân quả; vì sao SOTA offline thất bại trên WebRTC/LiveKit |
| 28–42 | State streaming: OLA, ẩn RNN/DF |
| 42–52 | Chế độ hỏng và checklist SLA |
| 52–60 | Bài tập nhỏ |

## Giải thích cốt lõi

### Ba khái niệm độ trễ

1. **Đệm** — thời gian gom mẫu trước khi xử lý frame.
2. **Thuật toán** — look-ahead, group delay bộ lọc, trễ OLA.
3. **Hệ thống** — quantum OS/callback, cầu JS/Wasm, jitter mạng.

### Real-time factor

$$
\mathrm{RTF} = \frac{T_{\mathrm{proc}}}{T_{\mathrm{audio}}}
$$

Streaming cần **dư địa**: RTF trung bình 0.9 vẫn chết khi GC/thermal đẩy một frame lên RTF 2.0.

**Ví dụ:** hop \(R=480\) tại \(48\,\mathrm{kHz}\) → \(10\,\mathrm{ms}\). Ngân sách RTF \(\le 0.5\) ⇒ \(T_{\mathrm{proc}}\le 5\,\mathrm{ms}\) cho đường STFT+model+ISTFT (đã khấu hao).

**Trung bình đẹp vẫn có thể glitch.** 100 hop, mỗi hop 10 ms: 99 hop xong trong 3 ms, một hop mất 15 ms. Trung bình là \((99\times 3+15)/100=3.12\,\mathrm{ms}\), RTF trung bình \(0.312\). Hop chậm có RTF \(1.5\) và trượt callback. Phải kèm p95 hoặc p99, nếu không số trung bình sẽ che underrun.

**Quantum không phải hop.** Quantum 128 mẫu ở 48 kHz dài \(128/48000\approx 2.67\,\mathrm{ms}\). Hop 480 mẫu là \(480/128=3.75\) quantum. Processor phải gom quantum lẻ trong ring buffer. DeepFilterNet3 (arXiv:2305.08227) là bản real-time của họ đó; checkpoint offline vài trăm ms look-ahead không thành nhân quả chỉ vì bạn bọc nó trong `DeepFilterNoiseFilterProcessor`.

### Nhân quả và offline

DeepFilterNet2/3 nhấn thiết kế **real-time / causal** — lý do khóa học neo vào họ này thay vì chỉ mô hình diffusion offline.

### Frame, hop, trễ

$$
T_{\mathrm{hop}}=\frac{R}{f_s},\qquad T_{\mathrm{win}}=\frac{L}{f_s}
$$

Giảm \(L\) giảm trễ nhưng hại độ phân giải tần số — Chương 02 đào sâu.

### State streaming

OLA, ước lượng nhiễu/VAD, state hồi tiếp neural. Cold-start mỗi callback gây click; đổi sample rate không reset gây “bùn”.

### Chế độ hỏng

Underrun/glitch; tiếng nói cắt/ướt; drift ring buffer; artifact đuôi; cliff nhiệt.

## Ví dụ — mô hình này ship được không?

Offline: look-ahead 300 ms, RTF GPU 0.15, RTF CPU laptop 1.2 @ 48 kHz mono. Ngân sách gọi \(\le 40\,\mathrm{ms}\) look-ahead → **fail**. RTF 1.2 → **fail** nếu không downsample/quantize/mô hình nhỏ hơn.

## Bẫy thường gặp

1. Trích RTF paper đo offline batch lớn.
2. Bỏ qua latency đuôi p95/p99.
3. Dùng checkpoint non-causal “cho demo”.
4. Đo trễ bằng `Date.now()` xuyên nhiều tầng đệm ẩn.
5. Nhầm quantum AudioWorklet (ví dụ 128 mẫu ≈ 2.67 ms @ 48 kHz) với hop STFT.

## Mini-lab

**Mục tiêu.** In ngân sách hop 10 ms ở 48 kHz, rồi chỉ một hop bị spike mà RTF trung bình vẫn trông an toàn.

```python
fs, hop = 48_000, 480
t_audio_ms = 1_000 * hop / fs
t_proc_max_ms = 0.5 * t_audio_ms
mean_ms = (99 * 3 + 15) / 100
quantum_ms = 1_000 * 128 / fs
print(f"t_audio_ms={t_audio_ms:.1f} t_proc_max_ms={t_proc_max_ms:.1f}")
print(f"mean_ms={mean_ms:.2f} mean_rtf={mean_ms / t_audio_ms:.3f}")
print(f"spike_rtf={15 / t_audio_ms:.2f}")
print(f"quantum_ms={quantum_ms:.2f} quanta_per_hop={hop/128:.2f}")
```

**Expected.** `t_audio_ms=10.0 t_proc_max_ms=5.0`, `mean_ms=3.12 mean_rtf=0.312`, `spike_rtf=1.50`, `quantum_ms=2.67 quanta_per_hop=3.75`.

**Failure modes.** Lấy trung bình RTF rồi bỏ spike. Coi 128 mẫu là hop 10 ms. Đảo RTF nên máy chậm lại in số nhỏ hơn.

## Bài tập nhỏ

1. Hop 256 mẫu @ 16 kHz: hop ms? \(T_{\mathrm{proc}}\) max cho RTF 0.25?
2. Liệt kê ba state buffer hệ STFT-NS phải giữ giữa các hop.
3. Vì sao RTF trung bình 0.4 vẫn glitch trên Chrome khi tải cao?
4. Đề xuất checklist go/no-go 5 phép đo trước khi bật NS mặc định.

### Gợi ý đáp án

1. \(256/16000=16\,\mathrm{ms}\). RTF \(0.25\) cho phép \(4\,\mathrm{ms}\) xử lý.
2. Buffer chồng OLA, state cửa sổ phân tích, và hồi tiếp của mạng hoặc tracker nhiễu. Thêm sample rate và số kênh.
3. Trung bình giấu pause của GC, spike nhiệt, hoặc một hop vượt 16 ms. Callback cảm nhận p99.
4. Năm mục dùng được: look-ahead nhân quả tính bằng ms, p95 RTF trên CPU đích, số underrun trong cuộc gọi 10 phút, quy tắc downmix stereo, và một lần nghe ở đúng sample rate sản phẩm.

## Đọc thêm

- DeepFilterNet2 (arXiv:2205.05474) và DeepFilterNet3 (arXiv:2305.08227) — mục real-time / causal. Mã: https://github.com/Rikorose/DeepFilterNet.
- Tổng quan đồ thị xử lý WebRTC APM.
- Tài liệu MDN AudioWorklet (ràng buộc thời gian callback).
