---
layout: post
title: "01-07 Checklist bẫy Fourier cho kỹ sư"
chapter: "01"
order: 7
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Khi NS “nghe hỏng”, kỹ sư hay train lại mô hình trước. Bài này là checklist Fourier/STFT trước chuyến bay: đơn vị, cửa sổ, đối xứng, scale, resample, DC/Nyquist — để đổ lỗi mạng sau cùng.

![Các bản sao phổ khi lấy mẫu — hình đứng sau một bin Nyquist bị gán sai]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Figure. Bẫy chính của bài này là trục tần số sai: Nyquist là \(f_s/2\), và bin lệch một chỉ số là một giá trị Hertz khác, không phải sai số làm tròn.*

## Mục tiêu học tập

1. Chẩn đoán lỗi FT/DFT phổ biến trong pipeline audio.
2. Xác thực đơn vị (Hz vs bin vs tần số chuẩn hóa).
3. Áp checklist có cấu trúc trước khi đổ lỗi neural.
4. Nhận thất bại cửa sổ/COLA và đối xứng liên hợp bằng tai và bằng test.
5. Gắn checklist với debug kiểu Mezon/DeepFilterNet mà không bịa nội bộ.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–8 | Dạng war story: triệu chứng → nguyên nhân sai → bug thật |
| 8–30 | Đi checklist master kèm thí nghiệm tư duy |
| 30–45 | Unit test nên giữ trong repo |
| 45–55 | Thứ tự debug Mezon/DeepFilterNet |
| 55–60 | Bài tập |

## Checklist master

1. **Sự thật sample rate** — PCM = rate mô hình (hoặc resampler có tài liệu); có anti-alias khi giảm mẫu; không cứng 48 kHz.
2. **Đơn vị trục tần số** — \(f=k f_s/N\); lọc theo Hz dùng đúng \(f_s\).

**Đi số: bin Nyquist là một số nguyên, và nó biết \(f_s\).** Với \(N\) chẵn, bin Nyquist là \(k=N/2\), tại \(f_s/2\). Lấy \(N=512\), \(f_s=16\,\mathrm{kHz}\): bin đúng là \(k=256\) tại \(8000\,\mathrm{Hz}\). Chỉ số lệch một, \(k=255\), nằm ở \(255\times 16000/512=7968.75\,\mathrm{Hz}\). Mask nhắm “bin tiếng nói cuối” bằng 255 không chạm Nyquist, và test chỉ kiểm “một bin cao nào đó đổi” vẫn xanh. Cùng chỉ số đó nếu bạn tưởng mảng 16 kHz là 48 kHz thì thành \(256\times 48000/512=24000\,\mathrm{Hz}\): bạn tưởng đang sửa gần 24 kHz trong khi mẫu chỉ có năng lượng tới 8 kHz. `setSuppressionLevel(0–100)` khi ấy đổi độ sâu trên trục sai. Sửa rate và bản đồ bin trước khi đụng `DeepFilterNet3Core`.

**Đi số: tráo phần thực và phần ảo.** Khung PCM thực có DFT đối xứng liên hợp, \(X[k]=X^*[(N-k)\bmod N]\), và bin DC cùng Nyquist là thực. Tráo thực với ảo thì đẳng thức đó vỡ với độ lệch cỡ chính phổ. Nghịch đảo mọc phần ảo khác không; ép “lấy phần thực rồi đi tiếp” giấu nó thành cặn đục, lệch pha. Mini-lab assert cả hai bẫy.
3. **Chuẩn hóa FFT / Parseval** — khớp docs thư viện; round-trip STFT→ISTFT giữ năng lượng.
4. **Cửa sổ & COLA** — analysis/synthesis + hop thỏa COLA; khớp training.
5. **Đối xứng liên hợp / packing** — input iFFT thực Hermitian; DC/Nyquist imag ~0.
6. **Bố cục kênh** — interleaved vs planar; chính sách stereo→mono.
7. **Hop / kế toán trễ** — look-ahead ms; đệm ring; warmup metric nhất quán.
8. **DC & rác thấp** — DC blocker nếu lệch mic; đừng nhầm DC với nhiễu mô hình phải xóa.
9. **Hiển thị dB** — nhất quán \(20\log_{10}|X|\); clamp tránh \(\log 0\).
10. **Resampler + miền mô hình** — metric ở rate đã thỏa thuận; không resample kép trong A/B.

## Kịch bản debug

Warble 100 Hz ↔ hop 10 ms + COLA hỏng. “Mô hình cắt phụ âm” ↔ kiểm rate thật có năng lượng >6 kHz không; map bin 48 vs 16. SI-SDR đẹp, user ghét ↔ pha/musical noise (Ch. 08).

## Unit test nên có

Impulse round-trip; Parseval wrapper; sine resample không spur alias; assert downmix mono.

## Thứ tự debug Mezon / DeepFilterNet (công khai)

1. Rate/kênh theo README gói / model card.
2. Giao frame (callback, ring) — chủ đề Ch. 05.
3. Vệ sinh STFT (checklist này).
4. Mới đổi variant mô hình / tùy chọn npm.
5. Trích paper DeepFilterNet công khai; không claim đồ thị Mezon chưa công bố.

## Bẫy thường gặp

1. Đổi ba thứ cùng lúc (rate, hop, model).
2. Tin một demo quán cà phê.
3. Lỡ dùng checkpoint non-causal trong wrapper streaming.
4. Bỏ qua thời gian hop p99.
5. “Sửa” warble bằng NS mạnh hơn.

## Mini-lab

**Mục tiêu.** Assert phải bắt phổ bị tráo thực/ảo, và chỉ bin Nyquist lệch một không phải 8 kHz.

```python
import numpy as np

def hermitian_error(X):
    n = np.arange(X.shape[0])
    mirror = np.conj(X[(X.shape[0] - n) % X.shape[0]])
    return np.max(np.abs(X - mirror))

x = np.array([1.0, 0.5, -0.2, 0.1, 0.0, -0.3, 0.4, 0.2])
X = np.fft.fft(x)
swapped = X.imag + 1j * X.real

def nyquist_hz(n_fft, fs):
    return (n_fft // 2) * fs / n_fft

print(f"good={hermitian_error(X):.3e}")
print(f"swapped={hermitian_error(swapped):.3f}")
print(f"nyquist={nyquist_hz(512, 16000):.2f}")
print(f"off_by_one={(512 // 2 - 1) * 16000 / 512:.2f}")
assert hermitian_error(X) < 1e-8
assert hermitian_error(swapped) > 1e-3
assert nyquist_hz(512, 16000) == 8000.0
```

**Expected.** `good=0.000e+00`, `swapped=3.400`, `nyquist=8000.00`, `off_by_one=7968.75`. Ba assert đều qua. Xóa assert của phổ tráo thì phổ hỏng vẫn lọt; trỏ `nyquist_hz` vào \(N/2-1\) thì assert cuối nổ.

**Failure modes.** Kiểm đối xứng bằng `np.allclose(X, np.conj(X[::-1]))` và quên chỉ số 0 phải khớp chính nó (công thức trên dùng \((N-k)\bmod N\), nên DC ánh vào DC). Coi 7968.75 Hz là “đủ gần Nyquist” cho unit test.

## Bài tập nhỏ

1. Chọn ba mục checklist; đặt tên unit test cho mỗi mục.
2. Hop 5 ms: tần số warble nếu COLA hỏng?
3. Vì sao sai \(f_s\) trong \(f=kf_s/N\) bắt chước mô hình xấu?
4. Mẫu báo cáo sự cố 6 bước “NS nghe tệ trên Chrome”.
5. Mục nào bắt stereo interleaved đưa vào FFT mono?

### Gợi ý đáp án

1. Đặt tên test theo lỗi: `test_cola_impulse_roundtrip`, `test_parseval_scale`, `test_downmix_length`.
2. COLA hỏng ở hop 5 ms điều biên gần \(1/0.005=200\,\mathrm{Hz}\).
3. Mọi nhãn bin tỷ lệ với \(f_s\). Mô hình 16 kHz bị feed số 48 kHz trông như low-pass dù trọng số không đổi.
4. Rate, số kênh, hop tính bằng ms, p95 thời gian callback, một kiểm impulse COLA, rồi mới tới id mô hình. Mỗi lần thử chỉ đổi một thứ.
5. Bố cục kênh: stereo interleaved bị đọc như mono sẽ xen trái và phải vào các mẫu “thời gian” liên tiếp.

## Đọc thêm

- Oppenheim & Schafer — cửa sổ, scale, bẫy DFT.
- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — cấu hình và ghi chú real-time. Julius O. Smith, https://ccrma.stanford.edu/~jos/mdft/, cho các đối xứng DFT mà assert kiểm.
- Tài liệu profile ORT / trình duyệt để tách chi phí STFT vs net.
