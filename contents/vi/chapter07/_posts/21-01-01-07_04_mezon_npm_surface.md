---
layout: post
title: "07-04 Bề mặt npm Mezon (kỹ thuật, không chỉ wrapper)"
chapter: "07"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter07
lesson_type: required
draft: false
---

Gói npm `deepfilternet3-noise-filter` là **phương tiện** đưa DeepFilterNet3 vào app LiveKit/WebAudio — không phải toàn bộ giáo trình. Bài này ánh xạ API công khai sang khái niệm DSP và hệ thống ở Chương 02–06 để capstone cải thiện *kỹ thuật*, không phải trivia wrapper.

## Kế hoạch giảng 60 phút

- 0–10 phút: Bản đồ gói — Core vs TrackProcessor vs asset.
- 10–25 phút: Bảng API → khái niệm (frame, attenuation, worklet).
- 25–40 phút: Núm chỉnh latency vs chất lượng.
- 40–50 phút: Extend vs fork vs configure.
- 50–60 phút: Mini-lab: chú thích sample README bằng link chương.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Ánh xạ lời gọi npm API sang khái niệm DSP/suy luận.
- Liệt kê điểm mở rộng cho model/runtime tùy chỉnh.
- Không coi gói như hộp đen trong capstone.
- Quyết định configure vs fork có lập luận bảo trì.

## Bề mặt công khai (tóm tắt)

### `DeepFilterNoiseFilterProcessor`

- Options: `sampleRate`, `noiseReductionLevel`, `enabled`, `assetConfig.cdnUrl`
- `setSuppressionLevel`, `setEnabled`
- Dùng với `LocalAudioTrack.setProcessor`

### `DeepFilterNet3Core`

- `initialize`, `createAudioWorkletNode`, `setSuppressionLevel`, `destroy`

Repo: [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression).  
Đường local giảng viên (không sửa từ bài tập khóa): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.

## API → khái niệm khóa học

| API / artifact | Ý tưởng khóa học |
|----------------|------------------|
| 48 kHz | Ch 02 PCM / full-band |
| Worklet | Ch 05 callback realtime |
| Xử lý frame trong WASM | Ch 02 + DF Ch 04 |
| `noiseReductionLevel` | Mức aggressiveness — chất lượng vs artifact |
| CDN model | Ch 06 + 07-03 |
| SIMD WASM ≥1.2.0 | Ch 06 |
| `setProcessor` | Ch 07-01/02 điểm A |

Gương native (stretch): Rust `df-core` — Ch 09-03.

## Configure vs fork

| Tình huống | Ưu tiên |
|------------|---------|
| CDN URL, mức mặc định, UX bật/tắt | Configure |
| Lỗi lifecycle / lệch phiên bản LiveKit | PR upstream hoặc wrap tạm |
| Kiến trúc model mới | Fork / gói riêng — giữ license (Apache-2.0 OR MIT) |
| Bài tập khóa | **Không** sửa product repo; làm trên fork / notes / rust sibling |

## Checklist kỹ thuật (không cần sửa source gói)

1. Harness đánh giá WAV + SI-SDR/DNSMOS  
2. Chính sách UX (tắt NS khi music mode / CPU cao)  
3. Host asset CDN riêng  
4. Telemetry init/fallback (không upload audio)  
5. (Nâng cao) đổi ONNX nếu loader cho phép  
6. (Stretch) parity `process_frame` trong Rust  

## Bẫy thường gặp

1. Capstone = “bump dependency” không đo lường.
2. Nhầm bug wrapper với chất lượng model.
3. Quên license / ghi nguồn khi redistribute weights.
4. Sửa cây product dùng chung thay vì workspace cá nhân.

## Bài tập

1. Bảng hai cột: README API | kỹ thuật chương.
2. Đề xuất một cải tiến capstone **không** cần sửa source gói.
3. Đề xuất một cải tiến cần fork — biện minh.
4. Nghe A/B mức 40 vs 80 trên một clip quán cà phê.

## Đọc thêm

- npm `deepfilternet3-noise-filter`
- GitHub mezonai/mezon-noise-suppression
- Upstream Rikorose/DeepFilterNet
- Bài DeepFilterNet ICASSP 2022 (arXiv:2110.05588)
