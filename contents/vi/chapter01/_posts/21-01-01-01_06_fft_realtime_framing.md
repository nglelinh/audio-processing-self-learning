---
layout: post
title: "01-06 FFT trong audio khung thời gian thực"
chapter: "01"
order: 6
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Sách FFT dừng ở độ phức tạp; sản phẩm bắt đầu ở callback. Bài này đặt FFT trong khung STFT streaming: hop/s, độ trễ thuật toán, tái sử dụng buffer, và con trỏ case study hướng DeepFilterNet.

## Mục tiêu học tập

1. Ngân sách chi phí FFT trong callback / quantum AudioWorklet.
2. Liên hệ hop, FFT \(N\) điểm, và độ trễ thuật toán.
3. Tính số FFT/s cho cấu hình thoại thường gặp.
4. Nhận khi nào FFT chiếm RTF so với phép neural.
5. Vệ sinh streaming: buffer cấp sẵn, tái sử dụng plan, liên tục OLA.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | STFT streaming như chuỗi FFT có cửa sổ |
| 10–25 | Số: hop/s, FFT/s, công thức trễ |
| 25–40 | Ràng buộc audio thread; ring buffer; bất đẳng thức underrun |
| 40–52 | Case study: cấu hình STFT DeepFilterNet (paper công khai) |
| 52–60 | Bài tập |

## Giải thích cốt lõi

Mỗi hop: gom \(L\) mẫu → nhân cửa sổ → FFT → enhance → iFFT → OLA. State: buffer OLA, state RNN/DF, tracker nhiễu.

$$
T_{\mathrm{hop}}=\frac{R}{f_s},\qquad \mathrm{FFTs/s}\approx 2\cdot\frac{f_s}{R}
$$

(theo kênh). Quantum trình duyệt thường 128 mẫu ≈ 2.67 ms @ 48 kHz — **không** đồng nhất hop STFT 5–10 ms. Cần ring buffer.

Cần \(T_{\mathrm{proc}}(\ell)<T_{\mathrm{hop}}\) hầu như luôn, có đệm jitter. Paper họ DeepFilterNet mô tả front-end STFT, đặc trưng ERB, deep filtering phổ phức, hướng real-time. Khi đọc (Ch. 04), trích \(f_s\), kích thước cửa sổ/FFT, hop, claim nhân quả — ánh xạ công thức trên trước khi tích hợp `deepfilternet3-noise-filter`. Không bịa hằng số STFT Mezon chưa ghi.

## Ví dụ có số

48 kHz, \(R=480\) (10 ms): 100 hop/s, ~200 transform/s/kênh. 128 mẫu/quantum @ 48 kHz: bao nhiêu quantum để đủ hop 10 ms? → khoảng 3.75 → cần tích lũy.

## Bẫy thường gặp

1. Đồng nhất quantum AudioWorklet với hop mô hình.
2. Đo trễ chỉ trên main thread.
3. Reset state OLA mỗi callback.
4. Chạy FFT stereo khi mô hình mono.
5. Quên iFFT+OLA nằm trong ngân sách.

## Bài tập nhỏ

1. \(f_s=16\,\mathrm{kHz}\), \(R=256\): hop ms và hop/s?
2. Ngân sách \(T_{\mathrm{proc}}\) cho RTF 0.4 ở hop đó.
3. Quantum 128 @ 48 kHz: bao nhiêu quantum cho hop 10 ms?
4. Liệt kê state phải sống qua các hop.
5. Phác kế hoạch profile tách STFT / neural / ISTFT.

## Đọc thêm

- DeepFilterNet / 2 / 3 — mục cấu hình STFT / real-time.
- MDN AudioWorkletProcessor.
- Tổng quan WebRTC APM (xử lý theo khối khung).
