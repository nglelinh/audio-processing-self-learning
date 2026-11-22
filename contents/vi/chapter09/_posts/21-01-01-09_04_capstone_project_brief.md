---
layout: post
title: "09-04 Đề bài capstone"
chapter: "09"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Dự án cuối khóa (capstone) gồm một bản thiết kế hoàn chỉnh, một bản demo có số liệu đo đạc trên tập mẫu nhỏ và một câu chuyện tích hợp API công khai có cơ sở bảo vệ rõ ràng. Dự án không phải bản vá gửi trực tiếp vào kho sản phẩm chung [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression); bạn cần triển khai trên nhánh fork cá nhân hoặc trong cấu trúc thư mục `capstone/` được tạo ở bài lab này.

![Bản đồ đánh giá cho báo cáo capstone]({{ site.imgurl }}/generated/eval-metric-map.png)

*Hình. Báo cáo cuối khóa bám sát bản đồ đánh giá: chỉ tính SI-SDR khi có bản gốc sạch, ghi DNSMOS hoặc `n/a`, bổ sung ghi chú lắng nghe và một dòng hệ thống cho RTF. Quyết định phát hành phải dựa trên bằng chứng đo đạc.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ khởi tạo được cấu trúc thư mục dự án cuối khóa, tạo hỗn hợp tín hiệu 4 mẫu ở mức SNR cho trước, chọn một nhánh chính phù hợp, liệt kê đầy đủ các tệp sản phẩm mà người chấm sẽ kiểm tra, đồng thời xác định trước các dạng lỗi phổ biến ở từng mốc để tránh bỏ sót.

## Các nhánh đề tài (Track)

**A. Đánh giá và chính sách khử nhiễu (khuyến nghị).** Đóng băng tập mẫu âm thanh, hoàn thiện bảng 6 cột từ bài 08-04 và bảo vệ lựa chọn `setSuppressionLevel` bằng dữ liệu kiểm thử AB.

**B. Tích hợp hệ thống.** Thiết lập `assetConfig.cdnUrl` (ví dụ `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`), kiểm chứng quy tắc tự thêm tiền tố `v2/` trên bản ≥ 1.2.0 (gồm 1.3.0), kiểm thử `setEnabled` và diễn tập tình huống CDN bị chặn nhưng cuộc gọi vẫn phát hành âm thanh bình thường.

**C. Nhánh mở rộng Rust.** Thử nghiệm `df-core` tùy chọn từ bài 09-03. Nếu backend mới ở mức sao chép thẳng thì bắt buộc ghi nhãn `passthrough` (vẫn được tính điểm thành phần khi trung thực); không có điểm cho bất kỳ báo cáo nào ghi “NS works” trên vòng lặp chép thẳng.

Hãy chọn duy nhất một nhánh chính; các nhánh còn lại chỉ nên liệt kê trong mục ngoài phạm vi (non-goals).

## Các mốc công việc và lỗi thường gặp

| Mã mốc | Sản phẩm bàn giao | Lỗi thường gặp |
|----|----------|-----------|
| M0 | Phác thảo kiến trúc (09-01) và giả thuyết (09-02) | Dùng tên lớp nội bộ không công khai, hoặc thiếu tiêu chí thất bại |
| M1 | Số liệu nền (baseline) trên danh sách mẫu đóng băng | Thay đổi danh sách mẫu sau khi đã nhìn thấy điểm |
| M2 | Mã thay đổi nằm trong fork hoặc `capstone/` | Commit thử nghiệm trực tiếp lên kho sản phẩm chung |
| M3 | Bảng đánh giá 6 cột, dùng `n/a` đúng quy tắc | Tự bịa số SI-SDR cho bản ghi micro thực tế |
| M4 | Checklist buổi demo (09-05) | Phụ thuộc hoàn toàn vào CDN trực tuyến, không có bản ghi dự phòng |

Cần hoàn thành dứt điểm M0 trước khi thu thập số liệu M3 để tránh việc điều chỉnh ngược giả thuyết cho khớp kết quả.

## Danh sách sản phẩm người chấm sẽ kiểm tra

1. `capstone/design/sketch.md` — mục tiêu, luồng dữ liệu công khai, URL tài nguyên và giới hạn phạm vi.
2. `capstone/design/hypothesis.md` — giả thuyết, thiết kế thí nghiệm, tiêu chí thành công và thất bại.
3. `capstone/audio/` — các tệp WAV nhỏ hoặc tệp `.npy` từ bộ trộn, kèm README giải thích quy ước đặt tên.
4. `capstone/metrics/suite.md` — bảng 6 cột gồm `clip id`, `condition`, `SI-SDR` hoặc `n/a`, `DNSMOS` hoặc `n/a`, `listening note` và `RTF p95`.
5. `capstone/notes/reading.md` — tối thiểu 5 gạch đầu dòng liên kết kiến thức Chương 02–08 với API công khai hoặc các nguồn tài liệu ở bài 10-01.
6. `capstone/notes/limits.md` — nêu rõ giới hạn về ngôn ngữ, thiết bị và trạng thái nhánh Rust (`not attempted`, `passthrough` hoặc backend thực).

Trang trình chiếu (slide) là tùy chọn; lưu ý ảnh chụp màn hình con số mà người khác không thể chạy lại không được công nhận là kết quả đánh giá.

## Tiêu chí và trọng số đánh giá

- **Trọng số cao:** Kỹ thuật đo đạc có thực chất và bảng kết quả trung thực (kể cả các ô `n/a`); người chấm có thể chạy lại bộ trộn hoặc script kiểm tra.
- **Trọng số trung bình:** Kịch bản demo xử lý ổn định tình huống tai nghe và sự cố chặn CDN.
- **Trọng số thấp:** Hình thức trình bày trực quan.
- **Không tính điểm:** Chỉnh sửa kho sản phẩm chung khi chưa được phép, hoặc mô tả backend `passthrough` là “đã khử nhiễu”.

Các mục nằm ngoài phạm vi dự án gồm: huấn luyện kiến trúc mô hình mới, yêu cầu nhánh Rust khớp từng bit như điều kiện hoàn thành, và đẩy âm thanh người dùng lên mô hình đám mây khi không có thiết kế bảo mật quyền riêng tư.

## Mini-lab

Thực hiện từ một thư mục làm việc trống (tuyệt đối **không** chạy trong kho sản phẩm chung):

```bash
mkdir -p capstone/{design,audio,metrics,notes}
find capstone -type d | sort
python3 -c 'import numpy as np; s=np.array([1.,0,-1,.5]); n=np.array([.2,-.2,.2,-.2]); g=np.linalg.norm(s)/(10**(10/20)*np.linalg.norm(n)); y=s+g*n; np.save("capstone/audio/mix.npy", y); print(np.round(y,3).tolist())'
```

**Kết quả kỳ vọng**

```text
capstone
capstone/audio
capstone/design
capstone/metrics
capstone/notes
[1.237, -0.237, -0.763, 0.263]
```

Đoạn mã trên trộn tín hiệu tham chiếu `s` từ bài 08-01 với véctơ nhiễu 4 mẫu ở mức SNR 10 dB: hệ số `g` chuẩn hóa biên độ nhiễu sao cho $$10\log_{10}(\|s\|^2/\|gn\|^2) = 10$$, và các giá trị in ra là $$s + gn$$ làm tròn đến 3 chữ số thập phân. Kiểm tra lại bằng `find capstone -type f | sort` để chắc chắn tệp `capstone/audio/mix.npy` đã được lưu.

**Lỗi thường gặp.** Chạy lệnh `mkdir` bên trong bản sao kho sản phẩm chung; tính sai SNR do áp dụng tỉ số biên độ hai lần; quên lệnh `np.save` rồi nộp mỗi cây thư mục rỗng; hoặc nhầm lẫn mảng `[1.237, -0.237, -0.763, 0.263]` là đầu ra của DeepFilterNet (thực tế đây là tín hiệu hỗn hợp có nhiễu).

Sau khi chạy xong, hãy thêm danh sách các mốc M0–M4 (ghi trạng thái `todo` hoặc `done`) vào `capstone/design/sketch.md` để người chấm thấy rõ cấu trúc kế hoạch ngay cả khi các mốc mới ở trạng thái `todo`.

## Bài tập

1. Chọn một trong ba nhánh A, B hoặc C rồi viết bản giả thuyết M0 lưu vào `capstone/design/`.
2. Chốt trước 10 tên tệp âm thanh trong `capstone/audio/CLIPS.txt` trước khi bắt đầu chấm bất kỳ chỉ số nào.
3. Tạo tệp `capstone/notes/reading.md` với 5 gạch đầu dòng kèm URL thực tế mà bạn dự định đọc.
4. Chọn một dạng lỗi trong bảng mốc dễ xảy ra nhất với kế hoạch của bạn và chỉ ra tệp nào sẽ giúp phát hiện sớm lỗi đó.
5. Chạy lại câu lệnh trộn ở mức 0 dB (đổi `10/20` thành `0/20`) và giải thích nguyên nhân giá trị các mẫu thay đổi.

### Gợi ý đáp án

1. Nếu chọn nhánh C mà chưa nạp mô hình thực, bắt buộc vẫn phải ghi rõ nhãn `passthrough`.
2. Tệp `CLIPS.txt` chỉ lưu danh sách tên tệp trước khi có điểm số nhằm tránh chọn lọc thiên lệch.
3. Trích dẫn các URL thực có trong bài 10-01, không tự bịa tài liệu tham khảo.
4. Hai lỗi phổ biến nhất là vi phạm M2 (commit vào kho sản phẩm chung) và M3 (điền SI-SDR giả cho tệp thực tế).
5. Tại mức SNR 0 dB, năng lượng nhiễu bằng năng lượng tín hiệu ($$\|gn\| = \|s\|$$), nên hệ số `g` tăng lên và nhiễu chi phối rõ rệt hơn trên dạng sóng đầu ra.

## Video tham khảo

- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. **Xem trước.** Video cho thấy một báo cáo khử nhiễu thuyết phục luôn kết hợp dữ liệu, kiểm thử lắng nghe và chi phí tính toán — đúng mô hình mà dự án cuối khóa thu gọn lại.
- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, tiếng Anh. Định dạng so sánh trước – sau là hình mẫu trực quan cho phần trình diễn âm thanh trong buổi demo.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Tham khảo cách trình bày sơ đồ hệ thống kèm phân tích độ trễ để bảo vệ thiết kế kỹ thuật.
