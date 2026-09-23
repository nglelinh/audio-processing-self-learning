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

SI-SDR có thể vẫn cao trong khi giọng hóa kim loại, và DNSMOS có thể trượt đúng miền người dùng đang ở. Bài nghe là cột bắt được cả hai, nếu bạn khống chế độ to, thứ tự, và lưới clip. Không cần lab chứng nhận ITU để học kỷ luật này. Bạn cần protocol viết ra, nhãn bịt, và một bảng có quyền thua. Bài này là thiết kế AB nhỏ (hoặc kiểu MUSHRA nhẹ) cho nhóm kỹ sư đang quyết có đổi `setSuppressionLevel` trên `DeepFilterNoiseFilterProcessor` hay không.

![Bản đồ đánh giá với cột nghe người]({{ site.imgurl }}/generated/eval-metric-map.png)

*Hình. Bài nghe là cột chậm và đáng giá. Nó phân xử khi SI-SDR và DNSMOS bất đồng, chuyện bình thường trên micro thật.*

## Bạn làm được gì sau bài này

Bạn chọn được AB hay thang kiểu MUSHRA nhẹ, chuẩn hóa độ to, xáo thứ tự, viết hướng dẫn cho người chấm bằng tiếng Anh và tiếng Việt, và báo thắng, thua, hòa theo điều kiện. Bạn cũng biết khi nào dogfood một ngày là đủ.

## Chọn protocol khớp quyết định

Dogfood — dùng khử nhiễu trong cuộc họp thật — bắt crash, CPU tăng, và câu “tôi ghét cái này”. Nó không ước lượng tỉ lệ thích. AB hỏi mỗi người chấm thích A, thích B, hoặc hòa, trên một cặp. Đó là công cụ đúng cho mức 80 với mức 60, hoặc processor bật với bypass bằng `setEnabled(false)`. ABC thêm mỏ neo micro thô. Thang kiểu MUSHRA, gợi từ ITU-R BS.1534, chấm nhiều hệ với mỏ neo và cần tập người chấm nhiều hơn. ITU-T P.808 mô tả test tiếng nói hội thoại thuê đám đông; đọc như chuẩn để tôn trọng, rồi chạy biến thể nhẹ và nói vậy trong báo cáo. Đừng gắn nhãn test hành lang năm người là P.808.

## Khống chế để kết quả nói về khử nhiễu

Độ to là nhiễu kinh điển. Nếu file đã khử nhỏ hơn, người được bảo chấm “dễ chịu” sẽ chọn nó dù âm xát đã chết. Chuẩn hóa độ to tích hợp về một đích chung và ghi công cụ. Xáo hệ nào là A trên từng clip. Đừng để mức mới luôn nằm bên phải. Hiện “Hệ 1” và “Hệ 2”, không hiện “DF3-80”. Cùng tai nghe khi có thể, và ghi thiết bị khi không. Ưu tiên 5–10 giây có nhiễu khó và một phụ âm, không phải một phút làm người chấm mệt. Đường phát phải giống hệt: cùng trình duyệt, cùng sample rate, không limiter thêm một phía.

Phải có clip tiếng nói sạch làm đối chứng. Bộ khử chỉ giúp ồn quán mà làm hỏng câu yên thì không ship làm mặc định. Có ít nhất một nhiễu xung (bàn phím) và một nhiễu babble. Một clip quán yêu thích là cách bộ metric overfit.

## Lưới, không phải đống file

| Nhiễu | Độ khó | Thiết bị | Vì sao có mặt |
|-------|--------|----------|----------------|
| Ồn quán | Khó | Mic laptop | Nhiễu giống tiếng nói chồng |
| Bàn phím | Vừa | Laptop | Xung; dễ cắt quá |
| Quạt hoặc điều hòa | Dễ hơn | Điện thoại | Nhiễu dừng; băng thông khác |
| Giao thông | Khó | Điện thoại | Ồn trầm |
| Phòng yên | Đối chứng | Laptop | Phát hiện khử quá tay |

Tám đến mười lăm clip và năm đến mười người chấm là test nhóm nhỏ. Ghi $$N$$ trong bảng. Lặp hai clip với nhãn đảo làm kiểm tra chú ý. Nếu người chấm tự mâu thuẫn cả hai, để phiếu đó ra và nói rõ. Dịch tờ hướng dẫn sang tiếng Việt khi người chấm làm việc bằng tiếng Việt. Tiêu chí phải cùng nghĩa: phụ âm rõ, giọng tự nhiên, ít bị nhiễu gây phân tâm, và phạt giọng bít, timbre robot, hoặc mất từ. Bảo họ bỏ qua khác biệt độ to còn sót.

## Bạn báo cáo gì

Với AB, báo số lần ứng viên thắng, baseline thắng, và hòa, tổng và theo điều kiện. Bàn phím thắng mà quán thua là quyết định tách: có thể ship mức khử thấp hơn làm mặc định và ghi nhiễu quán còn lại, hoặc từ chối đổi mặc định. Đừng gộp các hàng đó thành một phần trăm chiến thắng. Kèm một ví dụ bạn có quyền phát ngày demo (bài 09-05), ghi tên điều kiện.

Dạng bảng cho người quyết:

| Điều kiện | Mới thắng | Cũ thắng | Hòa | N |
|-----------|-----------|----------|-----|---|
| Bàn phím | 7 | 2 | 1 | 10 |
| Quán | 4 | 5 | 1 | 10 |
| Yên | 3 | 2 | 5 | 10 |

Hàng yên toàn hòa là thành công nếu ứng viên không được đụng tiếng nói sạch. Hàng yên mà “cũ” thắng nghĩa là mức mới đang ăn giọng.

## Khi dogfood là cả bài test

Chỉ dogfood cho thay đổi phải giống mẫu: fallback CDN, một dòng log, cache header. Dùng cho cờ nội bộ không đổi cái người nghe mặc định. Bắt test có cấu trúc khi đổi mức khử mặc định, ship WASM hoặc archive mô hình mới, hoặc trả lời “giọng nghe lạ”. Việc RTF chỉ bỏ nghe khi mẫu ra khớp wav vàng trong dung sai bạn đã ghi. Bản nhanh hơn mà không gần mẫu là một hệ mới.

## Mini-lab

Viết `ab_protocol.md` cho một lần đổi mức (ví dụ 80 với 60 trên `setSuppressionLevel`). Rồi chạy checker. Lab đậu khi protocol nêu độ to, bịt mắt, đối chứng sạch, và cả hai ngôn ngữ.

```python
from pathlib import Path
text = Path("ab_protocol.md").read_text().lower()
need = ["loudness", "blind", "tie", "quiet", "keyboard", "cafe", "vietnamese", "setsuppressionlevel"]
missing = [n for n in need if n not in text]
print("missing", missing or "none")
print("chars", len(text))
```

Đầu ra kỳ vọng:

```text
missing none
chars <một số nguyên lớn hơn 400>
```

Số ký tự là của bạn. Dòng `missing none` là tín hiệu đậu. Kiểu hỏng: tên file không bịt trên UI người chấm; không có lựa hòa, ép thích khi hai clip như nhau; không có đối chứng yên; hướng dẫn chỉ tiếng Anh cho hội đồng nói tiếng Việt; chấm đổi mức trên giọng một người.

Thân protocol tối thiểu thỏa checker sẽ nêu nhiệm vụ cả hai ngôn ngữ, ghi `setSuppressionLevel`, và liệt kê ba điều kiện. Hãy mở rộng bằng đoạn hướng dẫn trong bài này, đừng nhồi từ khóa.

## Bài tập

1. Viết đoạn hướng dẫn người chấm bằng tiếng Anh và bản tiếng Việt tự nhiên. Giữ cùng các mức phạt.
2. Liệt kê chín tên file cho lưới 3×3 (babble, bàn phím, yên × laptop, điện thoại, headset).
3. Bàn phím: mới thắng 7–2–1. Quán: 4–5–1. Yên: 3–2–5. Bạn ship mức mặc định nào, và test lại gì?
4. Định luật kiểm tra chú ý cho một clip lặp.
5. Nêu hai thay đổi sản phẩm không cần protocol này, và một thay đổi cần.

### Gợi ý đáp án

1. Phạt giọng bít, timbre robot, và mất từ. Bỏ qua lệch độ to nhỏ. Tiếng Việt phải nghe như lời dặn đồng nghiệp, không phải dịch word-for-word.
2. Mã hóa điều kiện và thiết bị trong tên, ví dụ `babble__laptop__01.wav`.
3. Đừng ship chỉ vì hàng bàn phím. Quán thua và yên hòa nghĩa là giữ mặc định cũ hoặc test lại mức giữa. Nói rõ bạn chọn gì.
4. Đảo A/B trên bản lặp. Người chấm đổi chính lựa chọn của mình thì trượt kiểm tra.
5. Fallback CDN mà mẫu không đổi thì dogfood được. Mặc định mới của `setSuppressionLevel` thì không.
