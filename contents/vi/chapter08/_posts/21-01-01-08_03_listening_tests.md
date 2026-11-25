---
layout: post
title: "08-03 Kiểm thử lắng nghe"
chapter: "08"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter08
lesson_type: required
draft: false
---

Trong giới kỹ thuật âm thanh có một câu đùa rất thật: *"Nếu muốn thuật toán mới của bạn thắng trong buổi nghe thử nội bộ, chỉ cần vặn âm lượng của nó to hơn bản cũ đúng 2 decibel!"* Nghe có vẻ khó tin, nhưng đó là một thiên lệch tâm lý–thính giác đã được chứng minh hàng chục năm nay: tai người có xu hướng đánh giá âm thanh to hơn là "rõ hơn, đầy đặn hơn" — ngay cả khi chất lượng xử lý của nó tệ hơn. Nếu không kiểm soát chặt độ lớn âm lượng, không ẩn nhãn và không tách kết quả theo từng điều kiện, buổi nghe thử sẽ chỉ xác nhận lại định kiến sẵn có của chính bạn.

Chỉ số SI-SDR có thể vẫn cao dù giọng nói nghe bị kim loại, còn DNSMOS có thể chấm lệch ngay trên miền dữ liệu người dùng thực tế. Bài kiểm thử lắng nghe (listening test) là trụ cột giúp phát hiện cả hai sai sót đó, với điều kiện bạn kiểm soát chặt độ lớn âm lượng (loudness), thứ tự phát và danh mục mẫu âm thanh. Bạn không cần một phòng lab đạt chứng nhận ITU để áp dụng kỷ luật này; điều quan trọng là có quy trình văn bản rõ ràng, ẩn nhãn hệ thống và bảng kết quả cho phép phương án mới có thể thua. Bài học này trình bày thiết kế bài kiểm thử mù AB (hoặc thang điểm kiểu MUSHRA thu gọn) dành cho nhóm kỹ sư đang cân nhắc thay đổi `setSuppressionLevel` trên `DeepFilterNoiseFilterProcessor`.

**Mạch bài học:** Thiên lệch âm lượng trong nghe thử → Kiến thức cần nhớ (Thử nghiệm mù & Xáo trộn, Chuẩn hóa độ lớn LUFS/RMS, Thiết kế phân tầng & Kiểm tra tập trung) → Chọn giữa Dogfood, AB, ABC và MUSHRA thu gọn → Ma trận 5 điều kiện nhiễu & bảng kết quả thắng/thua/hòa → Giải thích tính tay hệ số chuẩn hóa âm lượng LUFS và bẫy gộp trung bình bảng AB → Mini-lab và Bài tập.

![Bản đồ đánh giá với cột nghe người]({{ site.imgurl }}/generated/eval-metric-map.png)

*Hình. Kiểm thử lắng nghe là cột tốn thời gian nhất nhưng có giá trị quyết định, đóng vai trò phân xử khi SI-SDR và DNSMOS cho kết quả trái ngược nhau trên micro thực tế.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ chọn được hình thức đánh giá phù hợp giữa AB và thang kiểu MUSHRA thu gọn, chuẩn hóa độ lớn âm lượng, xáo trộn thứ tự mẫu, soạn hướng dẫn người nghe song ngữ Anh – Việt, báo cáo kết quả thắng/thua/hòa tách riêng theo từng điều kiện, và phân biệt được khi nào chỉ cần dùng thử nội bộ (dogfood) một ngày là đủ.

## Kiến thức cần nhớ: Kỷ luật khoa học thực nghiệm trong đánh giá thính giác

### 1. Thiết kế mù (Blinding) và Xáo trộn ngẫu nhiên (Randomization)
- **Là gì:** Ẩn hoàn toàn tên hệ thống ("Hệ 1 / Hệ 2" thay vì "DF3-80 / Cũ") và đảo ngẫu nhiên vị trí A/B trên từng đoạn âm thanh để triệt tiêu hiệu ứng kỳ vọng (confirmation bias) và thói quen bấm một bên.
- **Nghiên cứu gì:** Biến cảm nhận chủ quan thành dữ liệu thực nghiệm đáng tin cậy ngay cả ở quy mô nhóm 5–10 người trong văn phòng.

### 2. Kiểm soát biến nhiễu vật lý: Chuẩn hóa độ lớn âm lượng (Loudness Normalization)
- **Là gì:** Đưa tất cả các tệp so sánh về cùng một mức độ lớn tích hợp (integrated loudness, ví dụ $$-23\text{ LUFS}$$ theo chuẩn phát thanh EBU R128) trước khi phát qua cùng một chuỗi thiết bị.
- **Nghiên cứu gì:** Loại bỏ thiên lệch "to hơn = hay hơn" và đảm bảo người chấm thực sự so sánh độ rõ phụ âm, độ tự nhiên và nhiễu nền chứ không so sánh mức khuếch đại đầu ra.

### 3. Phân tầng điều kiện (Stratified Reporting) và Attention Check
- **Là gì:** Thiết kế ma trận mẫu có cả mẫu đối chứng phòng yên tĩnh, lặp lại ngẫu nhiên 2 cặp đảo nhãn để sàng lọc người chấm mất tập trung, và báo cáo thắng/thua/hòa riêng cho từng điều kiện.
- **Nghiên cứu gì:** Ngăn chặn lỗi gộp trung bình che giấu điểm yếu nghiêm trọng (ví dụ thắng ở tiếng gõ phím nhưng lại làm méo giọng ở quán cà phê hay phòng yên tĩnh).

## Chọn quy trình khớp với quyết định kỹ thuật

Dùng thử nội bộ (dogfood) — bật bộ khử nhiễu ngay trong các cuộc họp hàng ngày — rất hiệu quả để bắt lỗi treo ứng dụng, CPU tăng vọt hoặc cảm giác khó chịu rõ rệt, nhưng không giúp ước lượng tỉ lệ ưa chuộng giữa hai cấu hình. Kiểm thử AB yêu cầu người nghe chọn thích mẫu A, thích mẫu B hoặc hòa trên từng cặp âm thanh; đây là công cụ chuẩn xác để so sánh mức khử 80 với mức 60, hoặc so sánh bật processor với chế độ bypass (`setEnabled(false)`). Biến thể ABC bổ sung thêm mẫu neo (anchor) từ tín hiệu micro thô. Thang điểm kiểu MUSHRA (lấy cảm hứng từ chuẩn ITU-R BS.1534) cho phép chấm đồng thời nhiều hệ thống cùng mẫu neo nhưng đòi hỏi số người nghe lớn hơn. Tương tự, chuẩn ITU-T P.808 mô tả quy trình đánh giá giọng nói qua cộng đồng (crowdsourcing): hãy đọc để nắm vững nguyên tắc, rồi ghi nhận trung thực trong báo cáo rằng bạn đang chạy phiên bản thu gọn thay vì gắn mác “P.808” cho một buổi nghe thử 5 người trong văn phòng.

## Kiểm soát biến nhiễu để kết quả phản ánh đúng bộ khử nhiễu

Chênh lệch độ lớn âm lượng là nguồn thiên lệch kinh điển: nếu một tệp nhỏ tiếng hơn, người nghe được yêu cầu chấm độ “dễ chịu” có thể chọn nhầm nó ngay cả khi các âm xát đã bị mất. Vì vậy, cần chuẩn hóa độ lớn âm lượng tích hợp (integrated loudness) về cùng một mức đích và ghi rõ công cụ đã dùng. Xáo trộn ngẫu nhiên vị trí A/B trên từng đoạn âm thanh để mức khử mới không bao giờ cố định ở một bên; hiển thị nhãn ẩn như “Hệ 1” và “Hệ 2” thay vì “DF3-80”. Cố gắng dùng chung một loại tai nghe (hoặc ghi rõ thiết bị nghe nếu khác nhau), ưu tiên các đoạn dài 5–10 giây chứa nhiễu khó cùng phụ âm rõ nét thay vì đoạn dài cả phút gây mệt tai. Đường phát lại phải hoàn toàn đồng nhất: cùng trình duyệt, cùng tần số lấy mẫu, không chèn thêm bộ giới hạn biên độ (limiter) ở riêng một nhánh.

Luôn đưa vào các đoạn giọng nói sạch làm mẫu đối chứng. Một cấu hình chỉ làm tốt ở quán cà phê nhưng lại làm méo giọng trong phòng yên tĩnh không đủ điều kiện làm giá trị mặc định. Tập mẫu cũng cần có ít nhất một loại nhiễu xung (gõ bàn phím) và một loại nhiễu đám đông (babble), tránh tối ưu quá khớp vào duy nhất một đoạn thu quán cà phê quen thuộc.

## Thiết kế ma trận mẫu thay vì gom tệp rời rạc

| Loại nhiễu | Độ khó | Thiết bị thu | Vai trò trong ma trận |
|-------|--------|----------|----------------|
| Ồn quán cà phê | Khó | Micro laptop | Tạp âm nhiều giọng nói chồng lấn |
| Gõ bàn phím | Vừa | Laptop | Nhiễu xung; dễ bị cắt nhầm vào phụ âm |
| Quạt hoặc điều hòa | Dễ hơn | Điện thoại | Nhiễu dừng; kiểm tra băng thông khác |
| Tiếng giao thông | Khó | Điện thoại | Nhiễu tần số thấp kéo dài |
| Phòng yên tĩnh | Đối chứng | Laptop | Phát hiện hiện tượng khử quá tay |

Một bài kiểm thử nhóm nhỏ thường gồm 8–15 đoạn âm thanh và 5–10 người chấm (luôn ghi rõ số lượng $$N$$ trong bảng). Lặp lại ngẫu nhiên 2 đoạn với nhãn A/B đảo ngược làm bài kiểm tra mức độ tập trung (attention check); nếu người chấm tự mâu thuẫn trên cả hai cặp lặp, loại phiếu đó ra và ghi chú minh bạch. Khi người chấm sử dụng tiếng Việt, hãy dịch tờ hướng dẫn sang tiếng Việt tự nhiên với cùng hệ tiêu chí: ưu tiên phụ âm rõ ràng, giọng nói tự nhiên, ít tạp âm gây xao nhãng; đồng thời chấm trừ các lỗi giọng bị nghẹt, âm sắc robot hoặc mất từ, và dặn người nghe bỏ qua sai khác âm lượng nhỏ nếu còn sót.

## Giải thích: Tính tay hệ số chuẩn hóa âm lượng và đọc bảng kết quả AB phân tầng

### Phép tính 1: Chuẩn hóa hai tệp lệch 3 dB về cùng mức đích $$-23\text{ LUFS}$$
Giả sử tệp A đo được độ lớn tích hợp $$L_A = -26\text{ LUFS}$$ còn tệp B đo được $$L_B = -23\text{ LUFS}$$. Nếu phát thẳng không chuẩn hóa, tệp B có công suất gấp $$10^{3/10} \approx \mathbf{2{,}0\text{ lần}}$$ tệp A — người nghe sẽ thiên vị B ngay cả khi hai tệp giống hệt nhau!
Để đưa tệp A về đúng mức đích $$L_{\text{target}} = -23\text{ LUFS}$$, ta nhân toàn bộ mẫu của tệp A với hệ số biên độ:
$$ g_A = 10^{(L_{\text{target}} - L_A)/20} = 10^{(-23 - (-26))/20} = 10^{3/20} \approx \mathbf{1{,}4125}. $$
(Trước khi lưu WAV, kiểm tra thêm đỉnh cực đại $$\max_n \vert g_A x_A[n] \vert < 1{,}0$$ để chắc chắn phép nhân không gây cắt ngọn / clipping!).

### Phép tính 2: Vì sao không bao giờ được gộp bảng AB thành một tỉ lệ thắng duy nhất?
Xét bảng kết quả ngay bên dưới ($$N = 10$$ người chấm cho mỗi điều kiện, tổng $$30$$ lượt chấm):
- **Nếu gộp chung cả 3 hàng:** Mới thắng $$7 + 4 + 3 = \mathbf{14}$$ lượt, Cũ thắng $$2 + 5 + 2 = \mathbf{9}$$ lượt, Hòa $$1 + 1 + 5 = \mathbf{7}$$ lượt. Nhìn con số tổng `14–9–7` (tỉ lệ thắng ròng 61% không tính hòa), nhiều người sẽ vội vã bấm nút phát hành!
- **Khi tách riêng từng hàng:** Ở **Quán cà phê**, hệ thống mới **thua 4–5**! Nếu người dùng ứng dụng của bạn họp nhiều ở quán cà phê hoặc không gian mở, việc phát hành cấu hình này sẽ làm tệ đi chính kịch bản quan trọng nhất. Phân tầng giúp bạn quyết định đúng: giữ mặc định cũ hoặc thử một mức khử trung gian (ví dụ 70 thay vì 80).

## Cách trình bày báo cáo kết quả

Với bài kiểm thử AB, hãy báo cáo đầy đủ số lượt ứng viên mới thắng, hệ nền (baseline) thắng và số lượt hòa — cả tổng thể lẫn tách riêng theo từng điều kiện. Trường hợp thắng ở tiếng bàn phím nhưng thua ở quán cà phê đòi hỏi quyết định phân nhánh rõ ràng: có thể phát hành mức khử thấp hơn làm mặc định kèm ghi nhận phần nhiễu quán còn lại, hoặc từ chối thay đổi mặc định; tuyệt đối không gộp tất cả các hàng thành một con số tỉ lệ thắng duy nhất. Nên đính kèm một mẫu minh họa có quyền phát công khai trong buổi demo (bài 09-05) kèm tên điều kiện cụ thể.

Mẫu bảng tổng hợp phục vụ ra quyết định:

| Điều kiện | Mới thắng | Cũ thắng | Hòa | N |
|-----------|-----------|----------|-----|---|
| Bàn phím | 7 | 2 | 1 | 10 |
| Quán cà phê | 4 | 5 | 1 | 10 |
| Phòng yên | 3 | 2 | 5 | 10 |

Ở hàng phòng yên tĩnh, kết quả chủ yếu là “hòa” được xem là đạt yêu cầu vì bộ khử nhiễu không làm biến dạng giọng sạch; ngược lại, nếu phương án “cũ” thắng áp đảo ở hàng này thì cấu hình mới đang làm hao hụt giọng nói.

## Khi nào dùng thử nội bộ (dogfood) là đủ

Chỉ nên dừng ở bước dùng thử nội bộ đối với những thay đổi không làm biến đổi mẫu âm thanh đầu ra, chẳng hạn sửa cơ chế fallback CDN, thêm dòng log, chỉnh header cache hoặc bật cờ thử nghiệm nội bộ không tác động tới trải nghiệm mặc định. Ngược lại, bắt buộc phải chạy kiểm thử lắng nghe có cấu trúc khi đổi mức khử nhiễu mặc định, phát hành tệp WASM hoặc gói mô hình mới, hay điều tra phản hồi “giọng nghe lạ”. Ngay cả các tối ưu tốc độ RTF cũng chỉ được bỏ qua bước nghe thử nếu đầu ra khớp với tệp WAV chuẩn trong đúng dung sai đã quy định; một bản chạy nhanh hơn nhưng lệch mẫu đầu ra phải được xem là một hệ thống mới.

## Mini-lab

Soạn tệp `ab_protocol.md` mô tả quy trình kiểm thử AB cho một thay đổi mức khử nhiễu (ví dụ so sánh mức 80 và mức 60 trên `setSuppressionLevel`), sau đó chạy script kiểm tra bên dưới. Bài lab đạt yêu cầu khi tài liệu đề cập rõ chuẩn hóa độ lớn âm lượng, ẩn nhãn (nghe mù), lựa chọn hòa, mẫu đối chứng yên tĩnh, các điều kiện nhiễu và hướng dẫn song ngữ.

```python
from pathlib import Path
text = Path("ab_protocol.md").read_text().lower()
need = ["loudness", "blind", "tie", "quiet", "keyboard", "cafe", "vietnamese", "setsuppressionlevel"]
missing = [n for n in need if n not in text]
print("missing", missing or "none")
print("chars", len(text))
```

**Kết quả kỳ vọng**

```text
missing none
chars <một số nguyên lớn hơn 400>
```

Độ dài ký tự phụ thuộc vào phần viết của bạn; dòng `missing none` xác nhận đạt chuẩn.

**Lỗi thường gặp.** Để lộ tên tệp trên giao diện chấm điểm; bỏ lựa chọn “hòa” khiến người nghe buộc phải đoán khi hai mẫu giống hệt nhau; thiếu mẫu đối chứng phòng yên; chỉ viết hướng dẫn tiếng Anh cho nhóm chấm tiếng Việt; hoặc chỉ đánh giá thay đổi mức khử trên giọng của duy nhất một người nói.

Bản quy trình tối thiểu đạt chuẩn cần trình bày nhiệm vụ bằng cả hai ngôn ngữ, ghi rõ `setSuppressionLevel` và liệt kê đủ ba điều kiện nhiễu; hãy viết thành hướng dẫn hoàn chỉnh theo cấu trúc bài học thay vì nhồi từ khóa.

## Bài tập

1. Viết đoạn hướng dẫn người chấm bằng tiếng Anh và bản tiếng Việt tự nhiên tương ứng, giữ thống nhất toàn bộ các tiêu chí chấm trừ.
2. Liệt kê 9 tên tệp cho một ma trận 3×3 (tạp âm đám đông, bàn phím, phòng yên × laptop, điện thoại, tai nghe có micro).
3. Với kết quả: Bàn phím (mới thắng 7–2–1), Quán cà phê (4–5–1), Phòng yên (3–2–5), bạn sẽ chọn giữ mức mặc định nào và cần kiểm thử lại điều gì?
4. Xây dựng quy tắc kiểm tra mức độ tập trung (attention check) dựa trên một đoạn âm thanh lặp lại.
5. Nêu hai thay đổi sản phẩm không cần chạy quy trình nghe thử này, và một thay đổi bắt buộc phải chạy.

### Gợi ý đáp án

1. Tiêu chí chấm trừ gồm giọng bị nghẹt, âm sắc robot và mất từ; yêu cầu người nghe bỏ qua chênh lệch âm lượng nhỏ. Bản tiếng Việt cần diễn đạt tự nhiên như lời trao đổi với đồng nghiệp, tránh dịch sát từng chữ.
2. Mã hóa rõ điều kiện và thiết bị ngay trong tên tệp, ví dụ `babble__laptop__01.wav`.
3. Không phát hành chỉ vì thắng ở điều kiện bàn phím: kết quả thua ở quán cà phê và hòa ở phòng yên cho thấy nên giữ mặc định cũ hoặc kiểm thử thêm một mức trung gian, đồng thời nêu rõ lựa chọn cuối cùng.
4. Đảo ngược nhãn A/B trên bản lặp lại của cùng một đoạn; nếu người chấm chọn hai phương án trái ngược nhau thì đánh dấu không đạt kiểm tra tập trung.
5. Sửa cơ chế fallback CDN không làm đổi mẫu âm thanh thì chỉ cần dogfood; thay đổi giá trị mặc định của `setSuppressionLevel` bắt buộc phải chạy kiểm thử lắng nghe.

## Video tham khảo

- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. **Xem trước.** Xem phần trình bày về đánh giá P.808 qua cộng đồng (tham chiếu, mẫu neo và sàng lọc người chấm) — nền tảng kỷ luật lắng nghe áp dụng ngay cả ở quy mô nhóm nhỏ.
