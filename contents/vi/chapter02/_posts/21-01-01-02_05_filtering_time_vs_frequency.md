---
layout: post
title: "02-05 Lọc miền thời gian vs miền tần số"
chapter: "02"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Khử nhiễu là lọc dưới bất định. Đôi khi FIR/IIR miền thời gian; đôi khi nhân bin STFT; đôi khi mạng dự đoán các phép nhân đó. Bài này so sánh miền để chọn công cụ có chủ đích.

## Mục tiêu học tập

1. Đối chiếu lọc LTI miền thời gian với gain nhân miền STFT.
2. Giải thích tích chập vòng vs tuyến tính và vì sao có OLA/OLS.
3. Liên hệ gain Wiener / spectral subtraction cổ điển với lọc STFT.
4. Mô tả khi miền thời gian vẫn thắng (DC block, heuristic click).
5. Tránh phép “lọc” phá COLA streaming.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Ôn tích chập LTI; đáp ứng tần số |
| 12–28 | Gain miền STFT như bộ lọc biến thiên thời gian |
| 28–42 | Tích chập qua FFT; OLA/OLS |
| 42–52 | Ví dụ NS: high-pass, Wiener, neural mask |
| 52–60 | Bài tập |

## Giải thích cốt lõi

$$
y[n]=(h*x)[n]
$$

\(H(e^{j\omega})\) nhân DTFT nếu \(h\) cố định — tốt cho DC blocker, EQ nhẹ, LPF chống alias; kém một mình với nhiễu không dừng.

Miền STFT: \(\hat{X}(\ell,k)=G(\ell,k)Y(\ell,k)\). \(G\) đổi chậm ≈ lọc biến thiên chậm; \(G\) nhảy mỗi hop/bin → musical noise. Spectral subtraction và Wiener (Ch. 03) là công thức cho \(G\); mask neural học \(G\) (hoặc deep filter giàu hơn).

FIR dài: nhân FFT + OLA/OLS để ra tích chập *tuyến tính*. Nhân STFT mỗi khung với \(H\) cố định không luôn đồng nhất cùng FIR miền thời gian vì rò cửa sổ.

| Nhu cầu | Ưu tiên |
|---------|---------|
| EQ nhẹ / bỏ DC | IIR/FIR nhỏ miền thời gian |
| NS không dừng | STFT + \(G\) thích nghi/neural |
| Cổng click CPU cực thấp | detector miền thời gian |
| FIR vang dài | FFT OLA/OLS |

Deep filtering DeepFilterNet dự đoán lọc trên hệ số STFT phức — vẫn “lọc miền tần số” nhưng hơn đường chéo \(G(\ell,k)\).

## Ví dụ có số

DC blocker đơn giản \(y[n]=x[n]-x[n-1]\) (phác) — không xóa babble quán cà phê. Wiener hoạt hình \(G=P_x/(P_x+P_n)\). Xóa bin ngẫu nhiên mỗi hop → birdies.

## Bẫy thường gặp

1. Coi nhân gain STFT ≡ FIR tùy ý chính xác.
2. FIR rất dài trên audio thread không tăng tốc FFT.
3. Xếp high-pass + NS không đo mất tiếng nói.
4. FIR pha tuyến tính group delay lớn trên đường gọi.
5. Quên nhân quả real-time khi thiết kế lọc offline “hay”.

## Bài tập nhỏ

1. Một lọc nên làm miền thời gian trước NS.
2. Vì sao gain per-bin không làm mượt gây click/twitter?
3. OLA vs OLS: một câu phân biệt.
4. Group delay 30 ms từ FIR pha tuyến tính — an toàn cho gọi?
5. Phác neural mask vẫn là lọc \(G(\ell,k)\).

## Đọc thêm

- Oppenheim & Schafer — lọc, tích chập FFT, xử lý STFT.
- Khảo sát speech enhancement cổ điển (cầu Ch. 03).
- Paper DeepFilterNet — phát biểu deep filtering.
