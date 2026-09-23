---
layout: post
title: "04-01 Tổng quan tăng cường tiếng nói bằng mạng nơ-ron"
chapter: "04"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

Tăng cường tiếng nói bằng mạng nơ-ron (SE) thay gain thiết kế tay bằng mô hình train trên hỗn hợp nhiễu–sạch lớn. Bài tổng quan này lập bản đồ không gian thiết kế—**masking vs mapping vs generative** SE, miền thời gian vs spectrogram, họ loss, và vì sao kiến trúc **streaming** khác Transformer offline—để họ DeepFilterNet (04-02+) và RNNoise (04-06) có chỗ rõ trên bản đồ. Chỉ trích dẫn mốc đã xác minh: RNNoise, DNS Challenge, DeepFilterNet.

## Mục tiêu học tập

Bạn đối chiếu ước lượng mask, ánh xạ phổ và SE sinh mẫu; liệt kê loss giám sát phổ biến ở mức cao; giải thích vì sao đồ thị nhân quả / streaming cấm ngữ cảnh hai chiều ngây thơ; và đặt RNNoise cùng DeepFilterNet trên phác thảo phức tạp–chất lượng cho sản phẩm.

## Kế hoạch 60 phút

- **0–10 phút** — Từ IRM Wiener đến mask học: dữ liệu mua được gì.
- **10–25 phút** — Masking vs mapping vs generative; miền sóng vs STFT.
- **25–40 phút** — Hỗn hợp train (kiểu DNS), loss (biên độ, SI-SDR, phức, cảm nhận).
- **40–50 phút** — Ràng buộc streaming vs SE offline; xem trước RTF (Ch. 05).
- **50–60 phút** — Bẫy, bài tập, lộ đọc vào 04-02.

## Giải thích cốt lõi

### Mạng xuất gì?

**1. Masking.** Dự đoán $$M$$ rồi $$\hat{S}=M\odot Y$$ (hoặc áp lên biên độ, giữ pha nhiễu). Mục tiêu IRM vọng lại gain Wiener $$\xi/(\xi+1)$$.

**2. Mapping / hồi quy.** Dự đoán trực tiếp phổ sạch $$\hat{S}=f_\theta(Y)$$. Linh hoạt hơn; dễ làm mượt quá nếu loss yếu.

**3. Generative SE.** GAN / diffusion / score-based tổng hợp tiếng nói khớp hậu nghiệm. Trần chất lượng cao hơn offline; khó stream RTF thấp. DeepFilterGAN (04-04) gắn regenerator GAN nhẹ sau predictor kiểu DeepFilterNet.

### Miền thời gian vs spectrogram

| Họ | Đầu vào | Ưu | Nhược |
|----|---------|-----|-------|
| Dạng sóng (Conv-TasNet-like) | PCM | End-to-end pha | Nặng cho full-band realtime |
| Mask / lọc STFT | Spectrogram phức | Dễ hiểu, hiệu quả | Latency cửa sổ |
| Hybrid ERB + deep filter | Band thính giác + STFT | Điểm ngọt DeepFilterNet | Phức tạp triển khai |

Mô hình họ DeepFilterNet là hệ **spectrogram / deep filtering** tối ưu ngân sách CPU full-band (48 kHz)—không phải khổng lồ dạng sóng offline.

### Công thức train giám sát (kiểu DNS)

1. Lấy mẫu tiếng sạch, nhiễu, tùy chọn RIR.
2. Trộn SNR ngẫu nhiên (và mức vang).
3. Train $$f_\theta$$ khôi phục tiếng sạch hoặc mask.
4. Đánh giá SI-SDR, PESQ/STOI (nếu có quyền), DNSMOS (Ch. 08).

Chuỗi **DNS Challenge** phổ biến hóa tập train lớn và baseline NS thời gian thực—đọc overview cho quy ước dữ liệu/metric, không khẳng định một mạng luôn thắng.

### Họ loss (mức cao)

- MSE / MAE phổ trên biên độ hoặc log-biên độ.
- Loss phổ phức (real/imag).
- SI-SDR miền thời gian (Ch. 08).
- Multi-resolution STFT.
- Loss cảm nhận / discriminator (GAN, nặng hơn).

### Vì sao streaming ≠ Transformer SE offline

Offline có thể dùng khung tương lai hoặc attention cả chuỗi. VoIP thời gian thực cần:

- **Latency thuật toán** ≈ cửa sổ + look-ahead + buffer (Ch. 02, 05),
- Chỉ convolution nhân quả / RNN một chiều,
- **State kích thước cố định**—không KV cache phình,
- **RTF ≪ 1** trên CPU đích, thường WASM (Ch. 06).

### Mốc trên bản đồ

```text
 phức tạp thấp                         chất lượng cao hơn
     │                                        │
  RNNoise ── CRN siêu nhẹ ── DeepFilterNet2/3 ── tinh chỉnh generative
```

`deepfilternet3-noise-filter` của Mezon nằm nhánh chất lượng DF3 với ràng buộc on-device—không phải nhánh RNNoise—nhưng RNNoise vẫn là **cầu dạy** tốt nhất (04-06).

## Bẫy thường gặp

- So PESQ offline với RTF streaming bất công.
- Train chỉ nhiễu dừng rồi deploy quán cà phê.
- Bỏ qua pha / mask chỉ biên độ ở SNR thấp không nghe kiểm.
- Coi “Transformer lớn hơn” luôn tốt hơn cho NS sản phẩm.
- Coi npm wrapper là thuật toán (nhắc Chương 09).

## Bài tập

1. Phân loại RNNoise, U-Net IRM biên độ, Conv-TasNet, DeepFilterNet theo masking/mapping/generative và time/STFT.
2. Hop = 10 ms, look-ahead = 2 khung: cận dưới latency thuật toán trước khi tính neural?
3. Tranh luận SI-SDR vs log-mel MSE cho telephony streaming.
4. Lướt overview DNS Challenge; nêu 3 tính chất dataset ảnh hưởng tổng quát hóa sản phẩm.

## Đọc thêm

- Paper và repo RNNoise (Jean-Marc Valin et al.).
- Overview / dataset DNS Challenge (Microsoft).
- Paper DeepFilterNet — baseline full-band realtime của khóa học.
- Loizou, *Speech Enhancement* — nền mask cổ điển.
