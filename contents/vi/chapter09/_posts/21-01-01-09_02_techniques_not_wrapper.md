---
layout: post
title: "09-02 Kỹ thuật vượt qua npm wrapper"
chapter: "09"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Điểm đánh giá dự án cuối khóa (capstone) tập trung vào các kỹ thuật đo đạc được: cấu hình khung và chồng lấp, chính sách chọn mức khử nhiễu, bộ công cụ đánh giá (harness), cơ chế ứng phó khi CDN lỗi hoặc kiểm soát ngân sách RTF — không phải việc đổi tên gói `deepfilternet3-noise-filter` hay tái cấu trúc nhỏ trong kho sản phẩm chung. Lớp wrapper chỉ là phương tiện vận chuyển, còn tầng hệ số ERB và bộ lọc sâu (deep filter) của DeepFilterNet mới là giá trị cốt lõi. Bài học này yêu cầu bạn xác lập trước một giả thuyết rõ ràng, một tập số liệu nền (baseline) và một bảng kết quả mà người quản trị kho mã có thể tự chạy lại để kiểm chứng.

![Khối DeepFilterNet: đường ERB và deep filter nhiều khung]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. Chuỗi kỹ thuật nằm dưới lớp wrapper: PCM 48 kHz, STFT, nhánh hệ số khuếch đại ERB, bộ lọc sâu trên phổ phức, sau đó là ISTFT và cộng chồng lấp (overlap-add). Dự án cuối khóa cần nêu rõ bạn đang khảo sát hoặc tối ưu khâu nào.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ đề xuất được một cải tiến gắn chặt với kiến thức Chương 02–08, định nghĩa trước tiêu chí thành công và thất bại trước khi đo lần hai, giữ toàn bộ mã thử nghiệm trong fork cá nhân hoặc thư mục độc lập, đồng thời nêu rõ API công khai nào được tác động (`setSuppressionLevel`, `setEnabled`, hoặc `assetConfig.cdnUrl`) và chỉ số nào giữ nguyên `n/a`.

## Danh mục đề tài ánh xạ theo chương

| Hướng đề tài | Kiến thức nền tảng | Sản phẩm kiểm chứng được |
|----|------------|---------------------|
| Bộ đánh giá theo bảng 6 cột (bài 08-04) | Chương 08 | Tệp `suite.md` và script kiểm tra |
| Chọn mức khử mặc định bằng kiểm thử AB | Bài 08-03 | Quy trình AB, cỡ mẫu $$N$$, bảng thắng/thua theo điều kiện |
| Ghi log RTF p95 và luật hạ mức tự động | Chương 05, 07 | Tên thiết bị, giá trị p95, hành động hạ tải tương ứng |
| Đối chiếu NS trình duyệt với processor | Chương 03, 07 | Bảng kiểm tra ràng buộc `getSettings()` |
| Đường dẫn CDN, tiền tố `v2/` và diễn tập lỗi | Chương 07 | Nhật ký tình huống bị chặn mạng và tải từ cache |
| Bộ trộn tín hiệu tổng hợp ngoại tuyến và SI-SDR | Chương 02, bài 08-01 | Kiểm chứng mốc 13.80 / −10.67 rồi chạy trên WAV của bạn |
| Nhánh mở rộng Rust `df-core` | Bài 09-03 | Tùy chọn mở rộng; nếu chỉ chép thẳng phải ghi rõ `passthrough` |

Không chấp nhận các đề tài chỉ chỉnh giao diện CSS, nâng phiên bản thư viện mà không có bảng so sánh, hoặc gộp hai giả thuyết không liên quan vào cùng một báo cáo. Nếu bạn chưa nêu được số liệu baseline cần thu thập trước tiên, bạn chưa có một thí nghiệm hợp lệ.

## Cấu trúc Giả thuyết – Thí nghiệm – Đo lường

Hãy viết hoàn chỉnh khối này trước khi thay đổi bất kỳ tham số nào:

```text
Hypothesis: Đưa setSuppressionLevel từ 80 xuống 60 giảm phụ âm bị bít
            trên clip bàn phím mà không sụp ở quán.

Experiment: Cùng 12 clip. Mức 80 và 60. AB với ít nhất 6 người.
            SI-SDR chỉ trên cặp tổng hợp. DNSMOS chỉ khi ghim một checkpoint;
            không thì n/a. RTF p95 trên một laptop có tên.

Success:    Nghe bàn phím không thích 80 hơn về độ tự nhiên, quán hòa hoặc
            hơn bypass, đối chứng nói yên chủ yếu hòa, RTF p95 nằm trong
            ngân sách bạn đã ghi.

Fail:       Người nghe quán rõ ràng thích 80, hoặc tiếng yên thua, hoặc
            p95 trễ quantum AudioWorklet. Khi đó bạn không đổi mặc định.
```

Các con số trong khung trên chỉ là ví dụ định dạng, không phải kết quả thực nghiệm; báo cáo của bạn phải thay bằng số đo thực tế và vẫn không được tự đặt ra ngưỡng chuẩn DNSMOS chính thức.

## Các chỉ số cần khai báo minh bạch

Về mặt chất lượng âm thanh, cần có SI-SDR trên các cặp tổng hợp đã căn chỉnh thời gian, DNSMOS (hoặc `n/a`) trên tệp thực tế và ghi chú nghe thử. Về mặt hệ thống, cần báo cáo RTF p95 (hoặc nêu trung thực nếu mới chỉ đo được trung bình) cùng kết quả kiểm tra khởi tạo khi CDN bị chặn. Về trải nghiệm người dùng, cần xác nhận `setEnabled(false)` trả về đúng tín hiệu micro gốc và việc thiếu tài nguyên vẫn cho phép phát hành cuộc gọi. Mọi cột chưa thực hiện phải ghi `n/a` kèm lý do; không bao giờ sao chép con số `13.80` từ bài lab SI-SDR vào bảng sản phẩm rồi gán cho DeepFilterNet.

## Bản ghi quyết định kỹ thuật dành cho người duy trì kho mã

Trình bày kết luận của bạn dưới dạng một bản ghi quyết định (decision record) ngắn gọn gồm 5 mục:

- **Bối cảnh:** API công khai nào và nội dung chương nào đang được đề cập.
- **Quyết định:** Mức khử nhiễu, cờ tính năng hoặc cấu trúc bộ công cụ đánh giá được chọn.
- **Số liệu đánh giá:** Bảng 6 cột hoặc đường dẫn tới tệp báo cáo.
- **Các phương án đã loại bỏ:** Bao gồm cả lý do không chỉnh sửa kho sản phẩm chung.
- **Phần chưa đo lường:** Các ngôn ngữ, thiết bị hoặc chỉ số ASR chưa bao phủ.

Sơ đồ DeepFilterNet là nền tảng kỹ thuật của bản ghi này: nếu thay đổi chỉ nằm ở chính sách CDN, hãy nêu rõ bạn không can thiệp vào hệ số ERB hay các tap của bộ lọc sâu; nếu thay đổi nằm ở mức khử, hãy ghi rõ bạn chỉ điều chỉnh `setSuppressionLevel(0–100)` chứ không huấn luyện lại mạng.

## Giới hạn phạm vi thực hiện

Phiên bản tối thiểu khả thi (MVP) của dự án gồm: danh sách mẫu âm thanh đóng băng, một cột baseline, một thay đổi duy nhất và một báo cáo hoàn chỉnh. Phần mở rộng (stretch) có thể là đo thêm trên thiết bị thứ hai, chạy thêm một checkpoint DNSMOS cố định hoặc thử nghiệm nhánh Rust ở bài 09-03. Các công việc nằm ngoài phạm vi gồm: huấn luyện kiến trúc khử nhiễu mới, chạy suy luận đám mây trên âm thanh người dùng, và gửi bản vá trực tiếp vào kho sản phẩm chung.

## Mini-lab

Tạo tệp `hypothesis.md` chứa đủ bốn nhãn `Hypothesis:`, `Experiment:`, `Success:` và `Fail:`, đồng thời nêu rõ một API công khai và ít nhất một chỉ số ghi `n/a`, sau đó kiểm tra bằng đoạn mã sau:

```python
from pathlib import Path
text = Path("hypothesis.md").read_text()
need = ["Hypothesis:", "Experiment:", "Success:", "Fail:", "n/a", "setSuppressionLevel"]
missing = [n for n in need if n not in text]
print("missing", missing or "none")
print("lines", len(text.splitlines()))
```

Nếu giả thuyết của bạn xoay quanh `setEnabled` hoặc `cdnUrl` thay vì `setSuppressionLevel`, hãy đổi từ khóa cuối trong danh sách `need` cho khớp và ghi chú trong tệp.

**Kết quả kỳ vọng** (với đề tài điều chỉnh mức khử nhiễu):

```text
missing none
lines <số dòng của bạn, ít nhất 8>
```

**Lỗi thường gặp.** Viết giả thuyết nhưng thiếu tiêu chí thất bại; đặt điều kiện thành công chỉ gói gọn trong “SI-SDR tăng”; chỉnh sửa tệp trong kho sản phẩm chung làm bước triển khai; hoặc hiểu nhầm rằng sơ đồ ERB đòi hỏi bạn phải tự huấn luyện lại bộ lọc.

## Bài tập

1. Viết một câu giả thuyết sẽ dùng để chấm điểm và tự kiểm tra xem một người ngoài có thể bác bỏ (falsify) câu đó bằng số liệu hay không.
2. Liệt kê tập số liệu baseline cần thu thập trước khi thay đổi cấu hình, bao gồm ít nhất một ô `n/a`.
3. Chia đề tài của bạn thành phần MVP và phần mở rộng (stretch) trong 5 dòng ngắn gọn.
4. Tạo khung tiêu đề cho bản ghi quyết định kỹ thuật rồi điền trước hai mục *Bối cảnh* và *Các phương án đã loại bỏ*.
5. Chỉ vào một khối trên sơ đồ DeepFilterNet và nêu rõ dự án của bạn có tác động trực tiếp vào khối đó hay không.

### Gợi ý đáp án

1. Giả thuyết đạt chuẩn phải nêu rõ tham số điều chỉnh, điều kiện kiểm thử (bàn phím, quán cà phê, phòng yên) và chỉ số đo; câu chung chung kiểu “làm cho tốt hơn” không thể bác bỏ được.
2. Baseline có thể là mức 80 hoặc chế độ bypass trên cùng tập tệp; các đoạn ghi âm thực tế ghi `n/a` ở cột SI-SDR do không có bản gốc sạch.
3. MVP gồm bảng số liệu 6 cột và kiểm thử AB; phần mở rộng gồm thiết bị thứ hai hoặc nhánh Rust; huấn luyện lại mô hình không nằm trong cả hai.
4. Mục *Các phương án đã loại bỏ* nên bao gồm phương án “giữ nguyên không làm gì” và “vá trực tiếp vào kho sản phẩm chung”.
5. Chính sách chọn mức khử hoặc bộ công cụ đánh giá đều không thay đổi trực tiếp thuật toán tính gain ERB — hãy trình bày thẳng thắn điều này.

## Video tham khảo

- [Short-Time Fourier Transform Explained Easily](https://www.youtube.com/watch?v=-Yxj3yfvY-4) — Valerio Velardo - The Sound of AI, tiếng Anh. **Xem trước.** Khung xử lý và bước nhảy (hop) là các kỹ thuật đo đạc được — nền tảng cốt lõi cần nắm trước khi triển khai dự án cuối khóa.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Chu trình đánh giá gồm dữ liệu, kiểm thử lắng nghe và chi phí tính toán tương ứng trực tiếp với cấu trúc thí nghiệm trong bài.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Trình bày cụ thể cơ chế kết hợp hệ số ERB và bộ lọc sâu kèm độ trễ thuật toán.
