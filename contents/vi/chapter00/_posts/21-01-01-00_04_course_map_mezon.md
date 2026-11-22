---
layout: post
title: "00-04 Lộ trình khóa học và ngữ cảnh sản phẩm Mezon"
chapter: "00"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter00
lesson_type: required
draft: false
---

Bài học này đóng vai trò như bản đồ và cam kết học tập cho toàn khóa: các chương được sắp xếp từ nền tảng biến đổi Fourier đến bài tập tổng kết (capstone) gắn với Mezon, chỉ rõ bề mặt công khai của sản phẩm là gì và định hướng cách học để tránh nhầm lẫn giữa "biết gọi wrapper" với "nắm vững kỹ thuật".

![TrackProcessor của LiveKit, chỗ công khai để gắn bộ lọc nhiễu lên một media track]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Hình. Sơ đồ chỉ minh họa điểm tích hợp công khai: gắn một TrackProcessor lên media track, không tiết lộ cấu trúc nội bộ chưa công bố của Mezon.*

## Mục tiêu học tập

1. Nắm được lộ trình xuyên suốt các chương: từ DSP → khử nhiễu cổ điển → DeepFilterNet → thời gian thực và suy luận trên thiết bị → tích hợp sản phẩm → đánh giá → bài tập tổng kết.
2. Mô tả kiến trúc `mezon-noise-suppression` ở **mức tổng quan** chỉ dựa trên thông tin công khai.
3. Nêu rõ nguyên tắc sư phạm của khóa học: giảng dạy nền tảng kỹ thuật; gói npm `deepfilternet3-noise-filter` là *bề mặt ứng dụng*, không phải toàn bộ giáo trình.
4. Xây dựng lộ trình học phù hợp (đầy đủ hoặc rút gọn) tùy theo nền tảng cá nhân.
5. Biết nơi tra cứu đề cương khóa học và quy tắc đóng góp.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–15 | Rà soát bảng chương trong `COURSE_OUTLINE.md` và đánh dấu các kiến thức tiên quyết |
| 15–30 | Ngữ cảnh sản phẩm: GitHub, gói npm và đường dẫn nội bộ của giảng viên; những điều nên và không nên làm |
| 30–45 | Giới thiệu sơ bộ bài tập tổng kết (Chương 09) và tư duy đánh giá (Chương 08) |
| 45–55 | Lập phiếu lộ trình học tập cá nhân |
| 55–60 | Bài tập nhỏ |

## Giải thích cốt lõi

### Bản đồ chương (00–10)

| Ch | Chủ đề | Mục đích |
|----|--------|----------|
| 00 | Định khung bài toán | Thống nhất thuật ngữ và ngữ cảnh Mezon |
| 01 | Fourier & biến đổi rời rạc (**chuyên sâu**) | Đọc và phân tích STFT/FFT dưới góc nhìn kỹ sư |
| 02 | Pipeline xử lý âm thanh | Chuỗi PCM → định khung → STFT → đánh đổi độ trễ |
| 03 | NS / AEC / beamforming cổ điển | Các giả định nền tảng mà DeepFilterNet vẫn kế thừa |
| 04 | Tăng cường tiếng nói bằng mạng nơ-ron & họ DeepFilterNet | Ý tưởng cốt lõi của mô hình và khảo sát các nhánh kế thừa |
| 05 | Ràng buộc thời gian thực | RTF, AudioWorklet, bộ đệm vòng (ring buffer) và quản lý trạng thái |
| 06 | Suy luận trên thiết bị (on-device) | ONNX/tract, lượng tử hóa và WASM/SIMD |
| 07 | Tích hợp sản phẩm | WebRTC, LiveKit, CDN và đóng gói npm |
| 08 | Đánh giá | SI-SDR, DNSMOS, kiểm tra nghe và bộ chỉ số DNS |
| 09 | Capstone: Mezon NS | Triển khai kỹ thuật đầu–cuối |
| 10 | Tài liệu & hướng đi tiếp | Danh mục nguồn tham khảo chọn lọc |

Chương **01** và **02** là hai học phần trọng tâm (mỗi chương gồm bảy bài), không phải phần phụ lục DSP lướt qua.

### Lộ trình gợi ý

- **Lộ trình đầy đủ** (mới tiếp cận DSP): 00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09.
- **Lộ trình rút gọn** (đã vững DSP, mới tiếp cận neural SE): 00 → danh mục kiểm tra 01–02 → 04 → 05–07 → 08 → 09.
- **Hướng tích hợp sản phẩm:** 00, 02-07, 05, 06, 07, 08, 09 — vẫn cần đọc bài 01-07 về các bẫy thường gặp.

### Ngữ cảnh Mezon (thông tin công khai)

- Kho mã nguồn: https://github.com/mezonai/mezon-noise-suppression
- Gói npm: `deepfilternet3-noise-filter` **1.3.0**
- Các lớp công khai trên bề mặt API: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`
- Tham số điều khiển công khai: `setSuppressionLevel(0–100)`
- Tần số lấy mẫu mặc định: **48 kHz toàn băng (full-band)**
- Đường dẫn trên máy giảng viên (không bắt buộc với học viên): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`

**Quy tắc thực hành:** không chỉnh sửa trực tiếp kho mã sản phẩm từ bài học; không suy diễn kiến trúc nội bộ chưa công bố; bài tập tổng kết chứng minh năng lực hiểu về định khung, độ trễ và đánh giá; phần Rust `df-core` là nội dung mở rộng ở Chương 09.

### "Dạy kỹ thuật, không chỉ gọi wrapper"

Biết cách gọi API từ gói npm là hữu ích nhưng chưa đủ. Kỹ sư cần trả lời được các câu hỏi nền tảng: mô hình giả định kích thước hop, cửa sổ và tần số lấy mẫu nào; độ trễ thuật toán phát sinh từ đâu; tín hiệu stereo được xử lý theo quy tắc gì; và chất lượng được đo lường ra sao — lời giải nằm trải dài từ Chương 01–02 đến Chương 04–08.

`setSuppressionLevel` trông chỉ như một lời gọi hàm đơn giản, nhưng để hiểu đúng bản chất, ta phải lần theo bản đồ kiến thức: giá trị số nguyên đó chọn điểm làm việc cho độ lợi hoặc mặt nạ đã huấn luyện (Chương 03–04), mặc định 48 kHz quyết định tần số Nyquist và phép tính hop (Chương 01–02), còn bộ xử lý vẫn phải hoàn tất trong ngân sách thời gian của callback (Chương 05). Sơ đồ LiveKit ở trên chỉ minh họa trước vị trí gắn `DeepFilterNoiseFilterProcessor` lên track âm thanh (Chương 07), chứ không phải cơ sở để suy đoán các bộ đệm chưa công bố trong mã nguồn nội bộ của giảng viên.

### Ví dụ ánh xạ triệu chứng lỗi → chương tương ứng

Triệu chứng: "Âm thanh sau khử nhiễu có tiếng rung giật (warble) kiểu robot lặp lại mỗi 10 ms."

1. **Chương 02** — kiểm tra lệch kích thước hop, cửa sổ hoặc cộng chồng lấp OLA.
2. **Chương 01** — kiểm tra sai lệch chỉ số bin FFT sau khi lấy mẫu lại (resample).
3. **Chương 05** — kiểm tra hiện tượng underrun gây lặp khung.
4. **Chương 04** — kiểm tra khả năng mặt nạ tuần hoàn quá mạnh — *bước cuối cùng*, chỉ xét sau khi đã loại trừ lỗi pipeline.

Hiện tượng rung giật chu kỳ 10 ms tương ứng tần số điều biến \(100\,\mathrm{Hz}\) vì \(1/0.010=100\). Con số này gợi ý mạnh tới điều biến biên độ theo nhịp hop (Chương 02) trước khi nghi ngờ checkpoint mô hình bị lỗi (Chương 04). Phần Mini-lab dưới đây chuyển phép tính này thành điều kiện kiểm tra đạt/không đạt theo thời gian xử lý p95.

## Bẫy thường gặp

1. Nhảy thẳng vào trọng số mô hình ở Chương 04 trước khi đảm bảo đúng tần số lấy mẫu và quy tắc gộp kênh mono.
2. Coi tên gói npm là bằng chứng về cấu trúc đồ thị mô hình nội bộ chưa công bố.
3. Chỉ theo dõi một phiên bản ngôn ngữ (EN hoặc VI) mà bỏ sót các bản cập nhật ở ngôn ngữ còn lại.
4. Bỏ qua Chương 08 và vội kết luận hiệu quả chỉ dựa trên một đoạn nghe thử tại quán cà phê.

## Mini-lab

**Mục tiêu.** Liên hệ triệu chứng "rung giật mỗi 10 ms" với bước nhảy hop ở tần số lấy mẫu mặc định 48 kHz, sau đó kiểm tra ngưỡng đạt/không đạt bằng thời gian xử lý p95.

```python
fs, hop = 48_000, 480
hop_ms = 1_000 * hop / fs
warble_hz = 1_000 / hop_ms
print(f"hop_ms={hop_ms:.1f} warble_if_cola_fails_hz={warble_hz:.0f}")
for p95_ms in (6.0, 12.0):
    print(p95_ms, p95_ms < hop_ms)
```

**Kết quả kỳ vọng.** `hop_ms=10.0 warble_if_cola_fails_hz=100`, tiếp theo là `6.0 True`, rồi `12.0 False`.

**Lỗi thường gặp.** Đổ lỗi cho `DeepFilterNet3Core` trước khi kiểm tra kích thước hop; chấp nhận mức p95 bằng 12 ms chỉ vì thời gian trung bình là 4 ms; hoặc diễn giải sơ đồ LiveKit như đặc tả kiến trúc nội bộ.

## Bài tập nhỏ

1. Ghi lại nền tảng hiện tại của bạn (DSP: chưa biết / cơ bản / vững; WebAudio: chưa biết / đã dùng) và chọn lộ trình đầy đủ hay rút gọn.
2. Từ `COURSE_OUTLINE.md`, liệt kê bảy tiêu đề bài học tiếng Anh của Chương 01.
3. Nêu ba nguồn công khai hợp lệ được phép trích dẫn khi mô tả hành vi của DeepFilterNet.
4. Viết một tiêu chí nghiệm thu *đo lường được* cho bài tập tổng kết (ví dụ: "p95 RTF ≤ 0.5 trên máy X ở 48 kHz mono").

### Gợi ý đáp án

1. Nếu chưa có nền tảng DSP và WebAudio, nên đi theo lộ trình đầy đủ. Nếu đã vững DSP nhưng mới làm quen với neural SE, có thể đi theo lộ trình rút gọn nhưng vẫn nên đọc danh mục kiểm tra 01-07 thay vì bỏ hẳn.
2. Bảy tiêu đề tương ứng với trường `title:` trong `contents/en/chapter01/_posts/`, theo thứ tự từ 1 đến 7 (từ trực giác Fourier liên tục đến danh mục các bẫy thường gặp).
3. Ba bài báo arXiv:2110.05588, arXiv:2205.05474, arXiv:2305.08227, cùng tệp README tại https://github.com/mezonai/mezon-noise-suppression. Kho mã tham chiếu: https://github.com/Rikorose/DeepFilterNet.
4. Tiêu chí cần ghi rõ cấu hình máy thử nghiệm, tần số lấy mẫu (48 kHz toàn băng nếu bám cấu hình mặc định của sản phẩm), chế độ mono hoặc quy tắc downmix, và một chỉ số phân vị đuôi như p95 RTF. Nhận xét cảm tính như "nghe sạch hơn" không phải là tiêu chí nghiệm thu.

## Đọc thêm

- Các tệp `COURSE_OUTLINE.md`, `AGENTS.md` và `README.md` trong kho tài liệu này.
- Tệp README GitHub công khai: `mezonai/mezon-noise-suppression`.
- Trang gói npm: `deepfilternet3-noise-filter`.
- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) cho ngữ cảnh thuật toán, không dùng để suy diễn chi tiết riêng của Mezon.

## Video tham khảo

- [But what is the Fourier Transform?  A visual introduction.](https://www.youtube.com/watch?v=spUNpyF58BY) — 3Blue1Brown, tiếng Anh. **Xem trước.** Giúp hình dung trực quan miền tần số trước khi các chương đầu của lộ trình đi vào định nghĩa toán học và bài toán khử nhiễu.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Đây là đích đến ở phần mạng nơ-ron của lộ trình: đầu vào STFT và đầu ra khử nhiễu toàn băng theo thời gian thực.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Minh họa con đường từ tập dữ liệu mở đến tính năng gọi thoại thực tế; các chương sau sẽ bám sát vòng lặp đánh giá đó.
