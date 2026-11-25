---
layout: post
title: "06-02 Lượng tử hóa cho mô hình tiếng nói"
chapter: "06"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter06
lesson_type: required
draft: false
---

Trong thị giác máy tính, lượng tử hóa một mạng phân loại ảnh xuống INT8 thường chỉ làm độ chính xác top-1 nhích xuống 0,3% — mắt người chẳng hề nhận ra. Thế nhưng khi bạn mang đúng công thức lượng tử hóa đó áp vào một mô hình khử nhiễu giọng nói, chỉ một sai số làm tròn vỏn vẹn **0,004** ở tầng xuất mặt nạ gain cũng đủ biến khoảng lặng thành tiếng rít kim loại khó chịu (musical noise) hoặc thổi bay toàn bộ phụ âm gió nhẹ! Tại sao bài toán tiếng nói lại nhạy cảm với độ phân giải gần 0 đến vậy?

**Lượng tử hóa (quantization)** giúp thu nhỏ dung lượng trọng số và thường đẩy nhanh tốc độ suy luận của mô hình tăng cường giọng nói. Điều này ảnh hưởng trực tiếp tới dung lượng tải xuống của bản WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) và hệ số thời gian thực trên CPU. Tuy nhiên, lượng tử hóa không cẩn thận có thể làm méo giọng nói hoặc gây trôi trạng thái hồi tiếp. Rủi ro lớn nhất không nằm ở các trọng số có giá trị lớn mà nằm ở các hệ số khuếch đại (gain) gần 0, vì chúng nhân trực tiếp lên từng bin tần số. Bài học này trình bày lượng tử hóa INT8 ở góc độ kỹ thuật triển khai, cách hiệu chuẩn trên dữ liệu giọng nói thay vì ảnh, kèm một bài lab số học tự kiểm chứng.

**Mạch bài học:** Vì sao tiếng nói nhạy hơn ảnh khi nén xuống INT8 → Kiến thức cần nhớ (Ánh xạ tuyến tính INT8, Độ nhạy tương đối theo thang dB gần 0, Hiệu chuẩn theo miền giọng nói & giữ lớp nhạy cảm ở `float32`) → Công thức lượng tử hóa đối xứng & bảng 4 chế độ (Dynamic, Static PTQ, QAT, Weight-only) → Giải thích tính tay sai số theo dB trên 4 bin gain và so sánh tỉ lệ per-tensor vs. per-channel → Cổng kiểm duyệt phát hành, Mini-lab và Bài tập.

![Trọng số đã lượng tử hóa được đóng vào kho mô hình trước khi trình duyệt tải WASM]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Hình. Quá trình lượng tử hóa diễn ra trước bước đóng gói và biên dịch WASM mà trình duyệt sẽ tải về.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ phân biệt được lượng tử hóa INT8 động và tĩnh, tính được hệ số tỉ lệ đối xứng cùng sai số tuyệt đối lớn nhất trên một véctơ gain, giải thích được vì sao các bin có gain gần 0 gây suy giảm chất lượng nghe rõ rệt nhất, và thiết kế được quy trình kiểm duyệt kết hợp nghe thử A/B với SI-SDR trước khi phát hành trọng số lượng tử hóa.

## Kiến thức cần nhớ: Toán học và cảm thụ âm thanh phía sau lượng tử hóa INT8

### 1. Lượng tử hóa tuyến tính (Uniform Affine / Symmetric Quantization)
- **Là gì:** Nén số thực 32-bit (`float32`, 4 byte) xuống số nguyên 8-bit (`int8`, 1 byte, 255 mức đối xứng trong $$[-127, 127]$$) bằng phép chia cho bước lượng tử $$s$$ và làm tròn: $$q = \mathrm{clip}(\mathrm{round}(g / s), -128, 127)$$.
- **Nghiên cứu gì:** Giảm gấp 4 lần dung lượng trọng số và lưu lượng băng thông bộ nhớ, đồng thời cho phép dùng các lệnh nhân-cộng số nguyên nhanh hơn trên CPU — đổi lại là nhiễu làm tròn bị chặn bởi $$s/2$$.

### 2. Sai số tuyệt đối đều vs. Cảm thụ logarit (dB) của tai người
- **Là gì:** Lượng tử hóa đều tạo ra sai số *tuyệt đối* như nhau ($$\le s/2$$) trên toàn dải giá trị, nhưng tai người cảm nhận âm lượng theo thang **logarit (decibel)** — tức phụ thuộc vào sai số *tương đối* $$\hat{g}/g$$.
- **Nghiên cứu gì:** Giải thích nghịch lý cốt lõi của bài: cùng một sai số tuyệt đối $$0{,}0039$$ là hoàn toàn vô hại ở $$g = 0{,}5$$ (chỉ lệch 0,07 dB), nhưng lại là thảm họa gần **+6 dB** ở bin nhiễu có $$g = 0{,}004$$!

### 3. Hiệu chuẩn (Calibration) và Lượng tử hóa hỗn hợp (Mixed Precision)
- **Là gì:** Quy trình chạy một tập âm thanh đại diện (khoảng lặng, giọng nhỏ, tạp âm đám đông, SNR thấp) qua mô hình để ước lượng dải động từng lớp (Static PTQ), kết hợp giữ nguyên các lớp nhạy cảm (tầng xuất gain, trạng thái hồi tiếp GRU) ở `float32`.
- **Nghiên cứu gì:** Tránh hai lỗi chí mạng: dải tỉ lệ bị kéo giãn bởi một giá trị ngoại lai (per-tensor thay vì per-channel) và sai số lượng tử hóa tích lũy thành trôi trạng thái trên cuộc gọi dài.

## Kế hoạch 60 phút

- **0–10 phút** — Dung lượng tải và hệ số thời gian thực của bản WASM họ DeepFilter.
- **10–25 phút** — Lượng tử hóa INT8 đối xứng, tỉ lệ theo tensor so với tỉ lệ theo kênh.
- **25–40 phút** — Dữ liệu âm thanh hiệu chuẩn và vì sao không thể dùng thống kê của ImageNet.
- **40–50 phút** — Các bin gain gần 0, nhiễu dư và hiện tượng trôi trạng thái.
- **50–60 phút** — Thực hành mini-lab, bẫy thường gặp và làm bài tập.

## Giải thích cốt lõi

### Công thức tỉ lệ lượng tử hóa

Một giá trị dấu phẩy động $$g$$ được ánh xạ sang mã số nguyên $$q$$ thông qua hệ số tỉ lệ $$s$$ và điểm không (zero-point) tùy chọn $$z$$:

$$
g \approx s\,(q - z).
$$

Với véctơ gain sử dụng lượng tử hóa đối xứng (không có zero-point):

$$
s = \frac{\max_i |g_i|}{127}, \qquad q_i = \mathrm{clip}\big(\mathrm{round}(g_i / s), -128, 127\big), \qquad \hat g_i = s\, q_i.
$$

Khi phép làm tròn hoạt động chuẩn, sai số khôi phục trên mỗi phần tử không vượt quá khoảng nửa bước lượng tử $$s/2$$. Các nhân tính toán GEMM sẽ thực hiện phép nhân trên số nguyên rồi quy đổi ngược về thang số thực. Đối với lớp tích chập (convolution), dùng hệ số tỉ lệ **theo từng kênh (per-channel)** thường vượt trội so với dùng một hệ số duy nhất cho cả tensor, bởi một kênh có giá trị ngoại lai lớn sẽ làm phình hệ số $$s$$ của toàn bộ các kênh còn lại.

### Nơi sai số lượng tử hóa trở thành tạp âm nghe thấy được

Giả sử giá trị gain lớn nhất bằng $$1$$. Khi đó $$s = 1/127 \approx 0.00787$$, và sai số tuyệt đối chỉ ở mức vài phần nghìn. So với một bin có biên độ đầy thang, sai số này không đáng kể; nhưng với một bin có gain thực là $$0.004$$, chỉ một mức mã nguyên đã tương đương toàn bộ tín hiệu. Trong bài mini-lab, véctơ $$[1.0,\ 0.5,\ 0.02,\ 0.004,\ 0.0]$$ được lượng tử hóa thành các mã $$[127,\ 64,\ 3,\ 1,\ 0]$$. Bin $$0.004$$ bị đẩy lên thành $$1/127 \approx 0.00787$$ — tức gần gấp đôi giá trị thật của một bin yếu — trong khi sai số tuyệt đối lớn nhất trên cả véctơ là khoảng $$0.00394$$, xuất phát từ nửa bước làm tròn ở giá trị $$0.5$$ chứ không phải ở bin đầy thang.

Trong khử nhiễu giọng nói, những giá trị gain nhỏ đó đại diện cho các bin bị nhiễu lấn át và các họa âm yếu. Ép một họa âm về mã $$0$$ sẽ khiến nguyên âm nghe mỏng và khô; ngược lại, làm tròn một bin gần im lặng lên 1 mức lượng tử sẽ làm rò rỉ một nền âm đơn điệu (tonal floor) — nguyên nhân phổ biến gây nhiễu nhạc (musical noise). Sai số trọng số trong lớp tích chập còn được các lớp phía sau làm mượt bớt, nhưng sai số ở đầu ra gain lại nhân thẳng vào các bin STFT rồi được cộng dồn ở bước overlap-add. Vì vậy, cần hiệu chuẩn cẩn thận và nghe kiểm tra trực tiếp đầu ra gain, kể cả khi giữ riêng nhánh này ở `float32`.

## Giải thích: Tính tay sai số lượng tử hóa theo thang dB và bẫy Per-Tensor

### Phép tính 1: Quy đổi sai số lượng tử hóa INT8 sang decibel trên 4 bin mẫu
Với $$s = 1/127 \approx 0{,}007874$$, hãy lập bảng kiểm tra từng phần tử của véctơ $$g = [1{,}0,\; 0{,}5,\; 0{,}02,\; 0{,}004]$$ và tính sai số cảm thụ $$\Delta\text{dB} = 20\log_{10}(\hat{g}/g)$$:

| Gain thật $$g$$ | $$g / s$$ | Mã nguyên $$q$$ | Gain khôi phục $$\hat{g} = s\,q$$ | Sai số tuyệt đối $$\vert \hat{g} - g \vert$$ | Sai số theo dB ($$20\log_{10}(\hat{g}/g)$$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $$1{,}000$$ | $$127{,}00$$ | $$127$$ | $$1{,}0000$$ | $$0{,}0000$$ | $$0{,}00\text{ dB}$$ (chính xác) |
| $$0{,}500$$ | $$63{,}50$$ | $$64$$ | $$0{,}5039$$ | $$0{,}00394$$ | $$+0{,}07\text{ dB}$$ (không nghe thấy) |
| $$0{,}020$$ | $$2{,}54$$ | $$3$$ | $$0{,}0236$$ | $$0{,}00362$$ | $$+1{,}45\text{ dB}$$ (bắt đầu nhận ra) |
| $$0{,}004$$ | $$0{,}508$$ | $$1$$ | $$0{,}00787$$ | $$0{,}00387$$ | **$$+5{,}88\text{ dB}$$** (rò rỉ nhiễu rõ rệt!) |

Hãy nhìn cột cuối cùng: dù sai số tuyệt đối ở $$0{,}500$$ còn *lớn hơn* ở $$0{,}004$$ một chút ($$0{,}00394$$ so với $$0{,}00387$$), nhưng trên thang logarit mà tai người nghe, bin $$0{,}004$$ bị khuếch đại vọt gần **+6 dB** (gấp đôi biên độ, gấp bốn lần công suất nhiễu lọt qua!).

### Phép tính 2: Vì sao Per-Channel thắng áp đảo Per-Tensor trên lớp tích chập?
Giả sử một lớp `Conv` có 2 kênh: kênh 0 có trọng số cực đại $$4{,}0$$, còn kênh 1 chỉ có trọng số cực đại $$0{,}1$$.
- **Lượng tử hóa Per-Tensor (dùng chung một $$s$$):** $$s = 4{,}0 / 127 \approx 0{,}0315$$. Toàn bộ kênh 1 bị ép vào chỉ $$\lfloor 0{,}1 / 0{,}0315 \rfloor = 3$$ mức số nguyên $$\{-3, -2, -1, 0, 1, 2, 3\}$$ — mất hơn **5 bit** độ phân giải!
- **Lượng tử hóa Per-Channel (mỗi kênh một $$s_c$$):** Kênh 0 dùng $$s_0 = 4{,}0/127$$, còn kênh 1 dùng $$s_1 = 0{,}1/127 \approx 0{,}000787$$ — giữ trọn vẹn cả 255 mức INT8 cho kênh 1!

### Các phương pháp lượng tử hóa

| Chế độ | Nguyên lý | Ưu điểm | Hạn chế |
|--------|---|----|-------|
| Động (Dynamic) | Lượng tử hóa giá trị kích hoạt ngay khi chạy | Dễ thử nghiệm | Phát sinh chi phí tính toán thêm; độ trễ biến động |
| PTQ tĩnh (Static PTQ) | Hiệu chuẩn dải giá trị trước khi triển khai | Suy luận nhanh | Cần tập âm thanh hiệu chuẩn mang tính đại diện |
| QAT | Huấn luyện có mô phỏng nhiễu lượng tử | Chất lượng tốt khi hội tụ | Chi phí huấn luyện cao |
| Chỉ trọng số (Weight-only) | Lưu trọng số ở INT8 hoặc INT4, giữ kích hoạt dạng float | Giảm dung lượng đơn giản | Mức tăng tốc thấp hơn |

Với bài toán tăng cường giọng nói streaming, lượng tử hóa sau huấn luyện dạng tĩnh (Static PTQ) bằng bộ công cụ của ONNX Runtime là bước thử nghiệm đầu tiên hợp lý. Chỉ nên chuyển sang huấn luyện có nhận biết lượng tử hóa (QAT) nếu chỉ số SI-SDR hoặc kết quả nghe thử bị sụt giảm rõ rệt. Lượng tử hóa là công đoạn thuộc khâu **đóng gói**: nó phải thực hiện trước khi nén tệp mô hình và trước khi trình duyệt biên dịch WASM (bài 06-04, bài 07-03). Không nên lượng tử hóa một đồ thị khi bước STFT vẫn còn lệch với môi trường sản phẩm.

Trong quy trình này, ONNX vẫn giữ vai trò định dạng trao đổi đồ thị: tệp sau khi lượng tử hóa được đưa vào gói mô hình rồi mới tới bước chạy trên WASM.

### Tập hiệu chuẩn phải là giọng nói, không phải ImageNet

Nếu chỉ hiệu chuẩn trên nhiễu trắng (white noise), hệ số tỉ lệ thu được sẽ sai lệch khi gặp tạp âm đám đông (babble) ở quán cà phê hoặc giọng nói gần micro. Tập hiệu chuẩn cần bao phủ đầy đủ các tình huống: khoảng lặng, chỉ có nhiễu, giọng nói gần âm lượng lớn, bản trộn SNR thấp và đoạn mẫu có tiếng vọng dư nếu hệ thống có xử lý vọng. Một phút bản trộn đa dạng kiểu DNS là mức tối thiểu để thực hành; trong môi trường sản phẩm cần tập dữ liệu rộng hơn và được đóng băng cố định. Nếu bỏ qua bước này, mô hình dễ gặp hiện tượng bơm tiếng (pumping) hoặc nhiễu dư gắt mà các phép đo trên giọng sạch không phát hiện ra.

### Các thành phần thường giữ nguyên `float32`

Các cổng tính toán theo từng phần tử (elementwise) nhạy cảm, tầng xuất hệ số gain cuối cùng và những lớp quá nhỏ (nơi chi phí chuyển đổi INT8 lớn hơn lợi ích mang lại) thường được giữ lại ở `float32`. Nguyên tắc giữ lớp đầu và lớp cuối là kinh nghiệm thực tiễn phổ biến chứ không phải định lý cố định, nên vẫn cần đo kiểm thực tế. Trạng thái hồi tiếp là trường hợp đặc biệt cần lưu ý: một lỗi tràn số vốn chỉ gây ra một tiếng tách nhỏ trên mạng truyền thẳng lại có thể tích lũy và dao động đến hết cuộc gọi trong mạng hồi tiếp. Cần theo dõi dải giá trị trạng thái trên luồng âm thanh liên tục dài 30 phút (bài 05-04).

### Cổng kiểm duyệt trước khi phát hành

1. Đo độ chênh lệch SI-SDR và DNSMOS so với mô hình `float` trên tập kiểm thử đóng băng (Chương 08).
2. Nghe thử bắt buộc chọn (forced-choice) trên tối thiểu 10 cặp đoạn âm thanh, bao gồm cả các trường hợp có gain gần 0.
3. Chạy thử trên luồng âm thanh dài để phát hiện sớm hiện tượng trôi trạng thái.
4. Đo trực tiếp hệ số thời gian thực trên thiết bị đích, không suy diễn tốc độ chỉ từ việc dung lượng tệp giảm.

Các ghi chú khảo sát về FastEnhancer và `faster-enhancer.c` cho thấy các nhân tính toán INT8 hợp nhất có thể cải thiện hệ số thời gian thực đáng kể, trong khi PTQ mặc định của ORT thường cho mức cải thiện khiêm tốn hơn — do đó luôn cần tự đo đạc. Ngoài ra, mức tăng tốc 20–30% mà README của gói gán cho SIMD (bài 06-03) là một cơ chế tối ưu khác, không phải kết quả của lượng tử hóa.

## Mini-lab

Lưu đoạn mã sau thành `quant_gain.py` và chạy bằng lệnh `python3 quant_gain.py`. Script sử dụng hàm `round` của Python (quy tắc làm tròn nửa về số chẵn), khớp với các mã đầu ra bên dưới.

```python
g = [1.0, 0.5, 0.02, 0.004, 0.0]
scale = max(abs(x) for x in g) / 127.0
q = [max(-128, min(127, int(round(x / scale)))) for x in g]
hat = [scale * qi for qi in q]
err = max(abs(a - b) for a, b in zip(g, hat))
print(f"scale={scale:.8f}")
print(f"q={q}")
print(f"max_abs_error={err:.8f}")
```

**Kết quả kỳ vọng**

```text
scale=0.00787402
q=[127, 64, 3, 1, 0]
max_abs_error=0.00393701
```

**Lỗi thường gặp**

- Chia nhầm cho $$128$$: biên dương của kiểu INT8 có dấu là $$127$$, nên mã đầy thang phải là $$127$$ chứ không phải $$128$$.
- Chỉ kiểm tra sai số tương đối trên bin $$1.0$$ rồi kết luận bộ lượng tử hóa vô hại, trong khi bin $$0.004$$ mới là trường hợp tiêu biểu của khử nhiễu giọng nói.
- Lượng tử hóa trước khi đồng bộ chuẩn hóa STFT, khiến độ lệch dù chỉ một bin tần số bị đóng cứng vào hệ số tỉ lệ.
- Nhầm lẫn rằng bài lab minh họa dùng cùng cơ chế zero-point với bộ lượng tử hóa tĩnh của ORT trong sản phẩm; công cụ thực tế có thể dùng lược đồ affine có zero-point, còn bài lab chủ đích dùng lược đồ đối xứng.

## Bẫy thường gặp

- Chỉ hiệu chuẩn mô hình trên dữ liệu nhiễu trắng.
- Phát hành mô hình INT8 nhưng không ghi lại độ chênh lệch chất lượng cho nhóm hỗ trợ kỹ thuật.
- Bỏ qua nguy cơ tràn số bên trong các tensor trạng thái.
- Coi tệp `.tar.gz` có dung lượng nhỏ hơn là bằng chứng cho thấy AudioWorklet đã đáp ứng ngân sách thời gian thực.

## Bài tập

1. Tính lại hệ số tỉ lệ đối xứng cho tập trọng số nằm trong khoảng $$[-0.8,\ 0.8]$$. Giá trị $$s$$ bằng bao nhiêu và $$0.8$$ ánh xạ sang mã nguyên nào?
2. Liệt kê 8 loại đoạn âm thanh cần có trong một tập hiệu chuẩn sau huấn luyện kiểu Mezon.
3. Thiết kế một phiếu đánh giá nghe mù so sánh bản `float` với bản INT8, trong đó có ít nhất hai điều kiện kiểm tra vùng gain gần 0 (giọng nói nhỏ và nền nhiễu).
4. Tra cứu tài liệu chính thức của ONNX Runtime và nêu tên điểm vào (entry point) cho tác vụ lượng tử hóa mà bạn sẽ sử dụng (chưa cần chạy thực tế).
5. Dựa trên bin $$0.004$$ trong bài mini-lab, giải thích vì sao tầng xuất gain là ứng viên kém phù hợp cho lượng tử hóa INT8 mạnh, ngay cả khi các lớp tích chập vẫn lượng tử hóa tốt.

### Gợi ý đáp án

1. $$s = 0.8 / 127$$. Vì $$0.8$$ là giá trị tuyệt đối lớn nhất, nó ánh xạ tới mã $$127$$. Không dùng $$255$$ trừ khi chuyển sang lược đồ affine không dấu và nêu rõ quy ước.
2. Tám loại đoạn âm thanh gồm: khoảng lặng, chỉ có nhiễu, giọng nói âm lượng lớn, tiếng nói thì thầm, tạp âm đám đông ở SNR thấp, tiếng gõ bàn phím không dừng, một âm đơn tần (tone), và đoạn mẫu có tiếng vọng dư.
3. Sử dụng bài kiểm thử bắt buộc chọn (forced-choice), cân bằng âm lượng giữa hai mẫu, ẩn nhãn thuật toán và bổ sung tiêu chí đánh giá “nhiễu nhạc / giọng bị mỏng”.
4. Bắt đầu từ mục lượng tử hóa trong tài liệu ONNX Runtime: sử dụng quy trình Static PTQ kèm một `CalibrationDataReader`. Tên lớp cụ thể có thể thay đổi theo phiên bản API, nên cần trích dẫn đúng trang tài liệu đang dùng.
5. Giá trị $$0.004$$ bị làm tròn lên xấp xỉ $$0.00787$$, tức sai lệch tương đối gần gấp đôi áp thẳng lên một bin tần số. Khác với sai số trọng số ở các lớp ẩn vốn được các lớp sau lọc bớt, sai số trực tiếp trên mặt nạ gain sẽ đi thẳng ra tín hiệu âm thanh.

## Đọc thêm

- Hướng dẫn lượng tử hóa trong [tài liệu ONNX Runtime](https://onnxruntime.ai/docs/).
- Jacob và cộng sự — tài liệu nền tảng kinh điển về lượng tử hóa cho suy luận thuần số nguyên trên thiết bị di động.
- Các ghi chú về FastEnhancer / `faster-enhancer.c` liên quan tới runtime tăng cường giọng nói dùng INT8 (tài liệu tham khảo mở rộng).
- Các thảo luận về dung lượng mô hình và hiệu năng thời gian thực trong kho mã nguồn gốc DeepFilterNet.

## Video tham khảo

- [Quantization explained with PyTorch - Post-Training Quantization, Quantization-Aware Training](https://www.youtube.com/watch?v=0VdNflU08yA) — Umar Jamil, tiếng Anh. **Xem trước.** Video trình bày rõ lượng tử hóa sau huấn luyện (PTQ) và lượng tử hóa có nhận biết khi huấn luyện (QAT), giải thích vì sao một giá trị ngoại lai lớn trong khoảng min-max lại làm giảm độ phân giải của toàn bộ các giá trị gain nhỏ.
- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, tiếng Anh. Đoạn nói về INT8 minh họa cách đưa lượng tử hóa vào ONNX Runtime sau phần lý thuyết trên PyTorch.
- [Enable Model Quantization for ONNX and TensorRT!](https://www.youtube.com/watch?v=phmFvMOHt4I) — Nicolai Nielsen Tech, tiếng Anh. Minh họa quy trình nạp một đồ thị ONNX đã lượng tử hóa (phần TensorRT chỉ mang tính tham khảo, trọng tâm của bài vẫn là rủi ro trên mô hình giọng nói).
