---
layout: post
title: "01-04 DFT như ma trận / cơ sở trực chuẩn"
chapter: "01"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Debug NS đòi hỏi coi DFT như đổi cơ sở có metric (Parseval), không chỉ như đồ thị màu. Bài này nối trực giao, dạng ma trận, chỉ số bin, và rò phổ.

## Mục tiêu học tập

1. Nhìn DFT như hình chiếu lên mũ phức.
2. Viết DFT như ma trận; biết quy ước unitary vs không chuẩn hóa.
3. Dùng kiểm tra năng lượng kiểu Parseval khi xác thực STFT/ISTFT.
4. Đổi fluently giữa chỉ số bin, Hz, và tần số chuẩn hóa.
5. Dự đoán và nhận ra rò phổ khi sinusoid lệch bin.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Mũ trực giao; góc nhìn tích trong |
| 12–28 | Ma trận \(\mathbf{F}\); scale unitary; quy ước thư viện |
| 28–42 | Bin↔Hz; DC/Nyquist; tần số âm |
| 42–52 | Rò lệch bin; phác lab tone+nhiễu |
| 52–60 | Bài tập / checklist |

## Giải thích cốt lõi

\(w_k[n]=e^{j2\pi kn/N}\) trực giao với \(\langle w_k,w_\ell\rangle=N\delta_{k\ell}\). \(\mathbf{X}=\mathbf{F}\mathbf{x}\). Nhiều API FFT: thuận không chia, nghịch chia \(1/N\) (hoặc ngược) — **bug scale ISTFT** là sát thủ chất lượng im lặng.

$$
f_k=\frac{k}{N}f_s
$$

Parseval dạng phổ biến: \(\sum|x|^2=(1/N)\sum|X|^2\). Sinusoid không đủ số chu kỳ nguyên trong khối → sidelobe (rò); cửa sổ làm giảm sidelobe, nới lobe chính (Ch. 02).

## Ví dụ có số

48 kHz, \(N=1024\), \(\Delta f\approx46.875\,\mathrm{Hz}\). HVAC ~100 Hz gần bin 2–3. Nhiễu trắng đơn vị dài 256: năng lượng thời gian ~256; sum \(|X|^2\) ~65536 với DFT không chuẩn hóa.

## Bẫy thường gặp

1. Áp \(1/N\) hai lần.
2. Đọc nửa phổ gương như nội dung độc nhất gấp đôi.
3. Sửa nửa phổ không gương liên hợp.
4. So chuẩn FFT khác ngôn ngữ (NumPy vs FFTW…).
5. Dùng `|X|**2` không chuẩn hóa công suất cửa sổ khi ước PSD.

## Bài tập nhỏ

1. Với \(N=4\), viết \(\mathbf{F}\) tường minh.
2. \(k=32\), \(f_s=16\,\mathrm{kHz}\), \(N=256\) → Hz?
3. Vì sao tone lệch bin trông băng rộng dưới cửa sổ chữ nhật?
4. Thiết kế unit test 5 dòng Parseval cho wrapper FFT.
5. Bin DC khổng lồ ⇒ triệu chứng miền thời gian?

## Đọc thêm

- Oppenheim & Schafer — tính chất DFT, Parseval.
- Tài liệu thư viện FFT (cờ chuẩn hóa).
- Tutorial STFT tiếng nói về scale và công suất cửa sổ.
