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

![TrackProcessor của LiveKit, chỗ công khai để gắn bộ lọc nhiễu lên một media track]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. Hình chỉ là khe tích hợp công khai: một TrackProcessor trên media track. Nó không lộ phần nội bộ chưa công bố của Mezon.*

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

- Repo: https://github.com/mezonai/mezon-noise-suppression
- npm: `deepfilternet3-noise-filter` **1.3.0**
- Lớp công khai trên bề mặt đó: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`
- Điều khiển công khai: `setSuppressionLevel(0–100)`
- Rate mặc định: **48 kHz full-band**
- Path giảng viên (không bắt buộc): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`

**Quy tắc:** không sửa product repo từ bài khóa học; không bịa kiến trúc chưa công bố; capstone chứng minh hiểu framing/latency/eval; Rust `df-core` là stretch (Ch. 09).

### “Kỹ thuật chứ không phải wrapper”

Biết gọi API npm là hữu ích nhưng chưa đủ. Bạn phải trả lời được hop/cửa sổ/sample rate giả định, nguồn độ trễ thuật toán, xử lý stereo thế nào, và đo chất lượng ra sao — câu trả lời nằm ở Ch. 01–02, 04–08.

`setSuppressionLevel` là một lời gọi. Giải thích nó thì phải đi theo bản đồ: số nguyên chọn điểm làm việc của gain hoặc mask đã train (Ch. 03–04), mặc định 48 kHz khóa Nyquist và phép hop (Ch. 01–02), processor vẫn phải xong trong callback (Ch. 05). Hình LiveKit ở trên chỉ xem trước chỗ `DeepFilterNoiseFilterProcessor` có thể ngồi trên track (Ch. 07). Hình đó không cho phép đoán buffer chưa công bố trong cây mã của giảng viên.

### Ví dụ ánh xạ bug → chương

Triệu chứng: “NS có warble robot mỗi 10 ms.”

1. **02** — lệch hop/cửa sổ/OLA.
2. **01** — đọc bin FFT sai sau resample.
3. **05** — underrun lặp frame.
4. **04** — mask tuần hoàn quá mạnh — *cuối cùng*, sau vệ sinh pipeline.

Warble mỗi 10 ms là \(100\,\mathrm{Hz}\) vì \(1/0.010=100\). Con số đó chỉ modulation biên độ theo nhịp hop (Ch. 02) trước khi chỉ checkpoint hỏng (Ch. 04). Mini-lab biến cùng phép tính đó thành pass/fail trên thời gian xử lý p95.

## Bẫy thường gặp

1. Nhảy tới trọng số Ch. 04 trước khi đúng sample rate và downmix mono.
2. Lấy tên gói npm làm bằng chứng đồ thị mô hình chưa công bố.
3. Chỉ học một ngôn ngữ (EN hoặc VI) rồi bỏ lỡ sửa ở locale kia.
4. Bỏ Ch. 08 và tuyên bố thắng từ một demo quán cà phê.

## Mini-lab

**Mục tiêu.** Gắn bug “warble mỗi 10 ms” với một hop ở rate mặc định 48 kHz, rồi chặn bằng thời gian xử lý p95.

```python
fs, hop = 48_000, 480
hop_ms = 1_000 * hop / fs
warble_hz = 1_000 / hop_ms
print(f"hop_ms={hop_ms:.1f} warble_if_cola_fails_hz={warble_hz:.0f}")
for p95_ms in (6.0, 12.0):
    print(p95_ms, p95_ms < hop_ms)
```

**Expected.** `hop_ms=10.0 warble_if_cola_fails_hz=100`, rồi `6.0 True`, rồi `12.0 False`.

**Failure modes.** Đổ cho `DeepFilterNet3Core` trước khi đo hop. Chấp nhận p95 12 ms vì trung bình chỉ 4 ms. Đọc sơ đồ LiveKit như đặc tả kiến trúc nội bộ.

## Bài tập nhỏ

1. Ghi nền tảng (DSP: không/có/chắc; WebAudio: không/có) và chọn lộ trình đầy đủ hay nhanh.
2. Từ COURSE_OUTLINE.md, liệt kê bảy tiêu đề bài EN Chương 01.
3. Nêu ba nguồn công khai được phép trích dẫn về hành vi DeepFilterNet.
4. Viết một tiêu chí thành công capstone *đo được* (ví dụ “p95 RTF ≤ 0.5 trên máy X @ 48 kHz mono”).

### Gợi ý đáp án

1. Chưa DSP và chưa WebAudio thì đi đủ. DSP chắc mà mới neural SE thì đi nhanh, vẫn đọc checklist 01-07 chứ không bỏ hẳn.
2. Bảy tiêu đề là trường `title:` trong `contents/en/chapter01/_posts/`, order 1 đến 7, từ trực giác Fourier liên tục đến checklist bẫy.
3. arXiv:2110.05588, arXiv:2205.05474, arXiv:2305.08227, cộng README https://github.com/mezonai/mezon-noise-suppression. Bản tham chiếu: https://github.com/Rikorose/DeepFilterNet.
4. Ghi tên máy, rate (48 kHz full-band nếu bạn nói mặc định sản phẩm), mono hoặc luật downmix, và một thống kê đuôi như p95 RTF. “Nghe sạch hơn” không phải tiêu chí.

## Đọc thêm

- `COURSE_OUTLINE.md`, `AGENTS.md`, `README.md` trong repo này.
- README GitHub công khai: `mezonai/mezon-noise-suppression`.
- Trang npm: `deepfilternet3-noise-filter`.
- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) cho ngữ cảnh thuật toán, không phải khẳng định riêng Mezon.
