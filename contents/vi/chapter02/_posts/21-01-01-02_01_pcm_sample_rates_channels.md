---
layout: post
title: "02-01 PCM, tốc độ mẫu và kênh"
chapter: "02"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Bộ khử nhiễu neural ăn tensor; micro sinh PCM. Bài này làm rõ định dạng buffer, rate và bố cục kênh — nguồn bug “tích hợp” số một trước khi mô hình chạy.

## Mục tiêu học tập

1. Mô tả encoding PCM phổ biến trên trình duyệt và stack native (s16, f32, planar vs interleaved).
2. Đổi fluently giữa mẫu, giây và byte.
3. Xử lý bố cục mono/stereo trước mô hình NS mono.
4. Giải thích lệch đồng hồ thiết bị / `AudioContext.sampleRate`.
5. Gắn định dạng kỳ vọng với đường tích hợp WebRTC / Mezon công khai.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Mở dump thô: đọc byte như s16 LE mono @ 16 kHz |
| 10–25 | Encoding, endian, float Full Scale, clipping |
| 25–40 | Kênh: interleaved/planar; chính sách downmix |
| 40–52 | Đồng hồ & chỗ đặt resample trong đồ thị |
| 52–60 | Bài tập |

## Giải thích cốt lõi

**PCM** lưu biên độ lấy mẫu đều. `int16` \(\in[-32768,32767]\); `float32` thường \(\in[-1,1]\) FS. \(x_{f32}\approx x_{s16}/32768\).

$$
N_{\mathrm{samples}}=t\cdot f_s,\qquad N_{\mathrm{bytes}}=N_{\mathrm{samples}}\cdot C\cdot B
$$

**Ví dụ:** 20 ms, 48 kHz, stereo s16 → 3840 byte.

Interleaved `LRLR...` vs planar. Đưa stereo interleaved vào FFT mono “như mono” tạo tần số giả — thảm họa. Downmix: trung bình \((L+R)/2\), hoặc chỉ trái/phải — **ghi rõ một chính sách**.

Đo `sampleRate`; đừng cứng mã. Đặt một resampler chất lượng cao ở biên khối NS về rate nội tại mô hình. Tích hợp trình duyệt thường Float32 từ Web Audio/worklet, hay 48 kHz, mono sau downmix — xác nhận README `deepfilternet3-noise-filter` hiện tại khi ship.

## Ví dụ có số

1 s mono f32 @ 16 kHz = 64000 byte. s16 sát ±32767 clipping sinh hài. Stereo interleaved 960 frame hiểu nhầm thành 960 mẫu mono → xử lý “L/R xáo” như 20 ms mono.

## Bẫy thường gặp

1. Giả định endian luôn LE khi đọc file.
2. Float ngoài \([-1,1]\) sau xử lý → méo sink.
3. Cứng 48 kHz.
4. Input stereo bị cắt thầm nửa buffer.
5. Nhầm header WAV với PCM thô từ callback.

## Bài tập nhỏ

1. Byte cho 10 ms mono s16 @ 16 kHz?
2. Pseudocode downmix interleaved → mono trung bình.
3. Vì sao stereo phản tương quan \((L=-R)\) nguy hiểm với mean downmix?
4. Ba chỗ sampleRate có thể khác trên đường gửi WebRTC.
5. Đổi s16 −16000 sang float FS với /32768.

## Đọc thêm

- Web Audio `AudioBuffer` / buffer `AudioWorkletProcessor`.
- Ràng buộc media track WebRTC và ghi chú PCM.
