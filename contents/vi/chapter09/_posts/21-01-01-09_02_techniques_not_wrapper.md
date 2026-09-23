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

Điểm capstone dành cho kỹ thuật đo được: khung và chồng lấn, chính sách mức khử, harness đánh giá, đường CDN lỗi, hoặc ngân sách RTF. Không dành cho việc đổi tên `deepfilternet3-noise-filter` hay refactor tiện tay trong repo sản phẩm chung. Wrapper là xe. Tầng ERB và deep filter của DeepFilterNet là lý do chiếc xe tồn tại. Bài này ép một giả thuyết, một baseline, và một bảng người giữ repo chạy lại được.

![Khối DeepFilterNet: đường ERB và deep filter nhiều khung]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. Kỹ thuật dưới wrapper: PCM 48 kHz, STFT, đường gain ERB, deep filter trên phổ phức, rồi ISTFT và overlap-add. Capstone của bạn nên gọi tên bạn đang học khối nào.*

## Bạn làm được gì sau bài này

Bạn đề xuất được một thay đổi bám chương 02–08, viết luật thành công và thất bại trước khi có số thứ hai, và giữ việc trong fork cá nhân hoặc harness ngoài. Bạn cũng nói nút công khai nào sẽ đụng (`setSuppressionLevel`, `setEnabled`, hoặc `assetConfig.cdnUrl`) và metric nào giữ `n/a`.

## Thực đơn ánh xạ chương

| Ý | Nhiên liệu | Sản phẩm chấm được |
|----|------------|---------------------|
| Harness với phiếu sáu cột của 08-04 | Ch. 08 | `suite.md` và checker |
| Mức mặc định chọn bằng test AB | 08-03 | Protocol, N, thắng theo điều kiện |
| Log RTF p95 và luật hạ mức đã viết | 05, 07 | Thiết bị, p95, cái bạn tắt |
| Ghi NS trình duyệt đối với processor này | 03, 07 | Checklist ràng buộc |
| Base CDN và tiền tố `v2/`, kèm diễn tập lỗi | 07 | Log tải bị chặn và tải từ cache |
| Mixer tổng hợp offline và SI-SDR | 02, 08-01 | Lab 13.80 / −10.67, rồi wav của bạn |
| Rust `df-core` | 09-03 | Kéo tùy chọn, passthrough phải ghi vậy |

Từ chối sửa chỉ CSS, bump dependency không có bảng, và hai giả thuyết không liên quan trong một báo cáo. Nếu bạn không gọi được số baseline sẽ thu trước, bạn chưa có thí nghiệm.

## Giả thuyết, thí nghiệm, đo

Viết khối này trước khi xoay núm:

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

Số trong khung là mẫu, không phải kết quả. Báo cáo của bạn thay bằng số đo. Vẫn không có ngưỡng DNSMOS chính thức để núp.

## Metric bạn phải gọi tên

Chất lượng là SI-SDR trên cặp tổng hợp đã căn, DNSMOS hoặc `n/a` trên file thật, và ghi chú nghe. Hệ thống là RTF p95 hoặc lời thật rằng bạn chỉ có trung bình, cộng việc init có fail khi CDN bị chặn không. UX là `setEnabled(false)` có trả mic thô không và asset thiếu có vẫn cho publish cuộc gọi không. Bỏ cột nào thì ghi `n/a` và lý do. Đừng chép 13.80 từ lab SI-SDR vào bảng sản phẩm rồi gọi là DeepFilterNet.

## Ghi chú người giữ repo giữ được

Dùng bản quyết định ngắn:

- Bối cảnh: API công khai nào và chương nào.
- Quyết định: mức, cờ, hoặc bố trí harness.
- Metric: phiếu sáu cột hoặc đường dẫn tới nó.
- Phương án đã loại, gồm “sửa repo chung”.
- Việc chưa đo: ngôn ngữ, điện thoại, ASR.

Hình DeepFilterNet là nội dung kỹ thuật của ghi chú đó. Nếu thay đổi chỉ là chính sách CDN, nói bạn không chỉnh gain ERB hay tap deep filter. Nếu thay đổi là núm mức, nói núm là `setSuppressionLevel(0–100)` và bạn không huấn luyện lại mạng.

## Cắt phạm vi

MVP của khóa này là danh sách clip đóng băng, một cột baseline, một thay đổi, và một báo cáo. Phần kéo là thiết bị thứ hai, checkpoint DNSMOS bạn thật sự chạy, hoặc đường Rust ở 09-03. Huấn luyện mạng enhance mới nằm ngoài. Suy luận mây trên audio khách hàng cũng vậy. Mọi patch chỉ rơi trên repo sản phẩm chung cũng vậy.

## Mini-lab

Viết `hypothesis.md` với bốn nhãn `Hypothesis:`, `Experiment:`, `Success:`, và `Fail:`. Gọi một API công khai và một metric sẽ là `n/a`. Chạy:

```python
from pathlib import Path
text = Path("hypothesis.md").read_text()
need = ["Hypothesis:", "Experiment:", "Success:", "Fail:", "n/a", "setSuppressionLevel"]
missing = [n for n in need if n not in text]
print("missing", missing or "none")
print("lines", len(text.splitlines()))
```

Nếu giả thuyết dùng `setEnabled` hoặc `cdnUrl` thay vì `setSuppressionLevel`, đổi token bắt buộc cuối thành tên đó và nói trong file. Đầu ra kỳ vọng cho bài mức khử:

```text
missing none
lines <số dòng của bạn, ít nhất 8>
```

Kiểu hỏng: giả thuyết không có luật fail; thành công chỉ là “SI-SDR tăng”; sửa file trong repo sản phẩm chung như bước hiện thực; cho rằng sơ đồ ERB nghĩa là bạn phải huấn luyện lại bộ lọc.

## Bài tập

1. Viết một câu giả thuyết bạn sẽ đem chấm. Hỏi người lạ có bác bỏ được không.
2. Liệt kê số baseline sẽ thu trước khi đổi, gồm ít nhất một `n/a`.
3. Tách ý thành MVP và phần kéo trong năm dòng.
4. Phác các heading bản quyết định để trống, rồi điền Bối cảnh và Phương án đã loại.
5. Chỉ một khối trên hình ERB và nói capstone của bạn có đụng nó không.

### Gợi ý đáp án

1. Gồm núm, điều kiện (bàn phím, quán, yên), và metric. “Làm cho tốt hơn” không bác bỏ được.
2. Baseline là mức 80 hoặc bypass trên cùng file. Clip thật có SI-SDR `n/a` cho đến khi có tham chiếu sạch.
3. MVP là bảng và AB. Phần kéo là thiết bị thứ hai hoặc Rust. Huấn luyện không phải cái nào.
4. Phương án đã loại nên có “không làm gì” và “vá repo chung” (bác).
5. Chính sách mức không chỉnh gain ERB. Harness đánh giá cũng không. Nói thẳng vậy.
