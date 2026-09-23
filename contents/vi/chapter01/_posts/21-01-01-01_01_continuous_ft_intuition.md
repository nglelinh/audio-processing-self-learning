---
layout: post
title: "01-01 Trực giác biến đổi Fourier liên tục"
chapter: "01"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Tăng cường tiếng nói sống ở miền tần số nhiều hơn miền sóng thô. Bài này xây trực giác Fourier thời gian liên tục (CTFT) để mã STFT về sau không còn là đống tham số ma thuật.

![Một sóng được tách thành vài sinusoid; cộng lại thì ra sóng ban đầu]({{ site.imgurl }}/generated/fourier-intuition.png)

*Figure. Tần số là một tọa độ: mỗi sinusoid là một tone cơ sở, biến đổi đo xem tín hiệu chứa bao nhiêu tone đó.*

## Mục tiêu học tập

1. Giải thích tần số như tốc độ dao động và như tọa độ trong một cơ sở tín hiệu.
2. Nêu CTFT thuận/nghịch và câu chuyện phân tích–tổng hợp.
3. Dùng tính tuyến tính, dịch thời gian ở mức vận hành.
4. Nối phổ biên độ/pha với cảm thụ nghe ở mức cao.
5. Giải thích vì sao tiếng nói và nhiễu thường tách sạch hơn ở miền tần số — và khi trực giác đó thất bại.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–8 | Móc: cùng sóng, tranh thời gian vs tần số; vì sao stack VoIP mang tính phổ |
| 8–20 | Sinusoid, Euler, trực giác hàm riêng LTI |
| 20–35 | Cặp CTFT; biên độ/pha; ví dụ tuyến tính & dịch |
| 35–48 | Formant tiếng nói vs nền nhiễu; huyền thoại pha; con trỏ DeepFilterNet |
| 48–60 | Bẫy, bài tập, xem trước lấy mẫu |

## Giải thích cốt lõi

### Tần số là hệ tọa độ

Sinusoid phức \(e^{j\Omega t}\) dao động với \(\Omega\) rad/s (\(f=\Omega/(2\pi)\) Hz). Chúng là **hàm riêng của hệ LTI**: lọc LTI chỉ nhân mỗi mũ phức với \(H(j\Omega)\), không sinh tần số mới. Đó là lý do NS miền tần số hấp dẫn: dưới cộng tính và gần LTI ngắn hạn, có thể làm suy “bin nhiễu” và cho qua “bin tiếng nói”. Thực tế lộn xộn hơn (nhiễu không dừng, lỗi mask, pha), nhưng hình ảnh hàm riêng giải thích kiến trúc hầu hết NS cổ điển và SE neural miền STFT.

### Biến đổi Fourier thời gian liên tục

$$
X(j\Omega)=\int_{-\infty}^{\infty}x(t)e^{-j\Omega t}\,\mathrm{d}t
$$

$$
x(t)=\frac{1}{2\pi}\int_{-\infty}^{\infty}X(j\Omega)e^{j\Omega t}\,\mathrm{d}\Omega
$$

**Phân tích** đo “bao nhiêu” mỗi tần số; **tổng hợp** dựng lại sóng. \(X=|X|e^{j\phi}\): biên độ ↔ phân bố năng lượng (formant, rít); pha ↔ cấu trúc thời gian (tấn công, cấu trúc pitch). UI spectrogram vẽ biên độ — dễ gây thói quen sai “pha không quan trọng”. Sau mask mạnh, xử lý pha/phổ phức là lựa chọn thiết kế hạng nhất — deep filtering trên phổ phức của DeepFilterNet một phần vì mask biên độ đơn độc có hạn.

### Tính chất dùng thật

**Tuyến tính:** phổ cộng **tuyến tính**, không cộng theo dB. **Dịch thời gian:** trễ là dốc pha. **Parseval:** xóa vùng phổ lớn *phải* giảm năng lượng sóng. **Điều chế:** dịch phổ — giải thích stack hài của pitch tuần hoàn.

### Tiếng nói vs nhiễu (vật lý hoạt hình)

Tiếng nói hữu thanh: kích thích gần tuần hoàn \(f_0\), hài \(kf_0\), formant. Vô thanh: mây cao tần — cắt cao quá phá độ rõ. Nhiễu dừng: HVAC thấp; quạt phẳng. Babble: cần mô hình thời gian (RNN/TCN…) như SE hiện đại.

### Cầu tới phần còn lại Chương 01

Micro cho mẫu. Tích phân liên tục thành DTFT/DFT/FFT trên cửa sổ. Một câu cần giữ: **tần số là hệ số cơ sở; bin STFT là ước lượng cục bộ, đã cửa sổ hóa của các hệ số đó.**

## Ví dụ có số

Hai tone \(x(t)=\cos(2\pi\cdot 440\,t)+0.3\cos(2\pi\cdot 880\,t)\). Euler không phải khẩu hiệu:

$$
\cos\theta=\frac{e^{j\theta}+e^{-j\theta}}{2}.
$$

Cosine 440 Hz là cặp vạch tại \(\pm 440\,\mathrm{Hz}\), mỗi vạch biên độ phức \(1/2\); cosine 880 Hz là cặp tại \(\pm 880\,\mathrm{Hz}\) với biên độ \(0.15\). LPF 600 Hz cắt họa âm octave và làm tối tembre — NS “low-pass cho hết rít” mắc lỗi tương tự với phụ âm. Trên đường 48 kHz full-band (mặc định của `deepfilternet3-noise-filter`) các phụ âm đó được phép sống trên 8 kHz. Trễ 5 ms tại 1 kHz: dịch pha \(-2\pi f t_0\). Cộng dB sai: không được viết “−20 dB + −20 dB = −40 dB” cho hỗn hợp tuyến tính.

## Bẫy thường gặp

1. Coi spectrogram biên độ là toàn bộ câu chuyện.
2. Cộng giá trị dB như biên độ tuyến tính.
3. Nhầm \(\Omega\) (rad/s) với \(f\) (Hz).
4. “Độ phân giải tần số càng lớn càng tốt” quên cái giá độ trễ.
5. Kỳ vọng ký hiệu CTFT xuất hiện nguyên văn trong code.

## Mini-lab

**Mục tiêu.** Tổng hợp một giây 200 Hz + 600 Hz + 1000 Hz ở 8 kHz và đọc bin đỉnh của `rfft`. Với \(N=f_s\), chỉ số bin bằng tần số tính bằng Hz.

```python
import numpy as np

fs = 8000
t = np.arange(fs) / fs
x = (
    np.sin(2 * np.pi * 200 * t)
    + np.sin(2 * np.pi * 600 * t)
    + np.sin(2 * np.pi * 1000 * t)
)
mag = np.abs(np.fft.rfft(x))
order = np.sort(np.argsort(mag)[-3:])
print(order.tolist())
print(np.round(mag[order], 1).tolist())
```

**Expected.** `[200, 600, 1000]` và `[4000.0, 4000.0, 4000.0]`. Mỗi sine biên độ 1, đủ số chu kỳ nguyên, rơi vào một bin dương với độ lớn \(N/2=4000\).

**Failure modes.** Dùng `np.fft.fft` rồi báo chỉ số tần số âm như một đỉnh thứ hai. Chọn \(N\) không chia hết chu kỳ, đỉnh bị nhòe khỏi bin nguyên. Đọc độ lớn 4000 như hệ số \(1/2\) của cosine trong ví dụ — scale `rfft` của sine là \(N/2\).

## Bài tập nhỏ

1. Viết \(\sin(\Omega t)\) bằng mũ phức (Euler).
2. Trễ 2 ms: dịch pha tại 500 Hz và 2 kHz (trước khi wrap).
3. Phác phổ hoạt hình: nguyên âm hữu thanh, nhiễu trắng, tiếng bàn phím, babble.
4. Một đoạn: vì sao thích mũ phức khi phân tích LTI?
5. Một trường hợp miền thời gian có thể thắng spectral subtraction ngây thơ (gợi ý: xung click).

### Gợi ý đáp án

1. \(\sin\theta=(e^{j\theta}-e^{-j\theta})/(2j)\). Hai vạch, trái dấu, hệ số \(1/(2j)\).
2. \(\Delta\phi=-2\pi f t_0\). 500 Hz và 2 ms: \(-2\pi\) radian, đúng một vòng. 2 kHz: \(-8\pi\) radian, bốn vòng. Biên độ không đổi.
3. Nguyên âm: chồng hài cộng formant. Nhiễu trắng: phẳng. Click: gai trải băng. Babble: một chồng hài thứ hai, lộn xộn hơn.
4. Lọc LTI nhân \(e^{j\Omega t}\) với \(H(j\Omega)\) và không đẻ tần số mới. Cosine tách thành hai hàm riêng đó.
5. Click một mẫu đã trải trên mọi bin. Cổng ngắn ở miền thời gian bắt được; tracker nền chậm thì không.

## Đọc thêm

- Oppenheim & Schafer, *Discrete-Time Signal Processing* — các chương tổng quan Fourier.
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — sinusoid như cơ sở, trước khi viết STFT.
- DeepFilterNet (arXiv:2110.05588) — enhancement chạy trên miền STFT / deep filtering. Bài này chỉ lấy động cơ.
