---
layout: post
title: "04-05 Mô hình streaming siêu nhẹ"
chapter: "04"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

Hãy thử tưởng tượng bạn vừa tìm thấy trên mạng một mô hình khử nhiễu tiếng nói chỉ tốn **0,05 GMAC** — nhẹ hơn DeepFilterNet2 tới bảy lần trên giấy. Bạn hăm hở xuất sang ONNX, nhúng vào trình duyệt hay bo mạch nhúng, rồi bật micro thử nghiệm... và lập tức nghe thấy tiếng *tách, tách* liên hồi vì mỗi khung xử lý bị trễ hạn! Chuyện gì vừa xảy ra? Một mô hình ít phép nhân-cộng hơn tại sao lại chạy *chậm hơn* ngoài đời thực, và tại sao một mạng GRU chạy êm ru suốt đoạn demo 3 giây lại bỗng dưng méo tiếng sau 40 phút họp trực tuyến?

Nhiều sản phẩm không đủ ngân sách tài nguyên như mức laptop mà DeepFilterNet2 giả định. Các tên gọi **GTCRN**, **FastEnhancer**, **μNet** và **Fast-ULCNet** thường xuất hiện trong danh sách rút gọn (shortlist) cho nhóm bộ tăng cường tiếng nói streaming siêu nhẹ. Bài học này **không** gắn tiêu đề bài báo, năm xuất bản hay URL cho bốn cái tên đó; thay vào đó, bài tập trung vào phương pháp đo kiểm để ra quyết định: lý giải vì sao bảng số phép tính MAC và hệ số RTF thực tế (wall-clock) thường tách rời nhau, và vì sao hiện tượng trôi trạng thái GRU sau một giờ chạy liên tục là một dạng lỗi khác hẳn với lỗi hop chậm.

**Mạch bài học:** Ngộ nhận "ít MAC = chạy nhanh" → Kiến thức cần nhớ (Nghẽn băng thông bộ nhớ, Độ trễ đuôi p95, Ổn định hệ động lực hồi tiếp dài hạn) → Đối chiếu ngân sách phần cứng & số liệu DF2 → Bốn cái tên định hướng trong shortlist → Giải thích tính tay sự tách rời MAC/RTF và cơ chế tích lũy trôi trạng thái sau 270.000 hop → Danh mục kiểm tra, Mini-lab và Bài tập.

![RTF đối chiếu quantum AudioWorklet: thời gian tường mỗi khối audio, không phải bảng MAC]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Hình. RTF là tỷ số giữa thời gian xử lý thực tế và thời lượng âm thanh. Một quantum AudioWorklet 128 mẫu ở 48 kHz dài khoảng 2,67 ms. Mô hình siêu nhẹ đạt yêu cầu là mô hình giữ được phân vị p95 thời gian xử lý nằm gọn trong hop thực tế trên đúng CPU đích; bốn cái tên GTCRN, FastEnhancer, μNet và Fast-ULCNet chỉ đóng vai trò điểm neo trong danh sách rút gọn.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ giải thích được (thông qua bảng số liệu có thể kiểm chứng của DeepFilterNet2) vì sao GMAC và RTF có thể biến thiên ngược chiều nhau; đưa bốn tên mô hình siêu nhẹ vào danh mục kiểm tra lựa chọn mà không suy đoán kết quả; và thiết kế bài kiểm tra ổn định trạng thái dài hạn độc lập với từng bài báo.

## Kiến thức cần nhớ: Điều gì quyết định tốc độ và độ bền của mô hình streaming siêu nhẹ?

### 1. Nghẽn tính toán (Compute-bound) vs. Nghẽn bộ nhớ (Memory-bound)
- **Là gì:** Trong kiến trúc máy tính hiện đại, thời gian chạy một lớp mạng nơ-ron bị chặn bởi giá trị lớn hơn giữa thời gian tính toán (số MAC / tốc độ ALU) và thời gian vận chuyển dữ liệu từ RAM/cache vào thanh ghi (số byte đọc-ghi / băng thông bộ nhớ).
- **Nghiên cứu gì:** Giải thích vì sao một lớp tích chập nhóm tinh vi hoặc thao tác `gather` cắt lát băng tần có số MAC rất nhỏ nhưng lại chạy chậm rì trên CPU/WASM: bộ xử lý dành phần lớn thời gian *chờ* dữ liệu từ cache thay vì nhân-cộng.

### 2. Phân phối thời gian thực tế (Wall-clock RTF) và phân vị đuôi (p95, p99)
- **Là gì:** Thay vì đánh giá tốc độ bằng số trung bình hay GMAC lý thuyết, kỹ thuật thời gian thực đo thời gian tường (wall-clock) từng hop trên đúng thiết bị đích và khóa ngưỡng ở phân vị p95/p99.
- **Nghiên cứu gì:** Đảm bảo không xảy ra underrun (vỡ tiếng) trong dòng âm thanh liên tục — nơi chỉ cần 1% số khung vượt quá hạn hop 10 ms là người nghe đã thấy tiếng nổ lách tách mỗi giây.

### 3. Tính ổn định của hệ hồi tiếp rời rạc (Recurrent State Drift)
- **Là gì:** Một mạng GRU chạy streaming là một hệ động lực rời rạc $$h_t = F(h_{t-1}, x_t)$$ lặp hàng trăm nghìn bước liên tiếp mà không reset.
- **Nghiên cứu gì:** Nếu các cổng quên (update/reset gate) tiến gần 1 và xuất hiện sai số lượng tử hóa nhỏ hoặc tín hiệu đầu vào lệch phân bố (như khoảng lặng kéo dài), sai số nhỏ ở mỗi hop có thể tích lũy thành **trôi trạng thái (state drift)** — lỗi vô hình ở đoạn test 3 giây nhưng phá hỏng cuộc gọi 45 phút.

## Kế hoạch 60 phút

- **0–10 phút** — So sánh hai ngân sách tài nguyên: chip DSP tai nghe và tab trình duyệt trên laptop.
- **10–25 phút** — Dùng số liệu DF2 để chứng minh số MAC tách rời khỏi RTF thực tế.
- **25–40 phút** — Định vị ngắn gọn bốn cái tên siêu nhẹ và danh mục thông số bắt buộc phải tự đo.
- **40–50 phút** — Hiện tượng trôi trạng thái (state drift) qua hàng chục phút gọi liên tục.
- **50–60 phút** — Mini-lab, danh mục kiểm tra và bài tập.

## Giải thích cốt lõi

### Hai ngân sách phần cứng khác hẳn bảng đo DF2

DeepFilterNet2 (arXiv:2205.05474) báo cáo RTF **0,04** ở mức **0,356 GMAC** trên laptop Core i5-8250U, so với bản ICASSP đạt 0,348 GMAC nhưng RTF **0,11**; trong khi vòng chạy `tract` năm 2023 ghi nhận RTF **0,19** trên cùng i5-8250U. Trên cùng bảng DF2, RNNoise có khoảng 0,06 M tham số, RTF 0,027 và PESQ 2,33 (so với PESQ 3,08 của DF2). Đây là những con số hiệu năng duy nhất đã được công bố mà bài học này trích dẫn. Tai nghe hay điện thoại là lớp phần cứng hoàn toàn khác, nên RTF laptop không thể suy diễn sang RTF di động. Các kiến trúc siêu nhẹ hướng tới bộ nhớ cực nhỏ và hop ngắn, thường chấp nhận điểm PESQ gần mức 2,33 hơn là 3,17 — sự đánh đổi hoàn toàn hợp lý khi lựa chọn còn lại là vỡ tiếng do underrun.

### Vì sao cột MAC trong bài báo dễ gây hiểu nhầm

Đếm số phép nhân-cộng (MAC) ngầm giả định mọi phép tính đều mất thời gian thực tế như nhau, nhưng trên phần cứng thực tế điều này không đúng:

- Các thao tác gom dữ liệu theo nhóm hoặc theo băng tần (gather) phải nhảy cóc trong bộ nhớ, khiến đơn vị tính toán (ALU) phải chờ bộ nhớ đệm (cache) — lập luận này thường gắn với tên gọi FastEnhancer (chỉ nêu tên, không trích bài báo ở đây).
- Một phép nhân ma trận dày (GEMM) lớn hơn một chút nhưng được runtime hợp nhất (fused) thường hoàn thành nhanh hơn một lớp tích chập nhóm tinh vi mà ONNX Runtime không vector hóa tốt.
- Lớp tích chập theo trục thời gian phải duy trì vòng đệm activation quá khứ. DF2 rút kernel từ $$2\times 3$$ xuống $$1\times 3$$ (trừ lớp đầu vào) giúp RTF giảm từ 0,11 xuống 0,04 dù GMAC hầu như đứng yên. Đây là nguyên tắc cốt lõi khi đánh giá mọi mô hình siêu nhẹ: hãy đếm lưu lượng byte di chuyển ở mỗi hop chứ không chỉ nhìn số MAC.

**Quy tắc đo kiểm (Chương 05):** Chạy đơn luồng, loại bỏ giai đoạn khởi động (warm-up), đo phân vị p50 và p95 thời gian xử lý thực tế mỗi hop rồi chia cho độ dài hop trên đúng thiết bị đích theo nhịp callback. Cột MAC trong bài báo chỉ nên coi là giả thuyết ban đầu.

### Bốn cái tên định hướng (chỉ ở mức danh mục)

| Tên | Vai trò trong danh sách rút gọn | Phạm vi bài học này không nêu |
|-----|---------------------------------|-------------------------------|
| **GTCRN** | Mạng tích chập–hồi tiếp theo nhóm siêu nhẹ, thường được nhắc tới | Không nêu tiêu đề, năm, URL, MAC hay MOS |
| **FastEnhancer** | Tên gắn với định hướng tối ưu tốc độ trên thiết bị (kể cả đo trên ONNX Runtime) | Không nêu số liệu kết quả |
| **μNet** | Tên gắn với ràng buộc bộ nhớ cực thấp (DSP, tai nghe) | Không nêu số liệu kết quả |
| **Fast-ULCNet** | Tên gắn với nhánh ULCNet và bài toán trạng thái RNN trong luồng dài | Không nêu số liệu kết quả |

Một số cái tên cùng nhóm như ULCNet, UL-UNAS, AdaptCRN, CoFi-Lite hay FSPEN chỉ là từ vựng mở rộng tùy chọn, không nằm trong phạm vi kiểm tra và không gắn trích dẫn tại đây.

### Vấn đề trạng thái khi chạy dài hơn đoạn demo

Các đoạn nghe thử dài 3 giây che giấu hoàn toàn hiện tượng trôi trạng thái GRU. Với hop 10 ms, một cuộc gọi 45 phút tương ứng $$45\times 60\times 100=270\,000$$ bước cập nhật liên tiếp. Sai số lượng tử hóa, cổng hồi tiếp kém ổn định hoặc các khoảng lặng kéo dài ngoài phân bố huấn luyện có thể đẩy trạng thái ẩn lệch dần, gây ra nhiễu nhạc tăng chậm hoặc giọng nói bị suy hao dần theo thời gian thay vì lỗi tức thời tại $$t=0$$. Trong khi Fast-ULCNet thường được nhắc đến trong chủ đề này, bạn có thể áp dụng ngay các phép kiểm tra kỹ thuật độc lập sau:

- Trong các khoảng lặng đã phát hiện, kéo mượt trạng thái GRU về 0 dần trong vài trăm mili giây thay vì đặt về 0 đột ngột trong một hop (đặt 0 cứng sẽ gây click hoặc lọt nhiễu như bài 05-04).
- Giới hạn chuẩn (norm) của vector trạng thái nếu kiến trúc cho phép mà không làm sai lệch độ lợi.
- Ghi biểu đồ phân bố (histogram) độ lợi tại phút thứ 1 và phút thứ 40 với cùng mức tín hiệu vào — sự dịch chuyển rõ rệt là dấu hiệu trôi trạng thái.

## Giải thích: Tự tính tay sự tách rời MAC/RTF và cơ chế tích lũy trôi trạng thái

Hãy kiểm chứng hai hiện tượng cốt lõi của bài bằng hai phép tính ngắn gọn trên giấy.

### Phép tính 1: Vì sao GMAC tăng 2,3% mà RTF lại giảm gần 3 lần?
Lấy đúng hai hàng số liệu công bố của DeepFilterNet2 trên cùng CPU Core i5-8250U:
- **Bản DF ICASSP:** $$\text{GMAC}_1 = 0{,}348$$, $$\text{RTF}_1 = 0{,}11 \implies$$ mỗi hop 10 ms mất $$T_1 = 0{,}11 \times 10 = 1{,}10\text{ ms}$$.
- **Bản DF2 tinh gọn:** $$\text{GMAC}_2 = 0{,}356$$ (tăng $$\frac{0{,}356 - 0{,}348}{0{,}348} \approx +2{,}3\%$$), nhưng $$\text{RTF}_2 = 0{,}04 \implies$$ mỗi hop 10 ms chỉ mất $$T_2 = 0{,}04 \times 10 = 0{,}40\text{ ms}$$ (**nhanh hơn $$2{,}75\times$$**).

Lý do nằm ở **cường độ số học (arithmetic intensity)**: giả sử một nhân CPU có thông lượng thực dụng $$40\text{ GMAC/s}$$ và băng thông cache/RAM hiệu dụng $$20\text{ GB/s}$$. Nếu một lớp nhỏ phải đọc-ghi $$160\text{ KB}$$ tensor trung gian (vòng đệm activation của kernel $$2\times 3$$) chỉ để thực hiện $$50\,000$$ MAC:
- Thời gian tính toán thuần: $$\frac{50\,000}{40\times 10^9} = 1{,}25\,\mu\text{s}$$.
- Thời gian di chuyển bộ nhớ: $$\frac{160\,000\text{ B}}{20\times 10^9\text{ B/s}} = 8{,}00\,\mu\text{s}$$ — **chậm gấp $$6{,}4$$ lần thời gian tính toán!**
Chỉ cần rút kernel từ $$2\times 3$$ xuống $$1\times 3$$ và hợp nhất lớp (operator fusion) để giữ activation trong thanh ghi, ta cắt mạnh vế bộ nhớ $$8{,}00\,\mu\text{s}$$ dù tổng số MAC gần như không giảm.

### Phép tính 2: Sai số lượng tử hóa tí hon $$\varepsilon = 10^{-4}$$ tích lũy thành trôi trạng thái ra sao?
Mô hình hóa một chiều trạng thái ẩn GRU trong khoảng lặng kéo dài bằng phương trình sai phân tuyến tính hóa:
$$ h_t = a\,h_{t-1} + \varepsilon, $$
với hệ số giữ trạng thái $$a = 0{,}999$$ (cổng cập nhật rất nhỏ để nhớ ngữ cảnh dài) và sai số làm tròn/lượng tử hóa mỗi bước $$\varepsilon = 10^{-4}$$, khởi đầu $$h_0 = 0$$.
- Sau đoạn demo 3 giây ($$t = 300$$ hop ở hop 10 ms):
  $$ h_{300} = \varepsilon\,\frac{1 - a^{300}}{1 - a} = 10^{-4} \cdot \frac{1 - 0{,}999^{300}}{0{,}001} \approx 0{,}1 \times (1 - 0{,}741) = 0{,}0259. $$
  Giá trị nhỏ này hầu như chưa gây méo đáng kể khi nghe thử 3 giây.
- Sau 1 phút ($$t = 6\,000$$ hop) và kéo dài tới phút thứ 45 ($$t = 270\,000$$ hop): vì $$0{,}999^{6000} \approx 0{,}0025 \to 0$$, trạng thái tiến tới giới hạn lệch:
  $$ h_\infty = \frac{\varepsilon}{1 - a} = \frac{10^{-4}}{10^{-3}} = 0{,}1000 $$
  — lớn gấp **1.000 lần** sai số một bước! Nếu hệ số giữ $$a = 0{,}9995$$, độ lệch tăng gấp đôi lên $$0{,}20$$, đủ đẩy đầu ra cổng sigmoid dịch khỏi vùng hiệu chuẩn và làm mờ giọng nói khi người dùng bắt đầu nói lại.

### Khi nào nhánh DeepFilterNet3 vẫn là lựa chọn phù hợp

Hãy ưu tiên mô hình thuộc nhánh DeepFilterNet3 trên trình duyệt laptop khi WASM SIMD giữ vững ngân sách hop và kích thước trọng số vài megabyte là chấp nhận được. Ngược lại, hãy cân nhắc nhóm siêu nhẹ cho chip DSP hoặc CPU rất yếu nơi chấp nhận một phần nhiễu dư. Một phương án phân tầng hợp lý là dùng AEC cổ điển kết hợp bộ khử dư siêu nhẹ trên thiết bị nhúng, và dùng DF3 trên trình duyệt. Lưu ý không đưa trực tiếp trọng số 16 kHz vào đồ thị 48 kHz rồi coi đó là "DF3 bản nhẹ" — luôn phải lấy mẫu lại có chủ đích.

## Danh mục kiểm tra cho danh sách rút gọn

1. Đồ thị có nhân quả không và cần bao nhiêu khung nhìn trước?
2. Hoạt động ở 16 kHz hay 48 kHz, và bộ lấy mẫu lại đặt ở đâu?
3. Phân vị p95 của RTF trên **đúng thiết bị đích** (đơn luồng, cache nóng, theo nhịp callback).
4. Dung lượng trọng số và thời gian khởi động lạnh (tách biệt khỏi RTF).
5. Kết quả chạy thử liên tục ít nhất 30 phút có xen lẫn khoảng lặng.
6. Giấy phép sử dụng của bộ trọng số.
7. Mọi toán tử trong đồ thị đều được hỗ trợ bởi phiên bản ONNX Runtime hoặc `tract` đang dùng.

## Bẫy thường gặp

- Chọn mô hình triển khai chỉ dựa trên cột MAC nhỏ nhất.
- Chuyển đổi các lớp tích chập nhóm mà runtime WASM lại thực thi bằng vòng lặp vô hướng (scalar).
- Bỏ qua bài kiểm tra ổn định liên tục 30 phút.
- Đưa dữ liệu PCM 48 kHz trực tiếp vào mô hình có lưới STFT huấn luyện ở 16 kHz.

## Mini-lab

**Mục tiêu.** Kiểm chứng hiện tượng "GMAC xấp xỉ nhau nhưng RTF chênh lệch lớn" từ bảng số liệu công bố của DeepFilterNet2, sau đó áp dụng tiêu chí chọn theo p95 RTF trên một cặp mô hình giả định.

```bash
python3 - << 'PY'
# Numbers from the DeepFilterNet2 paper's Voicebank table (notebook i5).
rows = [
    ("DF ICASSP row", 0.348, 0.11),
    ("DF2 simplified", 0.356, 0.04),
]
for name, gmac, rtf in rows:
    print(f"{name}: gmac={gmac:.3f} rtf={rtf:.2f} rtf_per_gmac={rtf/gmac:.3f}")
# Hypothetical shortlist. These MACs are lab fiction, not paper results.
fake = [("modelA", 0.05, 0.30), ("modelB", 0.08, 0.12)]
best = min(fake, key=lambda r: r[2])
print("lower_p95_rtf", best[0])
PY
```

**Kết quả kỳ vọng.** `DF ICASSP row: gmac=0.348 rtf=0.11 rtf_per_gmac=0.316`, `DF2 simplified: gmac=0.356 rtf=0.04 rtf_per_gmac=0.112`, và cuối cùng `lower_p95_rtf modelB`. Dù `modelB` có số MAC cao hơn, nó vẫn thắng vì đạt RTF thực tế thấp hơn.

**Lỗi thường gặp.** Nhầm cặp số giả định là kết quả thực của GTCRN hay FastEnhancer; dùng RTF 0,04 của laptop cho điện thoại; hoặc chỉ xếp hạng theo tỷ số `rtf_per_gmac` trong khi phân vị p95 lại vượt hạn hop.

## Bài tập

1. **Chọn kiến trúc theo thiết bị.** Với ba môi trường: DSP tai nghe, Chrome trên laptop tầm trung và thiết bị loa họp cỡ Raspberry Pi, hãy chọn DF3 hoặc "một mô hình siêu nhẹ" và giải thích lý do ngân sách trong một câu.
2. **Thiết kế bài đo hiệu năng.** Xác định số hop warm-up, độ dài hop và phân vị dùng làm ngưỡng đạt/không đạt; giải thích vì sao không dùng giá trị trung bình làm ngưỡng.
3. **Tính toán trôi trạng thái.** Với hop 10 ms trong cuộc gọi 40 phút, mạng GRU thực hiện bao nhiêu lần cập nhật? Cần so sánh đại lượng nào giữa đầu và cuối phiên chạy?
4. **Định vị danh mục.** Viết đúng một câu mô tả vai trò cho từng cái tên GTCRN, FastEnhancer, μNet và Fast-ULCNet mà không kèm con số hay năm xuất bản.

### Gợi ý đáp án

1. DSP tai nghe: chọn mô hình siêu nhẹ vì RTF 0,04 của DF2 đo trên Core i5; Chrome trên laptop: chọn DF3 nếu WASM SIMD giữ p95 gọn trong hop và kích thước tải chấp nhận được; bo mạch cỡ Raspberry Pi: bài báo DF2 nêu khả năng chạy thời gian thực trên Pi 4 cho chính mô hình đó, còn mô hình siêu nhẹ là phương án dự phòng nếu p95 bản biên dịch thực tế không đạt.
2. Bỏ qua 50 hop đầu để làm nóng cache, chọn hop = 10 ms = 0,01 s, và đặt ngưỡng trên p95 (đồng thời theo dõi p99) vì giá trị trung bình che giấu các khung trễ gây underrun (Chương 05).
3. Tổng số bước cập nhật là $$40\times 60\times 100=240\,000$$ lần. Hãy so sánh histogram độ lợi băng tần hoặc chuẩn của vector trạng thái trên cùng một đoạn âm thanh hiệu chuẩn lặp lại, thay vì so trực tiếp hai dạng sóng khác nhau.
4. Chỉ sử dụng phần mô tả vai trò một dòng trong bảng ở trên; việc thêm số liệu cụ thể khi chưa đọc tài liệu gốc đồng nghĩa với suy đoán.

## Đọc thêm

- Schröter et al., DeepFilterNet2, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474) — đối chiếu hai hàng RTF 0,11 và 0,04 minh họa sự tách rời giữa MAC và RTF.
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227) — số đo RTF 0,19 của bản `tract`.
- Valin, [arXiv:1709.08243](https://arxiv.org/abs/1709.08243) — mốc đối chiếu kiến trúc lai nhỏ gọn (bài 04-06).
- Các tài liệu gốc bạn tự tra cứu cho GTCRN, FastEnhancer, μNet và Fast-ULCNet (bài này cố ý không gắn đường dẫn).

## Video tham khảo

- [RNNoise, Neural Speech Enhancement, and the Browser](https://www.youtube.com/watch?v=nsscrYdrGRE) — W3C, tiếng Anh. **Xem trước.** Minh họa một bộ khử nhiễu đủ gọn cho trình duyệt và Raspberry Pi — đúng bài toán ngân sách của nhóm streaming siêu nhẹ.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Biểu đồ đánh đổi giữa độ phức tạp và chất lượng làm rõ tiêu chuẩn mà các mô hình siêu nhẹ phải đáp ứng.
- [Zoom on Web: getting connected with advanced web technology](https://www.youtube.com/watch?v=nhTxJBgTywc) — Chrome for Developers, tiếng Anh. Phần nói về SIMD giải thích vì sao ngay cả mô hình rất nhỏ vẫn cần runtime vector hóa khi hop chỉ dài vài mili giây.
