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

Bài này là bản đồ và hợp đồng học tập: các chương đi từ nền Fourier đến capstone gắn Mezon, bề mặt sản phẩm công khai là gì, và cách học để không nhầm “biết gọi wrapper” với “nắm kỹ thuật”.

## Mục tiêu học tập

1. Điều hướng bản đồ chương từ DSP → NS cổ điển → DeepFilterNet → realtime/on-device → sản phẩm → đánh giá → capstone.
2. Mô tả stack mezon-noise-suppression ở **mức cao** chỉ bằng thông tin công khai.
3. Nêu hợp đồng sư phạm: dạy kỹ thuật; npm `deepfilternet3-noise-filter` là *bề mặt*, không phải toàn bộ giáo trình.
4. Lập lộ trình học (đầy đủ vs rút gọn) theo nền tảng của bạn.
5. Biết chỗ tìm outline cố vấn và quy tắc đóng góp.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–15 | Đi bảng chương trong COURSE_OUTLINE.md; đánh dấu tiên quyết |
| 15–30 | Ngữ cảnh sản phẩm: GitHub / npm / path local; nên và không nên |
| 30–45 | Xem trước capstone (Ch. 09) và tư duy đánh giá (Ch. 08) |
| 45–55 | Phiếu lộ trình cá nhân |
| 55–60 | Bài tập nhỏ |

## Giải thích cốt lõi

### Bản đồ chương (00–10)

| Ch | Chủ đề | Vì sao có |
|----|--------|-----------|
| 00 | Định khung bài toán | Từ vựng chung, ngữ cảnh Mezon |
| 01 | Fourier & biến đổi rời rạc (**sâu**) | Đọc STFT/FFT như kỹ sư |
| 02 | Pipeline xử lý âm thanh | PCM → frame → STFT → tradeoff trễ |
| 03 | NS / AEC / beamforming cổ điển | Prior mà DeepFilterNet vẫn đứng trên |
| 04 | SE neural & họ DeepFilterNet | Ý tưởng mô hình và khảo sát kế thừa |
| 05 | Ràng buộc thời gian thực | RTF, AudioWorklet, ring buffer, state |
| 06 | Suy luận trên thiết bị | ONNX/tract, lượng tử hóa, WASM/SIMD |
| 07 | Tích hợp sản phẩm | WebRTC, LiveKit, CDN, npm |
| 08 | Đánh giá | SI-SDR, DNSMOS, listening, DNS metrics |
| 09 | Capstone: Mezon NS | Kỹ thuật end-to-end |
| 10 | Tài liệu & hướng đi tiếp | Chỉ nguồn đã chọn lọc |

Chương **01** và **02** là module hạng nhất (mỗi bên bảy bài), không phải phụ lục DSP.

### Lộ trình gợi ý

- **Đầy đủ** (mới DSP): 00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09.
- **Nhanh** (DSP chắc, mới neural SE): 00 → checklist 01–02 → 04 → 05–07 → 08 → 09.
- **Tích hợp sản phẩm:** 00, 02-07, 05, 06, 07, 08, 09 — vẫn đọc 01-07 pitfalls.

### Mezon (công khai)

Repo `mezonai/mezon-noise-suppression`, npm `deepfilternet3-noise-filter`, path giảng viên `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.

**Quy tắc:** không sửa product repo từ bài khóa học; không bịa kiến trúc chưa công bố; capstone chứng minh hiểu framing/latency/eval; Rust `df-core` là stretch (Ch. 09).

### “Kỹ thuật chứ không phải wrapper”

Biết gọi API npm là hữu ích nhưng chưa đủ. Bạn phải trả lời được hop/cửa sổ/sample rate giả định, nguồn độ trễ thuật toán, xử lý stereo thế nào, và đo chất lượng ra sao — câu trả lời nằm ở Ch. 01–02, 04–08.

### Ví dụ ánh xạ bug → chương

Triệu chứng: “NS có warble robot mỗi 10 ms.”

1. **02** — lệch hop/cửa sổ/OLA.
2. **01** — đọc bin FFT sai sau resample.
3. **05** — underrun lặp frame.
4. **04** — mask tuần hoàn quá mạnh — *cuối cùng*, sau vệ sinh pipeline.

## Bẫy thường gặp

1. Nhảy tới trọng số Ch. 04 trước khi đúng sample rate và downmix mono.
2. Lấy tên gói npm làm bằng chứng đồ thị mô hình chưa công bố.
3. Chỉ học một ngôn ngữ (EN hoặc VI) rồi bỏ lỡ sửa ở locale kia.
4. Bỏ Ch. 08 và tuyên bố thắng từ một demo quán cà phê.

## Bài tập nhỏ

1. Ghi nền tảng (DSP: không/có/chắc; WebAudio: không/có) và chọn lộ trình đầy đủ hay nhanh.
2. Từ COURSE_OUTLINE.md, liệt kê bảy tiêu đề bài EN Chương 01.
3. Nêu ba nguồn công khai được phép trích dẫn về hành vi DeepFilterNet.
4. Viết một tiêu chí thành công capstone *đo được* (ví dụ “p95 RTF ≤ 0.5 trên máy X @ 48 kHz mono”).

## Đọc thêm

- `COURSE_OUTLINE.md`, `AGENTS.md`, `README.md` trong repo này.
- README GitHub công khai: `mezonai/mezon-noise-suppression`.
- Trang npm: `deepfilternet3-noise-filter`.
- Paper DeepFilterNet cho ngữ cảnh thuật toán (không phải khẳng định riêng Mezon).
