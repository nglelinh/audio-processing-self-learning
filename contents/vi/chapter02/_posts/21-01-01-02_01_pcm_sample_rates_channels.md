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

Bộ khử nhiễu neural ăn tensor; micro cho ra PCM. Định dạng buffer, tốc độ mẫu và cách xếp kênh là chỗ tích hợp hay hỏng nhất, trước cả khi mô hình chạy. Sai \(f_s\) không chỉ làm tiếng “tối” đi: năng lượng bị gập qua tần số Nyquist. Tone 7 kHz lấy mẫu ở 8 kHz trùng mẫu với tone 1 kHz, và không mask STFT nào gỡ được phép gập đó.

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

![Lấy mẫu 8 kHz: sine 1 kHz là duy nhất, sine 7 kHz rơi đúng các mẫu đó và alias thành 1 kHz]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Hình. Với \(f_s=8\,\mathrm{kHz}\), tần số gập là 4 kHz, nên tone 7 kHz và tone 1 kHz cho cùng một dãy mẫu.*

## Giải thích cốt lõi

### PCM

**PCM** (pulse-code modulation) lưu biên độ lấy mẫu đều.

| Định dạng | Dải | Ghi chú |
|-----------|-----|---------|
| `int16` (`s16`) | \([-32768,32767]\) | WebRTC, WAV; chú ý endian |
| `float32` | thường \([-1,1]\) FS | `AudioBuffer` của Web Audio |
| `int32` / 24-bit trong container | hiếm trên đường nóng NS | đổi một lần ở biên |

$$
x_{f32} \approx \frac{x_{s16}}{32768}
$$

Một số thư viện chia cho 32767. Chọn một quy ước ở biên đồ thị và đừng trộn hai cách trong STFT. Mẫu đã bị clip trong driver không phải “tiếng nói to”: đó là phi tuyến cứng, hài của nó nằm cùng bin với phụ âm xát. Để vài dB headroom trước bộ khử nhiễu.

### Thời gian, mẫu, byte

$$
N_{\mathrm{samples}} = t\cdot f_s,\qquad
N_{\mathrm{bytes}} = N_{\mathrm{samples}}\cdot C\cdot B
$$

\(C\) là số kênh, \(B\) là byte mỗi mẫu (2 với s16, 4 với f32).

**Ví dụ:** 20 ms, 48 kHz, stereo s16 → \(0.02\cdot48000\cdot2\cdot2=3840\) byte. Cùng 20 ms mono float32 cũng ra 3840 byte — cùng độ dài, khác bố cục. Chỉ nhìn `byteLength` thì nhận cả hai. Quantum 128 mẫu của Web Audio là \(2.67\,\mathrm{ms}\) ở 48 kHz và \(8\,\mathrm{ms}\) ở 16 kHz, không phải “10 ms”.

### Nyquist, và vì sao 16 kHz không phải bước downsample miễn phí

Định lý lấy mẫu (Oppenheim & Schafer): tín hiệu giới hạn băng, phổ tắt từ \(f_s/2\) trở lên, được xác định bởi các mẫu. Hình vẽ là ca hỏng. Với \(f_s=8\,\mathrm{kHz}\),

$$
\sin(2\pi\cdot 7000\cdot n/f_s)=-\sin(2\pi\cdot 1000\cdot n/f_s).
$$

Sau khi lấy mẫu, Wiener, spectral subtraction hay DeepFilterNet đều không tách được hai tone đó.

| Tốc độ | Nyquist | Phần giữ lại |
|--------|---------|----------------|
| 8 kHz | 4 kHz | thoại băng hẹp; năng lượng xát hầu như đã mất |
| 16 kHz | 8 kHz | thoại wideband; rate cổ điển và DNS Challenge |
| 48 kHz | 24 kHz | full-band; rate DeepFilterNet công bố, và rate `deepfilternet3-noise-filter` 1.3.0 kỳ vọng |

Hạ 48 kHz xuống 16 kHz chỉ hợp lệ sau một low-pass chặn băng trên 8 kHz. “Lấy mỗi mẫu thứ ba” sẽ alias 8–24 kHz vào 0–8 kHz; upsample lại sau đó không trả băng đã mất. Đường full-band Mezon ở lại 48 kHz, trừ khi bạn chủ đích chọn mô hình 16 kHz và có lọc chống alias.

### Interleaved và planar

- **Stereo interleaved:** `LRLRLR...`
- **Planar:** hết L rồi đến R (hoặc hai con trỏ)

Đưa stereo interleaved vào FFT mono “như mono” tạo tần số giả — cùng kiểu gập như hình. Đọc `L,R,L,R` thành một dãy sẽ đổ năng lượng gần \(f_s/2\). Tách kênh hoặc downmix rõ ràng, rồi mới nhân cửa sổ.

### Downmix cho NS tiếng nói

Chọn một chính sách và ghi lại:

1. **Trung bình:** \(m=(L+R)/2\) (cẩn thận khi hai kênh tương quan hoặc phản tương quan).
2. **Chỉ trái / chỉ phải:** khi biết capsule sản phẩm.
3. **Theo năng lượng:** hiếm trong realtime.

Đừng trung bình sau khi đã chạy NS độc lập trên L và R nếu không có chính sách không gian — pha sẽ loạn. Stereo phản tương quan \(L=-R\) (tone test, hoặc một số mic mid-side) cho trung bình bằng đúng 0. Mô hình “thành công” bằng cách xuất im lặng.

### Đồng hồ

`AudioContext.sampleRate` có thể là 44100, 48000, hoặc khác. Track getUserMedia có thể đã bị trình duyệt resample. **Đo** `sampleRate`; đừng cứng mã. Đặt một resampler tốt ở biên khối NS, về đúng rate của mô hình.

44.1 kHz là bẫy của DAC tiêu dùng. Mẫu 44.1 kHz bị gán nhãn 48 kHz sẽ dịch mọi tần số theo \(44100/48000\approx 0.919\), hài rơi sai băng ERB. Đọc rate của context và resample một lần.

### Kỳ vọng Mezon / WebRTC (công khai)

Tích hợp trình duyệt thường gặp Float32 từ Web Audio, hay 48 kHz, mono sau downmix. DeepFilterNet công bố là full-band 48 kHz ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)). Khi ship, đối chiếu README `deepfilternet3-noise-filter` hiện tại, đừng đóng đinh giả định của bài này.

## Ví dụ có số

1 giây mono f32 @ 16 kHz → \(16000\cdot4=64000\) byte. 10 ms mono s16 @ 16 kHz → \(0.010\cdot16000\cdot2=320\) byte, tức 160 mẫu — một hop cổ điển, không phải quantum 128 mẫu.

s16 sát ±32767 sinh hài mà NS có thể coi là tiếng nói hoặc nhiễu. Nên chừa headroom trước NS.

Stereo interleaved dài 960 frame bị hiểu thành 960 mẫu mono @ 48 kHz: bạn xử lý 10 ms L/R xáo như thể 20 ms mono. 960 mẫu ở 48 kHz đúng là độ dài phân tích DeepFilterNet. Sai stride một lần là lệch mọi hop phía sau.

## Bẫy thường gặp

1. Giả định endian luôn LE khi đọc file.
2. Float ngoài \([-1,1]\) sau xử lý → méo ở sink.
3. Cứng 48 kHz.
4. Input stereo bị cắt thầm nửa buffer.
5. Nhầm header WAV với PCM thô từ callback.

## Mini-lab

**Mục tiêu.** Cho thấy tone 7 kHz lấy mẫu ở 8 kHz khớp tone 1 kHz đảo dấu, và kiểm tra hai độ dài buffer hay gặp.

```python
import numpy as np

fs = 8000
n = np.arange(int(0.004 * fs))  # 4 ms, cùng ý với hình
s1 = np.sin(2 * np.pi * 1000 * n / fs)
s7 = np.sin(2 * np.pi * 7000 * n / fs)
alias_err = np.max(np.abs(s7 + s1))
print("max |s7 - (-s1)|", alias_err)

def nbytes(seconds, fs, channels, bytes_per_sample):
    return int(round(seconds * fs)) * channels * bytes_per_sample

print("20 ms stereo s16 @ 48 kHz", nbytes(0.020, 48000, 2, 2))
print("10 ms mono s16 @ 16 kHz", nbytes(0.010, 16000, 1, 2))
```

**Kỳ vọng.** `alias_err` cỡ \(10^{-14}\) (coi như 0). Hai độ dài byte là `3840` và `320`.

**Khi hỏng.** `linspace` làm rơi hoặc nhân đôi mẫu cuối thì sai số alias nhảy từ sai số số học lên \(O(1)\). Quên `channels` hoặc dùng 4 byte cho s16 sẽ in 7680 hoặc 640 và lệch WAV với worklet. Nếu `alias_err` khoảng 2, bạn so `s7` với `s1` mà quên dấu trừ của phép gập — mẫu khớp về độ lớn và ngược dấu, đó chính là alias.

## Bài tập nhỏ

1. Byte cho 10 ms mono s16 @ 16 kHz?
2. Pseudocode downmix interleaved → mono trung bình.
3. Vì sao stereo phản tương quan \((L=-R)\) nguy hiểm với mean downmix?
4. Ba chỗ sampleRate có thể khác trên đường gửi WebRTC.
5. Đổi s16 −16000 sang float FS với /32768.

### Gợi ý đáp án

1. \(0.010\times16000=160\) mẫu, nhân 2 byte → 320.
2. Đọc từng cặp `(L, R)`, xuất `(L+R)/2` ở float; đừng trung bình trên byte.
3. Trung bình đồng nhất bằng 0, mô hình thấy im lặng.
4. Thiết bị thu, `AudioContext`, và rate gốc của mô hình (48 kHz, 16 kHz, hoặc 44.1 kHz).
5. \(-16000/32768\approx -0.488\).

## Đọc thêm

- Oppenheim & Schafer, *Discrete-Time Signal Processing* — lấy mẫu và tần số Nyquist.
- Web Audio `AudioBuffer` / buffer `AudioWorkletProcessor`.
- Ràng buộc media track WebRTC và ghi chú PCM.
- Framing full-band DeepFilterNet: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
