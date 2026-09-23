---
layout: post
title: "02-03 Cửa sổ hóa và rò phổ"
chapter: "02"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Cửa sổ điều khiển tradeoff giữa rò phổ và bề rộng lobe chính. Trong NS, cửa sổ sai (hoặc cặp analysis/synthesis lệch) tạo musical noise và warble theo hop.

## Mục tiêu học tập

1. Giải thích rò phổ từ cắt chữ nhật.
2. So sánh định tính Hann, Hamming, Blackman.
3. Nối bề rộng lobe chính với độ phân giải tần số và định vị thời gian.
4. Nêu tương tác cửa sổ với COLA và mask NS.
5. Chọn cửa sổ nhất quán với STFT front-end pretrained.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Demo rò cửa sổ chữ nhật (tư duy/đồ thị) |
| 12–28 | Catalog cửa sổ; sidelobe vs lobe chính |
| 28–42 | COLA + chọn cửa sổ; cửa sổ kép |
| 42–52 | Musical noise và huyền thoại bin độc lập |
| 52–60 | Bài tập |

## Giải thích cốt lõi

Nhân \(w[n]\) ↔ tích chập phổ với \(W\). Chữ nhật: sidelobe cao. Cửa sổ taper: sidelobe thấp, lobe chính rộng. Độ phân giải hiệu dụng \(\sim\alpha f_s/L\); định vị thời gian \(\sim L/f_s\). NS tiếng nói cần cửa sổ cỡ vài chục ms.

Gain nhảy loạn trên bin kề chiến với smoothing vốn có của cửa sổ — hoặc tạo musical noise khi coi bin độc lập. Một số pipeline dùng \(\sqrt{\mathrm{Hann}}\) hai phía. **Khớp training**; đừng đổi Blackman “cho đẹp” bừa.

## Ví dụ có số

16 kHz, \(L=512\), tone đúng bin 32 vs 32.5. Spectral subtraction bin độc lập → birdies; làm mượt giúp nhưng làm mờ tiếng nói — căng thẳng cổ điển trước SE neural.

## Bẫy thường gặp

1. Áp cửa sổ hai lần (API đã cửa sổ + nhân tay).
2. Dùng chữ nhật vì “FFT cần thế”.
3. Quên gain cửa sổ khi Parseval / SI-SDR.
4. Cửa sổ khác nhau train vs serve.
5. Kỳ vọng cửa sổ chữa aliasing.

## Bài tập nhỏ

1. Vì sao cửa sổ taper giảm sidelobe?
2. \(L\) gấp đôi ⇒ lobe chính roughly thế nào?
3. Hop thân thiện COLA phổ biến với Hann?
4. Mask per-bin hung hãn tạo musical noise thế nào?
5. Một lý do \(\sqrt{\mathrm{Hann}}\) xuất hiện trong codebase STFT?

## Đọc thêm

- Oppenheim & Schafer — cửa sổ và phân tích phổ.
- Handout so sánh cửa sổ DSP.
- Mục cấu hình STFT DeepFilterNet.
