---
layout: post
title: "01-05 Thuật toán FFT và độ phức tạp"
chapter: "01"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

DFT ngây thơ là \(O(N^2)\). Thoại thời gian thực không chịu nổi mỗi hop trên CPU điện thoại hay trong AudioWorklet. Bài này giải thích vì sao FFT là \(O(N\log N)\), radix-2 mang lại gì, và ràng buộc thực tế trong stack ORT/WASM/native.

## Mục tiêu học tập

1. Giải thích FFT \(O(N\log N)\) so với DFT \(O(N^2)\).
2. Mô tả chia để trị Cooley–Tukey radix-2 ở mức hoạt hình.
3. Liệt kê ràng buộc: kích thước lũy thừa 2, tối ưu real-FFT, tái sử dụng plan.
4. Ước chi phí FFT so với phép neural trong ngân sách hop.
5. Hiểu “gọi FFT” trong đồ thị ONNX vs WASM viết tay.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Số học độ phức tạp: \(N=1024\) naive vs FFT |
| 10–28 | Ý tưởng butterfly radix-2; nhận thức bit-reversal |
| 28–42 | Real FFT; N không phải lũy thừa 2 (mixed radix / pad) |
| 42–52 | Phong cảnh thư viện: native, WASM SIMD, op FFT ORT |
| 52–60 | Bài tập |

## Giải thích cốt lõi

Mỗi trong \(N\) đầu ra cộng \(N\) MAC phức → \(\Theta(N^2)\). Với \(N=1024\) đã ~\(10^6\) MAC/lượt; nhân FFT+iFFT và số hop/s → dễ đau trên mobile khi cộng neural net.

Cooley–Tukey: tách chẵn/lẻ, đệ quy, \(\log_2 N\) tầng, mỗi tầng \(\Theta(N)\) → \(\Theta(N\log N)\). Twiddle là phép quay butterfly. Plan FFT tạo **một lần**; **không allocate** trên audio thread; ưu tiên SIMD (Ch. 06).

Speech PCM thực → real-FFT gần nửa công phức. Cửa sổ 960 mẫu (20 ms @ 48 kHz) có thể mixed-radix hoặc pad 1024 — **khớp training**.

NS cổ điển nhỏ: FFT có thể chiếm đa số. DeepFilterNet-class: matmul thường chiếm đa số, nhưng FFT vẫn đáng kể ở rate cao / hop nhỏ / build không SIMD.

## Ví dụ có số

Hop 10 ms → 100 cặp FFT+iFFT/s/kênh. \(N=512\) ~ vài nghìn MAC/lượt → ~\(10^6\) MAC/s phía FFT — nhỏ so với conv-RNN nhiều lớp, nhưng hop 2.5 ms + \(N=1024\) tăng nhanh.

## Bẫy thường gặp

1. Dựng lại FFT plan mỗi hop.
2. Dùng API phức trên dữ liệu thực bỏ qua lợi ích packing.
3. Nghĩ \(O(N\log N)\) nghĩa là “miễn phí”.
4. Đổi \(N\) lên lũy thừa 2 kế mà không kiểm tương thích mô hình.
5. So thời gian DEBUG vs Release / thiếu SIMD.

## Bài tập nhỏ

1. \(\log_2 1024\) tầng; so thô \(N\log N\) vs \(N^2\).
2. Vì sao real-FFT roughly giảm một nửa công?
3. Ba mối quan tâm FFT trên AudioWorklet/WASM.
4. Hop giảm một nửa, \(N\) cố định → CPU FFT roughly thế nào?
5. Một lý do tránh pad khi dùng STFT front-end pretrained.

## Đọc thêm

- Tổng quan dòng Cooley–Tukey; mục FFT trong Oppenheim & Schafer.
- Tài liệu FFTW / pocketfft / FFT nền tảng.
- Tài liệu toán tử STFT/DFT ONNX khi dùng ORT.
