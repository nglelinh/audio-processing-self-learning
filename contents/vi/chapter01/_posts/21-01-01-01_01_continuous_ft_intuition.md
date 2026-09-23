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

Hai tone 440 + 0.3×880 Hz; LPF 600 Hz làm tối tembre — NS “low-pass cho hết rít” mắc lỗi tương tự với phụ âm. Trễ 5 ms tại 1 kHz: dịch pha \(-2\pi f t_0\). Cộng dB sai: không được viết “−20 dB + −20 dB = −40 dB” cho hỗn hợp tuyến tính.

## Bẫy thường gặp

1. Coi spectrogram biên độ là toàn bộ câu chuyện.
2. Cộng giá trị dB như biên độ tuyến tính.
3. Nhầm \(\Omega\) (rad/s) với \(f\) (Hz).
4. “Độ phân giải tần số càng lớn càng tốt” quên cái giá độ trễ.
5. Kỳ vọng ký hiệu CTFT xuất hiện nguyên văn trong code.

## Bài tập nhỏ

1. Viết \(\sin(\Omega t)\) bằng mũ phức (Euler).
2. Trễ 2 ms: dịch pha tại 500 Hz và 2 kHz (trước khi wrap).
3. Phác phổ hoạt hình: nguyên âm hữu thanh, nhiễu trắng, tiếng bàn phím, babble.
4. Một đoạn: vì sao thích mũ phức khi phân tích LTI?
5. Một trường hợp miền thời gian có thể thắng spectral subtraction ngây thơ (gợi ý: xung click).

## Đọc thêm

- Oppenheim & Schafer, *Discrete-Time Signal Processing* — các chương tổng quan Fourier.
- Giáo trình DSP đại học về CTFT (ví dụ MIT OCW).
- Paper DeepFilterNet — thấy enhancement chạy miền STFT / deep filtering (chỉ động cơ cho bài này).
