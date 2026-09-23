---
layout: post
title: "04-02 DeepFilterNet: ý tưởng deep filtering"
chapter: "04"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

**DeepFilterNet** phổ biến hóa công thức thực dụng cho SE **full-band, thời gian thực**: xử lý biểu diễn thô thang **ERB** để khử nhiễu hiệu quả, rồi áp **deep filtering đa khung** miền STFT để phục hồi cấu trúc tuần hoàn tinh. Bài này tập trung *ý tưởng*—ERB + deep filter, đường spectrogram phức, nhân quả—để DF2/DF3 (04-03) đọc như nâng cấp tiến hóa chứ không phải phát minh mới.

## Mục tiêu học tập

Bạn giải thích xử lý band ERB so với độ phân giải STFT đầy đủ, mô tả deep filtering như bộ lọc phức đa khung học được (không chỉ mask từng bin), nêu vì sao thiết kế nhắm SE CPU 48 kHz realtime, và chỉ ra hệ sinh thái mã nguồn mở chính thức để thí nghiệm.

## Kế hoạch 60 phút

- **0–10 phút** — Động lực: chất lượng full-band không tốn MAC đều mọi bin.
- **10–25 phút** — Đường encoder ERB: đặc trưng nén lấy cảm hứng thính giác.
- **25–40 phút** — Deep filtering: hệ số đa khung trên phổ phức; so gain Wiener.
- **40–50 phút** — Nhân quả, look-ahead, định hướng repo `DeepFilterNet`.
- **50–60 phút** — Bẫy, bài tập, cầu DF2/DF3.

## Giải thích cốt lõi

### Trực giác hai tầng

Thính giác người phân giải tần số xấp xỉ thang **ERB**—mịn ở tần thấp, thô ở tần cao. Họ DeepFilterNet tận dụng:

1. **Tầng thô (ERB):** tăng cường trong không gian đặc trưng ERB chiều thấp—rẻ, khử nhiễu mạnh.
2. **Tầng tinh (deep filter):** bộ lọc phức đa khung ngắn trên bin STFT để phục hồi họa âm và chi tiết mà ERB làm nhòe.

```text
PCM → STFT → đặc trưng ERB → enhancer ERB neural → (gain)
                ↘ STFT phức → deep filter đa khung → ISTFT → PCM
```

Tên module cụ thể đổi theo phiên bản; giữ cartoon rồi đối chiếu paper/code đã pin.

### Deep filtering ≠ mask một khung

Mask cổ điển: $$\hat{S}(k,\ell)=M(k,\ell)Y(k,\ell)$$. **Deep filter** dự đoán hệ số trộn ngữ cảnh thời gian ngắn:

$$
\hat{S}(k,\ell)=\sum_{\tau=0}^{T-1} H(k,\ell,\tau)\, Y(k,\ell-\tau),
$$

với $$H$$ phức (học được)—FIR theo thời gian từng bin, tổng quát hóa “nhân gain”. HDF-Net (04-04) sau này khảo sát deep filtering phân cấp thời gian vs tần số.

**Nối Chương 03:** Wiener là gain *một tap* tối ưu dưới giả định Gauss. Deep filter học hiệu chỉnh đa tap khi giả định vỡ.

### Spectrogram phức và full-band realtime

Làm việc với phần thực/ảo cho phép chỉnh pha cục bộ qua bộ lọc—quan trọng với tiếng hữu thanh. Full-band 48 kHz làm số bin STFT nổ; nén ERB giữ mạng nhỏ; deep filtering đổ năng lực vào chỗ có cấu trúc tuần hoàn. Đó là lý do sản phẩm kiểu Mezon xuất đồ thị họ DF sang ONNX/WASM thay vì SE offline khổng lồ.

### Nhân quả

VoIP: bộ lọc phải **nhân quả** (hoặc look-ahead cố định nhỏ đã tính vào ngân sách latency). Khi đọc code/ONNX: không nhìn tương lai quá cấu hình; state RNN mang qua khung (Ch. 05); hop STFT khớp quantum AudioWorklet.

### Hệ sinh thái chính thức

Dùng **repo DeepFilterNet chính thức** làm nguồn sự thật cho config, weight pretrained và CLI. Lab khóa học nên pin commit/tag. Wrapper sản phẩm (`deepfilternet3-noise-filter`) đóng gói đường triển khai—không thay việc hiểu ý tưởng lõi.

## Checklist giải thích cho đồng đội

1. SE full-band realtime, không chỉ nghiên cứu offline.
2. Đường ERB khử hiệu quả.
3. Deep filter đa khung cho cấu trúc tinh.
4. Xử lý STFT phức.
5. Streaming nhân quả, state bị chặn.
6. Weight/code mở → có thể xuất ONNX (Ch. 06).

## Bẫy thường gặp

- Gọi mọi mạng mask là “DeepFilterNet”.
- Bỏ ERB, chỉ nói U-Net mask.
- Đo chất lượng 16 kHz rồi nhận full-band sản phẩm.
- Quên latency OLA/cửa sổ trong tuyên bố “realtime”.
- Trộn config DF1/DF2/DF3 tùy tiện.

## Bài tập

1. Viết cạnh nhau phương trình Wiener một khung vs deep filter đa khung; khoanh phần học vs ước lượng.
2. Nếu ERB dùng $$B\ll K$$ band, lập luận MAC tầng thô giảm roughly theo $$B/K$$.
3. Clone repo chính thức; chạy enhance WAV; ghi tag và lệnh.
4. Tìm look-ahead / hop trong config; tính cận dưới latency thuật toán.

## Đọc thêm

- Paper DeepFilterNet gốc (Schröter et al.).
- README / model card repo chính thức.
- Nền ERB (Moore / Glasberg)—trực giác tùy chọn.
- Tiếp: DeepFilterNet2 và DeepFilterNet3 (04-03).
