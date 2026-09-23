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

DFT lấy mẫu DTFT của dãy hữu hạn tại \(\omega_k=2\pi k/N\). Nhân hai DFT ↔ tích chập **vòng** dài \(N\) — cần OLA/OLS cho tích chập tuyến tính dài.

Cắt cửa sổ chữ nhật dài \(L\) làm smearing phổ (lobe chính ~ \(1/L\)). Zero-pad làm dày mẫu DTFT, **không** tạo độ phân giải quan sát dài hơn.

Tín hiệu thực: \(X[k]=X^*[N-k]\); thông tin độc nhất \(0..N/2\). Đổi \(N\) giữa train và infer với masker neural là bug.

Ví dụ: \(f_s=48\,\mathrm{kHz}\), \(N=960\) (20 ms) → \(\Delta f=50\,\mathrm{Hz}\). @16 kHz, \(N=512\) → \(31.25\,\mathrm{Hz}\).

## Ví dụ có số

1 kHz @ 16 kHz, \(N=512\) ≈ bin 32; năng lượng lan bin lân cận vì lobe — mask nên mượt. Zero-pad 64→512 mẫu tone: đồ thị mượt hơn nhưng bề rộng lobe Hz vẫn do 64 mẫu quan sát chi phối.

## Bẫy thường gặp

1. Quảng cáo zero-pad là siêu phân giải.
2. Quên tích chập vòng vs tuyến tính.
3. So \(|X[k]|\) khác \(N\) không chuẩn hóa.
4. Phá đối xứng liên hợp rồi iFFT “lấy phần thực”.
5. Đổi \(N\) train/serve.

## Bài tập nhỏ

1. Bin gần 1 kHz nhất @ 16 kHz, \(N=512\).
2. Một câu: zero-pad vs cửa sổ dài hơn.
3. Tone đúng bin vs giữa hai bin — cái nào rò hơn với cửa sổ chữ nhật?
4. Vì sao STFT dùng hop \(R<N\) thay vì chỉ DFT không chồng?
5. Weights kỳ vọng 513 bin biên độ ⇒ \(N\) real-FFT là bao nhiêu?

## Đọc thêm

- Oppenheim & Schafer — quan hệ DTFT/DFS/DFT.
- Giáo trình cửa sổ và độ phân giải.
- DeepFilterNet / RNNoise — kích thước FFT khung.
