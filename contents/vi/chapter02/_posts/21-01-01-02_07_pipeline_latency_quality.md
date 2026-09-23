---
layout: post
title: "02-07 Tradeoff độ trễ–chất lượng của pipeline"
chapter: "02"
order: 7
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Mỗi lựa chọn STFT và mô hình là thỏa thuận với độ trễ, CPU và chất lượng. Bài này khép Chương 02 bằng cách làm rõ các tradeoff cho pipeline real-time gắn Mezon.

## Mục tiêu học tập

1. Liệt kê giai đoạn pipeline làm tăng trễ và CPU.
2. Tradeoff cửa sổ/hop/FFT với chất lượng và trễ bằng số.
3. Giải thích chế độ hỏng chất lượng khi tối ưu trễ quá đà.
4. Dựng scorecard go/no-go cho cấu hình ship.
5. Nối tradeoff với mục tiêu thiết kế real-time họ DeepFilterNet.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Sơ đồ pipeline đầu–cuối (mic → NS → encoder) |
| 10–28 | Thí nghiệm tư duy quét tham số có số |
| 28–42 | Chế độ hỏng chất lượng vs trễ |
| 42–52 | Scorecard ship kiểu Mezon |
| 52–60 | Bài tập |

## Giải thích cốt lõi

Các giai đoạn điển hình: capture/quantum → resample → downmix mono → STFT → đặc trưng (ERB…) → enhance → ISTFT/OLA → resample sink → bàn giao encoder. Mỗi giai: đo ms và đóng góp RTF.

| Núm ↑ | Trễ | CPU | Xu hướng chất lượng |
|-------|-----|-----|---------------------|
| Cửa sổ \(L\) | ↑ | ↑ | chi tiết tần tốt hơn; thời gian mờ hơn |
| Hop \(R\)↓ | CPU↑; trễ hạt có thể↓ | ↑ | mask thường mượt hơn |
| Mô hình lớn | ≈ nếu lookahead cố định | ↑ | thường ↑ đến khi RTF gãy |
| Look-ahead | ↑ | ↑ | thường ↑ |
| Sample rate | ↑ | ↑ | ↑ băng nếu mô hình train đúng rate |

@ 48 kHz: quantum 128 ≈ 2.67 ms; hop 480 = 10 ms; cửa sổ 960 = 20 ms. @ 16 kHz cùng *ms* dùng ít mẫu hơn (FFT rẻ hơn) nhưng ít băng thông hơn.

**Thiếu ngân sách trễ:** cửa sổ quá ngắn → hài pitch không tách → mask thô. **Thừa trễ:** hội thoại vụng; lệch AEC nếu NS đặt sai chỗ. **Thiếu dư địa CPU:** glitch p99.

Scorecard ví dụ: look-ahead ≤ ngân sách sản phẩm; p95 RTF ≤ 0.5 trên thiết bị; round-trip COLA đạt ngưỡng; DNSMOS/listening vs baseline WebRTC NS; không warble hop. Thay số minh họa bằng SLA của bạn.

Paper DeepFilterNet nhấn vận hành real-time: kiến trúc và STFT chọn để giữ trễ nhân quả và compute thực tế. Khi tích hợp gói Mezon công khai, ràng buộc mô hình đã công bố là cứng; tradeoff nằm ở **chỗ đặt đồ thị, resample, ngân sách thiết bị**, không phải im lặng đổi kích thước STFT pretrained.

## Ví dụ có số

Config A: 16 kHz, L=20 ms, R=10 ms, model nhỏ, RTF 0.2, MOS ổn → có thể ship. Config B: 48 kHz, L=40 ms, R=5 ms, model lớn, RTF 0.9, MOS offline cao, glitch điện thoại → **không ship B**. Ngân sách 40 ms: nếu model cần look-ahead 30 ms, phải đàm phán lại sản phẩm hoặc model.

## Bẫy thường gặp

1. Chỉ tối ưu RTF trung bình.
2. Đổi L/R không tái tạo tập eval.
3. So chất lượng ở độ trễ khác nhau một cách bất công.
4. Quên chi phí resample trong RTF.
5. Lấy timing build debug làm sự thật production.

## Bài tập nhỏ

1. Vẽ pipeline 9 giai; đánh dấu chỗ log timestamp.
2. Hop 10→5 ms: hop/s và CPU roughly?
3. Ba metric scorecard cho softphone CSKH.
4. Vì sao 48 kHz có thể hại mô hình train 16 kHz dù CPU cho phép?
5. Một artifact chất lượng từ cửa sổ quá ngắn.

## Đọc thêm

- DeepFilterNet2/3 — mục thiết kế real-time.
- Tài liệu cân nhắc độ trễ WebRTC APM.
- Hướng dẫn hiệu năng MDN AudioWorklet.
