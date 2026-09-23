---
layout: post
title: "09-01 Tour kiến trúc Mezon NS"
chapter: "09"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Chương capstone này đi qua stack **Mezon noise suppression** như case study sản phẩm: DeepFilterNet3 WASM trên trình duyệt bọc cho LiveKit, thử nghiệm Rust native tùy chọn, và các kỹ thuật khóa học nằm dưới. **Không sửa product repository từ bài tập khóa** — hãy đọc, phác thảo, và thử nghiệm trên workspace của bạn.

## Kế hoạch giảng 60 phút

- 0–10 phút: Mục tiêu sản phẩm (NS họp realtime on-device).
- 10–30 phút: Bản đồ module — npm, WASM, model, LiveKit processor, CDN.
- 30–45 phút: Ánh xạ module → chương 02–08.
- 45–55 phút: Bài tập phác kiến trúc cho advisor.
- 55–60 phút: Đường dẫn local và quy tắc clone.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Ánh xạ module repo sang chương khóa học.
- Nhận diện lớp suy luận, I/O, và tích hợp.
- Viết phác kiến trúc ngắn cho advisor.
- Nêu vị trí đường Rust `df-core` tùy chọn.

## Con trỏ sản phẩm

| Artifact | Vị trí |
|----------|--------|
| GitHub | [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) |
| npm | `deepfilternet3-noise-filter` |
| Local giảng viên (TS) | `/Users/nguyenlelinh/ncc/mezon-noise-suppression` |
| Rust sibling tùy chọn | `mezon-noise-suppression-rust` |
| Upstream | [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) |

## Kiến trúc phân lớp

```text
App / LiveKit Room          ← Ch 07
DeepFilterNoiseFilterProcessor / Core + Worklet  ← Ch 07, 05
WASM libDF (+ SIMD) + model tar (CDN)            ← Ch 06, 04, 07-03
DSP: ERB + deep filtering, frames                ← Ch 02, 04

Tùy chọn native: df-cli / df-audio / df-core     ← Ch 09-03
```

### Lớp suy luận / I/O / tích hợp

- Weights ONNX/tar DF3 qua WASM `libDF` (đường sản phẩm); tương lai tract/ORT/libDF trên Rust.
- Mic → frame worklet (thường 480 mẫu @ 48 kHz / 10 ms trong tài liệu stub).
- LiveKit `setProcessor`, CDN `assetConfig`, UX enable / mức khử.

## Mẫu phác cho advisor

```markdown
## Mezon NS — phác kiến trúc
- Mục tiêu: NS uplink on-device cho họp LiveKit
- Đường dữ liệu: mic → TrackProcessor → DF3 WASM → publish
- Asset: WASM + ONNX tar qua CDN layout v2 (≥1.2.0)
- Điều khiển: setEnabled, setSuppressionLevel
- Eval: SI-SDR, DNSMOS, AB listening, RTF
- Phi mục tiêu: suy luận cloud raw audio; sửa product repo trong homework
- Stretch: parity df-core + goldens
```

## Checklist chương ↔ module

| Chương | Tìm gì trong Mezon |
|--------|--------------------|
| 02 | Frame length, sample rate |
| 03 | Tương tác cờ AEC/NS trình duyệt |
| 04 | Vì sao DF3; núm attenuation |
| 05–07 | Worklet, WASM, processor, CDN |
| 08 | Cách chứng minh thay đổi |

## Bài tập

1. Điền mẫu phác advisor bằng lời của bạn (≤1 trang).  
2. Vẽ sequence `connect` → tải asset → `setProcessor` → đổi level.  
3. Ba event telemetry không upload audio.  
4. So đường TS WASM vs stub `df-core`.

## Đọc thêm

- README gói + GitHub  
- DeepFilterNet README / ICASSP 2022 (arXiv:2110.05588)  
- Chương 03–07
