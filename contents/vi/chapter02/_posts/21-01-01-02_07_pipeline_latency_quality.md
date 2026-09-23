---
layout: post
title: "02-07 Đánh đổi độ trễ và chất lượng của pipeline"
chapter: "02"
order: 7
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Mỗi lựa chọn STFT và mô hình là một thỏa thuận giữa độ trễ, CPU và chất lượng. Phân biệt ngăn quyết định ship sai: **độ trễ thuật toán là audio muộn bao nhiêu, real-time factor (RTF) là CPU có theo kịp không.** Mô hình nhanh vẫn có thể quá muộn.

## Mục tiêu học tập

1. Liệt kê các chặng pipeline cộng độ trễ và CPU.
2. Đổi cửa sổ/hop/kích thước FFT lấy chất lượng và độ trễ, có số.
3. Giải thích kiểu hỏng chất lượng khi tối ưu độ trễ quá tay.
4. Lập phiếu đạt/không đạt cho cấu hình đem ship.
5. Nối các đánh đổi với mục tiêu thiết kế realtime kiểu DeepFilterNet.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Sơ đồ pipeline đầu-cuối (mic → NS → encoder) |
| 10–28 | Thí nghiệm tưởng tượng, có số |
| 28–42 | Các kiểu hỏng chất lượng và độ trễ |
| 42–52 | Phiếu cho pipeline kiểu Mezon |
| 52–60 | Bài tập |

![Các quantum AudioWorklet trên trục thời gian; process() đôi khi vượt một quantum: RTF là thời gian tường trên thời lượng audio, khác với độ trễ thuật toán của cửa sổ STFT]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Hình. Mỗi vạch là một quantum render; RTF so thời gian tường của process() với thời lượng audio đó, một con số khác với độ trễ thuật toán của cửa sổ STFT.*

## Giải thích cốt lõi

### Hai đồng hồ

Độ trễ thuật toán là tính chất của đồ thị tín hiệu. Với STFT nhân quả ở bài 02-02,

$$
D_{\mathrm{alg}}\approx T_L=\frac{L}{f_s},
$$

cộng look-ahead, trễ resample, và buffer gói. Ở 48 kHz, \(L=960\) đóng góp khoảng **20 ms** dù FFT tốn 0.2 ms hay 2 ms thời gian tường. Mẫu muộn vì phải đợi đầy cửa sổ.

RTF là tính chất của bản cài:

$$
\mathrm{RTF}=\frac{T_{\mathrm{wall}}(D)}{D}.
$$

\(D\) là thời lượng audio vừa xử lý (một hop, hoặc một quantum). \(\mathrm{RTF}<1\) nghĩa là xong trước khi khối sau đến hạn. Nó không nói bạn đã nhét bao nhiêu look-ahead. Cảnh báo phía kia của hình: RTF trung bình 0.4 vẫn click nếu p99 vượt hop. Hãy log p95/p99.

Quantum 128 mẫu ở 48 kHz dài \(128/48000\approx 2.67\,\mathrm{ms}\). Đó là lưới trên hình, không phải hop của mô hình. Hop 10 ms trải khoảng bốn quantum; thanh `process()` đỏ là quantum mà FFT và mạng bị overrun. Khởi động lạnh (biên dịch WASM/ONNX) là việc main thread, không phải RTF trạng thái dừng.

### Các chặng (điển hình)

1. Thu / buffer quantum AudioWorklet
2. Resample về rate mô hình
3. Downmix mono
4. Cắt frame STFT (cửa sổ/hop)
5. Đổi đặc trưng (ví dụ ERB)
6. Tăng cường neural hoặc cổ điển
7. Đặc trưng ngược / ISTFT / OLA
8. Resample về rate sink
9. Giao cho encoder WebRTC

Với mỗi chặng, log riêng độ trễ trên dạng sóng và phần đóng góp RTF. Resampler có thể rẻ về RTF mà vẫn thêm group delay; một phiên ONNX có thể đắt về RTF mà không thêm look-ahead ngoài STFT.

### Núm và hệ quả

| Tăng núm | Độ trễ | CPU | Xu hướng chất lượng |
|----------|--------|-----|---------------------|
| Cửa sổ \(L\) | tăng | tăng (FFT lớn hơn) | chi tiết tần số tốt hơn; thời gian nhòe hơn |
| Hop \(R\) | bản thân hop không phải \(D_{\mathrm{alg}}\); \(R\) nhỏ thì hops/s tăng | tăng khi \(R\) giảm | mask thường mượt hơn |
| Cỡ mô hình | gần như không đổi nếu look-ahead cố định | tăng | thường tăng cho đến khi RTF vỡ |
| Look-ahead | tăng | tăng | chất lượng thường tăng |
| Tốc độ mẫu | tăng | tăng | băng thông tăng nếu mô hình được train cho rate đó |

**Phải đo.** Cắt \(R\) từ 480 xuống 240 ở 48 kHz làm đôi hops/s (100 → 200) và CPU của STFT; \(D_{\mathrm{alg}}\) vẫn gần \(L/f_s\) trừ khi cửa sổ cũng ngắn lại. Rút cửa sổ làm rộng bin (bài 02-03). Đó là đổi chất lượng, không phải một chiến thắng RTF miễn phí.

### Số nên giữ

Ở 48 kHz:

- quantum 128 mẫu ≈ 2.67 ms
- hop 480 mẫu = 10 ms → 100 quyết định/giây
- cửa sổ 960 mẫu = thang đệm 20 ms

Ở 16 kHz, cùng *số mili giây* thì ít mẫu hơn (FFT rẻ hơn) nhưng băng thông hẹp hơn. Cùng *số mẫu* thì khác mili giây: \(L=512\) ở 16 kHz là 32 ms, không phải 20 ms. Thời gian tường 3 ms trên hop 10 ms là \(\mathrm{RTF}=0.3\), thoải mái. Thời gian tường 12 ms trên cùng hop đó là \(\mathrm{RTF}=1.2\), overrun, dù 12 ms vẫn nhỏ hơn cửa sổ 20 ms. Mini-lab in cả hai cặp để hai đồng hồ nằm ở hai biến khác nhau.

### Các kiểu hỏng

**Ngân sách trễ quá ít:** cửa sổ quá ngắn thì hài không tách được, mask gắt.

**Trễ quá nhiều:** cuộc gọi thấy muộn, và look-ahead đặt trước AEC trông như đường echo đang trôi.

**Headroom CPU quá ít:** một overrun p99 (thanh đỏ) đã thành tiếng nổ, dù RTF trung bình đẹp.

### Phiếu ship (ví dụ)

| Tiêu chí | Đích (minh họa) | Đạt? |
|----------|-----------------|------|
| Look-ahead thuật toán | ≤ ngân sách sản phẩm (cỡ 20–40 ms) | |
| p95 RTF trên thiết bị | ≤ 0.5 | |
| Khứ hồi COLA | sai số dưới ngưỡng | |
| DNSMOS / nghe | so baseline NS của WebRTC | |
| Không warble hop | nghe + spectrogram | |

Thay số minh họa bằng SLA của sản phẩm. Đừng đánh dấu “RTF ≤ 0.5” thành đạt độ trễ thuật toán, hoặc ngược lại.

### Kết luận kiểu DeepFilterNet

Thiết lập full-band đã công bố là 48 kHz, STFT 960 điểm (20 ms), overlap 50% (hop 10 ms), cộng look-ahead vài frame ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)). Coi đó là ràng buộc cứng. Chỗ đánh đổi là vị trí trên đồ thị, resample, và ngân sách thiết bị. `deepfilternet3-noise-filter` 1.3.0 là processor 48 kHz trên hợp đồng đó; nếu p95 RTF trượt, đừng lặng lẽ đổi hop.

## Ví dụ có số

Config A: 16 kHz, L=20 ms, R=10 ms, mô hình nhỏ, RTF 0.2, MOS ổn.
Config B: 48 kHz, L=40 ms, R=5 ms, mô hình lớn, RTF 0.9, MOS offline cao hơn, giật trên điện thoại → **đừng ship B**.

Cửa sổ của B đã 40 ms, và RTF trung bình 0.9 không còn chỗ cho quantum thanh đỏ.

Ngân sách thuật toán 40 ms mà đã chi 20 ms cho cửa sổ thì không nuốt thêm vài frame look-ahead 10 ms. Đừng “tiết kiệm” 20 ms bằng cách chỉ báo 3 ms thời gian tường.

## Bẫy thường gặp

1. Chỉ tối ưu RTF trung bình.
2. Đổi L/R mà không làm lại tập eval.
3. So chất lượng ở các độ trễ khác nhau một cách không công bằng.
4. Quên chi phí resample trong RTF.
5. Lấy timing của bản debug làm sự thật production.

## Mini-lab

**Mục tiêu.** In độ trễ frame thuật toán và RTF như hai con số khác nhau cho một hop 48 kHz, kể cả ca overrun. Không cần thiết bị audio.

```python
fs, L, R = 48000, 960, 480
frame_ms = 1000 * L / fs
hop_ms = 1000 * R / fs
quantum_ms = 1000 * 128 / fs
print("algorithmic frame ms", frame_ms)
print("hop ms", hop_ms, "quantum ms", round(quantum_ms, 2))

def rtf(wall_ms, audio_ms):
    return wall_ms / audio_ms

print("RTF if process() takes 3 ms", rtf(3.0, hop_ms))
print("RTF if process() takes 12 ms", rtf(12.0, hop_ms))
```

**Kỳ vọng.** Trễ frame `20.0` ms, hop `10.0` ms, quantum khoảng `2.67` ms. RTF in `0.3` và `1.2`. Ca sau trễ hop dù 12 ms vẫn nhỏ hơn cửa sổ 20 ms.

**Khi hỏng.** Chia thời gian tường cho cửa sổ thay vì cho hop thì ra RTF 12/20 = 0.6 và giấu overrun. Coi RTF 0.3 là “độ trễ 3 ms” là trộn hai đồng hồ, và phiếu sẽ đậu trong khi người dùng vẫn nghe thấy trễ hoặc tiếng nổ. p99 bằng 12 ms với trung bình 3 ms chính là cảnh báo của hình: hãy log cả hai.

## Bài tập nhỏ

1. Vẽ pipeline 9 giai; đánh dấu chỗ log timestamp.
2. Hop 10→5 ms: hop/s và CPU roughly?
3. Ba metric scorecard cho softphone CSKH.
4. Vì sao 48 kHz có thể hại mô hình train 16 kHz dù CPU cho phép?
5. Một artifact chất lượng từ cửa sổ quá ngắn.

### Gợi ý đáp án

1. Đóng dấu lúc thu, sau resample, vào STFT, ra STFT, và lúc giao encoder; trừ để tách độ trễ khỏi thời gian tường.
2. hops/s tăng đôi (100 → 200 ở 48 kHz nếu hop từng là 480 mẫu); CPU STFT xấp xỉ tăng đôi. \(D_{\mathrm{alg}}\) không giảm một nửa trừ khi \(L\) đổi.
3. Ví dụ p95 RTF, độ trễ thuật toán so với ngân sách cuộc gọi, và một lượt nghe/DNSMOS trên tên riêng và chữ số.
4. Bin và mép ERB của mạng được bố trí cho 16 kHz; audio 48 kHz bị gán nhãn 16 kHz là sai phổ, và băng thừa có thể alias vào nếu quên low-pass.
5. Hài không tách được và mask gắt, nhấp nháy. Plosive bị nhòe là lỗi ngược lại, do cửa sổ quá dài.

## Đọc thêm

- Framing realtime DeepFilterNet, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) và [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Tổng quan WebRTC APM: [modules/audio_processing](https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/).
- Hướng dẫn hiệu năng AudioWorklet trên MDN — quantum so với hop của bạn.
