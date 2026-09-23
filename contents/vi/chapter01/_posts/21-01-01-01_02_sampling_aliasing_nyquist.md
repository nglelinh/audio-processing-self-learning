---
layout: post
title: "01-02 Lấy mẫu, aliasing và Nyquist"
chapter: "01"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Mọi track WebRTC và mọi forward DeepFilterNet đều giả định một sample rate. Sai rate tạo bug aliasing im lặng trông như “hồi quy chất lượng mô hình”. Bài này làm định lý lấy mẫu thành công cụ vận hành.

![Phổ bị sao chép theo mỗi sample rate; các bản sao chồng khi tín hiệu quá rộng]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Figure. Lấy mẫu lặp phổ mỗi \(f_s\) hertz; chỗ chồng là aliasing, bộ khử nhiễu neural không gỡ được.*

## Mục tiêu học tập

1. Nêu định lý lấy mẫu và tốc độ / tần số Nyquist.
2. Giải thích aliasing bằng số liệu audio cụ thể.
3. Chọn 8 / 16 / 48 kHz có chủ đích cho pipeline NS tiếng nói.
4. Mô tả lọc chống alias trước ADC và trước decimation.
5. Liệt kê bẫy resample khi nối đồng hồ trình duyệt với rate mô hình neural.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Hậu kiểm: “chạy ONNX 16 kHz ở 48 kHz là chất lượng sập” |
| 10–25 | Lấy mẫu xung; bản sao phổ; phác Nyquist |
| 25–40 | Alias có số; bảng băng thông tiếng nói; chọn rate sản phẩm |
| 40–52 | Anti-alias + thiết kế resample; ghi chú WebAudio/WebRTC |
| 52–60 | Bẫy và bài tập |

## Giải thích cốt lõi

Lấy mẫu lý tưởng nhân \(x_c(t)\) với chuỗi xung chu kỳ \(T=1/f_s\) → phổ **lặp** mỗi \(f_s\) Hz. Nếu các bản sao chồng lên nhau → **aliasing**, không lọc số nào gỡ độc nhất được.

Trên lưới \(t=n/f_s\),

$$
\cos\!\left(2\pi\frac{f}{f_s}n\right)
=\cos\!\left(2\pi\frac{f-mf_s}{f_s}n\right)
$$

vì \(2\pi m n\) là số nguyên vòng. Gấp đại diện về \([0,f_s/2]\). Cosine 7 kHz lấy mẫu ở 8 kHz, chọn \(m=1\): \(|7000-8000|=1000\,\mathrm{Hz}\). Hai cosine đó là cùng một dãy mẫu. Sine đổi dấu: \(\sin(2\pi\cdot 7n/8)=-\sin(2\pi\cdot 1n/8)\), vì sine lẻ dưới phép dịch tròn đó. “Khớp” nghĩa là mẫu bằng nhau, không phải “nghe gần giống”.

Nếu \(x_c\) giới hạn băng \(B\) Hz, chọn \(f_s>2B\) (**tốc độ Nyquist** \(2B\); **tần số Nyquist** \(f_s/2\)).

Sau lấy mẫu: \(\omega=2\pi f/f_s\). \(\omega=\pi\) luôn là Nyquist theo mẫu — giá trị Hz phụ thuộc \(f_s\). Cùng hệ số FIR cắt khác Hz ở 16 vs 48 kHz.

| Rate | Nyquist | Dùng điển hình |
|------|---------|----------------|
| 8 kHz | 4 kHz | telephony hẹp |
| 16 kHz | 8 kHz | ML tiếng nói wideband |
| 48 kHz | 24 kHz | đồng hồ WebRTC/full-band; mặc định của `deepfilternet3-noise-filter` 1.3.0 |

Trước ADC: LPF analog. Trước **giảm mẫu** 48→16 (hệ số 3): LPF gần 8 kHz *rồi* mới lấy mỗi mẫu thứ ba. Bỏ LPF là bug.

Đưa PCM 48 kHz vào STFT train ở 16 kHz không “cho mạng thêm độ phân giải”. Bạn gán nhầm Hertz cho mọi bin, và nếu không có LPF gần 8 kHz thì năng lượng 8–24 kHz gấp vào đúng băng mạng từng học là tiếng nói. Resample: drop/repeat sai; nội suy tuyến tính yếu gần Nyquist; production dùng polyphase / libsamplerate-class. NS neural rất nhạy: tone alias thành “nhiễu lạ” mô hình chưa từng thấy.

## Ví dụ có số

Tone 5 kHz @ \(f_s=8\,\mathrm{kHz}\) → alias 3 kHz. Frame 20 ms: \(L_{16k}=320\), \(L_{48k}=960\). Compute roughly tỉ lệ samples/s — nhảy 16→48 kHz có thể ~3× thông lượng STFT nếu giữ nguyên độ dài cửa sổ theo giây.

## Bẫy thường gặp

1. Chạy mô hình train 16 kHz trên PCM 48 kHz “vì cao hơn thì tốt”.
2. Nghĩ float32 thì không alias — alias thuộc về rate, không phải bit depth.
3. Trộn 44.1 với 48 không có resampler.
4. Resample FFT sai biên khối (click).
5. Nhầm bit depth (nhiễu lượng tử) với sample rate (băng thông).

## Mini-lab

**Mục tiêu.** Lấy mẫu cosine 7 kHz ở 8 kHz và chỉ ra nó trùng dãy cosine 1 kHz.

```python
import numpy as np

fs = 8000
n = np.arange(32)
high = np.cos(2 * np.pi * 7000 * n / fs)
low = np.cos(2 * np.pi * 1000 * n / fs)
err = np.max(np.abs(high - low))
print(f"{err:.3e}")
print(np.round(high[:8], 6).tolist())
```

**Expected.** Sai số dưới `1e-12` (thường khoảng `1.354e-14`). Tám mẫu đầu làm tròn thành `[1.0, 0.707107, -0.0, -0.707107, -1.0, -0.707107, -0.0, 0.707107]`.

**Failure modes.** So sine mà quên dấu trừ. Kết luận “không alias” chỉ vì cả hai mảng là float64. Lọc thấp *sau* bộ lấy mẫu 8 kHz rồi hy vọng tone 7 kHz quay lại.

## Bài tập nhỏ

1. Tần số Nyquist @ 48 kHz và 16 kHz?
2. Alias của tone 10 kHz khi \(f_s=16\,\mathrm{kHz}\).
3. Số mẫu trong 10 ms ở 8/16/48 kHz.
4. Checklist 4 bước 48 kHz mono Float32 → input mô hình 16 kHz an toàn.
5. Vì sao \(\omega=\pi\) là Hz khác nhau ở \(f_s\) khác nhau?

### Gợi ý đáp án

1. Tần số Nyquist là \(f_s/2\): 24 kHz ở 48 kHz, 8 kHz ở 16 kHz.
2. 10 kHz tại \(f_s=16\,\mathrm{kHz}\) gấp một lần: \(16-10=6\,\mathrm{kHz}\).
3. 10 ms là 80, 160 và 480 mẫu.
4. Xác nhận mono float 48 kHz; LPF gần 8 kHz; decimate hệ số 3; sine 1 kHz vẫn ra 1 kHz và năng lượng trên 8 kHz đã hết.
5. \(\omega=\pi\) là nửa chu kỳ mỗi mẫu, tức \(f_s/2\) hertz. Tần số số đã chuẩn hóa; tần số vật lý thì không.

## Đọc thêm

- Oppenheim & Schafer — định lý lấy mẫu và đa tốc độ.
- Julius O. Smith, *Mathematics of the DFT*, https://www.dsprelated.com/freebooks/mdft/ — lấy mẫu và trục tần số mà FFT dùng.
- Web Audio `sampleRate`; tài liệu ràng buộc getUserMedia WebRTC.
