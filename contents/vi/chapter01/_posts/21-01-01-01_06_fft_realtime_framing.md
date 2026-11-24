---
layout: post
title: "01-06 FFT trong audio khung thời gian thực"
chapter: "01"
order: 6
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Giáo trình FFT thường dừng lại ở phân tích độ phức tạp, còn kỹ thuật sản phẩm bắt đầu từ audio callback. Bài học này đặt FFT vào trong vòng lặp STFT streaming: số hop mỗi giây, độ trễ thuật toán, tái sử dụng bộ đệm và tình huống thực tế theo hướng DeepFilterNet.

![Các khung phân tích chồng nhau, mỗi khung một FFT có cửa sổ, cộng lại phía tổng hợp]({{ site.imgurl }}/generated/stft-ola.png)

*Hình. FFT thời gian thực vận hành theo nhịp đồng hồ: nhận một hop mới, tính biến đổi trên khung đã áp cửa sổ, rồi tổng hợp ra ngoài bằng overlap-add. Hệ cơ sở vẫn là DFT, còn lịch trình là bước nhảy hop.*


Thuật toán FFT trong sách giáo khoa luôn giả định bạn có sẵn cả một mảng tín hiệu đứng yên trên bàn. Nhưng tiếng nói của con người không bao giờ đứng yên: chỉ trong 100 mili giây, miệng bạn đã kịp chuyển từ phụ âm xát cao tần /s/ sang nguyên âm trầm ấm /a/. Muốn đưa FFT vào cuộc gọi thoại thời gian thực, kỹ sư phải **cắt dòng âm thanh liên tục thành từng lát khung (frame)** gối đầu lên nhau — đủ ngắn để giọng nói coi như "gần dừng" (quasi-stationary) bên trong mỗi lát, nhưng đủ dài để phân tách được các vạch tần số!

---

## Bản đồ kiến thức nền: Chia khung FFT Thời gian thực đứng trên ba trụ cột nào?

### 1. Giả thiết Gần dừng (Quasi-Stationarity) của Tiếng nói
Dây thanh và khoang miệng con người chuyển động theo quán tính cơ học, nên đặc tính phổ của tiếng nói thay đổi chậm trong cửa sổ **10–30 ms**. Đó là lý do hầu hết hệ thống xử lý thoại (WebRTC, Opus, DeepFilterNet) đều chọn độ dài khung chuẩn quanh mốc **20 ms** và bước nhảy (hop) **10 ms**.

### 2. Đánh đổi Độ phân giải Thời gian – Tần số ($$\Delta f = f_s / N$$)
Chọn kích thước FFT $$N$$ quyết định trực tiếp khoảng cách giữa hai bin tần số liền kề: $$\Delta f = \frac{f_s}{N}$$. Khung càng dài thì $$\Delta f$$ càng mịn (nhìn rõ hài âm), nhưng độ trễ càng lớn và các tiếng nổ ngắn (như gõ bàn phím) càng bị nhòe theo thời gian.

### 3. Tính tương thích phần cứng và Mixed-Radix FFT
Ở tốc độ chuẩn 48 kHz, khung 20 ms tương ứng đúng $$N = 960\text{ mẫu}$$ — không phải lũy thừa của 2! Thay vì ép đệm 0 lên $$1\,024$$ (làm lệch lưới tần số), các thư viện hiện đại (RustFFT, PocketFFT) phân tích thừa số $$960 = 2^6 \cdot 3 \cdot 5$$ để chạy **mixed-radix FFT** gần nhanh ngang radix-2 thuần!

---

### Khung giải thích: tự tay kiểm tra bộ thông số khung thực chiến của DeepFilterNet (nên đọc chậm)

Hãy kiểm chứng trọn bộ thông số cốt lõi của hệ thống khử nhiễu 48 kHz bằng những phép chia sơ cấp:

1. **Độ dài khung & Bước nhảy:** Với $$f_s = 48\,000\text{ Hz}$$, chọn khung $$N = 960\text{ mẫu}$$ và bước nhảy $$H = 480\text{ mẫu}$$:
   - Thời lượng khung: $$T_{\text{frame}} = \frac{960}{48\,000} = \mathbf{20\text{ ms}}$$.
   - Bước nhảy (tốc độ cập nhật): $$T_{\text{hop}} = \frac{480}{48\,000} = \mathbf{10\text{ ms}}$$ (chồng lấp $$50\%$$, tức $$100\text{ khung/giây}$$).
2. **Lưới tần số `rfft`:** Vì tín hiệu micro là số thực, số bin phổ độc lập chỉ là:
   $$
   K = \frac{N}{2} + 1 = \frac{960}{2} + 1 = \mathbf{481\text{ bin}} \quad (k = 0, 1, \dots, 480).
   $$
   Khoảng cách mỗi bin đúng tròn trịa: $$\Delta f = \frac{48\,000}{960} = \mathbf{50\text{ Hz/bin}}$$!
3. **Tra cứu nhanh tần số của bất kỳ bin nào:**
   - Bin $$k = 0 \to 0\text{ Hz}$$ (DC); Bin $$k = 1 \to 50\text{ Hz}$$ (đúng tần số ù điện lưới 50 Hz!).
   - Bin $$k = 20 \to 20 \times 50 = \mathbf{1\,000\text{ Hz}}$$; Bin $$k = 480 \to \mathbf{24\,000\text{ Hz}}$$ (tần số Nyquist).
   - Lưu lượng dữ liệu phổ cần xử lý: $$100\text{ khung/giây} \times 481\text{ bin} = 48\,100$$ số phức/giây — cực gọn cho mạng nơ-ron chạy thời gian thực!

---

## Mục tiêu học tập

1. Lập ngân sách chi phí FFT trong phạm vi một callback hoặc quantum của AudioWorklet.
2. Liên hệ giữa bước nhảy hop, kích thước FFT \(N\) điểm và độ trễ thuật toán.
3. Tính toán số lượng phép FFT mỗi giây cho các cấu hình thoại phổ biến.
4. Nhận diện tình huống chi phí FFT chiếm tỷ trọng lớn trong RTF so với mạng nơ-ron.
5. Nắm các nguyên tắc đảm bảo ổn định cho luồng streaming: cấp phát sẵn bộ đệm, tái sử dụng FFT plan và duy trì liên tục trạng thái OLA.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Nhìn STFT streaming như một chuỗi các phép FFT có cửa sổ |
| 10–25 | Các con số cốt lõi: số hop/giây, số FFT/giây và công thức độ trễ |
| 25–40 | Ràng buộc trên audio thread, bộ đệm vòng (ring buffer) và bất đẳng thức tránh underrun |
| 40–52 | Nghiên cứu tình huống: cấu hình STFT của DeepFilterNet (theo bài báo công khai) |
| 52–60 | Bài tập nhỏ |

## Giải thích cốt lõi

Ở mỗi bước nhảy hop, pipeline thực hiện tuần tự: gom đủ \(L\) mẫu → nhân hàm cửa sổ → tính FFT → xử lý tăng cường tiếng nói → tính iFFT → cộng chồng lấp (OLA). Các trạng thái bắt buộc phải duy trì qua từng hop gồm bộ đệm OLA, trạng thái ẩn của RNN/DF và bộ theo dõi nền nhiễu.

$$
T_{\mathrm{hop}}=\frac{R}{f_s},\qquad \mathrm{FFTs/s}\approx 2\cdot\frac{f_s}{R}
$$

(tính trên mỗi kênh). Trên trình duyệt, một quantum AudioWorklet thường dài 128 mẫu (khoảng 2.67 ms ở 48 kHz) — **không** trùng với hop STFT 5–10 ms, do đó hệ thống bắt buộc phải có bộ đệm vòng (ring buffer).

**Phân tích đầy đủ một cấu hình mẫu.** Xét cấu hình \(f_s=48\,\mathrm{kHz}\) (tần số toàn băng mặc định của `deepfilternet3-noise-filter` 1.3.0), \(L=960\) và \(R=480\). Đây là cặp tham số minh họa cho bài học, không khẳng định đồ thị nội bộ chưa công bố của Mezon sử dụng chính xác cặp giá trị này.

$$
T_{\mathrm{hop}}=\frac{480}{48000}=10\,\mathrm{ms},\qquad
\frac{f_s}{R}=100\ \mathrm{hop/s},\qquad
T_{\mathrm{win}}=\frac{960}{48000}=20\,\mathrm{ms}.
$$

Tỷ lệ chồng lấp là \((L-R)/L=1/2\). Do hệ thống nhân quả chưa thể thực hiện phép FFT phân tích đầu tiên cho đến khi gom đủ 960 mẫu, độ trễ đệm trước phép biến đổi đầu tiên là 20 ms — đây là độ trễ thuật toán của *việc lấp đầy cửa sổ phân tích*. Việc xuất mẫu sớm hơn hoặc giữ thêm một hop nhìn trước (look-ahead) sẽ làm thay đổi hằng số độ trễ này nhưng không làm thay đổi tốc độ hop. Với hai phép biến đổi ở mỗi hop (thuận và nghịch), hệ thống thực hiện \(200\) phép FFT mỗi giây cho mỗi kênh, trong ngân sách thời gian thực tế (wall-clock) là 10 ms cho mỗi hop. Một quantum AudioWorklet 128 mẫu ở 48 kHz chỉ bằng \(128/480=0.267\) hop, nên cần \(480/128=3.75\) quantum để tích lũy đủ một hop \(R\) và \(960/128=7.5\) quantum để lấp đầy một cửa sổ \(L\). `DeepFilterNet3Core` cần được cấp dữ liệu đúng theo bước nhảy hop ghi trên model card; phép đếm trên giúp đối chiếu giữa thông số mô hình và nhịp callback thực tế.

Để tránh vỡ tiếng, hệ thống phải duy trì \(T_{\mathrm{proc}}(\ell)<T_{\mathrm{hop}}\) gần như ở mọi khung, có chừa biên độ cho dao động (jitter). Các bài báo thuộc họ DeepFilterNet mô tả phần tiền xử lý STFT, đặc trưng thang ERB và kỹ thuật deep filtering trên phổ phức hướng tới chạy thời gian thực. Khi đọc tài liệu ở Chương 04, hãy trích xuất các thông số \(f_s\), kích thước cửa sổ/FFT, hop và tuyên bố về tính nhân quả rồi đối chiếu trực tiếp với các công thức trên trước khi tích hợp `deepfilternet3-noise-filter`, tránh tự suy đoán các hằng số STFT chưa được công bố của Mezon.

## Ví dụ có số

Ở tần số 48 kHz với \(R=480\) (10 ms), tốc độ xử lý là 100 hop/giây, tương đương khoảng 200 lượt biến đổi/giây/kênh. Với kích thước quantum 128 mẫu ở 48 kHz, cần khoảng 3.75 quantum để gom đủ một hop 10 ms, do đó bắt buộc phải dùng bộ đệm tích lũy.

## Bẫy thường gặp

1. Đánh đồng quantum của AudioWorklet với bước nhảy hop của mô hình.
2. Chỉ đo độ trễ trên luồng chính (main thread).
3. Đặt lại trạng thái OLA sau mỗi lần gọi callback.
4. Chạy FFT cho cả hai kênh stereo trong khi mô hình chỉ nhận đầu vào mono.
5. Quên cộng chi phí iFFT và OLA vào ngân sách thời gian của hop.

## Mini-lab

**Mục tiêu.** Tính số hop mỗi giây và độ trễ lấp đầy cửa sổ phân tích cho cấu hình \(L=960\), \(R=480\) ở 48 kHz.

```python
fs, L, R = 48_000, 960, 480
hop_ms = 1_000 * R / fs
win_ms = 1_000 * L / fs
hops_per_s = fs / R
ffts_per_s = 2 * hops_per_s
print(f"hops_per_s={hops_per_s:.0f} hop_ms={hop_ms:.1f} win_ms={win_ms:.1f}")
print(f"ffts_per_s={ffts_per_s:.0f} algo_delay_ms={win_ms:.1f}")
```

**Kết quả kỳ vọng.** `hops_per_s=100 hop_ms=10.0 win_ms=20.0`, tiếp theo là `ffts_per_s=200 algo_delay_ms=20.0`. Giá trị độ trễ in ra là thời gian gom đủ một cửa sổ phân tích, không phải tổng độ trễ đầu–cuối của toàn bộ sản phẩm.

**Lỗi thường gặp.** Gán độ trễ thuật toán bằng đúng bước nhảy hop (10 ms) mà quên thời gian lấp đầy cửa sổ; chỉ đếm một phép FFT mỗi hop trong khi phép biến đổi nghịch cũng tiêu tốn thời gian; hoặc áp máy móc cặp \(L, R\) này lên một model card đang quy định cấu hình khác.

## Bài tập nhỏ

1. Với \(f_s=16\,\mathrm{kHz}\) và \(R=256\), hãy tính độ dài hop (ms) và số hop mỗi giây.
2. Tính ngân sách thời gian xử lý \(T_{\mathrm{proc}}\) để đạt RTF 0.4 với cấu hình hop ở câu 1.
3. Với quantum 128 mẫu ở 48 kHz, cần bao nhiêu quantum để gom đủ một hop 10 ms?
4. Liệt kê các trạng thái cần được bảo toàn giữa các hop liên tiếp.
5. Phác thảo kế hoạch đo hiệu năng (profiling) tách riêng ba công đoạn: STFT, suy luận neural và ISTFT.

### Gợi ý đáp án

1. Độ dài hop là \(256/16000=16\,\mathrm{ms}\), tương ứng \(1000/16=62.5\) hop/giây.
2. Với RTF 0.4 trên hop 16 ms, thời gian xử lý tối đa là \(6.4\,\mathrm{ms}\).
3. Một hop 10 ms ở 48 kHz gồm 480 mẫu, tương ứng \(480/128=3.75\) quantum. Sau khi gom 4 quantum sẽ dư ra 0.25 quantum (32 mẫu) cần được giữ lại trong bộ đệm vòng cho hop tiếp theo.
4. Phần đuôi bộ đệm OLA, cửa sổ phân tích, bộ đếm hop và các trạng thái ẩn hồi tiếp bên trong bộ khử nhiễu.
5. Đặt ba bộ đo thời gian tách biệt cho FFT phân tích, lượt suy luận mạng nơ-ron và iFFT + OLA, sau đó báo cáo phân vị p95 trên ít nhất vài nghìn hop.

## Đọc thêm

- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — các mục về cấu hình STFT và vận hành thời gian thực. Kho mã tham chiếu: https://github.com/Rikorose/DeepFilterNet.
- Tài liệu MDN về `AudioWorkletProcessor`.
- Tổng quan WebRTC APM (cơ chế xử lý theo khối khung).

## Video tham khảo

- [Short-Time Fourier Transform Explained Easily](https://www.youtube.com/watch?v=-Yxj3yfvY-4) — Valerio Velardo - The Sound of AI, tiếng Anh. **Xem trước.** Trình bày bước chuyển từ một phép DFT cho toàn tệp sang tính DFT trên từng khung — đúng vị trí mà callback thời gian thực gọi FFT.
- [Short-time Fourier Transform and the Spectogram](https://www.youtube.com/watch?v=NA0TwPsECUQ) — Barry Van Veen, tiếng Anh. Bài giảng xử lý tín hiệu về STFT và phổ đồ tạo thành, giúp hình dung chuỗi FFT theo từng khung đặt trên nhịp thời gian thực.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Quan sát khối STFT ở đầu bộ khử nhiễu nhân quả: ở đây FFT là một phần ngân sách của hop chứ không chỉ là một công thức độ phức tạp trong sách giáo khoa.
