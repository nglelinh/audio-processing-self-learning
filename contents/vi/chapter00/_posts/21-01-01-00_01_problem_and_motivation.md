---
layout: post
title: "00-01 Vì sao khử nhiễu thời gian thực quan trọng"
chapter: "00"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter00
lesson_type: required
draft: false
---

Khử nhiễu thời gian thực (real-time noise suppression, NS) là ràng buộc sản phẩm quyết định cuộc gọi có dùng được trong văn phòng mở, trên đường, hay cạnh bàn phím cơ hay không. Bài này định khung *bài toán*, chưa đi sâu thuật toán: ai quan tâm, “tốt” nghĩa là gì, và khóa học gắn với sản phẩm Mezon công khai như thế nào.

## Mục tiêu học tập

Sau khoảng 60 phút, bạn cần:

1. Giải thích vì sao NS đơn kênh là yêu cầu hạng nhất trong VoIP, họp trực tuyến và giao diện thoại nhúng.
2. Tách ba mục tiêu tăng cường: **độ rõ (intelligibility)**, **chất lượng cảm thụ**, và đầu vào **thân thiện ASR**.
3. Phân biệt khử nhiễu real-time / nhân quả với xử lý offline theo ngôn ngữ sản phẩm (độ trễ, RTF).
4. Đặt khóa học trong ngữ cảnh stack Mezon công khai (`mezonai/mezon-noise-suppression`, npm `deepfilternet3-noise-filter`) mà không bịa nội bộ chưa công bố.
5. Nêu rõ phần *không* phải trọng tâm (toàn bộ stack AEC/AGC).

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–8 | Khởi động: hình dung ba cảnh (HVAC văn phòng, đường phố, bàn phím) — cái gì làm hỏng cuộc gọi |
| 8–20 | Mục tiêu sản phẩm: độ rõ / chất lượng / ASR; ánh xạ sang chế độ hỏng |
| 20–35 | Ràng buộc real-time: độ trễ khung, RTF; vì sao SOTA offline thường không ship được |
| 35–48 | Ngữ cảnh Mezon / DeepFilterNet (chỉ bề mặt công khai) và phạm vi khóa học |
| 48–60 | Bài tập nhỏ + thảo luận bẫy thường gặp |

## Giải thích cốt lõi

### Nhiễu như ràng buộc sản phẩm

Trong sản phẩm thoại, nhiễu không chỉ là \(n(t)\) trên giấy. Nó là **SLA người dùng nhìn thấy**:

- **Văn phòng / HVAC**: nhiễu gần dừng (quasi-stationary), tần số thấp; bộ ước lượng cổ điển xử lý khá tốt nhưng nếu bỏ mặc thì rất khó chịu.
- **Đường phố / quán cà phê**: bùng nổ không dừng; bộ theo dõi nền nhiễu cổ điển bị trễ; mô hình neural mới đáng giá.
- **Bàn phím / chuột**: xung băng rộng, xuyên qua formant tiếng nói.
- **Babble** (nhiều người nói): khó nhất ở đơn kênh vì “nhiễu” cùng họ thời–tần với tín hiệu đích.

Khối NS dùng được phải giảm các thành phần trên mà không biến tiếng nói thành tiếng “ướt”, không thêm hàng chục ms làm hỏng nhịp hội thoại, và không đốt CPU đến mức callback AudioWorklet bị underrun.

### Ba mục tiêu tăng cường (đừng gộp chúng)

1. **Độ rõ** — người nghe (hoặc ASR) có lấy được từ không? Méo phổ cắt phụ âm có thể *trông* sạch trên spectrogram mà vẫn phá độ rõ.
2. **Chất lượng cảm thụ** — kiểu MOS / DNSMOS: ít rít, ít musical noise, tembre tự nhiên.
3. **Đầu vào ASR** — một số pipeline tối ưu WER; NS mạnh giúp người nghe đôi khi *hại* ASR nếu cắt mất cue mà recognizer cần.

Chỉ số cổ điển (SI-SDR) và chỉ số nghe (DNSMOS) hay bất đồng; đội sản phẩm phải chọn mục tiêu chính. Khóa học này nhấn **chất lượng hội thoại thời gian thực** theo hướng Mezon / WebRTC, đồng thời dạy công cụ đánh giá ở Chương 08.

### Real-time và offline (xem sâu ở 00-03)

Offline có thể dùng cả utterance, ngữ cảnh hai chiều, mạng lớn. Real-time là **nhân quả (causal)**: tại thời điểm \(t\) chỉ dùng âm thanh đến \(t\) (cộng ngân sách look-ahead nhỏ có chủ đích).

Hai số chi phối review thiết kế:

- **Độ trễ thuật toán / đệm (ms)**
- **Real-time factor (RTF)**: thời gian xử lý tường chia thời lượng audio. Với streaming cần RTF worst-case \(\ll 1\) trên *thiết bị đích*.

### Mô hình hỗn hợp (một phương trình cần nhớ)

$$
y(t) = x(t) + n(t)
$$

sau STFT:

$$
Y(\ell,k) = X(\ell,k) + N(\ell,k)
$$

Hầu hết NS cổ điển và neural là chiến lược ước lượng \(X\) (hoặc mask / bộ lọc) từ \(Y\) dưới ràng buộc real-time. Vang phòng (reverb) là bài toán *liên quan nhưng tách*:

$$
y(t) = (x * h)(t) + n(t)
$$

### Ngữ cảnh sản phẩm Mezon (chỉ sự kiện công khai)

- GitHub: **`mezonai/mezon-noise-suppression`**
- npm: **`deepfilternet3-noise-filter`**
- Đường dẫn local của giảng viên (không bắt buộc học viên): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`

**Dạy kỹ thuật**, không dạy “cách gọi một npm wrapper”. Capstone Chương 09 yêu cầu hiểu pipeline, không reverse-engineer nội bộ chưa công bố.

### Phạm vi

| Trong phạm vi | Ngoài trọng tâm |
|---------------|-----------------|
| Định khung, STFT, NS cổ điển, DeepFilterNet, RTF, ORT/WASM, tích hợp WebRTC/LiveKit, metric | Thiết kế AEC đầy đủ, beamforming phần cứng, nội bộ Mezon chưa công bố |
| AEC/AGC/WebRTC APM như *ngữ cảnh* (Ch. 03) | Thay thế toàn bộ WebRTC APM |

## Ví dụ có số — phác thảo ngân sách độ trễ

Sản phẩm họp muốn \(\le 40\,\mathrm{ms}\) buffering thuật toán từ callback mic đến PCM sạch đưa vào encoder.

Giả sử \(f_s = 48\,\mathrm{kHz}\), cửa sổ \(L = 480\) (10 ms), hop \(R = 240\) (5 ms), mô hình cần một frame look-ahead.

Tại 48 kHz, 1 ms = 48 mẫu. Nếu forward neural mất 8 ms tường trên hop 20 ms thì RTF \(=0.4\) — còn dư. Nếu mất 22 ms sẽ underrun trừ khi tăng hop (độ trễ) hoặc thu nhỏ mô hình.

## Bẫy thường gặp

1. Tối ưu SI-SDR offline rồi ship cùng checkpoint streaming mà không đo độ trễ nhân quả và RTF thiết bị.
2. Dùng “% giảm nhiễu” như metric QA — không định nghĩa rõ.
3. Giả sử NS mono chạy nguyên trên stereo không có chính sách downmix.
4. Đổ lỗi cho neural khi bug là lệch sample rate, sai hop, hoặc lệch cửa sổ OLA.
5. Khẳng định “bí mật Mezon” từ khóa học — chỉ bám bề mặt công khai và literature DeepFilterNet.

## Bài tập nhỏ

1. Chọn cảnh 10 giây (quán cà phê). Liệt kê ba sự kiện nhiễu; gắn nhãn dừng / không dừng / giống tiếng nói.
2. Viết mỗi câu một mục tiêu độ rõ, chất lượng, ASR cho softphone chăm sóc khách hàng.
3. Với \(f_s=16\,\mathrm{kHz}\), hop \(R=160\), tính độ dài hop (ms) và thời gian xử lý tối đa trung bình để RTF \(=0.5\).
4. Đọc README công khai `mezonai/mezon-noise-suppression` (khi online) và liệt kê ba khả năng *đã được ghi* — không bịa thêm.

## Đọc thêm

- Tài liệu WebRTC Audio Processing Module (APM) — mục noise suppression.
- Các bài DeepFilterNet (INTERSPEECH / arXiv) — abstract và phần mở đầu.
- Trang tổng quan DNS Challenge (dataset và track).
