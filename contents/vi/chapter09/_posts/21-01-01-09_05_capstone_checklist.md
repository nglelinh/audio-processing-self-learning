---
layout: post
title: "09-05 Checklist capstone & demo day"
chapter: "09"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Buổi trình diễn cuối khóa (demo day) gói gọn trong 5 phút để chứng minh luồng phát hành âm thanh, bảng số liệu đo đạc và các giới hạn hệ thống đều được kiểm chứng thực tế. Một bộ slide bắt mắt nhưng thiếu chỉ số RTF và không có bản ghi dự phòng được coi là không đạt. Danh mục kiểm tra (checklist) dưới đây đóng vai trò sổ tay vận hành trước ngày demo: bao gồm lệnh kiểm tra, danh sách tệp và các kịch bản tiêm lỗi (fault injection) có chủ đích.

![RTF so với quantum render của AudioWorklet]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Hình. RTF là tỉ số giữa thời gian xử lý thực tế của một quantum và thời lượng của quantum đó. Giá trị trung bình dưới 1 vẫn có thể gây tràn hạn nếu phân vị p95 hoặc p99 vượt ngưỡng callback. Luôn ghi log p95 và tách riêng thời gian tải tài nguyên lúc khởi động.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ rà soát trọn vẹn đường truyền âm thanh, đường tải tài nguyên và các tệp số liệu, luyện tập kịch bản trình bày 5 phút, thực hiện tiêm lỗi chặn CDN mà cuộc gọi không gián đoạn, đồng thời trình bày mẫu âm thanh so sánh kèm nhãn điều kiện rõ ràng.

## Danh mục kiểm tra kỹ thuật

Sao chép các hạng mục sau vào tệp `capstone/notes/demo_checklist.md` và đánh dấu hoàn thành; mọi mục bỏ trống đều coi là chưa đạt trừ khi ghi rõ `n/a` kèm lý do.

**Đường truyền âm thanh:**

- Quyền truy cập micro hoạt động ổn định trên chính máy dùng để demo.
- Cả hai trạng thái `setEnabled(true)` và `setEnabled(false)` đều giữ nguyên track đã phát hành (nếu giao diện buộc phải vào lại phòng, cần ghi rõ đó là giới hạn).
- Trạng thái bật/tắt `noiseSuppression` của trình duyệt được ghi lại tường minh để tránh quy nhầm hiệu quả của trình duyệt cho `DeepFilterNoiseFilterProcessor`.
- Khi rời phòng họp, không để rò rỉ `AudioContext` gây nhiễu ở lần tham gia kế tiếp.

**Tải mô hình từ CDN:**

- Ở lần tải lạnh, gói ≥ 1.2.0 (gồm 1.3.0) gọi đúng `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`; kiểm tra trên tab Network để xác nhận **không** đưa sẵn `v2/` vào `assetConfig.cdnUrl`.
- Ở lần tải thứ hai, tài nguyên được phục vụ từ cache (hoặc ghi nhận rõ nếu chưa bật cache).
- Khi chặn kết nối CDN, cuộc gọi vẫn phát hành tín hiệu gốc chưa xử lý và giao diện hiển thị thông báo lỗi; lưu ảnh chụp hoặc dòng log vào `capstone/notes/`.

**Bảng số liệu (`capstone/metrics/suite.md`):**

- Đủ 6 cột: `clip id`, `condition`, `SI-SDR` hoặc `n/a`, `DNSMOS` hoặc `n/a`, `listening note` và `RTF p95`.
- Có ít nhất một hàng bản ghi thực tế với cột SI-SDR ghi `n/a`.
- Cột `RTF p95` ghi kèm tên thiết bị đo; nếu chỉ mới dừng ở dùng thử nội bộ (dogfood), ghi `n/a` chứ không ước đoán con số 0,2.
- Ghi đầy đủ phiên bản: `deepfilternet3-noise-filter`, tên gói nén mô hình, phiên bản DNSMOS (hoặc `not run`).

**Chuẩn bị cho buổi demo:**

- Có sẵn tệp ghi âm dự phòng phát được ngay nếu micro trực tiếp gặp sự cố.
- Chuẩn bị sẵn tai nghe trên bàn để tránh vọng loa.
- Chuẩn bị đủ ba nhóm mẫu: tiếng ồn quán cà phê (babble), tiếng gõ bàn phím và phòng yên tĩnh.

**Nhánh Rust (nếu có thực hiện):** Câu giới thiệu đầu tiên khớp với tệp `df_core_status.md`; nếu ở trạng thái `passthrough`, nói rõ “noise suppression is not running”.

## Kịch bản trình bày 5 phút

| Mốc thời gian | Nội dung trình bày | Tệp mở kèm |
|-----------|--------|----------------|
| 0:00–0:40 | Bài toán khử nhiễu uplink trên thiết bị cho LiveKit | `design/sketch.md` |
| 0:40–1:20 | Tám bước luồng công khai, không gọi lớp nội bộ | `publish-path.md` |
| 1:20–2:30 | Phát đối chiếu bản thô và bản đã xử lý, nêu rõ điều kiện | Tệp WAV dự phòng |
| 2:30–3:30 | Phân tích một hàng cải thiện và một hàng không cải thiện | `metrics/suite.md` |
| 3:30–4:20 | Kết luận giả thuyết, kể cả khi kết quả không đạt kỳ vọng | `design/hypothesis.md` |
| 4:20–5:00 | Giới hạn: ngôn ngữ, thiết bị, bản DNSMOS, trạng thái Rust | `notes/limits.md` |

Nếu chạy thử bị quá 5 phút, hãy rút gọn phần kiến trúc trước, tuyệt đối không cắt bỏ hàng phản ví dụ — việc chỉ ra trường hợp không cải thiện mới chứng minh bạn thực sự làm chủ hệ thống đánh giá.

## Thực hành tiêm lỗi (fault injection)

Chủ động chặn tên miền CDN (chuyển chế độ offline trong DevTools hoặc đặt sai `cdnUrl`) rồi tham gia phòng họp. Kết quả kỳ vọng: phòng họp vẫn có âm thanh, processor không giả vờ mô hình đang chạy, và bạn ghi lại xem công tắc `setEnabled` có còn phản hồi hay không. Sau đó khôi phục mạng và tải lại trang: kiểm tra tệp WASM cùng `.tar.gz` tải thành công từ nhánh `v2/`. Nếu hệ thống hành xử khác kỳ vọng, hãy ghi nhận thẳng vào mục giới hạn thay vì giấu đi.

Nếu có dữ liệu log RTF, hãy kiểm tra ở khung quantum chậm nhất thay vì chỉ nhìn trung bình; cột vượt ngưỡng trên biểu đồ chính là dấu hiệu lỗi. Nếu chưa tính được p95 thì để `n/a`.

## Mini-lab

Sau khi hoàn thiện `capstone/notes/demo_checklist.md`, kiểm tra độ đầy đủ bằng script sau:

```python
from pathlib import Path
text = Path("capstone/notes/demo_checklist.md").read_text().lower()
need = [
    "setenabled",
    "noisesuppression",
    "df_bg.wasm",
    "deepfilternet3_onnx.tar.gz",
    "si-sdr",
    "dnsmos",
    "rtf p95",
    "backup",
    "passthrough",
]
missing = [n for n in need if n not in text]
print("missing", missing or "none")
```

**Kết quả kỳ vọng**

```text
missing none
```

Vẫn giữ từ khóa `passthrough` trong tệp kể cả khi bạn không làm nhánh Rust (ví dụ ghi: “Rust: not attempted, so not a passthrough claim.”) để đảm bảo checklist không bỏ sót quy tắc xác nhận nhánh mở rộng.

**Lỗi thường gặp.** Đánh dấu đạt ở mục RTF mà không ghi tên thiết bị; dùng bản ghi dự phòng khác hoàn toàn với kịch bản demo trực tiếp; chèn sẵn `v2/` vào `cdnUrl` gây lỗi 404; hoặc giới thiệu bản Rust `passthrough` là “NS works”.

## Bài tập

1. Chạy thử kịch bản demo có bấm giờ, lưu thời lượng vào `capstone/notes/rehearsal.txt` và tinh chỉnh đến khi không vượt quá 5 phút.
2. Thực hiện bài kiểm tra chặn CDN và dán ghi nhận thực tế ngay bên dưới checklist.
3. Trao đổi mục giới hạn (`limits.md`) với một đồng nghiệp để mỗi người tìm ra ít nhất một phát biểu dễ bị hiểu là khẳng định quá mức.
4. Liệt kê danh sách thư mục từ bài 09-04 bạn sẽ nén hoặc đẩy lên fork cá nhân (loại trừ hoàn toàn kho sản phẩm chung).
5. Quan sát cột vượt ngưỡng trên biểu đồ RTF và nêu cách báo cáo trung thực nếu log của bạn hiện chỉ có giá trị trung bình.

### Gợi ý đáp án

1. Luôn cắt bớt phần giới thiệu kiến trúc trước, giữ lại các hàng phản ví dụ trong bảng số liệu.
2. Ghi nhận trung thực hành vi thực tế, ví dụ: “Âm thanh gốc vẫn được phát hành, mô hình không tải được, giao diện hiển thị thông báo lỗi”.
3. Các phát biểu quá mức thường gặp: báo cáo SI-SDR trên tệp ghi âm thực tế hoặc ghi điểm DNSMOS mà không nêu phiên bản checkpoint.
4. Nộp bốn thư mục `capstone/design`, `audio`, `metrics`, `notes` từ kho cá nhân, không đính kèm tệp nào thuộc kho sản phẩm chung.
5. Báo cáo giá trị trung bình đo được và ghi `n/a` ở cột RTF p95, tuyệt đối không tự ước đoán phân vị.

## Video tham khảo

- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. **Xem trước.** Các phần về đánh giá và tích hợp tương ứng trực tiếp với cấu trúc checklist: số liệu, kiểm thử lắng nghe và hệ thống gọi thực tế.
- [Sonic Boom! Audio Programming on Android and Chrome (Google I/O'19)](https://www.youtube.com/watch?v=EeQr0zfvF04) — Google for Developers, tiếng Anh. Minh họa cách đo lỗi giật tiếng (glitch) và trễ hạn callback — cơ sở cho bài tiêm lỗi hiệu năng.
- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, tiếng Anh. Tham khảo cách chuẩn bị mẫu âm thanh dự phòng để buổi demo luôn có âm thanh đối chiếu dù micro trực tiếp gặp sự cố.
