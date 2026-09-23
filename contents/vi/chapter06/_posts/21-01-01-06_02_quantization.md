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

**Lượng tử hóa** thu nhỏ trọng số và thường làm suy luận tăng cường tiếng nói nhanh hơn. Điều đó quyết định dung lượng tải WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) và hệ số realtime trên CPU. Nó cũng có thể làm hỏng tiếng nói hoặc làm state hồi tiếp trôi. Lỗi nguy hiểm không nằm ở trọng số lớn. Nó nằm ở gain gần 0, vì các gain đó nhân thẳng lên bin tần số. Bài này trình bày INT8 ở mức kỹ sư, hiệu chuẩn trên tiếng nói chứ không trên ảnh, và một lab số tự chấm.

![Trọng số đã lượng tử hóa được đóng vào kho mô hình trước khi trình duyệt tải WASM]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. Quantization happens before the WASM the browser loads.*

## Mục tiêu học tập

Bạn phân biệt lượng tử hóa INT8 động và tĩnh, tính thang đối xứng cùng sai số tuyệt đối lớn nhất trên một vector gain, giải thích vì sao bin có gain gần 0 gây hỏng nghe rõ nhất, và thiết kế cổng nghe A/B cộng SI-SDR trước khi ship trọng số đã lượng tử.

## Kế hoạch 60 phút

- **0–10 phút** — Dung lượng và hệ số realtime của một lượt tải WASM họ DeepFilter.
- **10–25 phút** — INT8 đối xứng, thang theo tensor đối với thang theo kênh.
- **25–40 phút** — Audio hiệu chuẩn, vì sao thống kê ImageNet không mang sang.
- **40–50 phút** — Gain gần 0, nhiễu dư, trôi state.
- **50–60 phút** — Mini-lab, bẫy, bài tập.

## Giải thích cốt lõi

### Thang bạn sẽ code

Giá trị float \(g\) ánh xạ sang mã nguyên \(q\) với thang \(s\) và zero-point tùy chọn \(z\):

$$
g \approx s\,(q - z).
$$

Với vector gain đối xứng, không zero-point:

$$
s = \frac{\max_i |g_i|}{127}, \qquad q_i = \mathrm{clip}\big(\mathrm{round}(g_i / s), -128, 127\big), \qquad \hat g_i = s\, q_i.
$$

Sai số khôi phục mỗi phần tử thường không quá khoảng nửa bước, \(s/2\), khi phép làm tròn đúng kỳ vọng. Kernel GEMM nhân số nguyên rồi đưa về thang float. Thang **theo kênh** trên convolution thường thắng một thang thô cho cả tensor, vì một kênh ngoại lai nếu không sẽ phình \(s\) của mọi kênh.

### Chỗ sai số thành tiếng nghe được

Giả sử gain đỉnh là \(1\). Khi đó \(s = 1/127 \approx 0.00787\), và sai số tuyệt đối chỉ vài phần nghìn. So với bin đầy thang thì chẳng là gì. So với bin có gain thật \(0.004\), một mã là toàn bộ tín hiệu. Vector trong mini-lab \([1.0,\ 0.5,\ 0.02,\ 0.004,\ 0.0]\) lượng tử thành mã \([127,\ 64,\ 3,\ 1,\ 0]\). Bin \(0.004\) nhảy tới \(1/127 \approx 0.00787\). Đó gần như là gấp đôi một bin yếu, còn sai số tuyệt đối lớn nhất của vector khoảng \(0.00394\), đến từ nửa bước của \(0.5\), không phải từ bin đầy thang.

Trong khử nhiễu, những gain nhỏ đó là bin do nhiễu thống trị và các họa âm yếu. Ép một họa âm về mã \(0\) thì nguyên âm bị mỏng. Làm tròn bin gần im lên một quantum thì bạn rò một sàn tonal đều, nguồn thường gặp của nhiễu nhạc. Sai số trọng số trong convolution còn bị các lớp sau lọc. Sai số gain nhân thẳng lên bin STFT rồi bị overlap-add cộng dồn. Hãy hiệu chuẩn và nghe đầu gain ngay cả khi bạn để nó ở float32.

### Các cách làm

| Chế độ | Ý | Ưu | Nhược |
|--------|---|----|-------|
| Động | Kích hoạt được lượng tử lúc chạy | Dễ thử | Chi phí thêm; trễ biến thiên |
| PTQ tĩnh | Hiệu chuẩn khoảng giá trị offline | Suy luận nhanh | Cần audio đại diện |
| QAT | Train kèm nhiễu lượng tử | Chất lượng tốt khi hội tụ | Tốn kém |
| Chỉ trọng số | Trọng số INT8 hoặc INT4, kích hoạt float | Giảm dung lượng đơn giản | Tăng tốc ít hơn |

Với tăng cường streaming, lượng tử hóa sau train kiểu tĩnh trong toolchain ONNX Runtime là thí nghiệm đầu hợp lý. Chuyển sang train có nhận biết lượng tử khi SI-SDR hoặc bài nghe tụt. Lượng tử hóa là bước **đóng gói**: nó chạy trước khi nén kho và trước khi trình duyệt biên dịch WASM (bài 06-04, bài 07-03). Đừng lượng tử một đồ thị mà STFT vẫn lệch với sản phẩm.

ONNX ở đây vẫn là định dạng trao đổi đồ thị. File đã lượng tử đi vào kho, rồi mới tới WASM.

### Hiệu chuẩn là tiếng nói, không phải ImageNet

Tập chỉ toàn white noise cho ra thang lệch babble quán cà phê và tiếng near-end. Hãy gồm im lặng, chỉ nhiễu, tiếng nói gần to, mix SNR thấp, và clip kiểu echo dư nếu echo nằm trong phạm vi. Một phút mix kiểu DNS đủ đa dạng là mức tối thiểu để học. Sản phẩm dùng tập rộng hơn và đóng băng tập đó. Nếu không, bạn gặp pumping hoặc nhiễu dư gắt mà điểm trên tiếng sạch không thấy.

### Phần thường giữ float32

Cổng elementwise nhạy, đầu gain cuối, và lớp rất nhỏ nơi chi phí INT8 lớn hơn lợi ích thường ở lại float. Lớp đầu và lớp cuối là heuristic phổ biến, không phải định lý. Hãy kiểm. State hồi tiếp là trường hợp riêng: tràn số mà ở mạng thuận chỉ là một click trên một bin có thể rung đến hết cuộc gọi. Theo dõi khoảng state trên stream 30 phút (bài 05-04).

### Cổng xác nhận

1. Delta SI-SDR và DNSMOS so với mô hình float trên tập đóng băng (Chương 08).
2. Từ mười clip ghép đôi trở lên, buộc chọn, gồm các trường hợp gain gần 0.
3. Stream dài để bắt trôi state.
4. Hệ số realtime trên thiết bị đích, không chỉ vì file nhỏ hơn.

Ghi chú khảo sát về FastEnhancer và faster-enhancer.c cho thấy kernel INT8 hợp nhất có thể đổi hệ số realtime khá nhiều. Lượng tử hóa sau train của ORT thường đổi ít hơn. Hãy đo. Mức 20–30% mà README gói gán cho SIMD (bài 06-03) là một khoản tăng tốc khác, không phải kết quả lượng tử hóa.

## Mini-lab

Chạy `python3 quant_gain.py` với script sau. Script dùng `round` của Python (làm tròn nửa về số chẵn), khớp các mã bên dưới.

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

**Expected**

```text
scale=0.00787402
q=[127, 64, 3, 1, 0]
max_abs_error=0.00393701
```

**Failure modes**

- Chia cho \(128\). Đầu dương của INT8 có dấu là \(127\), nên mã đầy thang là \(127\), không phải \(128\).
- Chỉ báo sai số tương đối trên bin \(1.0\) rồi kết luận bộ lượng tử vô hại. Bin \(0.004\) mới là ca khử nhiễu tiếng nói.
- Lượng tử trước khi STFT đã khớp. Lệch một bin tần số sẽ bị nướng vào thang.
- Giả định bài đồ chơi dùng cùng zero-point với bộ lượng tử tĩnh của ORT trong sản phẩm. Công cụ sản phẩm có thể dùng zero-point affine; lab cố ý đối xứng.

## Bẫy thường gặp

- Chỉ hiệu chuẩn trên white noise.
- Ship INT8 mà không ghi delta chất lượng cho đội hỗ trợ.
- Bỏ qua tràn số trong tensor state.
- Coi file `.tar.gz` nhỏ hơn là bằng chứng AudioWorklet đã vào ngân sách.

## Bài tập

1. Tính lại thang đối xứng cho trọng số nằm trong \([-0.8,\ 0.8]\). \(s\) bằng bao nhiêu, và \(0.8\) nhận mã nào?
2. Liệt kê tám loại clip cho tập hiệu chuẩn sau train kiểu Mezon.
3. Thiết kế phiếu nghe mù float đối với INT8, có ít nhất hai điều kiện gain gần 0 (tiếng nói nhỏ, sàn nhiễu).
4. Nêu điểm vào lượng tử hóa của ONNX Runtime mà bạn sẽ gọi, theo tài liệu chính thức, chưa cần chạy.
5. Với bin \(0.004\) của lab, giải thích vì sao đầu gain là ứng viên tệ cho INT8 mạnh ngay cả khi convolution thì không.

### Gợi ý đáp án

1. \(s = 0.8 / 127\). Giá trị \(0.8\) ánh xạ tới mã \(127\) nếu nó là max-abs. Đừng dùng \(255\) trừ khi bạn đã chuyển sang lược đồ affine không dấu và nói rõ.
2. Gồm im lặng, chỉ nhiễu, tiếng nói to, tiếng thì thầm, babble SNR thấp, bàn phím không dừng, một tone, và một clip kiểu echo dư.
3. Buộc chọn, cùng gain, nhãn giấu, thêm ô “nhiễu nhạc / giọng mỏng”.
4. Bắt đầu từ tài liệu lượng tử hóa của ONNX Runtime: lượng tử hóa sau train kiểu tĩnh với calibration reader. Tên lớp đổi theo phiên bản API; hãy trích đúng trang bạn mở.
5. \(0.004\) nhảy tới khoảng \(0.00787\). Bước tương đối đó áp thẳng lên một bin. Các lớp sau không làm mượt mask theo cách chúng làm mượt sai số trọng số.

## Đọc thêm

- Hướng dẫn lượng tử hóa trong [tài liệu ONNX Runtime](https://onnxruntime.ai/docs/).
- Jacob và cộng sự, lượng tử hóa cho suy luận chỉ số nguyên, tài liệu tham chiếu mobile kinh điển.
- Ghi chú FastEnhancer / faster-enhancer.c về runtime tăng cường INT8 (chỉ là con trỏ khảo sát).
- Thảo luận dung lượng và realtime của DeepFilterNet trong kho upstream.
