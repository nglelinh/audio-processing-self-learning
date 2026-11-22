---
layout: post
title: "10-02 Hướng học tiếp"
chapter: "10"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter10
lesson_type: required
draft: false
---

Sau khi hoàn thành dự án cuối khóa, bước hiệu quả nhất là chọn duy nhất một hướng chuyên sâu và thực hiện lộ trình thực hành 30 ngày tạo ra sản phẩm cụ thể, thay vì gom một danh sách đọc dài nhưng không bao giờ mở. Cả ba hướng dưới đây đều kế thừa chung bản đồ đánh giá của khóa học: SI-SDR xâm nhập khi có bản gốc sạch, DNSMOS (hoặc `n/a`) trên bản ghi thực tế, ghi chú lắng nghe và RTF khi xử lý thời gian thực. Các chủ đề mở rộng đi kèm chỉ nhằm gợi ý những thí nghiệm gọn nhẹ cuối tuần, không phải một khóa học thứ hai bắt buộc phải hoàn thành.

![Bản đồ đánh giá để chọn dự án tiếp]({{ site.imgurl }}/generated/eval-metric-map.png)

*Hình. Dù chọn hướng chuyên sâu nào, bản đồ đánh giá vẫn giữ nguyên giá trị: một bộ lọc DSP cổ điển, một bản tái hiện bài báo mạng nơ-ron hay một chính sách tích hợp LiveKit đều được đánh giá dựa trên đúng cột chỉ số mà chúng tác động.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ chọn được một trong ba hướng đi (DSP cổ điển, tăng cường giọng nói bằng mạng nơ-ron hoặc sản phẩm hóa), xây dựng kế hoạch 30 ngày với tệp bàn giao cụ thể theo từng tuần, chọn một chủ đề thực nghiệm cuối tuần kèm phép đo rõ ràng, và hoàn thiện cây thư mục `capstone/` thành một dự án hồ sơ năng lực (portfolio) độc lập với kho sản phẩm chung.

## Hướng A — Đào sâu xử lý tín hiệu số (DSP) cổ điển

Tự cài đặt lại phép cộng chồng lấp (overlap-add) cho đến khi tín hiệu sóng sin được khôi phục trong đúng dung sai bạn in ra. Đọc mã nguồn SpeexDSP (<https://github.com/xiph/speexdsp>) hoặc WebRTC APM (<https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/>) đủ sâu để phân định rõ vai trò của khối khử nhiễu tách biệt khỏi khối khử vọng (AEC). Trên một bản thu stereo tự ghi, phân tích một tình huống thất bại của kỹ thuật tạo chùm tia (beamforming) — ví dụ người nói lệch trục hoặc micro tham chiếu bị nhiễu — mà không cần tự tuyên bố một thuật toán mới.

**Sản phẩm hoàn thành:** Tệp ghi chú `path-a/when-classical.md` phân tích một trường hợp cụ thể nơi cổng phổ đơn giản hoặc bộ lọc khuếch đại kiểu Wiener vượt trội mô hình mạng nặng về RTF mà không làm suy giảm kết quả nghe thử (chỉ ghi SI-SDR nếu có bản gốc sạch).

## Hướng B — Tăng cường giọng nói bằng mạng nơ-ron

Mỗi tuần đọc trọn vẹn một bài báo gốc trong danh mục bài 10-01, bắt đầu từ `arXiv:2110.05588`, `arXiv:2205.05474` và `arXiv:2305.08227`. Tái hiện một phép đo tốc độ bằng ONNX Runtime hoặc `tract` trên CPU laptop, báo cáo RTF bằng thời gian thực tế chia cho thời lượng âm thanh kèm tên CPU cụ thể. Nếu so sánh DeepFilterNet3 với các mô hình siêu nhẹ đã điểm tên (FastEnhancer, μNet, Fast-ULCNet, GTCRN), hãy thực hiện trên chính tập mẫu **của bạn** và không tự bịa URL bài báo; các tên như DPDFNet, DeepFilterGAN và HDF-Net cũng chỉ nên dùng như mốc tham khảo cho đến khi bạn trực tiếp mở trích dẫn gốc.

**Sản phẩm hoàn thành:** Tệp `path-b/table.md` theo đúng cấu trúc 6 cột của bài 08-04 kèm một đoạn phân tích giới hạn, tránh văn phong quảng bá bảng xếp hạng.

## Hướng C — Sản phẩm hóa và triển khai thực tế

Bám sát luồng công khai trên LiveKit: micro → `DeepFilterNoiseFilterProcessor` → `setProcessor` → phát hành track. Đo thời gian khởi động lạnh của `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` (với tiền tố `v2/` do bản 1.3.0 tự động thêm) trên điều kiện mạng thực tế của bạn, sau đó kiểm thử lại kịch bản CDN bị chặn. Nhánh mở rộng Rust `df-core` vẫn là tùy chọn thay thế cho hộp WASM; nếu mới dừng ở bước sao chép thẳng, tệp README trên portfolio phải ghi rõ `passthrough`.

**Sản phẩm hoàn thành:** Tệp `path-c/design.md` tổng hợp thời gian khởi tạo, chỉ số RTF p95 (hoặc `n/a`) và nhật ký xử lý lỗi khi CDN bị chặn.

## Các thí nghiệm mở rộng cuối tuần

| Chủ đề | Sản phẩm thực hành cuối tuần |
|--------|---------------------|
| Khử vọng (AEC) | Một bản thu có tiếng vọng lấn át tạp âm, kèm giải thích vì sao khử nhiễu (NS) không thể xóa tiếng vọng |
| Đa micro (Multi-mic) | Một bản thu stereo kèm đoạn phân tích ngắn giải thích nên tin cậy kênh nào |
| Tách người nói đích | Một đoạn tạp âm đám đông (babble) nơi điểm DNSMOS và cảm nhận tai nghe trái ngược nhau |
| Bộ mã hóa (Codec) | So sánh cùng một câu nói qua Opus bitrate thấp trước và sau khi khử nhiễu |
| Phụ đề tự động (ASR) | Đo WER hoặc đếm lỗi nhận dạng thủ công trên 10 câu (không đánh đồng với MOS) |

## Lộ trình thực hành 30 ngày

| Giai đoạn | Tệp cần bổ sung | Tiêu chí hoàn thành |
|------|-----------|----------|
| Ngày 1–3 | `notes/si_sdr.py` chạy lại bài lab `13.80` / `−10.67` | Cả hai giá trị khớp chính xác bài 08-01 |
| Ngày 4–7 | `audio/CLIPS.txt` gồm 20 tên tệp | Danh sách được chốt trước khi có điểm số |
| Ngày 8–14 | Bản MVP của hướng đã chọn (`path-a`, `path-b` hoặc `path-c`) | Tệp README có lệnh chạy tái lập rõ ràng |
| Ngày 15–21 | `metrics/suite.md` và ghi chú nghe thử cùng nhóm | Script kiểm tra bài 08-04 báo đủ 6 hàng dữ liệu (hoặc giải thích rõ nếu ít hơn) |
| Ngày 22–26 | Kịch bản `DEMO.md` dài không quá 5 phút | Đính kèm tên tệp âm thanh dự phòng rõ ràng |
| Ngày 27–30 | Cập nhật tài liệu trên fork **cá nhân** hoặc viết bản ADR tại nơi làm việc | Không commit vào kho sản phẩm Mezon chung trừ khi là công việc ngoài khóa học |

## Cấu trúc hồ sơ năng lực (Portfolio)

Một portfolio kỹ thuật thuyết phục nên bao gồm: bản phác thảo kiến trúc, bảng chỉ số 6 cột, quy trình nghe thử AB song ngữ Anh – Việt, bản ghi demo tối đa 3 phút và các thẻ đọc tài liệu từ bài 10-01. Trước khi công khai, nhớ xóa bỏ toàn bộ đường dẫn tuyệt đối của máy cá nhân.

## Mini-lab

Tạo tệp `path_plan.md` theo mẫu dưới đây:

```text
path: A
week1_file: notes/si_sdr.py
weekend: aec
command: python3 notes/si_sdr.py
```

Giá trị `path` chọn một trong `A`, `B` hoặc `C`; giá trị `weekend` chọn một trong `aec`, `multimic`, `target`, `codec`, `captions`. Kiểm tra định dạng bằng đoạn mã sau:

```python
from pathlib import Path
text = Path("path_plan.md").read_text().lower()
path_ok = any(f"path: {p}" in text for p in "abc")
weekend_ok = any(w in text for w in ("aec", "multimic", "target", "codec", "captions"))
print("path", "ok" if path_ok else "fix")
print("weekend", "ok" if weekend_ok else "fix")
print("command", "ok" if "command:" in text else "fix")
```

**Kết quả kỳ vọng**

```text
path ok
weekend ok
command ok
```

**Lỗi thường gặp.** Ôm đồm cả ba hướng trong cùng một tháng; ghi tên chủ đề cuối tuần mà không có sản phẩm bàn giao cụ thể; đặt mục tiêu RTF mà không nêu thiết bị đo; hoặc bắt đầu kế hoạch bằng việc sửa thẳng kho sản phẩm chung thay vì tạo fork riêng.

## Bài tập

1. Hoàn thiện `path_plan.md` cho hướng đi thực tế bạn chọn rồi chạy script kiểm tra.
2. Bổ sung danh sách tên tệp dự kiến hoàn thành theo từng tuần ngay bên dưới phần tiêu đề 4 dòng của tệp đó.
3. Chỉ ra một điểm thiếu rõ ràng trong tài liệu gốc (trang processor LiveKit, README npm hoặc README DeepFilterNet) mà bạn có thể viết bổ sung một đoạn hướng dẫn, kèm khẳng định chính của đoạn đó.
4. Phác thảo mục README cho portfolio liên kết tới cả 5 nhóm sản phẩm; nếu có nhánh Rust, đảm bảo tuân thủ quy tắc ghi nhãn `passthrough`.
5. Xác định cột nào trên bản đồ đánh giá sẽ ghi `n/a` trong hướng bạn chọn và giải thích lý do.

### Gợi ý đáp án

1. Chọn duy nhất một chữ cái (`A`, `B` hoặc `C`); việc đổi hướng giữa chừng ở ngày 20 đồng nghĩa bắt đầu lại kế hoạch mới.
2. Mọi đường dẫn tệp phải tự tái tạo được trên máy của người đọc, không trỏ tới đường dẫn cục bộ trên máy khác.
3. Các điểm thực tế thường thiếu rõ ràng: quy tắc tự thêm tiền tố `v2/` hoặc sự khác biệt giữa `setEnabled(false)` và lỗi tải tài nguyên CDN.
4. Liên kết trực tiếp đến từng tệp công khai, không trỏ vào kho riêng tư mà người đánh giá không mở được.
5. Bản ghi thực tế luôn ghi `n/a` ở cột SI-SDR; còn bài lab khôi phục tín hiệu DSP thuần có thể ghi `n/a` ở cột DNSMOS.

## Video tham khảo

- [The Fast Fourier Transform (FFT)](https://www.youtube.com/watch?v=E8HeD-MUrjY) — Steve Brunton, tiếng Anh. **Xem trước.** Điểm khởi đầu lý tưởng cho Hướng A: hiểu rõ độ phức tạp của DFT và cơ sở cài đặt FFT.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Trọng tâm cho Hướng B: nắm chắc một kiến trúc và chuỗi bài báo gốc thay vì lướt qua nhiều tên mô hình rời rạc.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Định hướng cốt lõi cho Hướng C: kết hợp dữ liệu thực, kiểm thử lắng nghe và ngân sách độ phức tạp trên cuộc gọi thật.
