---
layout: post
title: "04-03 DeepFilterNet2 và DeepFilterNet3"
chapter: "04"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

DeepFilterNet2 và DeepFilterNet3 giữ nguyên kiến trúc hai tầng gồm độ lợi ERB kết hợp deep filter, đồng thời cải tiến hàm mất mát huấn luyện, dung lượng bộ đệm thời gian, bổ sung bộ hậu lọc (post-filter) và cổng điều khiển theo SNR. Bài học này chỉ sử dụng các số liệu công bố trong arXiv:2205.05474 và arXiv:2305.08227, không suy đoán tên khối chưa công bố và không khẳng định gói npm khớp từng bit với các checkpoint trong bài báo.

![Cùng bộ xương ERB cộng deep filter qua các thế hệ DeepFilterNet]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. Khung kiến trúc cốt lõi được giữ nguyên qua các thế hệ: 32 độ lợi ERB cho đường bao phổ, theo sau bởi bộ lọc phức 5 tap trên các bin thấp của STFT. Các thay đổi công bố giữa các phiên bản nằm ở hàm mất mát và dữ liệu (STFT đa phân giải, DNS4, post-filter), giảm bộ đệm thời gian trong mạng và bổ sung cổng SNR để tắt tầng xử lý khi không cần thiết.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ nắm được các cải tiến của DeepFilterNet2 so với bản ICASSP 2022 (bộ đệm thời gian thực, hàm mất mát đa phân giải, post-filter và RTF công bố), vai trò của cổng SNR cục bộ cùng kết quả bảng Voicebank+Demand của DeepFilterNet3 trong bài báo Interspeech 2023, và hiểu rõ vị trí của gói `deepfilternet3-noise-filter` trong hệ sinh thái này.

## Kế hoạch 60 phút

- **0–10 phút** — Nhắc lại khung chuẩn: 32 băng ERB, 5 tap, cửa sổ 20 ms / hop 10 ms, độ trễ thuật toán 40 ms.
- **10–25 phút** — DeepFilterNet2: giải thích nguồn gốc con số RTF 0,04.
- **25–40 phút** — Cơ chế cổng SNR năm 2023 và hàng kết quả DeepFilterNet3 trên bảng đánh giá.
- **40–50 phút** — Lệch phân bố vang phòng (RIR), xuất mô hình ONNX và bề mặt gói npm.
- **50–60 phút** — Mini-lab và bài tập.

## Giải thích cốt lõi

### Cùng kiến trúc nền tảng, khác phiên bản checkpoint

Cả ba thế hệ đều hướng tới tần số 48 kHz, cửa sổ 20 ms, chồng lấp 50%, 32 băng ERB và bộ lọc phức 5 tap tới khoảng 5 kHz, với 2 khung nhìn trước tạo ra độ trễ thuật toán **40 ms**. Khi triển khai, luôn cố định cụ thể tệp trọng số thay vì chỉ ghi chung chung "DeepFilterNet": nạp checkpoint DF2 vào cấu hình DF3 sẽ gây lỗi kích thước tensor hoặc méo âm sắc.

### DeepFilterNet2 — arXiv:2205.05474

Bài báo DeepFilterNet2, “Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio” (IWAENC 2022, arXiv:2205.05474), giữ nguyên lưới STFT và đưa ra các cải tiến quyết định về chất lượng lẫn tốc độ:

- **Hàm mất mát.** Áp dụng khởi động (warmup) 3 epoch rồi giảm tốc độ học theo hàm cosine sau mỗi bước. Sử dụng hàm mất mát phổ đa phân giải sau ISTFT trên các cửa sổ 5, 10, 20 và 40 ms với hệ số nén $$c=0{,}3$$. Hạng trọng số pha trộn $$\alpha$$ của bản ICASSP được loại bỏ: bộ lọc 5 tap có thể tự "nghỉ" bằng cách đưa phần thực của tap hiện tại về 1 và các tap còn lại về 0.
- **Dữ liệu huấn luyện.** Dùng tập DNS4 tiếng Anh kết hợp mở rộng các dạng suy giảm: tín hiệu đích giữ ít vang hơn hỗn hợp đầu vào và khôi phục cả đoạn âm bị cắt đỉnh (clipping). Đây là cải thiện hữu ích cho bối cảnh phòng họp, nhưng không phải bảo đảm tuyệt đối cho mọi không gian thực tế.
- **Giảm bộ đệm thời gian trong mạng.** Kích thước kernel theo thời gian thu gọn từ $$2\times 3$$ xuống $$1\times 3$$ (ngoại trừ một lớp đầu vào nhân quả $$3\times 3$$), kích thước ẩn của GRU là 256, và các lớp tuyến tính theo nhóm được gom thành một phép nhân ma trận. Trên CPU nhỏ, chi phí lưu lượng truy xuất bộ nhớ của vòng đệm activation thường lấn át bản thân số phép MAC.
- **Bộ hậu lọc (Post-filter).** Áp dụng phép biến đổi dạng sin lên độ lợi ERB theo công thức $$G \leftarrow G\sin(\pi G/2)$$ để suy hao mạnh hơn các băng nhiễu, sau đó trộn theo hệ số cường độ $$\beta$$ (cần kiểm tra giá trị mặc định trong mã nguồn thay vì suy đoán; cờ `--pf` bật bộ hậu lọc này trên CLI).
- **Cùng CPU nhưng RTF khác biệt rõ rệt.** Đo trên Voicebank+Demand với CPU Core i5-8250U: bản ICASSP có 1,778 M tham số, 0,348 GMAC, RTF 0,11 và PESQ 2,81; bản DF2 tinh gọn có 2,306 M tham số, 0,356 GMAC, **RTF 0,04** và PESQ 3,08 (CSIG 4,30, CBAK 3,40, COVL 3,699, STOI 0,9429). Dù GMAC gần như tương đương, RTF giảm mạnh nhờ tối ưu kernel và cấu trúc GRU. Khi bật post-filter, RTF vẫn là 0,04 nhưng PESQ giảm nhẹ xuống **3,03** — nếu chỉ nhìn điểm PESQ mà không nghe thử, kỹ sư rất dễ loại bỏ một cải tiến cảm thụ có giá trị.

Phần tóm tắt bài báo cũng nêu tốc độ này đủ chạy trên Raspberry Pi 4, nhưng điều đó không đồng nghĩa với biên độ chịu nhiệt trên điện thoại di động.

### Bài báo năm 2023 và DeepFilterNet3 — arXiv:2305.08227

Bài báo “DeepFilterNet: Perceptually Motivated Real-Time Speech Enhancement” (Interspeech 2023, arXiv:2305.08227) hệ thống hóa lại framework và là trích dẫn mà tệp README dự án gắn trực tiếp với mô hình **DeepFilterNet3** (cần giữ đúng trích dẫn này, không tự đặt tiêu đề khác).

Quy tắc vận hành công bố của bản demo gồm:

- Tần số lấy mẫu 48 kHz, cửa sổ 20 ms, hop 10 ms, nhìn trước 2 khung, độ trễ thuật toán **40 ms**.
- 32 độ lợi ERB cho tầng đường bao.
- Bộ lọc phức $$N=5$$ áp dụng trên **96 bin** thấp nhất (4,8 kHz); các bin cao hơn giữ nguyên độ lợi ERB.
- Bộ mã hóa dự đoán thêm SNR cục bộ $$\xi\in[-15,35]$$ dB để điều khiển cổng: nếu $$\xi<-10$$ dB, cả hai bộ giải mã đều tắt và khung đầu ra bằng im lặng; nếu $$\xi>20$$ dB, bộ giải mã deep filter tắt; trong khoảng còn lại cả hai tầng cùng chạy.

Hệ quả thực tế: đoạn tiếng nói rơi xuống dưới −10 dB sẽ bị cắt về im lặng số, còn tiếng nói trên 20 dB bỏ qua tầng khôi phục họa âm nên tiếng ù nhẹ vẫn có thể sót lại giữa các họa âm. Vòng chạy bằng thư viện `tract` trong bài báo này ghi nhận **RTF 0,19** trên một luồng Core i5-8250U — khác với mức **0,04** đo trên bản biên dịch khác của DF2; không nên lấy trung bình hai con số này hay coi chúng là RTF trên điện thoại.

Trên bảng Voicebank+Demand, DeepFilterNet3 ghi nhận PESQ 3,17, CSIG 4,34, CBAK 3,61, COVL 3,77 và STOI 0,944 (so với PESQ 3,08 của DF2 và 2,81 của bản gốc). Cần nhớ đây chỉ là kết quả trên một tập kiểm thử chuẩn.

### Gói bọc, xuất ONNX và điều kiện phòng thực tế

Gói npm `deepfilternet3-noise-filter` 1.3.0 ([mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression)) chạy ONNX/WASM trong AudioWorklet với bề mặt API gồm `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor` và mức khử 0–100 qua `setSuppressionLevel`. Không nên giả định đầu ra khớp từng bit với CLI hay bảng bài báo; bất kỳ sự thay đổi nào về hop, look-ahead hay tần số lấy mẫu đều tạo thành một hệ thống khác.

Chuỗi xuất mô hình điển hình là PyTorch → ONNX → ONNX Runtime / WASM / `tract` → AudioWorklet hoặc callback native, trong đó trạng thái ẩn GRU phải được truyền tường minh như đầu vào và đầu ra của đồ thị (một đồ thị trục động nạp cả tệp chỉ là mô hình ngoại tuyến). Vì dữ liệu mô phỏng RT60 của bài báo đầu dừng ở 1 giây, hiện tượng khử quá mức trong phòng thực tế vang lớn thường bắt nguồn từ khoảng trống dữ liệu này — hãy nghe kiểm tra (Chương 08) trước khi tăng kích thước mạng.

## Bẫy thường gặp

- Nạp trọng số DF2 đi kèm ngưỡng cổng SNR của DF3 hoặc ngược lại.
- Trích dẫn PESQ 3,17 như thể đó là "điểm MOS thực tế của sản phẩm".
- Xem RTF 0,04 hay 0,19 đo trên Intel i5 là ngân sách chạy ổn định trên laptop không quạt hoặc điện thoại.
- Bật `--pf`, thấy PESQ giảm từ 3,08 xuống 3,03 rồi hủy bỏ ngay mà chưa nghe thử.
- Cho rằng `setSuppressionLevel(100)` tái hiện chính xác mức suy hao tuyệt đối (dB) trong bài báo, trong khi đây là tham số sản phẩm theo thang 0–100.

## Mini-lab

**Mục tiêu.** Chạy CLI hai lần (có và không có cờ post-filter) khi tải được trọng số, đồng thời luôn thực thi đoạn NumPy tính phép biến dạng sin không thứ nguyên trên bốn giá trị độ lợi để kiểm chứng ngoại tuyến.

```bash
deepFilter --output-dir out/noisy/ noisy.wav
deepFilter --pf --output-dir out/pf/ noisy.wav
python3 - << 'PY'
import numpy as np
G = np.array([0.0, 0.2, 0.5, 1.0])
Gp = G * np.sin(0.5 * np.pi * G)
np.set_printoptions(precision=6, suppress=True)
print(Gp)
PY
```

**Kết quả kỳ vọng.** Khi có trọng số và đầu vào 48 kHz: thu được hai tệp WAV đã xử lý khác nhau kèm log thời gian/RTF. Đoạn NumPy luôn in `[0. 0.061803 0.353553 1.]`, cho thấy độ lợi thấp `0.2` bị kéo xuống mạnh hơn nhiều so với độ lợi `1.0` — đúng cơ chế tăng suy hao vùng nhiễu của post-filter (bước pha trộn thứ hai dùng tham số $$\beta$$ cố ý không đưa vào đoạn mã này).

**Lỗi thường gặp.** Không có mạng để tải trọng số (giữ phần kết quả NumPy và ghi chú lỗi CLI); đưa tệp khác 48 kHz vào bản Rust `deep-filter`; so sánh trực tiếp RTF laptop với điện thoại; hoặc giả định đầu ra `--pf` khớp hoàn toàn với `setSuppressionLevel` của gói npm.

## Bài tập

1. **Bảng ba thế hệ.** Với bản ICASSP 2022, DeepFilterNet2 và DeepFilterNet3, hãy liệt kê hội nghị, mã arXiv, một cải tiến cơ chế nổi bật và một con số đánh giá bạn có thể bảo vệ.
2. **Cơ chế cổng SNR.** Với các mức SNR cục bộ lần lượt là −12 dB, +25 dB và +5 dB, những tầng xử lý nào sẽ hoạt động?
3. **Phân tích RTF.** Bảng DF2 ghi GMAC 0,356 với RTF 0,04, trong khi bản trước ghi GMAC 0,348 nhưng RTF tới 0,11. Vì sao mô hình có số MAC cao hơn một chút lại chạy nhanh hơn đáng kể?
4. **Bề mặt gói npm.** Nêu hai biểu tượng API công khai trên `deepfilternet3-noise-filter` và hai trách nhiệm kỹ thuật về hop và trạng thái mà gói không tự động miễn trừ cho người tích hợp.

### Gợi ý đáp án

1. ICASSP 2022 (`2110.05588`): kiến trúc hai tầng ERB + deep filter, PESQ 2,81 / 1,778 M tham số; IWAENC 2022 (`2205.05474`): rút gọn kernel thời gian, hàm mất mát đa phân giải và post-filter, RTF 0,04 và PESQ 3,08 trên bảng đo i5; Interspeech 2023 (`2305.08227`, gắn với DF3 trong README): cổng SNR cục bộ và PESQ 3,17. Tất cả điểm PESQ đều đo trên Voicebank+Demand, không phải dữ liệu sản phẩm.
2. Tại −12 dB: cả hai bộ giải mã tắt, xuất im lặng; tại +25 dB: chỉ chạy tầng ERB; tại +5 dB: chạy đầy đủ cả hai tầng.
3. Số phép MAC không phản ánh lưu lượng truy xuất bộ nhớ. Kernel thời gian ngắn hơn của DF2 giảm lượng activation phải đệm ở mỗi hop, giúp RTF hạ từ 0,11 xuống 0,04 dù GMAC giữ quanh 0,35.
4. Bề mặt công khai gồm `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor` và `setSuppressionLevel(0–100)`. Người tích hợp vẫn phải xử lý đúng chênh lệch giữa hop 10 ms và quantum 128 mẫu, duy trì trạng thái GRU/STFT xuyên qua các callback, và không mặc định khớp bit với CLI.

## Đọc thêm

- Schröter et al., DeepFilterNet2, IWAENC 2022, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474).
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227) (trích dẫn DeepFilterNet3 trong README).
- [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) cho checkpoint và công cụ `deepFilter`.
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) cho phần đóng gói AudioWorklet.

## Video tham khảo

- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. **Xem trước.** Trình bày khung kiến trúc nền tảng (STFT, độ lợi ERB và deep filter) mà DeepFilterNet2 và DeepFilterNet3 tiếp tục kế thừa.
- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, tiếng Anh. Đoạn nghe thử của tác giả để đánh giá trực tiếp bằng tai (các chỉ số DF2/DF3 cụ thể nằm trong bài báo).
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Minh họa quy trình thẩm định thế hệ mô hình mới dựa trên cùng bài toán, ngân sách độ phức tạp và đánh giá nghe — đúng tinh thần so sánh giữa DF2 và DF3.
