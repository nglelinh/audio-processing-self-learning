---
layout: post
title: "02-04 STFT / ISTFT cho tiếng nói (gắn DeepFilterNet)"
chapter: "02"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

STFT là biểu diễn xương sống của NS cổ điển và mô hình họ DeepFilterNet. Bài này dựng mô hình tinh thần STFT/ISTFT và gắn ý tưởng pipeline công khai (đặc trưng ERB, deep filtering phổ phức) mà không bịa nội bộ sản phẩm.

## Mục tiêu học tập

1. Có mô hình lưới STFT (thời gian × tần số).
2. Đối chiếu mask biên độ, mask phức, và ý tưởng deep filtering.
3. Nêu điều kiện tái dựng hoàn hảo thực tế.
4. Ánh xạ tham số STFT (rate, \(N\), hop, cửa sổ) sang trễ và độ phân giải.
5. Nối thiết kế STFT-centric công bố của DeepFilterNet với tham số kỹ thuật.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Định nghĩa STFT; spectrogram như \(\|STFT\|\) |
| 12–28 | ISTFT / OLA; drill tái dựng |
| 28–42 | Xử lý mag vs phức; trực giác deep filtering |
| 42–52 | Bài tập trích tham số từ paper DeepFilterNet |
| 52–60 | Bài tập |

## Giải thích cốt lõi

$$
X(\ell,k)=\sum_{n=0}^{L-1}x[n+\ell R]\,w[n]\,e^{-j2\pi kn/N}
$$

Cột = khung thời gian; hàng = bin. Enhance ước \(\hat{X}\) từ \(Y\) nhiễu.

| Biểu diễn | Dùng điển hình |
|-----------|----------------|
| Phổ phức | deep filtering, complex mask |
| Biên độ | Wiener cổ điển, mag mask |
| Log-mag / dB | đặc trưng, đồ thị |
| ERB / Mel | front-end tri giác (paper DeepFilterNet dùng ERB) |

**Mag mask:** tái sử dụng pha nhiễu — rẻ; lỗi pha khi SNR thấp. **Deep filtering:** học bộ lọc trộn bin lân cận trên phổ phức — mạnh hơn gain đường chéo độc lập. Đọc paper DeepFilterNet/2/3 cho kiến trúc chính xác; moral kỹ thuật: **bạn sửa lưới STFT dưới ràng buộc nhân quả rồi ISTFT**.

Unit test: STFT→ISTFT không model ≈ đồng nhất. Trích từ docs: \(f_s\), cửa sổ/\(N\), hop, look-ahead, giả định mono.

## Ví dụ có số

1 s @ 16 kHz, \(R=256\), \(N=512\) real FFT → ~62 khung, 257 bin độc nhất. Phase reuse thất bại khi bin SNR thấp → tiếng ướt.

## Bẫy thường gặp

1. Center frame offline nhưng không streaming.
2. Hop train ≠ hop serve.
3. Đưa Mel vào mô hình kỳ vọng ERB/STFT tuyến tính.
4. Batch ISTFT cả file trong prod.
5. Claim hằng số STFT Mezon từ khóa học.

## Bài tập nhỏ

1. Shape STFT ~ cho 2 s @ 48 kHz, \(R=480\), \(N=960\).
2. Vì sao tái sử dụng pha nhiễu thất bại khi nhiễu sâu?
3. Bốn tham số copy từ config DeepFilterNet vào checklist tích hợp.
4. COLA hỏng nghe thế nào sau ISTFT?
5. ERB vs STFT tuyến tính: một lý do dùng ERB?

## Đọc thêm

- Paper DeepFilterNet / 2 / 3 — STFT, ERB, deep filtering.
- Review STFT cổ điển.
- Oppenheim & Schafer — filter bank / STFT.
