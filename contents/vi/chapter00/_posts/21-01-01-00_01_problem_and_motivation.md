---
layout: post
title: "00-01 Vì sao khử nhiễu thời gian thực quan trọng"
chapter: "00"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter00
lesson_type: required
draft: false
---

Khử nhiễu thời gian thực (real-time noise suppression, NS) là ràng buộc sản phẩm quyết định liệu một cuộc gọi có thể sử dụng ổn định trong văn phòng mở, ngoài đường phố hay bên cạnh bàn phím cơ hay không. Bài học này định khung *bài toán* trước khi đi sâu vào thuật toán: ai quan tâm đến bài toán này, tiêu chí "tốt" được hiểu như thế nào, và khóa học gắn với bề mặt công khai của sản phẩm Mezon ra sao.

![Xử lý offline cả file đặt cạnh đường thoại nhân quả, không nhìn được tương lai]({{ site.imgurl }}/generated/realtime-vs-offline.png)

*Hình. Bộ khử nhiễu thời gian thực chỉ được sử dụng các mẫu tính đến thời điểm hiện tại, cộng thêm một ngân sách nhìn trước (look-ahead) nhỏ; trong khi đó, bộ xử lý ngoại tuyến (offline) có thể quan sát toàn bộ tệp âm thanh.*


Bạn đang họp trực tuyến quan trọng từ một quán cà phê đông đúc: tiếng máy pha espresso rít lên, tiếng gõ bàn phím cơ lách cách ngay sát micro, và tiếng quạt điều hòa ù nền đều đều. Nếu đầu dây bên kia vẫn nghe giọng bạn trong trẻo, tự nhiên mà không bị trễ nửa giây, đó là nhờ một **bộ khử nhiễu thời gian thực (Real-Time Noise Suppression)** đang âm thầm xử lý 48.000 mẫu âm thanh mỗi giây ngay trên thiết bị của bạn — chỉ với vài mili giây ngân sách tính toán cho mỗi khung âm thanh!

---

## Kiến thức cần nhớ: Bài toán Khử nhiễu Thời gian thực đứng trên ba trụ cột nào?

### 1. Xử lý tín hiệu số (DSP) nhân quả
Một hệ thống **nhân quả (causal)** tại thời điểm $$t$$ chỉ được phép nhìn dữ liệu từ quá khứ đến hiện tại ($$x[\tau]$$ với $$\tau \le t$$), cộng thêm tối đa một cửa sổ nhìn trước (look-ahead) rất nhỏ (10–20 ms). Khác với xử lý ngoại tuyến (offline) được đọc trước cả tệp âm thanh, bài toán thời gian thực là cuộc đánh đổi khắt khe giữa chất lượng âm thanh và độ trễ.

### 2. Tâm âm học (Psychoacoustics) và Ba mục tiêu đánh giá
Một bộ lọc xóa sạch nhiễu nhưng làm giọng người méo mó như robot là một bộ lọc thất bại. Ngành xử lý tiếng nói tách rạch ròi ba tiêu chí: **Độ rõ (Intelligibility — đo bằng STOI)** để nghe ra từng âm tiết, **Chất lượng cảm thụ (Perceptual Quality — đo bằng PESQ / DNSMOS)** để nghe tự nhiên dễ chịu, và **Độ thân thiện với ASR (WER)** để máy nhận dạng giọng nói không bị nhầm từ.

### 3. Kỹ thuật hệ thống thời gian thực và Hệ số RTF
Trong sản phẩm thật (như WebRTC hay gói `deepfilternet3-noise-filter` của Mezon), một mô hình dù đạt điểm chuẩn cao đến đâu cũng vô dụng nếu **Hệ số thời gian thực (Real-Time Factor — RTF)** vượt ngưỡng: $$\text{RTF} = \frac{T_{\text{xử lý}}}{T_{\text{khung}}} < 1$$ (trong thực tế thường đòi hỏi $$\text{RTF} \le 0.25$$ để chừa CPU cho video, mạng và hệ điều hành).

---

### Giải thích: tự tay tính ngân sách độ trễ và RTF cho một khung thoại 10 ms

Giả sử bạn triển khai bộ khử nhiễu ở tần số lấy mẫu chuẩn băng rộng đầy đủ $$f_s = 48\,000\text{ Hz}$$ với bước nhảy (hop) $$H = 480\text{ mẫu}$$:

1. **Thời lượng một khung âm thanh:**
   $$
   T_{\text{khung}} = \frac{480}{48\,000} = 0.010\text{ giây} = \mathbf{10\text{ ms}}.
   $$
   Nghĩa là cứ đúng mỗi 10 ms, hệ thống âm thanh lại ném vào bộ lọc một gói 480 mẫu mới.
2. **Kiểm tra hệ số thời gian thực (RTF):** Nếu mô hình mạng nơ-ron trên CPU mất $$T_{\text{xử lý}} = 1.8\text{ ms}$$ để lọc xong 1 khung:
   $$
   \text{RTF} = \frac{1.8\text{ ms}}{10\text{ ms}} = \mathbf{0.18} \ll 1 \quad (\text{chạy mượt mà, chiếm } 18\% \text{ một nhân CPU}).
   $$
   Nếu mô hình nặng hơn tốn $$12\text{ ms/khung}$$, $$\text{RTF} = 1.2 > 1$$: hàng đợi âm thanh sẽ ứ đọng dần rồi **rớt gói, rè tiếng** ngay lập tức!
3. **Tính tổng độ trễ thuật toán:** Nếu bộ lọc dùng cửa sổ FFT $$20\text{ ms}$$ (chồng lấp 50%) và nhìn trước 2 khung ($$20\text{ ms}$$), thì độ trễ tối thiểu của riêng khối khử nhiễu là:
   $$
   L_{\text{NS}} = T_{\text{khung}} + T_{\text{look-ahead}} + T_{\text{xử lý}} = 10 + 20 + 1.8 = \mathbf{31.8\text{ ms}},
   $$
   nằm gọn trong ngân sách cuộc gọi hai chiều mượt mà!

---

## Mục tiêu học tập

Sau khoảng 60 phút, bạn cần nắm được các nội dung sau:

1. Giải thích vì sao khử nhiễu (NS) đơn kênh là yêu cầu cốt lõi trong VoIP, họp trực tuyến và các giao diện thoại nhúng.
2. Phân biệt ba mục tiêu tăng cường tiếng nói: **độ rõ (intelligibility)**, **chất lượng cảm thụ (perceptual quality)** và đầu vào **thân thiện với ASR**.
3. Phân biệt khử nhiễu thời gian thực / nhân quả với xử lý ngoại tuyến theo ngôn ngữ sản phẩm (độ trễ và hệ số thời gian thực RTF).
4. Đặt khóa học trong ngữ cảnh công khai của Mezon (`mezonai/mezon-noise-suppression`, gói npm `deepfilternet3-noise-filter`) mà không suy đoán các chi tiết nội bộ chưa công bố.
5. Nêu rõ những phần *không* nằm trong trọng tâm của khóa học (chẳng hạn toàn bộ stack AEC/AGC).

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–8 | Khởi động: phân tích ba bối cảnh thực tế (hệ thống điều hòa văn phòng, đường phố, bàn phím cơ) để thấy yếu tố nào làm hỏng cuộc gọi |
| 8–20 | Mục tiêu sản phẩm: độ rõ, chất lượng cảm thụ và đầu vào ASR; ánh xạ sang các chế độ lỗi tương ứng |
| 20–35 | Ràng buộc thời gian thực: độ trễ khung, RTF; lý giải vì sao các mô hình SOTA ngoại tuyến thường không thể triển khai trực tiếp |
| 35–48 | Ngữ cảnh Mezon và DeepFilterNet (chỉ xét bề mặt công khai) cùng phạm vi khóa học |
| 48–60 | Bài tập nhỏ và thảo luận các bẫy thường gặp |

## Giải thích cốt lõi

### Nhiễu như một ràng buộc sản phẩm

Trong sản phẩm thoại, nhiễu không chỉ là thành phần \(n(t)\) trên giấy mà là **mức cam kết chất lượng (SLA) mà người dùng trực tiếp cảm nhận**:

- **Văn phòng / hệ thống HVAC**: nhiễu gần dừng (quasi-stationary) ở tần số thấp; các bộ ước lượng cổ điển xử lý tương đối tốt, nhưng nếu bỏ qua sẽ gây cảm giác khó chịu kéo dài.
- **Đường phố / quán cà phê**: các đợt nhiễu bùng nổ không dừng; bộ theo dõi nền nhiễu cổ điển thường đáp ứng chậm, nên mô hình mạng nơ-ron (neural) mới thực sự phát huy giá trị.
- **Bàn phím / chuột**: xung băng rộng, xuyên thẳng qua vùng formant của tiếng nói.
- **Babble (nhiều người nói xung quanh)**: trường hợp khó nhất đối với xử lý đơn kênh vì "nhiễu" có cùng cấu trúc thời gian–tần số với tín hiệu đích.

Một khối NS dùng được trong sản phẩm phải giảm được các thành phần nhiễu trên mà không biến giọng nói thành âm thanh bị méo "ướt", không cộng thêm hàng chục mili giây làm gián đoạn nhịp hội thoại, và không tiêu tốn CPU quá mức khiến callback của AudioWorklet bị hụt dữ liệu (underrun).

### Ba mục tiêu tăng cường (không nên đánh đồng)

1. **Độ rõ (intelligibility)** — người nghe (hoặc hệ thống nhận dạng tiếng nói ASR) có nhận diện đúng từng từ hay không. Méo phổ làm cắt mất phụ âm có thể khiến phổ đồ (spectrogram) *trông* sạch hơn nhưng lại làm giảm độ rõ.
2. **Chất lượng cảm thụ** — được đo qua các thang như MOS hoặc DNSMOS: ít tiếng rít, ít nhiễu nhạc (musical noise) và giữ được âm sắc (timbre) tự nhiên.
3. **Đầu vào cho ASR** — một số pipeline tối ưu trực tiếp tỷ lệ lỗi từ (WER); việc khử nhiễu quá mạnh dù dễ nghe với người dùng đôi khi lại *gây hại* cho ASR vì làm mất các đặc trưng mà bộ nhận dạng cần.

Các chỉ số đo lường cổ điển (như SI-SDR) và chỉ số cảm thụ (như DNSMOS) thường không đồng thuận với nhau, do đó đội ngũ sản phẩm cần xác định rõ mục tiêu ưu tiên. Khóa học này tập trung vào **chất lượng hội thoại thời gian thực** theo định hướng Mezon / WebRTC, đồng thời trang bị công cụ đánh giá ở Chương 08.

### Thời gian thực và ngoại tuyến (xem chi tiết ở bài 00-03)

Xử lý ngoại tuyến (offline) có thể sử dụng toàn bộ câu nói, ngữ cảnh hai chiều và các mô hình lớn. Ngược lại, xử lý thời gian thực bắt buộc phải **nhân quả (causal)**: tại thời điểm \(t\), hệ thống chỉ được sử dụng dữ liệu âm thanh tính đến \(t\) (cộng thêm một khoảng nhìn trước look-ahead nhỏ được thiết kế có chủ đích).

Hai đại lượng chính chi phối các buổi đánh giá thiết kế là:

- **Độ trễ thuật toán và bộ đệm (ms)**.
- **Hệ số thời gian thực (Real-Time Factor, RTF)**: tỷ số giữa thời gian xử lý thực tế (wall-clock) và thời lượng đoạn âm thanh. Với luồng thời gian thực (streaming), cần đảm bảo RTF ở trường hợp xấu nhất \(\ll 1\) trên *đúng thiết bị đích*.

### Mô hình hỗn hợp (phương trình nền tảng)

$$
y(t) = x(t) + n(t)
$$

Sau khi áp dụng biến đổi STFT:

$$
Y(\ell,k) = X(\ell,k) + N(\ell,k)
$$

Phần lớn các phương pháp khử nhiễu cổ điển lẫn mạng nơ-ron đều là chiến lược ước lượng \(X\) (hoặc ước lượng mặt nạ / hệ số bộ lọc) từ \(Y\) dưới ràng buộc thời gian thực. Hiện tượng vang phòng (reverb) là một bài toán *liên quan nhưng tách biệt*:

$$
y(t) = (x * h)(t) + n(t)
$$

### Ngữ cảnh sản phẩm Mezon (chỉ dựa trên thông tin công khai)

- Kho mã nguồn GitHub: **`mezonai/mezon-noise-suppression`**
- Gói npm: **`deepfilternet3-noise-filter`**
- Đường dẫn nội bộ trên máy giảng viên (không bắt buộc với học viên): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`

Khóa học này **dạy nguyên lý kỹ thuật**, không dừng lại ở việc "gọi một gói bọc (wrapper) npm". Bài tập tổng kết (Capstone) ở Chương 09 yêu cầu học viên nắm vững toàn bộ pipeline xử lý, không phải dịch ngược (reverse-engineer) các phần nội bộ chưa công bố.

### Phạm vi khóa học

| Trong phạm vi | Ngoài trọng tâm |
|---------------|-----------------|
| Định khung, STFT, khử nhiễu cổ điển, DeepFilterNet, RTF, ORT/WASM, tích hợp WebRTC/LiveKit, chỉ số đánh giá | Thiết kế AEC đầy đủ, beamforming phần cứng, các chi tiết nội bộ chưa công bố của Mezon |
| AEC/AGC/WebRTC APM ở mức *ngữ cảnh* (Chương 03) | Thay thế toàn bộ WebRTC APM |

## Ví dụ có số — phác thảo ngân sách độ trễ

Giả sử một sản phẩm họp trực tuyến yêu cầu độ trễ đệm thuật toán \(\le 40\,\mathrm{ms}\) tính từ callback micro cho đến khi có dữ liệu PCM sạch đưa vào bộ mã hóa (encoder).

Xét cấu hình \(f_s = 48\,\mathrm{kHz}\), cửa sổ \(L = 480\) mẫu (10 ms), bước nhảy hop \(R = 240\) mẫu (5 ms), và mô hình cần thêm một khung nhìn trước (look-ahead).

Tại tần số lấy mẫu 48 kHz, mỗi 1 ms tương ứng 48 mẫu, do đó ngân sách 40 ms tương đương \(40\times 48=1920\) mẫu. Riêng việc chờ gom đủ cửa sổ 480 mẫu đã chiếm 10 ms; cộng thêm một hop nhìn trước 5 ms, phần còn lại của phác thảo này chỉ còn 25 ms. Xét một tình huống khác: nếu thời gian suy luận (forward) mất 8 ms trên một hop dài 20 ms thì RTF bằng \(8/20=0.40\). Nếu cùng khối xử lý đó mất 22 ms thì RTF tăng lên \(1.1\), dẫn đến underrun, trừ khi ta kéo dài hop hoặc thu gọn mô hình. Phần Mini-lab dưới đây kiểm tra lại nhóm tham số đầu tiên.

## Bẫy thường gặp

1. Tối ưu SI-SDR ngoại tuyến rồi đưa cùng checkpoint đó vào luồng thời gian thực mà không đo độ trễ nhân quả và RTF trên thiết bị đích.
2. Sử dụng "% giảm nhiễu" làm chỉ số kiểm thử (QA) dù khái niệm này không được định nghĩa chặt chẽ.
3. Giả định bộ khử nhiễu đơn kênh (mono) có thể chạy trực tiếp trên tín hiệu stereo mà không có chính sách gộp kênh (downmix).
4. Đổ lỗi cho mô hình mạng nơ-ron trong khi lỗi thực sự nằm ở lệch tần số lấy mẫu (sample rate), sai kích thước hop hoặc lệch cửa sổ cộng chồng lấp (OLA).
5. Suy diễn "bí mật nội bộ của Mezon" từ nội dung khóa học — cần bám sát thông tin công khai và các bài báo khoa học về DeepFilterNet.

## Mini-lab

**Mục tiêu.** Tính lại phác thảo ngân sách ở 48 kHz bằng mã lệnh để tác động của việc đổi hop được thể hiện minh bạch thay vì ẩn trong bảng tính.

```python
fs, hop, window, budget_ms = 48_000, 240, 480, 40.0
hop_ms = 1_000 * hop / fs
window_ms = 1_000 * window / fs
print(f"hop_ms={hop_ms:.1f} window_ms={window_ms:.1f}")
print(f"samples_per_ms={fs/1000:.0f} budget_samples={budget_ms*fs/1000:.0f}")
print(f"remaining_ms={budget_ms - window_ms - hop_ms:.1f} rtf={8/20:.2f}")
```

**Kết quả kỳ vọng.** `hop_ms=5.0 window_ms=10.0`, tiếp theo là `samples_per_ms=48 budget_samples=1920`, và cuối cùng `remaining_ms=25.0 rtf=0.40`.

**Lỗi thường gặp.** Đảo nhầm giữa kích thước hop và độ dài cửa sổ, đếm số mẫu theo 16 kHz trong ngân sách 48 kHz, hoặc định nghĩa ngược RTF (lấy thời lượng âm thanh chia cho thời gian xử lý).

## Bài tập nhỏ

1. Chọn một đoạn bối cảnh dài 10 giây (ví dụ quán cà phê), liệt kê ba sự kiện nhiễu và phân loại chúng theo nhóm dừng / không dừng / giống tiếng nói.
2. Viết mỗi câu một mục tiêu tương ứng với độ rõ, chất lượng cảm thụ và đầu vào ASR cho phần mềm tổng đài chăm sóc khách hàng (softphone).
3. Với \(f_s=16\,\mathrm{kHz}\) và bước nhảy hop \(R=160\), hãy tính độ dài hop (ms) và thời gian xử lý trung bình tối đa để đạt RTF \(=0.5\).
4. Đọc tệp README công khai của `mezonai/mezon-noise-suppression` (khi trực tuyến) và liệt kê ba tính năng *đã được tài liệu hóa*, không suy diễn thêm.

### Gợi ý đáp án

1. Tiếng hệ thống HVAC biến đổi chậm (nhiễu dừng); tiếng đóng cửa thay đổi đột ngột (không dừng); người nói chuyện gần micro là nhiễu babble, có đặc trưng tương đồng với tiếng nói.
2. Độ rõ hướng tới việc nhận diện đúng từng từ; chất lượng cảm thụ hướng tới trải nghiệm nghe dễ chịu; đầu vào ASR hướng tới giảm tỷ lệ lỗi từ — mục tiêu thứ ba đôi khi xung đột với hai mục tiêu đầu.
3. Độ dài hop là \(160/16000=10\,\mathrm{ms}\). Với RTF \(=0.5\), thời gian xử lý trung bình tối đa cho mỗi hop là \(5\,\mathrm{ms}\).
4. Chỉ trích dẫn các gạch đầu dòng có trong README (tên gói, runtime, tần số lấy mẫu), không suy đoán cấu trúc đồ thị mô hình chưa công bố.

## Đọc thêm

- Tài liệu WebRTC Audio Processing Module (APM) — mục noise suppression.
- Schröter và cộng sự, DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — phần mở đầu giải thích vì sao khử nhiễu nhân quả là một bài toán sản phẩm. Kho mã nguồn: https://github.com/Rikorose/DeepFilterNet.
- Trang tổng quan DNS Challenge (bộ dữ liệu và các hạng mục đánh giá).

## Video tham khảo

- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. **Xem trước.** Video trình bày cách một sản phẩm gọi thoại nhìn nhận nhiễu nền từ phản hồi người dùng trước khi lựa chọn bộ lọc, đúng với khung bài toán của bài học này.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Tác giả giới thiệu bộ khử nhiễu toàn băng (full-band) nhân quả với độ trễ vài mili giây, minh họa trực tiếp ràng buộc thời gian thực đối lập với khử nhiễu ngoại tuyến.
- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, tiếng Anh. Đoạn nghe thử trước và sau xử lý giúp bạn hình dung trực quan hiệu quả trên nhiễu văn phòng và nhiễu không dừng thay vì chỉ nhìn bảng chỉ số.
