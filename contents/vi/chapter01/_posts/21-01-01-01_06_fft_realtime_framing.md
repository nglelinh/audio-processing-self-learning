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

![Các khung phân tích chồng nhau, mỗi khung một FFT có cửa sổ, cộng lại phía tổng hợp]({{ site.imgurl }}/generated/stft-ola.png)

*Figure. FFT thời gian thực là hình này trên đồng hồ: một hop mới vào, một biến đổi có cửa sổ, overlap-add ra. Cơ sở vẫn là DFT; lịch là hop.*

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

**Một cấu hình, đếm hết.** Lấy \(f_s=48\,\mathrm{kHz}\) (mặc định full-band của `deepfilternet3-noise-filter` 1.3.0), \(L=960\), \(R=480\). Đây là số của bài học, không phải khẳng định đồ thị chưa công bố của Mezon dùng đúng cặp này.

$$
T_{\mathrm{hop}}=\frac{480}{48000}=10\,\mathrm{ms},\qquad
\frac{f_s}{R}=100\ \mathrm{hop/s},\qquad
T_{\mathrm{win}}=\frac{960}{48000}=20\,\mathrm{ms}.
$$

Chồng là \((L-R)/L=1/2\). Bản nhân quả chưa chạy FFT phân tích đầu tiên khi chưa có 960 mẫu, nên trễ đệm trước biến đổi đó là 20 ms. Ta gọi đó là độ trễ thuật toán của *việc lấp đầy cửa sổ phân tích*. Nhả mẫu sớm hơn, hoặc giữ thêm một hop look-ahead, đổi hằng số; không đổi tốc độ hop. Hai biến đổi mỗi hop (thuận và nghịch) cho \(200\) FFT mỗi giây mỗi kênh. Ngân sách hop là 10 ms thời gian tường. Quantum AudioWorklet 128 mẫu ở 48 kHz bằng \(128/480=0.267\) hop, nên cần \(480/128=3.75\) quantum để đủ \(R\) và \(960/128=7.5\) quantum để đủ \(L\). `DeepFilterNet3Core` vẫn phải được feed theo hop mà model card ghi; phép đếm này để đối chiếu card với callback.

Cần \(T_{\mathrm{proc}}(\ell)<T_{\mathrm{hop}}\) hầu như luôn, có đệm jitter. Paper họ DeepFilterNet mô tả front-end STFT, đặc trưng ERB, deep filtering phổ phức, hướng real-time. Khi đọc (Ch. 04), trích \(f_s\), kích thước cửa sổ/FFT, hop, claim nhân quả — ánh xạ công thức trên trước khi tích hợp `deepfilternet3-noise-filter`. Không bịa hằng số STFT Mezon chưa ghi.

## Ví dụ có số

48 kHz, \(R=480\) (10 ms): 100 hop/s, ~200 transform/s/kênh. 128 mẫu/quantum @ 48 kHz: bao nhiêu quantum để đủ hop 10 ms? → khoảng 3.75 → cần tích lũy.

## Bẫy thường gặp

1. Đồng nhất quantum AudioWorklet với hop mô hình.
2. Đo trễ chỉ trên main thread.
3. Reset state OLA mỗi callback.
4. Chạy FFT stereo khi mô hình mono.
5. Quên iFFT+OLA nằm trong ngân sách.

## Mini-lab

**Mục tiêu.** Đếm hop mỗi giây và trễ lấp cửa sổ phân tích cho \(L=960\), \(R=480\) ở 48 kHz.

```python
fs, L, R = 48_000, 960, 480
hop_ms = 1_000 * R / fs
win_ms = 1_000 * L / fs
hops_per_s = fs / R
ffts_per_s = 2 * hops_per_s
print(f"hops_per_s={hops_per_s:.0f} hop_ms={hop_ms:.1f} win_ms={win_ms:.1f}")
print(f"ffts_per_s={ffts_per_s:.0f} algo_delay_ms={win_ms:.1f}")
```

**Expected.** `hops_per_s=100 hop_ms=10.0 win_ms=20.0`, rồi `ffts_per_s=200 algo_delay_ms=20.0`. Trễ in ra là thời gian gom một cửa sổ phân tích, không phải trễ miệng-đến-tai của cả sản phẩm.

**Failure modes.** Đặt độ trễ thuật toán bằng hop (10 ms) và quên cửa sổ phải đầy trước. Đếm một FFT mỗi hop trong khi nghịch đảo cũng nằm trên đồng hồ. Chép \(L\) và \(R\) lên model card đang ghi một cặp khác.

## Bài tập nhỏ

1. \(f_s=16\,\mathrm{kHz}\), \(R=256\): hop ms và hop/s?
2. Ngân sách \(T_{\mathrm{proc}}\) cho RTF 0.4 ở hop đó.
3. Quantum 128 @ 48 kHz: bao nhiêu quantum cho hop 10 ms?
4. Liệt kê state phải sống qua các hop.
5. Phác kế hoạch profile tách STFT / neural / ISTFT.

### Gợi ý đáp án

1. \(256/16000=16\,\mathrm{ms}\), nên hop/s \(=1000/16=62.5\).
2. RTF 0.4 trên hop 16 ms cho phép \(6.4\,\mathrm{ms}\) xử lý.
3. Hop 10 ms ở 48 kHz là 480 mẫu, \(480/128=3.75\) quantum. Gom bốn quantum vẫn còn phần dư 0.25 nếu ring buffer không giữ mẫu thừa.
4. Đuôi OLA, cửa sổ phân tích, bộ đếm hop, và state hồi tiếp trong bộ khử nhiễu.
5. Ba đồng hồ quanh FFT phân tích, forward neural, và iFFT cộng overlap-add, báo p95 trên ít nhất vài nghìn hop.

## Đọc thêm

- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — mục cấu hình STFT và real-time. Mã tham chiếu: https://github.com/Rikorose/DeepFilterNet.
- MDN AudioWorkletProcessor.
- Tổng quan WebRTC APM (xử lý theo khối khung).
