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

Mỗi lựa chọn về STFT và kiến trúc mô hình đều là một sự đánh đổi giữa độ trễ, tải CPU và chất lượng âm thanh. Nguyên tắc cốt lõi để tránh quyết định triển khai sai lầm là: **độ trễ thuật toán cho biết âm thanh bị trễ bao lâu, còn hệ số thời gian thực (RTF) cho biết CPU có xử lý kịp hay không.** Một mô hình chạy rất nhanh vẫn có thể gây độ trễ quá lớn cho cuộc gọi.


Trong phòng thí nghiệm, bạn có thể đẩy kích thước cửa sổ lên 64 ms và cho mạng nơ-ron nhìn trước nửa giây để ghi điểm PESQ cao chót vót trên bảng xếp hạng. Nhưng khi đưa lên cuộc gọi thoại thật, kỹ sư hệ thống phải đối mặt với **tam giác đánh đổi nghiệt ngã** của mọi pipeline âm thanh thời gian thực: **Độ trễ (Latency) – Chất lượng phổ (Quality) – Chi phí tính toán (CPU/RTF)**. Bài học tổng kết Chương 2 này giúp bạn nhìn toàn bộ pipeline STFT → Xử lý → ISTFT như một bài toán tối ưu kỹ thuật có thể đo đạc bằng con số!

---

## Kiến thức cần nhớ: Đánh đổi Độ trễ – Chất lượng – CPU trong Pipeline đứng trên ba trụ cột nào?

### 1. Giải phẫu tổng độ trễ (Algorithmic + Buffering + Compute Latency)
Độ trễ một chiều của pipeline không chỉ là thời gian chạy mô hình! Nó gồm 4 phần cộng dồn: (1) **Độ trễ khung STFT/OLA** (thường bằng $$N$$ hoặc $$H$$ tùy cách căn đệm), (2) **Độ trễ nhìn trước (Look-ahead)** nếu dùng tích chập tương lai $$L_{\text{la}}$$ khung, (3) **Độ trễ đệm đồng bộ kích thước khối** (ví dụ nối 128 mẫu AudioWorklet với 480 mẫu hop), và (4) **Thời gian tính toán CPU** $$T_{\text{compute}}$$.

### 2. Tỉ lệ thuận nghịch giữa Bước nhảy $$H$$ và Tải CPU
Giảm bước nhảy $$H$$ đi một nửa (ví dụ từ 10 ms xuống 5 ms, tăng chồng lấp từ 50% lên 75%) giúp giảm độ trễ phản hồi và làm mượt chuyển tiếp âm thanh, nhưng lập tức **nhân đôi số khung mỗi giây** (từ 100 lên 200 khung/giây) — kéo theo tải CPU của cả FFT lẫn mạng nơ-ron tăng đúng **gấp 2 lần**!

### 3. Thiết kế điểm ngọt thực chiến (Sweet Spot)
Các hệ thống thoại thương mại (WebRTC APM, RNNoise, DeepFilterNet3) hội tụ về một vùng thiết kế rất hẹp: **hop 10 ms, cửa sổ 20 ms, look-ahead 0–20 ms** (tổng độ trễ thuật toán 20–40 ms) và **RTF < 0.25** trên một nhân CPU tầm trung.

---

### Giải thích: tự tay so sánh hai cấu hình Pipeline STFT ở 48 kHz

Giả sử bạn đang chọn cấu hình STFT cho một mô hình khử nhiễu tốn cố định $$T_{\text{model}} = 2.0\text{ ms}$$ cho mỗi lần suy luận khung ở $$f_s = 48\,000\text{ Hz}$$:

1. **Cấu hình A (Ưu tiên độ trễ cực thấp):** $$N = 480\text{ (10 ms)},\ H = 240\text{ (5 ms)},\ \text{look-ahead} = 0$$.
   - Độ phân giải tần số: $$\Delta f = \frac{48\,000}{480} = \mathbf{100\text{ Hz/bin}}$$ (khá thô, khó tách hài âm giọng nam 100–130 Hz).
   - Số khung/giây: $$200\text{ khung/s}$$; hệ số thời gian thực: $$\text{RTF}_A = \frac{2.0\text{ ms}}{5.0\text{ ms}} = \mathbf{0.40}$$ (ngốn 40% nhân CPU!).
   - Độ trễ thuật toán: $$10 + 2.0 = \mathbf{12\text{ ms}}$$.
2. **Cấu hình B (Điểm ngọt kiểu DeepFilterNet):** $$N = 960\text{ (20 ms)},\ H = 480\text{ (10 ms)},\ \text{look-ahead} = 2\text{ khung (20 ms)}$$.
   - Độ phân giải tần số: $$\Delta f = \frac{48\,000}{960} = \mathbf{50\text{ Hz/bin}}$$ (mịn gấp đôi, tách sạch hài âm giọng nói!).
   - Số khung/giây: $$100\text{ khung/s}$$; hệ số thời gian thực: $$\text{RTF}_B = \frac{2.0\text{ ms}}{10.0\text{ ms}} = \mathbf{0.20}$$ (giảm **50% tải CPU** so với Cấu hình A!).
   - Độ trễ thuật toán: $$20 + 20 + 2.0 = \mathbf{42\text{ ms}}$$ (vẫn nằm thoải mái trong ngân sách 150 ms của VoIP).

Nhìn hai con số đặt cạnh nhau, bạn thấy ngay vì sao Cấu hình B là chuẩn vàng của công nghiệp thoại hiện đại!

---

## Mục tiêu học tập

1. Liệt kê các công đoạn trong pipeline đóng góp vào độ trễ và tải CPU.
2. Định lượng sự đánh đổi giữa kích thước cửa sổ, hop, kích thước FFT với chất lượng và độ trễ.
3. Giải thích các chế độ suy giảm chất lượng khi tối ưu độ trễ quá mức.
4. Lập bảng tiêu chí đạt/không đạt (scorecard) cho một cấu hình trước khi triển khai.
5. Liên hệ các sự đánh đổi này với mục tiêu thiết kế thời gian thực của DeepFilterNet.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Sơ đồ pipeline đầu–cuối (micro → NS → bộ mã hóa) |
| 10–28 | Phân tích định lượng qua các kịch bản cấu hình có số liệu |
| 28–42 | Các chế độ hỏng về chất lượng và độ trễ |
| 42–52 | Xây dựng bảng tiêu chí triển khai cho pipeline kiểu Mezon |
| 52–60 | Bài tập nhỏ |

![Các quantum AudioWorklet trên trục thời gian; process() đôi khi vượt một quantum: RTF là thời gian tường trên thời lượng audio, khác với độ trễ thuật toán của cửa sổ STFT]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Hình. Mỗi vạch đại diện cho một quantum render; RTF so sánh thời gian thực tế (wall-clock) của `process()` với thời lượng âm thanh tương ứng — đây là đại lượng tách biệt với độ trễ thuật toán của cửa sổ STFT.*

## Giải thích cốt lõi

### Hai đồng hồ độc lập

Độ trễ thuật toán là thuộc tính cố hữu của đồ thị tín hiệu. Với STFT nhân quả như đã xét ở bài 02-02:

$$
D_{\mathrm{alg}}\approx T_L=\frac{L}{f_s},
$$

cộng thêm số khung nhìn trước (look-ahead), trễ của bộ lấy mẫu lại và bộ đệm đóng gói. Ở 48 kHz, cửa sổ \(L=960\) luôn đóng góp khoảng **20 ms** bất kể phép FFT chạy mất 0.2 ms hay 2 ms trên CPU — tín hiệu bị trễ đơn giản vì hệ thống phải chờ thu đủ số mẫu lấp đầy cửa sổ.

Ngược lại, RTF là thuộc tính hiệu năng của bản cài đặt:

$$
\mathrm{RTF}=\frac{T_{\mathrm{wall}}(D)}{D}.
$$

Trong đó \(D\) là thời lượng âm thanh vừa xử lý (một hop hoặc một quantum). Điều kiện \(\mathrm{RTF}<1\) chỉ đảm bảo khối hiện tại xử lý xong trước khi khối tiếp theo đến hạn, chứ không phản ánh lượng look-ahead đã đưa vào thuật toán. Cảnh báo thứ hai từ hình minh họa: ngay cả khi RTF trung bình bằng 0.4, âm thanh vẫn bị lách tách nếu phân vị p99 vượt quá thời lượng hop — do đó luôn phải ghi nhận p95 và p99.

Một quantum 128 mẫu ở 48 kHz kéo dài \(128/48000\approx 2.67\,\mathrm{ms}\). Đây là nhịp lưới của AudioWorklet trong hình, không phải bước nhảy hop của mô hình. Một hop 10 ms trải qua gần bốn quantum; thanh `process()` màu đỏ minh họa quantum nơi phép FFT và mạng nơ-ron bị vượt hạn (overrun). Lưu ý rằng thời gian khởi động lạnh (biên dịch WASM/ONNX) diễn ra trên luồng chính, không tính vào RTF ở trạng thái ổn định.

### Các công đoạn điển hình trong pipeline

1. Thu âm / đệm theo quantum AudioWorklet
2. Lấy mẫu lại (resample) về tần số lấy mẫu của mô hình
3. Gộp kênh (downmix) về mono
4. Cắt khung STFT (áp cửa sổ và hop)
5. Trích xuất đặc trưng (ví dụ thang ERB)
6. Khử nhiễu bằng mạng nơ-ron hoặc thuật toán cổ điển
7. Biến đổi ngược đặc trưng, tính ISTFT và cộng chồng lấp OLA
8. Lấy mẫu lại về tần số của đầu ra (sink)
9. Chuyển sang bộ mã hóa (encoder) WebRTC

Với từng công đoạn, hãy đo tách biệt phần độ trễ trên dạng sóng và phần đóng góp vào RTF. Một bộ lấy mẫu lại có thể tiêu tốn rất ít RTF nhưng vẫn cộng thêm trễ nhóm (group delay); ngược lại, phiên chạy ONNX có thể chiếm RTF lớn mà không cộng thêm look-ahead ngoài phần STFT.

### Các tham số điều chỉnh và hệ quả

| Khi tăng tham số | Độ trễ | Tải CPU | Xu hướng chất lượng |
|------------------|--------|---------|---------------------|
| Độ dài cửa sổ \(L\) | Tăng | Tăng (FFT lớn hơn) | Độ phân giải tần số tốt hơn nhưng nhòe hơn theo thời gian |
| Bước nhảy hop \(R\) | Bản thân hop không quyết định toàn bộ \(D_{\mathrm{alg}}\); giảm \(R\) làm tăng hop/s | Tăng khi giảm \(R\) | Mặt nạ thường mượt hơn khi giảm \(R\) |
| Kích thước mô hình | Gần như không đổi nếu giữ nguyên look-ahead | Tăng | Thường cải thiện cho tới khi RTF vượt ngưỡng |
| Số khung look-ahead | Tăng | Tăng | Chất lượng thường cải thiện |
| Tần số lấy mẫu | Tăng (nếu giữ số mẫu) | Tăng | Mở rộng băng thông nếu mô hình được huấn luyện cho tần số đó |

**Nguyên tắc bắt buộc phải đo đạc.** Giảm \(R\) từ 480 xuống 240 ở 48 kHz làm tăng gấp đôi số hop mỗi giây (từ 100 lên 200) và gần gấp đôi chi phí CPU của STFT, trong khi \(D_{\mathrm{alg}}\) vẫn xấp xỉ \(L/f_s\) nếu không rút ngắn cửa sổ. Ngược lại, rút ngắn cửa sổ lại làm rộng búp chính theo tần số (bài 02-03) — đó là sự đánh đổi chất lượng chứ không phải khoản tối ưu RTF miễn phí.

### Các con số mốc cần ghi nhớ

Ở tần số 48 kHz:

- Quantum 128 mẫu ≈ 2.67 ms
- Hop 480 mẫu = 10 ms → 100 bước xử lý mỗi giây
- Cửa sổ 960 mẫu = thang đệm 20 ms

Ở 16 kHz, cùng *thời lượng mili giây* sẽ chứa ít mẫu hơn (FFT nhẹ hơn) nhưng băng thông hẹp hơn; ngược lại, cùng *số lượng mẫu* lại cho thời lượng khác hẳn (\(L=512\) ở 16 kHz là 32 ms chứ không phải 20 ms). Thời gian xử lý thực tế 3 ms trên hop 10 ms tương ứng \(\mathrm{RTF}=0.3\) (an toàn); thời gian 12 ms trên cùng hop đó cho \(\mathrm{RTF}=1.2\) (vượt hạn), dù 12 ms vẫn nhỏ hơn độ dài cửa sổ 20 ms. Phần Mini-lab tách riêng hai đại lượng này thành hai biến độc lập để tránh nhầm lẫn.

### Các chế độ hỏng thường gặp

- **Ngân sách độ trễ quá chặt:** cửa sổ quá ngắn khiến các họa âm không tách biệt được và mặt nạ trở nên gắt.
- **Độ trễ quá lớn:** cuộc gọi có cảm giác trễ rõ rệt; nếu đặt look-ahead trước bộ khử vọng AEC, đường tiếng vọng sẽ trông như bị trôi.
- **Biên độ dự phòng CPU quá nhỏ:** chỉ cần các khung ở phân vị p99 bị vượt hạn (thanh đỏ) đã đủ gây tiếng nổ lách tách dù RTF trung bình rất thấp.

### Phiếu tiêu chí triển khai (ví dụ minh họa)

| Tiêu chí | Mục tiêu minh họa | Đạt? |
|----------|-------------------|------|
| Độ trễ thuật toán + look-ahead | ≤ ngân sách sản phẩm (khoảng 20–40 ms) | |
| p95 RTF trên thiết bị đích | ≤ 0.5 | |
| Kiểm tra khứ hồi COLA | Sai số dưới ngưỡng cho phép | |
| DNSMOS / kiểm tra nghe | So sánh với baseline NS của WebRTC | |
| Không rung biên độ theo hop | Kiểm tra bằng nghe và phổ đồ | |

Hãy thay các giá trị minh họa bằng cam kết SLA thực tế của sản phẩm, và tuyệt đối không coi việc đạt "RTF ≤ 0.5" là đã thỏa mãn ngân sách độ trễ thuật toán hoặc ngược lại.

### Áp dụng vào cấu hình DeepFilterNet

Cấu hình toàn băng công bố của DeepFilterNet dùng tần số 48 kHz, STFT 960 điểm (20 ms), chồng lấp 50% (hop 10 ms) kèm vài khung look-ahead ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)). Hãy xem đây là các ràng buộc cứng của mô hình; không gian tối ưu nằm ở vị trí đặt trên đồ thị xử lý, khâu lấy mẫu lại và ngân sách phần cứng. Gói `deepfilternet3-noise-filter` 1.3.0 vận hành trên đúng giao ước 48 kHz đó — nếu phân vị p95 của RTF không đạt, không được tự ý thay đổi bước nhảy hop.

## Ví dụ có số

- **Cấu hình A:** 16 kHz, \(L=20\,\mathrm{ms}\), \(R=10\,\mathrm{ms}\), mô hình nhỏ, RTF 0.2, điểm MOS ổn định.
- **Cấu hình B:** 48 kHz, \(L=40\,\mathrm{ms}\), \(R=5\,\mathrm{ms}\), mô hình lớn, RTF 0.9, điểm MOS ngoại tuyến cao hơn nhưng bị giật trên điện thoại → **không triển khai B**.

Ở cấu hình B, riêng độ dài cửa sổ đã chiếm 40 ms và RTF trung bình 0.9 không còn đủ biên độ an toàn cho các quantum bị tăng tải đột biến.

Tương tự, với ngân sách thuật toán 40 ms đã dùng hết 20 ms cho cửa sổ, hệ thống không thể tùy tiện cộng thêm nhiều khung look-ahead 10 ms; càng không thể "tiết kiệm" 20 ms đó bằng cách chỉ báo cáo 3 ms thời gian xử lý thực tế.

## Bẫy thường gặp

1. Chỉ tối ưu RTF trung bình mà bỏ qua các phân vị đuôi.
2. Thay đổi \(L\) hoặc \(R\) nhưng không chạy lại toàn bộ quy trình đánh giá.
3. So sánh chất lượng giữa các mô hình có độ trễ khác nhau một cách thiếu công bằng.
4. Quên tính chi phí lấy mẫu lại (resample) vào tổng RTF.
5. Dùng số đo hiệu năng của bản biên dịch debug làm căn cứ triển khai thực tế.

## Mini-lab

**Mục tiêu.** In tách biệt độ trễ khung thuật toán và hệ số RTF cho một hop ở 48 kHz, bao gồm cả tình huống vượt hạn (overrun), không cần thiết bị âm thanh vật lý.

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

**Kết quả kỳ vọng.** Độ trễ khung là `20.0` ms, hop `10.0` ms và quantum khoảng `2.67` ms; RTF in ra lần lượt là `0.3` và `1.2`. Trường hợp sau vượt hạn hop dù 12 ms vẫn nhỏ hơn độ dài cửa sổ 20 ms.

**Lỗi thường gặp.** Chia thời gian xử lý thực tế cho độ dài cửa sổ thay vì cho hop sẽ cho ra RTF \(12/20 = 0.6\) và che giấu hoàn toàn lỗi overrun; diễn giải RTF 0.3 thành "độ trễ 3 ms" là đánh đồng hai đồng hồ độc lập, khiến bảng kiểm tra báo đạt trong khi người dùng vẫn nghe thấy độ trễ hoặc tiếng nổ. Tình huống p99 đạt 12 ms trong khi trung bình chỉ 3 ms chính là cảnh báo cốt lõi của hình minh họa: luôn phải ghi log cả hai.

## Bài tập nhỏ

1. Vẽ sơ đồ pipeline 9 công đoạn và đánh dấu các vị trí cần ghi mốc thời gian (timestamp).
2. Khi giảm hop từ 10 ms xuống 5 ms, số hop mỗi giây và tải CPU thay đổi xấp xỉ như thế nào?
3. Đề xuất ba chỉ số cho bảng đánh giá (scorecard) của phần mềm tổng đài chăm sóc khách hàng.
4. Vì sao đưa tín hiệu 48 kHz trực tiếp vào mô hình huấn luyện ở 16 kHz vẫn gây hại dù CPU dư sức xử lý?
5. Nêu một dạng méo chất lượng điển hình khi chọn cửa sổ phân tích quá ngắn.

### Gợi ý đáp án

1. Ghi mốc thời gian tại các điểm: thu mẫu, sau lấy mẫu lại, đầu vào STFT, đầu ra STFT và khi giao cho bộ mã hóa; lấy hiệu giữa các mốc để tách bạch độ trễ tín hiệu với thời gian xử lý thực tế.
2. Số hop mỗi giây tăng gấp đôi (từ 100 lên 200 ở 48 kHz nếu hop ban đầu là 480 mẫu), kéo theo tải CPU của phần STFT tăng gần gấp đôi; trong khi đó \(D_{\mathrm{alg}}\) không giảm đi một nửa trừ khi thay đổi cả \(L\).
3. Ví dụ: phân vị p95 của RTF, độ trễ thuật toán so với ngân sách cuộc gọi và điểm nghe/DNSMOS trên tập mẫu chứa tên riêng cùng chữ số.
4. Các bin tần số và biên dải ERB của mạng được thiết kế cố định cho 16 kHz; gán nhãn dữ liệu 48 kHz thành 16 kHz làm sai lệch toàn bộ trục phổ, đồng thời phần băng tần cao hơn có thể bị aliasing nếu thiếu lọc thông thấp.
5. Các họa âm không tách bạch được và mặt nạ trở nên gắt, nhấp nháy; ngược lại, chọn cửa sổ quá dài sẽ làm nhòe các âm bật (plosive).

## Đọc thêm

- Cấu hình định khung thời gian thực của DeepFilterNet: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) và [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Tổng quan WebRTC APM: [modules/audio_processing](https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/).
- Hướng dẫn tối ưu hiệu năng AudioWorklet trên MDN — mối quan hệ giữa quantum và bước nhảy hop.

## Video tham khảo

- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. **Xem trước.** Quan sát thông số độ trễ đặt cạnh kiến trúc hai tầng: độ trễ thuật toán cho biết tín hiệu đến muộn bao lâu, còn số phép tính cho biết CPU có theo kịp nhịp thời gian thực hay không.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Phần bàn về độ phức tạp thể hiện nửa còn lại của sự đánh đổi: mô hình nặng hơn có thể thắng điểm đánh giá nhưng vẫn trượt hạn hop.
- [Sonic Boom! Audio Programming on Android and Chrome (Google I/O'19)](https://www.youtube.com/watch?v=EeQr0zfvF04) — Google for Developers, tiếng Anh. Số đo độ trễ callback thực tế xác định giới hạn ngân sách mà hop STFT bắt buộc phải tuân theo.
