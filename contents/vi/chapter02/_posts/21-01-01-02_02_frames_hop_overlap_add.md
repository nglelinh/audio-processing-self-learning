---
layout: post
title: "02-02 Frame, hop và overlap-add"
chapter: "02"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Pipeline STFT cắt audio thành khung chồng lấn, xử lý từng khung, rồi dán bằng overlap-add (OLA). Sai hop/OLA sinh warble âm nhạc mà cập nhật trọng số neural không chữa được.

## Mục tiêu học tập

1. Định nghĩa độ dài frame \(L\), hop \(R\), tỷ lệ overlap.
2. Giải thích tái dựng OLA và điều kiện COLA.
3. Tính hệ quả độ trễ thuật toán của \(L\) và \(R\).
4. Chọn hop cho NS tiếng nói với trực giác trễ/chất lượng.
5. Có mô hình tinh thần buffer OLA streaming.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Sơ đồ frame/hop trên bảng |
| 12–28 | Toán OLA; COLA với ví dụ Hann |
| 28–42 | Cơ chế buffer streaming; hiệu ứng biên |
| 42–52 | Số liệu @ 16/48 kHz cho tiếng nói |
| 52–60 | Bài tập |

## Giải thích cốt lõi

Overlap \(\rho=1-R/L\). OLA: \(\hat{x}[n]=\sum_m y_m[n-mR]\). Nếu không sửa phổ và cửa sổ thỏa **COLA**, tái dựng \(x\) (trừ trễ/gain). Hann 50% overlap là lựa chọn COLA kinh điển khi dùng đúng.

\(L\) lớn → chi tiết tần số tốt, trễ đệm lớn. \(R\) nhỏ → cập nhật dày, CPU cao. NS sản phẩm thường hop khoảng 5–20 ms — **khớp mô hình**.

Buffer OLA: accumulator \(\ge L\); mỗi hop cộng frame mới, phát \(R\) mẫu “xong”, giữ đuôi overlap. Bắt/đầu–cuối: fade/flush tránh click.

## Ví dụ có số

48 kHz, \(L=960\), \(R=480\): \(\rho=0.5\), 100 hop/s. COLA hỏng → tremolo biên độ gần \(f_s/R\) Hz (ví dụ 100 Hz).

## Bẫy thường gặp

1. Analysis Hann + synthesis chữ nhật không kiểm COLA.
2. Đổi hop nhưng giữ cửa sổ của hop khác.
3. Phát đủ \(L\) mẫu mỗi hop (lệch đồng bộ).
4. Xóa nhớ OLA mỗi callback.
5. STFT offline (pad giữa) lệch STFT streaming khi eval.

## Bài tập nhỏ

1. Overlap \(L=1024\), \(R=256\)?
2. Hop ms @ 16 kHz với \(R=160\)?
3. Vì sao hop nhỏ hơn tăng CPU?
4. Phác buffer OLA sau 3 hop \(L=8\), \(R=4\).
5. Một tín hiệu test COLA (impulse hoặc chirp).

## Đọc thêm

- Oppenheim & Schafer — STFT / filterbank / OLA.
- Tài liệu cửa sổ COLA.
- Mô tả framing DeepFilterNet trong paper.
