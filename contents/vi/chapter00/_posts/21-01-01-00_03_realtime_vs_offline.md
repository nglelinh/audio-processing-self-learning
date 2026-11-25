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

Việc triển khai thành công một bộ khử nhiễu (NS) vào sản phẩm phụ thuộc ít hơn vào điểm MOS cao nhất trên bảng xếp hạng và phụ thuộc nhiều hơn vào khả năng vận hành ổn định trên luồng âm thanh (audio thread). Bài học này định nghĩa chặt chẽ độ trễ và hệ số thời gian thực (RTF), phân tích các ràng buộc của luồng xử lý streaming, đồng thời liệt kê những chế độ lỗi thường gặp khi gỡ lỗi trong các tích hợp kiểu Mezon.

![Cùng một bộ khử nhiễu, vẽ một lần là batch offline và một lần là khối streaming nhân quả]({{ site.imgurl }}/generated/realtime-vs-offline.png)

*Hình. Độ trễ nhìn trước (look-ahead) ở chế độ ngoại tuyến và bước nhảy hop ở chế độ thời gian thực là hai khoản trễ khác nhau; sơ đồ dùng để lập ngân sách độ trễ, không đại diện cho hai thuật toán riêng biệt.*


Nếu bạn tải một tập podcast lên phần mềm xử lý âm thanh để làm sạch trước khi đăng YouTube, phần mềm có thể đọc trọn cả 60 phút ghi âm, phân tích trước những đoạn im lặng ở phút thứ 40 để đoán chính xác tiếng ồn nền của căn phòng, rồi chạy một mạng Transformer khổng lồ mất 5 phút mới xong. Nhưng trong một **cuộc gọi thoại trực tiếp**, bạn không có đặc quyền biết trước người kia sẽ nói gì sau 1 giây nữa! Ranh giới giữa **xử lý thời gian thực (real-time / streaming)** và **xử lý ngoại tuyến (offline / batch)** không chỉ là chuyện tốc độ chạy nhanh hay chậm — nó thay đổi hoàn toàn kiến trúc toán học của thuật toán.

---

## Kiến thức cần nhớ: Bốn ràng buộc kỹ thuật tách biệt Thời gian thực với Ngoại tuyến là gì?

### 1. Tính nhân quả (Causality) và Cửa sổ nhìn trước (Look-Ahead)
Bộ lọc ngoại tuyến dùng **tích chập hai phía** và mạng hai chiều (Bi-LSTM / Transformer toàn cục) nhìn thấy cả quá khứ lẫn tương lai. Bộ lọc thời gian thực phải dùng **tích chập nhân quả** và mạng một chiều (GRU / Uni-LSTM / Causal Conv) với bộ đệm trạng thái ẩn (hidden state) truyền từ khung $$t-1$$ sang khung $$t$$, chỉ được nhìn trước tối đa 1–2 khung (10–20 ms).

### 2. Ngân sách độ trễ đầu–cuối (End-to-End Latency Budget)
Theo khuyến nghị **ITU-T G.114** cho thoại tương tác hai chiều, tổng độ trễ một chiều (từ miệng người nói đến tai người nghe) nên giữ **dưới 150 ms** để hai người không nói đè lên nhau. Trong 150 ms đó, mạng internet, bộ đệm chống rung (jitter buffer), codec (Opus) và phần cứng loa/micro đã ngốn phần lớn — bộ khử nhiễu thường chỉ được cấp **20–40 ms**!

### 3. Bố trí bộ nhớ và Quản lý trạng thái (Streaming State)
Trong chế độ streaming, thuật toán không được cấp phát bộ nhớ động tùy tiện trên luồng âm thanh (tránh giật do Garbage Collection trên trình duyệt/WASM), mà phải dùng **bộ đệm vòng (ring buffer)** cố định và lưu giữ chính xác trạng thái chồng lấp (overlap-add buffer) giữa các khung liên tiếp.

---

### Giải thích: tự tay lập bảng ngân sách độ trễ cho một cuộc gọi WebRTC 150 ms

Hãy cộng từng thành phần độ trễ trên một đường truyền thoại thực tế (một chiều) để thấy tại sao từng khung 10 ms lại quý giá đến thế:

1. **Thu âm phần cứng + hệ điều hành (Capture & AudioWorklet):** $$\approx 15\text{ ms}$$.
2. **Khối khử nhiễu thời gian thực (khung hop 10 ms + look-ahead 20 ms + suy luận 2 ms):** $$10 + 20 + 2 = \mathbf{32\text{ ms}}$$.
3. **Nén & giải nén Codec Opus:** $$\approx 22.5\text{ ms}$$.
4. **Truyền mạng Internet (một chiều) + Jitter Buffer:** $$40 + 25 = 65\text{ ms}$$.
5. **Phát ra loa (Playout):** $$\approx 10\text{ ms}$$.
- **Tổng độ trễ một chiều:** $$15 + 32 + 22.5 + 65 + 10 = \mathbf{144.5\text{ ms}} < 150\text{ ms}$$ (đạt chuẩn trò chuyện tự nhiên!).
- **Nếu thay bằng một mô hình bán-offline có look-ahead 300 ms:** tổng độ trễ vọt lên **$$424.5\text{ ms}$$** (khứ hồi gần 1 giây!) — dù chất lượng âm thanh sạch hơn vài phần trăm, cuộc gọi lập tức trở nên khó chịu vì hai đầu liên tục ngắt lời nhau!

---

## Mục tiêu học tập

1. Định nghĩa chính xác độ trễ thuật toán, độ trễ đệm và hệ số thời gian thực (RTF).
2. Giải thích các ràng buộc nhân quả / streaming so với khả năng nhìn trước (look-ahead) của xử lý ngoại tuyến.
3. Liên hệ kích thước khung, bước nhảy hop và ngân sách độ trễ đầu–cuối trong một cuộc gọi.
4. Liệt kê các chế độ lỗi phổ biến: underrun, âm thanh bị cắt khúc, trôi đồng hồ (clock drift) và gián đoạn trạng thái (state discontinuity).
5. Áp dụng tư duy đánh giá "RTF ở trường hợp xấu nhất trên thiết bị đích" khi lựa chọn mô hình.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Định nghĩa độ trễ và RTF kèm ví dụ tính toán |
| 12–28 | Pipeline STFT nhân quả; lý giải vì sao các mô hình SOTA ngoại tuyến thất bại trên WebRTC/LiveKit |
| 28–42 | Quản lý trạng thái streaming: bộ đệm OLA và trạng thái ẩn của RNN/DF |
| 42–52 | Các chế độ lỗi thực tế và danh mục kiểm tra SLA |
| 52–60 | Bài tập nhỏ |

## Giải thích cốt lõi

### Ba thành phần độ trễ

1. **Độ trễ đệm (buffering latency)** — thời gian chờ gom đủ mẫu trước khi có thể xử lý một khung.
2. **Độ trễ thuật toán (algorithmic latency)** — gồm khoảng nhìn trước (look-ahead), trễ nhóm của bộ lọc (group delay) và độ trễ từ phép cộng chồng lấp (OLA).
3. **Độ trễ hệ thống (system latency)** — kích thước quantum của hệ điều hành/callback, cầu nối JS/Wasm và độ rung mạng (network jitter).

### Hệ số thời gian thực (RTF)

$$
\mathrm{RTF} = \frac{T_{\mathrm{proc}}}{T_{\mathrm{audio}}}
$$

Hệ thống streaming luôn cần **biên độ an toàn**: một mô hình có RTF trung bình 0.9 vẫn sẽ gặp lỗi khi trình thu gom rác (GC) hoặc giảm xung do quá nhiệt đẩy thời gian xử lý của một khung lên RTF 2.0.

**Ví dụ:** Với bước nhảy hop \(R=480\) mẫu ở tần số \(48\,\mathrm{kHz}\), mỗi hop tương ứng \(10\,\mathrm{ms}\). Để giữ ngân sách RTF \(\le 0.5\), thời gian xử lý \(T_{\mathrm{proc}}\) cho toàn bộ chuỗi STFT + mô hình + ISTFT (tính khấu hao theo hop) phải thỏa mãn \(\le 5\,\mathrm{ms}\).

**Giá trị trung bình đẹp vẫn có thể gây méo tiếng (glitch).** Giả sử trong 100 hop dài 10 ms, có 99 hop hoàn thành trong 3 ms nhưng 1 hop mất 15 ms. Thời gian xử lý trung bình là \((99\times 3+15)/100=3.12\,\mathrm{ms}\), tương ứng RTF trung bình \(0.312\). Tuy vậy, riêng hop bị chậm có RTF bằng \(1.5\) và sẽ trượt hạn callback. Do đó, đánh giá hiệu năng bắt buộc phải đo kèm các phân vị đuôi như p95 hoặc p99; nếu chỉ nhìn giá trị trung bình, hiện tượng underrun sẽ bị che khuất.

**Quantum không đồng nhất với hop.** Một quantum 128 mẫu ở 48 kHz kéo dài \(128/48000\approx 2.67\,\mathrm{ms}\), trong khi hop 480 mẫu tương đương \(480/128=3.75\) quantum. Vì vậy, bộ xử lý phải gom các quantum lẻ vào bộ đệm vòng (ring buffer). DeepFilterNet3 (arXiv:2305.08227) được thiết kế cho chế độ thời gian thực trong họ mô hình này; một checkpoint ngoại tuyến có độ trễ nhìn trước vài trăm ms sẽ không tự động trở thành nhân quả chỉ nhờ được bọc bên trong `DeepFilterNoiseFilterProcessor`.

### Nhân quả và ngoại tuyến

DeepFilterNet2 và DeepFilterNet3 nhấn mạnh thiết kế **thời gian thực / nhân quả** — đây là lý do khóa học chọn họ mô hình này làm trọng tâm thay vì các mô hình khuếch tán (diffusion) ngoại tuyến.

### Khung, hop và độ trễ

$$
T_{\mathrm{hop}}=\frac{R}{f_s},\qquad T_{\mathrm{win}}=\frac{L}{f_s}
$$

Giảm độ dài cửa sổ \(L\) giúp hạ độ trễ nhưng đánh đổi bằng độ phân giải tần số — nội dung này sẽ được phân tích kỹ ở Chương 02.

### Trạng thái streaming

Một hệ thống streaming phải duy trì liên tục các trạng thái như bộ đệm OLA, bộ ước lượng nhiễu/VAD và trạng thái ẩn hồi tiếp của mạng nơ-ron. Khởi tạo lại từ đầu (cold-start) ở mỗi callback sẽ gây tiếng lách tách (click), còn thay đổi tần số lấy mẫu mà không đặt lại trạng thái sẽ khiến âm thanh bị đục và méo.

### Các chế độ lỗi thường gặp

Các lỗi điển hình bao gồm: hụt đệm/vỡ tiếng (underrun/glitch); tiếng nói bị cắt cụt hoặc méo "ướt"; trôi con trỏ bộ đệm vòng (ring buffer drift); nhiễu đuôi (tail artifacts); và sụt giảm hiệu năng đột ngột do quá nhiệt (thermal throttling).

## Ví dụ — mô hình này có triển khai được không?

Xét một mô hình ngoại tuyến có độ trễ nhìn trước 300 ms, đạt RTF 0.15 trên GPU nhưng RTF 1.2 trên CPU laptop ở 48 kHz mono. Nếu ngân sách cuộc gọi yêu cầu độ trễ nhìn trước \(\le 40\,\mathrm{ms}\), mô hình này **không đạt**. Với RTF 1.2 trên CPU đích, mô hình cũng **không đạt** trừ khi giảm tần số lấy mẫu, lượng tử hóa hoặc thu gọn kiến trúc.

## Bẫy thường gặp

1. Trích dẫn số liệu RTF từ bài báo vốn được đo ở chế độ ngoại tuyến với kích thước batch lớn.
2. Bỏ qua độ trễ đuôi (p95/p99).
3. Dùng checkpoint không nhân quả "tạm cho bản demo".
4. Đo độ trễ bằng `Date.now()` xuyên qua nhiều tầng đệm ẩn mà không tách rõ từng công đoạn.
5. Nhầm lẫn quantum của AudioWorklet (ví dụ 128 mẫu ≈ 2.67 ms ở 48 kHz) với bước nhảy hop của STFT.

## Mini-lab

**Mục tiêu.** In ngân sách xử lý cho hop 10 ms ở 48 kHz, đồng thời minh họa tình huống một hop tăng đột biến khiến callback trượt hạn dù RTF trung bình vẫn trông rất an toàn.

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

**Kết quả kỳ vọng.** `t_audio_ms=10.0 t_proc_max_ms=5.0`, `mean_ms=3.12 mean_rtf=0.312`, `spike_rtf=1.50`, `quantum_ms=2.67 quanta_per_hop=3.75`.

**Lỗi thường gặp.** Chỉ lấy RTF trung bình mà bỏ qua các điểm tăng đột biến (spike); đồng nhất 128 mẫu với hop 10 ms; hoặc tính ngược công thức RTF khiến máy chậm lại cho ra con số nhỏ hơn.

## Bài tập nhỏ

1. Với hop 256 mẫu ở tần số 16 kHz, hãy tính độ dài hop (ms) và thời gian xử lý tối đa \(T_{\mathrm{proc}}\) để đạt RTF 0.25.
2. Liệt kê ba bộ đệm trạng thái mà một hệ thống STFT-NS phải duy trì xuyên suốt giữa các hop.
3. Vì sao một mô hình có RTF trung bình 0.4 vẫn có thể gây vỡ tiếng trên Chrome khi hệ thống chịu tải cao?
4. Đề xuất danh mục kiểm tra go/no-go gồm 5 phép đo trước khi bật mặc định tính năng khử nhiễu.

### Gợi ý đáp án

1. Độ dài hop là \(256/16000=16\,\mathrm{ms}\). Với RTF \(0.25\), thời gian xử lý tối đa cho phép là \(4\,\mathrm{ms}\).
2. Bộ đệm cộng chồng lấp OLA, bộ đệm cửa sổ phân tích và trạng thái ẩn hồi tiếp của mạng nơ-ron (hoặc bộ theo dõi nền nhiễu); ngoài ra cần theo dõi cấu hình tần số lấy mẫu và số kênh.
3. Giá trị trung bình che lấp các khoảng dừng của GC, hiện tượng quá nhiệt hoặc những hop đơn lẻ vượt quá 16 ms — trong khi audio callback chịu ảnh hưởng trực tiếp bởi độ trễ đuôi (p99).
4. Năm phép đo thiết thực: độ trễ nhìn trước nhân quả (ms), phân vị p95 của RTF trên CPU đích, số lần underrun trong cuộc gọi kéo dài 10 phút, quy tắc gộp kênh stereo và một phiên nghe kiểm tra ở đúng tần số lấy mẫu của sản phẩm.

## Đọc thêm

- DeepFilterNet2 (arXiv:2205.05474) và DeepFilterNet3 (arXiv:2305.08227) — các mục về thiết kế thời gian thực / nhân quả. Mã nguồn: https://github.com/Rikorose/DeepFilterNet.
- Tài liệu tổng quan đồ thị xử lý của WebRTC APM.
- Tài liệu MDN về AudioWorklet (ràng buộc thời gian của callback).

## Video tham khảo

- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. **Xem trước.** Quan sát các thông số độ trễ và hệ số thời gian thực đặt cạnh sơ đồ hai tầng; đây chính là phép thử khả năng triển khai mà bài học này định nghĩa.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Phần phân tích đánh đổi giữa độ phức tạp và chất lượng cho thấy điểm số ngoại tuyến không đại diện cho ngân sách streaming.
- [Sonic Boom! Audio Programming on Android and Chrome (Google I/O'19)](https://www.youtube.com/watch?v=EeQr0zfvF04) — Google for Developers, tiếng Anh. Các số đo độ trễ callback minh họa nửa còn lại ở tầng thiết bị: độ trễ nhìn trước của thuật toán và nhịp đồng hồ của audio thread là hai bài toán khác nhau.
