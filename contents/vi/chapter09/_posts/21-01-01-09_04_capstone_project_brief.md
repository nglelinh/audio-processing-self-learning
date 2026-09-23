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

Capstone là một bản thiết kế viết ra, một demo có số đo trên tập clip nhỏ, và một câu chuyện API công khai bạn bênh được. Nó không phải patch vào repo sản phẩm chung [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression). Làm trong fork cá nhân hoặc trong cây `capstone/` mà lab này tạo. Đường giảng viên `/Users/nguyenlelinh/ncc/mezon-noise-suppression` là ngữ cảnh máy cục bộ tùy chọn, không phải checkout bắt buộc và không phải chỗ để bịa file.

![Bản đồ đánh giá cho báo cáo capstone]({{ site.imgurl }}/generated/eval-metric-map.png)

*Hình. Báo cáo dùng bản đồ đánh giá: SI-SDR chỉ khi có tham chiếu sạch, DNSMOS hoặc `n/a`, ghi chú nghe, và một dòng hệ thống cho RTF. Ô ship là một quyết định, không phải khẩu hiệu.*

## Bạn làm được gì sau bài này

Bạn tạo được các thư mục capstone, trộn tín hiệu bốn mẫu ở SNR đã biết, chọn một track chính, và liệt kê artifact người chấm sẽ mở. Bạn cũng nêu kiểu hỏng của từng mốc để trượt không biến thành bỏ qua im lặng.

## Các track

**A. Đánh giá và chính sách (nên chọn).** Đóng băng clip, điền phiếu sáu cột từ bài 08-04, và biện minh một lựa chọn `setSuppressionLevel` bằng ghi chú AB.

**B. Tích hợp.** Tập `assetConfig.cdnUrl` (ví dụ Mezon `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`), tiền tố `v2/` tự thêm trên gói ≥ 1.2.0 gồm 1.3.0, `setEnabled`, và diễn tập CDN bị chặn mà audio vẫn publish.

**C. Kéo Rust.** `df-core` tùy chọn từ bài 09-03. Backend passthrough phải ghi passthrough. Điểm một phần là thật nếu nhãn trung thực. Không có điểm cho “NS works” trên vòng chép.

Chọn một track chính. Track kia chỉ được xuất hiện như non-goal có tên.

## Mốc và cách chúng hỏng

| ID | Sản phẩm | Kiểu hỏng |
|----|----------|-----------|
| M0 | Phác kiến trúc (09-01) và giả thuyết (09-02) | Tên lớp riêng, hoặc không có luật fail |
| M1 | Baseline trên danh sách clip đóng băng | Chỉnh danh sách sau khi thấy điểm |
| M2 | Thay đổi nằm ở fork hoặc `capstone/`, không ở cây chung | Commit trên repo sản phẩm “chỉ để thử” |
| M3 | Bảng sáu cột, `n/a` đúng chỗ | SI-SDR bịa trên file mic thật |
| M4 | Checklist demo (09-05) | CDN sống là đường duy nhất, không có bản ghi dự phòng |

Các ID không giấu lịch tuần. Xong M0 trước khi thu M3, kẻo bạn uốn giả thuyết cho khớp số.

## Artifact người chấm mở

1. `capstone/design/sketch.md` — mục tiêu, đường dữ liệu công khai, URL asset, non-goal.
2. `capstone/design/hypothesis.md` — giả thuyết, thí nghiệm, thành công, thất bại.
3. `capstone/audio/` — wav nhỏ hoặc `.npy` từ mixer, cộng README tên file.
4. `capstone/metrics/suite.md` — clip id, condition, SI-SDR hoặc `n/a`, DNSMOS hoặc `n/a`, listening note, RTF p95.
5. `capstone/notes/reading.md` — ít nhất năm gạch đầu dòng nối chương 02–08 với API công khai hoặc URL bài ở 10-01.
6. `capstone/notes/limits.md` — ngôn ngữ, thiết bị, và trạng thái Rust (`not attempted` hoặc `passthrough` hoặc backend thật).

Slide là tùy chọn. Ảnh chụp điểm không chạy lại được không phải metric.

## Trọng số chấm

Nặng: kỹ thuật là thật và bảng trung thực, kể cả `n/a`. Nặng: người khác chạy lại mixer hoặc checker được. Vừa: đường demo sống sót tai nghe và CDN bị chặn. Nhẹ: bóng bẩy hình. Không điểm: sửa repo sản phẩm chung khi chưa được phép, và mọi báo cáo gọi passthrough là “khử nhiễu”.

Non-goal, nói để khỏi lan: huấn luyện mô hình đỉnh mới, parity Rust đúng từng bit như điều kiện tốt nghiệp, và tải audio khách hàng lên mô hình mây khi bạn không có thiết kế riêng tư.

## Mini-lab

Từ thư mục làm việc trống, **không** phải repo sản phẩm:

```bash
mkdir -p capstone/{design,audio,metrics,notes}
find capstone -type d | sort
python3 -c 'import numpy as np; s=np.array([1.,0,-1,.5]); n=np.array([.2,-.2,.2,-.2]); g=np.linalg.norm(s)/(10**(10/20)*np.linalg.norm(n)); y=s+g*n; np.save("capstone/audio/mix.npy", y); print(np.round(y,3).tolist())'
```

Đầu ra kỳ vọng:

```text
capstone
capstone/audio
capstone/design
capstone/metrics
capstone/notes
[1.237, -0.237, -0.763, 0.263]
```

Mixer dựng hỗn hợp 10 dB của tham chiếu `s` ở bài 08-01 với vector nhiễu bốn điểm. `g` co nhiễu sao cho $$10\log_{10}(\|s\|^2/\|gn\|^2) = 10$$. Các mẫu in ra là $$s + gn$$ làm tròn ba chữ số thập phân. Kiểm bằng `find capstone -type f | sort` rằng `capstone/audio/mix.npy` tồn tại.

Kiểu hỏng: chạy `mkdir` trong clone sản phẩm chung; SNR khác vì công thức dùng tỉ biên độ hai lần; quên `np.save` rồi nhận danh sách thư mục là cả lab; coi `[1.237, -0.237, -0.763, 0.263]` là đầu ra DeepFilterNet. Đó là hỗn hợp ồn.

Sau các lệnh, thêm checklist mốc vào `capstone/design/sketch.md` với M0–M4 ghi `todo` hoặc `done`. Người chấm phải thấy thư mục kể cả khi mọi mốc còn `todo`.

## Bài tập

1. Chọn track A, B, hoặc C và viết giả thuyết M0 trong `capstone/design/`.
2. Đóng băng mười tên file clip trong `capstone/audio/CLIPS.txt` trước khi chấm bất cứ thứ gì.
3. Bắt đầu `capstone/notes/reading.md` với năm gạch và URL thật bạn sẽ mở.
4. Gọi một kiểu hỏng dễ gặp nhất với bạn, từ bảng trên, và file sẽ phơi nó.
5. Chạy lại mixer một dòng ở 0 dB (đổi `10/20` thành `0/20`) và giải thích vì sao mẫu đổi.

### Gợi ý đáp án

1. Track C vẫn cần nhãn passthrough nếu chưa có mô hình.
2. Chỉ tên file. Chưa có điểm, nên bạn không lái được tập.
3. Dùng URL ở bài 10-01. Đừng bịa bài báo kế tục.
4. Trượt hay gặp là M2 trên repo chung, hoặc M3 với SI-SDR giả.
5. Ở 0 dB, $$\|gn\| = \|s\|$$, nên `g` lớn hơn và nhiễu hiện rõ hơn trên bản in.
