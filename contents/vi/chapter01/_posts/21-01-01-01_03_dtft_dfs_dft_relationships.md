---
layout: post
title: "01-03 Hệ thống quan hệ DTFT, DFS và DFT"
chapter: "01"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Code không bao giờ tính DTFT vô hạn. Nó tính DFT hữu hạn (qua FFT) trên các cửa sổ, hop nối hop. Bài này dựng bản đồ DTFT ↔ DFS ↔ DFT để siêu tham số STFT có nghĩa.

![Các tone cơ sở DFT: lưới rời rạc mà FFT thực sự tính]({{ site.imgurl }}/generated/dft-basis.png)

*Figure. DFT không vẽ một đường cong liên tục; nó báo tích trong với các tone phức rời rạc này, mỗi bin một tone.*

## Mục tiêu học tập

1. Phân biệt DTFT (thời gian rời rạc, tần số liên tục) với DFT (lưới hữu hạn).
2. Giải thích quan hệ tuần hoàn thời gian–tần số không cần chứng minh đầy đủ.
3. Đọc bin DFT như mẫu của phổ đoạn đã cửa sổ.
4. Đối chiếu zero-padding với độ phân giải tần số thật.
5. Dùng đối xứng liên hợp và giải thích “FFT N điểm” trong stack NS.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Taxonomy biến đổi; chỗ đứng của STFT |
| 12–28 | DTFT; cửa sổ như tích chập phổ |
| 28–42 | Công thức DFT; thiết kế thí nghiệm zero-pad |
| 42–52 | Đối xứng tín hiệu thực; cảnh báo tích chập vòng |
| 52–60 | Bài tập gắn lựa chọn N kiểu DeepFilterNet |

## Giải thích cốt lõi

| Tên | Thời gian | Tần số | Trong code NS? |
|-----|-----------|--------|----------------|
| CTFT | liên tục | liên tục | lý thuyết |
| DTFT | rời rạc vô hạn | liên tục, chu kỳ \(2\pi\) | lý thuyết |
| DFS | rời rạc tuần hoàn | rời rạc tuần hoàn | ít gọi tên |
| DFT/FFT | vector dài \(N\) | \(N\) bin | **mọi nơi** |
| STFT | khung cửa sổ | DFT mỗi khung | **xương sống NS** |

$$
X[k]=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N}
$$

DFT lấy mẫu DTFT của dãy hữu hạn tại \(\omega_k=2\pi k/N\). Viết tổng DTFT rồi ghim tần số:

$$
X(e^{j\omega})\Big|_{\omega=2\pi k/N}
=\sum_{n=0}^{N-1}x[n]e^{-j2\pi kn/N}
=X[k].
$$

Phép thế đó không bịa thêm thông tin giữa các bin. Nhân hai DFT ↔ tích chập **vòng** (circular convolution) dài \(N\) — cần OLA/OLS cho tích chập tuyến tính dài.

Cắt cửa sổ chữ nhật dài \(L\) làm smearing phổ (lobe chính ~ \(1/L\)). Zero-pad làm dày mẫu DTFT, **không** tạo độ phân giải quan sát dài hơn.

Tín hiệu thực: \(X[k]=X^*[N-k]\); thông tin độc nhất \(0..N/2\). Đổi \(N\) giữa train và infer với masker neural là bug.

Ví dụ: \(f_s=48\,\mathrm{kHz}\), \(N=960\) (20 ms) → \(\Delta f=50\,\mathrm{Hz}\). @16 kHz, \(N=512\) → \(31.25\,\mathrm{Hz}\).

## Ví dụ có số

1 kHz @ 16 kHz, \(N=512\) đúng bin 32 vì \(1000/31.25=32\); năng lượng vẫn lan bin lân cận vì lobe — mask nên mượt. Lấy 64 mẫu của tone 1 kHz ở 16 kHz: tone đi hết \(1000\times 64/16000=4\) chu kỳ, DFT dài 64 đỉnh ở bin 4. Pad lên 512, cùng 64 mẫu đỉnh ở bin 32. Bước bin đổi từ 250 Hz xuống 31.25 Hz, nhưng lobe chính tính bằng hertz vẫn do 64 mẫu quan sát đặt ra, cỡ 250 Hz. Ở mặc định 48 kHz, cùng cái bẫy xuất hiện khi ai đó zero-pad khung 10 ms rồi gọi bước bin mới là “độ phân giải pitch tốt hơn” mà không kéo dài cửa sổ mic thực sự đã gom.

## Bẫy thường gặp

1. Quảng cáo zero-pad là siêu phân giải.
2. Quên tích chập vòng vs tuyến tính.
3. So \(|X[k]|\) khác \(N\) không chuẩn hóa.
4. Phá đối xứng liên hợp rồi iFFT “lấy phần thực”.
5. Đổi \(N\) train/serve.

## Mini-lab

**Mục tiêu.** So DFT 64 điểm của tone 1 kHz ở 16 kHz với chính 64 mẫu đó khi zero-pad lên 512.

```python
import numpy as np

fs, n_win = 16_000, 64
n = np.arange(n_win)
tone = np.cos(2 * np.pi * 1000 * n / fs)
peak64 = int(np.argmax(np.abs(np.fft.rfft(tone))))
peak512 = int(np.argmax(np.abs(np.fft.rfft(tone, n=512))))
print(peak64, peak512, fs / n_win, fs / 512)
```

**Expected.** `4 32 250.0 31.25`. Chỉ số đỉnh đổi vì lưới dày hơn. Độ dài quan sát không đổi.

**Failure modes.** Đọc bin 32 ở \(N=512\) là “tone sắc hơn”. So chiều cao đỉnh `|rfft|` thô giữa hai độ dài mà không thống nhất scale. Quên cosine đúng bin còn một anh em tần số âm mà `rfft` không in riêng.

## Bài tập nhỏ

1. Bin gần 1 kHz nhất @ 16 kHz, \(N=512\).
2. Một câu: zero-pad vs cửa sổ dài hơn.
3. Tone đúng bin vs giữa hai bin — cái nào rò hơn với cửa sổ chữ nhật?
4. Vì sao STFT dùng hop \(R<N\) thay vì chỉ DFT không chồng?
5. Weights kỳ vọng 513 bin biên độ ⇒ \(N\) real-FFT là bao nhiêu?

### Gợi ý đáp án

1. \(\Delta f=16000/512=31.25\,\mathrm{Hz}\), nên 1 kHz là bin \(32\) đúng.
2. Zero-pad làm dày mẫu của cùng một DTFT. Cửa sổ dài hơn thì thu lobe chính.
3. Tone đúng bin trùng một vector cơ sở, cửa sổ chữ nhật thì nằm một bin. Tone giữa hai bin bị gián đoạn khi nối vòng, nên rò.
4. Hop \(R<N\) tạo chồng để ISTFT thỏa COLA (constant overlap-add). DFT kề nhau với \(R=N\) để lại mối nối chữ nhật.
5. Real FFT đóng gói giữ \(N/2+1\) bin, nên 513 bin nghĩa là \(N=1024\).

## Đọc thêm

- Oppenheim & Schafer — quan hệ DTFT/DFS/DFT.
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — DFT, DTFT, và zero-padding.
- DeepFilterNet (arXiv:2110.05588) và repo https://github.com/Rikorose/DeepFilterNet cho độ dài khung mà trọng số thực sự thấy. Tài liệu công khai của RNNoise là mốc so sánh FFT ngắn hơn.
