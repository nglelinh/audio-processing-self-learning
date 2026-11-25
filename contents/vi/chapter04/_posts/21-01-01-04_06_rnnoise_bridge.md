---
layout: post
title: "04-06 RNNoise như cầu nối giảng dạy"
chapter: "04"
order: 6
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

Năm 2017, giữa làn sóng mạng học sâu hàng chục triệu tham số đòi hỏi GPU đắt tiền, kỹ sư âm thanh Jean-Marc Valin (đồng tác giả codec Opus) đặt ra một câu hỏi táo bạo: *nếu ta để DSP cổ điển làm phần việc mà toán học đã giải rất tốt — chia băng tần cảm thụ và lọc lược cao độ — rồi chỉ giao cho một mạng nơ-ron tí hon đúng việc duy nhất mà DSP luôn chật vật (ước lượng độ lợi từng băng theo ngữ cảnh), thì kết quả sẽ nhẹ đến mức nào?* Câu trả lời là **RNNoise**: chỉ 87.503 trọng số, nằm gọn trong bộ nhớ đệm L2 và chạy trên CPU laptop với vỏn vẹn 1,3% tải một nhân!

**RNNoise** (Jean-Marc Valin, arXiv:1709.08243; [xiph/rnnoise](https://github.com/xiph/rnnoise)) kết hợp tầng tiền xử lý theo băng Bark, một bộ lọc lược cao độ (pitch comb filter) và một mạng GRU nhỏ dự đoán 22 hệ số độ lợi. Dù không đạt mức điểm Voicebank+Demand như DeepFilterNet3 (PESQ 3,17 trong arXiv:2305.08227), RNNoise minh họa trọn vẹn cùng một triết lý kiến trúc — ước lượng đường bao thô kết hợp tầng xử lý họa âm — với các con số đủ nhỏ để bạn kiểm chứng trực tiếp bằng tay.

**Mạch bài học:** Triết lý lai DSP + Học sâu của Valin → Kiến thức cần nhớ (Thang Bark & cửa sổ Vorbis, Bộ lọc lược cao độ, Hàm mất mát nén mũ & làm mượt độ lợi) → 22 băng Bark & 42 đặc trưng đầu vào → Kiến trúc GRU 215 đơn vị & ngân sách 40 Mflop/s → Giải thích tính tay trọn vẹn độ lợi $$g_b$$, hệ số lược $$\alpha_b$$, hàm mất mát và 3 bước làm mượt → So sánh DF3, Mini-lab và Bài tập.

![Đường ERB của DeepFilterNet, dùng để đối chiếu 22 băng Bark và gain GRU của RNNoise]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. Sơ đồ của DeepFilterNet gồm 32 độ lợi ERB và bộ lọc phức 5 tap trên các bin STFT thấp. RNNoise nằm ở phía đối chiếu (không phải bản vẽ lại sơ đồ này): dùng 22 băng thang Bark, một mạng GRU dự đoán độ lợi từng băng và một bộ lọc lược cao độ giữa các họa âm. Cả hai đều theo hướng kiến trúc lai, nhưng khác nhau về thang băng tần, cơ chế tầng hai và quy mô mạng.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ tính được độ lợi băng tần của RNNoise từ mặt nạ IRM, liệt kê đúng 42 đặc trưng đầu vào cùng kiến trúc GRU 215 đơn vị trong bài báo, đối chiếu pipeline này với 32 băng ERB và bộ lọc phức 5 tap của DeepFilterNet, đồng thời rút ra các thực hành kỹ thuật hệ thống (giao diện khung, làm mượt độ lợi, tối ưu trọng số vừa bộ nhớ đệm) có thể áp dụng cho AudioWorklet ngay cả khi triển khai DF3.

## Kiến thức cần nhớ: Kiến trúc lai DSP + Học sâu của RNNoise gồm những trụ cột nào?

### 1. Biểu diễn theo băng cảm thụ (Bark-scale Bands) và cửa sổ Princen–Bradley
- **Là gì:** Thay vì dự đoán mặt nạ cho cả 481 bin DFT ở 48 kHz, RNNoise gom phổ thành **22 băng Bark** bằng các bộ lọc tam giác chồng lấp, trên khung 20 ms dùng cửa sổ Vorbis thỏa mãn điều kiện tái tạo hoàn hảo $$w^2(n) + w^2(n + N/2) = 1$$.
- **Nghiên cứu gì:** Nén không gian đầu ra gấp hơn 20 lần (từ 481 xuống 22) mà vẫn giữ nguyên độ phân giải mà tai người thực sự phân biệt được, giúp mạng nơ-ron không lãng phí tham số vào các bin tần số cao dày đặc.

### 2. Bộ lọc lược cao độ (Pitch Comb Filter) cho cấu trúc họa âm
- **Là gì:** Khi giọng nói phát âm hữu thanh (như các nguyên âm), năng lượng tập trung ở các đỉnh họa âm cách đều nhau đúng tần số cơ bản $$f_0 = 1/T$$, còn nhiễu nằm xen kẽ giữa các đỉnh đó. Cộng tín hiệu với phiên bản trễ đúng chu kỳ cao độ $$T$$ — tức $$X(k) + \alpha_b P(k)$$ — sẽ khuếch đại họa âm và triệt tiêu nhiễu nằm ở khe giữa.
- **Nghiên cứu gì:** Thực hiện cùng nhiệm vụ khôi phục cấu trúc tinh như bộ lọc phức 5 tap (deep filtering) của DeepFilterNet, nhưng bằng DSP thuần túy tốn rất ít flop.

### 3. Hàm mất mát nén mũ ($$\gamma = 1/2$$) và bộ giữ mức chống nhiễu nhạc
- **Là gì:** Sai số huấn luyện được tính trên căn bậc hai của độ lợi $$(g_b^{1/2} - \hat{g}_b^{1/2})^2$$, và khi suy luận độ lợi đầu ra được làm mượt bằng bộ lọc một cực $$\tilde{g}_b = \max(\lambda \tilde{g}_b^{(\mathrm{prev})}, \hat{g}_b)$$.
- **Nghiên cứu gì:** Tránh hai cực đoan phổ biến trong khử nhiễu: khử quá tay làm mất phụ âm nhẹ (khi dùng log-loss) và độ lợi bật/tắt đột ngột giữa các khung gây tiếng "nhiễu nhạc" (musical noise).

## Kế hoạch 60 phút

- **0–10 phút** — So sánh trực quan giữa độ lợi theo băng tần với bộ lọc phức đa tap.
- **10–25 phút** — Cấu trúc 22 băng Bark, công thức độ lợi và bộ lọc lược cao độ.
- **25–40 phút** — 42 đặc trưng đầu vào, mạng GRU, hàm mất mát mũ $$\gamma=1/2$$ và phân tích độ phức tạp.
- **40–50 phút** — Những thực hành hệ thống chuyển giao sang WASM và kỳ vọng thực tế về PESQ.
- **50–60 phút** — Mini-lab và bài tập.

## Giải thích cốt lõi

### Chia khung và gom băng tần

RNNoise hoạt động ở 48 kHz với cửa sổ **20 ms** và chồng lấp **50%** (hop 10 ms, 480 mẫu) — trùng khớp về khung thời gian với DeepFilterNet. Bước phân tích và tổng hợp dùng hàm cửa sổ Vorbis:

$$
w(n)=\sin\left(\frac{\pi}{2}\sin^{2}\left(\frac{\pi n}{N}\right)\right),
$$

thỏa mãn tiêu chí Princen–Bradley để phép cộng chồng lấp tái tạo chính xác tín hiệu hằng. Phổ tần số được gom thành **22 băng** theo xấp xỉ thang Bark của codec Opus (chia theo bước Bark ở tần số cao và giữ tối thiểu bốn bin DFT mỗi băng ở tần số thấp), với các trọng số tam giác $$w_b(k)$$ có tổng bằng 1. Năng lượng mỗi băng là:

$$
E(b)=\sum_k w_b(k)\,|X(k)|^{2}.
$$

Thay vì dự đoán mặt nạ cho cả 481 bin, mạng chỉ xuất một độ lợi cho mỗi băng. Giá trị mục tiêu khi huấn luyện là căn bậc hai của IRM:

$$
g_b=\sqrt{\frac{E_s(b)}{E_x(b)}},
$$

sau đó nội suy ngược lên từng bin bằng chính các trọng số tam giác đó: $$r(k)=\sum_b w_b(k)\,\hat{g}_b$$. Nhờ độ lợi luôn bị chặn trong đoạn $$[0,1]$$, mạng nhỏ giữ được độ ổn định cao — trái ngược với mạng ánh xạ (mapping) dự đoán biên độ thô không có biên chặn tự nhiên.

Tầng đường bao của DeepFilterNet kế thừa trực tiếp ý tưởng này trên thang khác: **32 băng ERB** kèm một độ lợi thực thay vì 22 băng Bark. Sự khác biệt lớn nằm ở tầng thứ hai: RNNoise không dự đoán hệ số lọc STFT phức mà dùng một **bộ lọc lược cao độ (pitch comb filter)**. Với $$P(k)$$ là DFT của tín hiệu trễ đúng chu kỳ cao độ $$T$$, bộ lọc tổ hợp $$X(k)+\alpha_b P(k)$$ rồi chuẩn hóa lại năng lượng từng băng. Hệ số pha trộn $$\alpha_b$$ được tính theo tương quan cao độ $$p_b$$ và độ lợi băng:

$$
\alpha_b=\min\left(\sqrt{\frac{p_b^{2}(1-g_b^{2})}{(1-p_b^{2})g_b^{2}}},\,1\right),
$$

kèm điều kiện biên $$\alpha_b=1$$ khi $$p_b\ge g_b$$, và $$\alpha_b=0$$ khi $$g_b=1$$ hoặc $$p_b=0$$. Tổng phức 5 tap của DeepFilterNet đạt hiệu quả củng cố họa âm tương tự ngay bên trong mạng (tới khoảng 5 kHz) nhưng tốn chi phí MAC cao hơn nhiều; còn bộ lọc lược của RNNoise thuần DSP, rất nhẹ nhưng phụ thuộc chặt vào độ chính xác của bộ ước lượng cao độ.

### Đặc trưng đầu vào và kiến trúc GRU

Bài báo cố định 42 đặc trưng đầu vào gồm: 22 hệ số cepstrum thang Bark, đạo hàm bậc một và bậc hai của 6 hệ số đầu (thêm 12), 6 hệ số DCT của tương quan cao độ, chu kỳ cao độ và 1 đặc trưng đo độ không dừng: $$22+12+6+1+1=42.$$ Do không chuẩn hóa trung bình cepstrum, mức năng lượng tuyệt đối vẫn được giữ lại. Đáp ứng tần số micro được mô phỏng trong lúc huấn luyện bằng bộ lọc bậc hai ngẫu nhiên với hệ số thuộc $$[-3/8,3/8]$$.

Mạng nơ-ron gồm **215 đơn vị** chia trên **bốn lớp ẩn** (lớp lớn nhất có 96 đơn vị); Valin ghi nhận GRU hoạt động nhỉnh hơn LSTM và đơn giản hơn trong bài toán này. Một đầu ra phát hiện tiếng nói (VAD) chỉ tốn thêm 24 trọng số nhưng giúp định hướng một lớp GRU phân tách rõ tiếng nói và nhiễu khi huấn luyện. Hàm mất mát cho độ lợi là:

$$
L(g_b,\hat{g}_b)=\left(g_b^{\gamma}-\hat{g}_b^{\gamma}\right)^{2},\qquad \gamma=\tfrac{1}{2},
$$

thay vì dùng binary cross-entropy. Khi $$\gamma\to 0$$, hàm mất mát tiến gần sai số log-năng lượng và dễ gây khử quá mức; $$\gamma=1/2$$ là điểm cân bằng được chọn trong bài báo. Các băng không có cả tiếng nói lẫn nhiễu được đánh dấu không xác định và loại khỏi hàm mất mát để tránh dạy mạng xuất giá trị 0 trên khoảng lặng hoặc âm thanh đã lọc thông thấp.

Bước làm mượt độ lợi giới hạn tốc độ suy giảm của từng băng:

$$
\tilde{g}_b=\max\left(\lambda \tilde{g}_b^{(\mathrm{prev})},\,\hat{g}_b\right),\qquad \lambda=0{,}6,
$$

trong đó $$\lambda=0{,}6$$ ở hop 10 ms tương đương thời gian tắt (reverberation time) khoảng **135 ms**. Giảm $$\lambda$$ làm âm thanh nghe khô hơn, còn $$\lambda=1$$ khiến độ lợi không bao giờ hạ xuống. Bộ giữ mức một cực này chính là kỹ thuật chống nhiễu nhạc kế thừa từ tư duy ngưỡng sàn phổ ở Chương 03.

## Giải thích: Tính tay trọn vẹn một băng Bark của RNNoise

Giả sử tại một băng tần hữu thanh (ví dụ băng 300–500 Hz), năng lượng tiếng nói sạch là $$E_s(b) = 16$$ và năng lượng nhiễu không tương quan là $$E_n(b) = 9$$, nên năng lượng tín hiệu hỗn hợp là $$E_x(b) = 16 + 9 = 25$$. Tương quan cao độ đo được ở băng này là $$p_b = 0{,}6$$.

1. **Tính độ lợi mục tiêu $$g_b$$:**
   $$ g_b = \sqrt{\frac{E_s(b)}{E_x(b)}} = \sqrt{\frac{16}{25}} = 0{,}8. $$
2. **Tính hệ số pha trộn bộ lọc lược $$\alpha_b$$:** Vì $$p_b = 0{,}6 < g_b = 0{,}8$$, ta thay thẳng vào công thức:
   $$ \alpha_b = \sqrt{\frac{0{,}6^2(1 - 0{,}8^2)}{(1 - 0{,}6^2)\cdot 0{,}8^2}} = \sqrt{\frac{0{,}36 \times 0{,}36}{0{,}64 \times 0{,}64}} = \frac{0{,}36}{0{,}64} = 0{,}5625. $$
   Kiểm tra nhanh trường hợp cực đoan: nếu tín hiệu có rất nhiều nhiễu ($$g_b = 0{,}5 < p_b = 0{,}6$$), điều kiện biên lập tức kẹp $$\alpha_b = 1$$ để bộ lọc lược lọc mạnh nhất giữa các họa âm; còn nếu tín hiệu sạch hoàn toàn ($$g_b = 1$$), $$\alpha_b = 0$$ để không làm méo giọng sạch!
3. **Tính hàm mất mát với $$\gamma = 1/2$$:** Nếu mạng dự đoán $$\hat{g}_b = 0{,}5$$ thay vì $$g_b = 0{,}8$$:
   $$ L(0{,}8,\,0{,}5) = \left(\sqrt{0{,}8} - \sqrt{0{,}5}\right)^2 \approx (0{,}8944 - 0{,}7071)^2 \approx 0{,}0351. $$
   So sánh với vùng độ lợi nhỏ (ví dụ $$g_b = 0{,}3$$ và $$\hat{g}_b = 0{,}0$$, cùng sai số tuyệt đối $$0{,}3$$): $$(\sqrt{0{,}3} - 0)^2 = 0{,}3000$$ — phạt nặng gấp **8,5 lần**! Nhờ căn bậc hai, hàm mất mát rất nhạy với việc khử sạch âm nhỏ xuống 0.
4. **Theo dõi 3 hop làm mượt độ lợi ($$\lambda = 0{,}6$$):** Giả sử hop trước đang ở $$\tilde{g}_b^{(0)} = 0{,}9$$ và tiếng nói đột ngột ngừng nên mạng dự đoán $$\hat{g}_b = 0{,}3$$ ở các hop kế tiếp:
   - Hop 1: $$\tilde{g}_b^{(1)} = \max(0{,}6 \times 0{,}9,\; 0{,}3) = 0{,}54$$.
   - Hop 2: $$\tilde{g}_b^{(2)} = \max(0{,}6 \times 0{,}54,\; 0{,}3) = 0{,}324$$.
   - Hop 3: $$\tilde{g}_b^{(3)} = \max(0{,}6 \times 0{,}324,\; 0{,}3) = \max(0{,}1944,\; 0{,}3) = 0{,}30$$.
   Độ lợi hạ êm trong 30 ms thay vì tụt thẳng đứng từ $$0{,}9 \to 0{,}3$$ trong một hop, tránh hẳn tiếng "khựng" cơ học.

### So sánh độ phức tạp với DeepFilterNet

Mạng có tổng cộng **87.503** trọng số — khi lượng tử hóa 8-bit, toàn bộ trọng số nằm gọn trong bộ nhớ đệm L2 mà bài báo ghi nhận không suy giảm chất lượng. Tính mỗi phép nhân-cộng là 2 flop, mạng tiêu tốn khoảng 175.000 flop mỗi khung, tương ứng **17,5 Mflop/s** ở tốc độ 100 khung/giây. Cộng thêm khoảng 7,5 Mflop/s cho FFT và 10 Mflop/s cho tìm cao độ ở 12 kHz, tổng chi phí chỉ vào khoảng **40 Mflop/s**. Mã C chưa vector hóa chỉ dùng khoảng **1,3%** một nhân Haswell i7-4800MQ và khoảng **14%** trên Cortex-A53 1,2 GHz. Con số này thấp hơn rất nhiều so với ngân sách ~0,35 GMAC/s của DeepFilterNet. Trên bảng so sánh của DeepFilterNet2, RNNoise đạt PESQ **2,33** và RTF **0,027**, so với bản DF2 tinh gọn đạt PESQ **3,08** và RTF **0,04** (tốc độ trên laptop cùng bậc, nhưng chất lượng PESQ của RNNoise thấp hơn trên tập kiểm thử đó).

Tập huấn luyện của RNNoise chỉ gồm khoảng 6 giờ tiếng nói và 4 giờ nhiễu (mở rộng thành 140 giờ qua lấy mẫu lại giữa 40 và 54 kHz), nhỏ hơn rất nhiều so với hơn 750 giờ tiếng nói trong cấu hình DeepFilterNet ICASSP. Do đó, các dạng xung click hay ngôn ngữ ngoài tập 6 giờ ban đầu rất dễ vượt khỏi khả năng của mô hình mặc định.

### Thực hành hệ thống chuyển giao sang sản phẩm

Chuỗi sản phẩm vẫn sử dụng AudioWorklet theo hướng DF3 (`DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`) chứ không thay bằng RNNoise. Tuy vậy, nhiều kỷ luật hệ thống từ RNNoise có giá trị trực tiếp: xử lý đúng một hop mỗi lần gọi (480 mẫu; quantum 128 mẫu vẫn cần bộ đệm vòng ở bài 05-03); tính trước hàm cửa sổ và bảng trọng số băng; cân nhắc làm mượt độ lợi (lưu ý $$\lambda=0{,}6$$ là hằng số của RNNoise, không tự áp mặc định cho DF3 mà chưa nghe kiểm tra); lượng tử hóa để giữ trọng số gọn trong cache; và giữ nguyên bộ lọc lược cao độ nếu triển khai mạng siêu nhỏ cỡ này (bỏ bộ lọc lược sẽ biến nó thành một thuật toán khác).

## Bẫy thường gặp

- Phủ nhận giá trị kỹ thuật của mã nguồn C chỉ vì điểm PESQ 2,33 trên bảng so sánh.
- Kỳ vọng mô hình RNNoise mặc định đạt chất lượng ngang mức PESQ 3,17 của DF3.
- Tái cài đặt phần GRU nhưng xóa bỏ bộ lọc lược cao độ.
- Dùng RNNoise làm mục tiêu thay vì làm ngưỡng sàn kiểm thử hồi quy ("chất lượng tối thiểu phải vượt qua") cho DF3 48 kHz.

## Mini-lab

**Mục tiêu.** Kiểm chứng tổng số đặc trưng, ngân sách flop mỗi giây và một bước làm mượt độ lợi bằng chính các hằng số trong bài báo (không cần tệp âm thanh hay kết nối mạng).

```bash
python3 - << 'PY'
bfcc, deriv, pitch_dct, pitch_period, nonstat = 22, 12, 6, 1, 1
features = bfcc + deriv + pitch_dct + pitch_period + nonstat
weights = 87503
flops_per_frame = weights * 2  # multiply-add counted as two flops
mflops = flops_per_frame * 100 / 1e6  # 10 ms hop
g_hat, g_prev, lam = 0.3, 0.9, 0.6
g_smooth = max(lam * g_prev, g_hat)
print(features, flops_per_frame, round(mflops, 1), round(g_smooth, 2))
PY
```

**Kết quả kỳ vọng.** `42 175006 17.5 0.54`. Độ lợi sau làm mượt giữ ở mức $$0{,}6\times 0{,}9=0{,}54$$ vì ước lượng tức thời 0,3 sẽ hạ băng quá nhanh; con số "175.000" trong bài báo là giá trị làm tròn của $$2\times 87503=175006$$.

**Lỗi thường gặp.** Quên cộng các thành phần đạo hàm nên báo 22 đặc trưng; dùng nhầm hop 20 ms làm giảm một nửa xuống 8,8 Mflop/s; đặt $$\lambda=0$$ nhưng vẫn gọi là "đã làm mượt"; hoặc triển khai RNNoise vào sản phẩm và kỳ vọng chất lượng ngang DF3.

## Bài tập

1. **Sơ đồ chuỗi xử lý.** Vẽ luồng PCM → cửa sổ 960 điểm → 22 băng → 42 đặc trưng → GRU → 22 độ lợi → bộ lọc lược cao độ → tổng hợp, và đánh dấu rõ bước nhảy hop 10 ms.
2. **Hệ số pha trộn.** Khi $$g_b=1$$, hệ số $$\alpha_b$$ bằng bao nhiêu và bộ lọc lược tác động như thế nào lên khung tiếng nói sạch?
3. **Tính bước làm mượt.** Cho độ lợi làm mượt trước đó bằng 0,8, ước lượng mới bằng 0,2 và $$\lambda=0{,}6$$. Độ lợi đầu ra hiện tại là bao nhiêu? Cần bao nhiêu hop liên tiếp có ước lượng 0,2 để độ lợi giảm xuống dưới 0,3?
4. **Thiết kế API.** Phác thảo giao diện `process_frame(state, in[480], out[480])` và liệt kê ít nhất ba trường trong `state` bắt buộc phải bảo toàn qua các lần gọi.

### Gợi ý đáp án

1. Bước nhảy hop 480 mẫu ở 48 kHz; mạng GRU nhận 42 đặc trưng đầu vào và xuất 22 độ lợi kèm 1 tín hiệu VAD; bộ lọc lược dùng chu kỳ cao độ $$T$$ cùng hệ số $$\alpha_b$$ theo từng băng trước khi chuẩn hóa lại năng lượng băng.
2. Nhờ điều kiện biên, khi $$g_b=1$$ thì $$\alpha_b=0$$: bộ lọc lược được bỏ qua hoàn toàn để tiếng nói sạch không bị méo do lọc cao độ.
3. Hop đầu: $$\max(0{,}6\times 0{,}8,\,0{,}2)=\max(0{,}48,\,0{,}2)=0{,}48$$; hop thứ hai: $$\max(0{,}6\times 0{,}48,\,0{,}2)=0{,}288 < 0{,}3$$. Vậy cần đúng 2 hop.
4. Tối thiểu gồm trạng thái ẩn GRU, mảng độ lợi đã làm mượt $$\tilde{g}_b$$ và bộ đệm lịch sử OLA / cao độ; xóa bất kỳ thành phần nào giữa luồng sẽ gây tiếng click hoặc lọt một đoạn nhiễu ngắn (bài 05-04).

## Đọc thêm

- Valin, “A Hybrid DSP/Deep Learning Approach to Real-Time Full-Band Speech Enhancement,” [arXiv:1709.08243](https://arxiv.org/abs/1709.08243) (công bố tại IEEE MMSP 2018 và được DeepFilterNet trích dẫn).
- Mã nguồn và trọng số lượng tử hóa 8-bit: [github.com/xiph/rnnoise](https://github.com/xiph/rnnoise).
- Bộ khử MMSE của SpeexDSP — mốc đối chiếu cổ điển trong cùng bài báo.
- Schröter et al., [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) và [arXiv:2205.05474](https://arxiv.org/abs/2205.05474) — đối chiếu 32 băng ERB và bảng PESQ 2,33 so với 3,08.

## Video tham khảo

- [RNNoise, Neural Speech Enhancement, and the Browser](https://www.youtube.com/watch?v=nsscrYdrGRE) — W3C, tiếng Anh. **Xem trước.** Trình bày trực tiếp sự kết hợp giữa đặc trưng DSP, mạng GRU nhỏ và độ lợi theo băng chạy trong trình duyệt với look-ahead rất ngắn.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Dùng để đối chiếu kiến trúc ERB + deep filter quy mô lớn hơn mà RNNoise không đặt mục tiêu thay thế về mặt điểm số.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Đặt RNNoise trong bức tranh thước đo chất lượng sản phẩm thực tế.
