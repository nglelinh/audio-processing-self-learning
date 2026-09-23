---
layout: post
title: "01-07 Checklist bẫy Fourier cho kỹ sư"
chapter: "01"
order: 7
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Khi NS “nghe hỏng”, kỹ sư hay train lại mô hình trước. Bài này là checklist Fourier/STFT trước chuyến bay: đơn vị, cửa sổ, đối xứng, scale, resample, DC/Nyquist — để đổ lỗi mạng sau cùng.

## Mục tiêu học tập

1. Chẩn đoán lỗi FT/DFT phổ biến trong pipeline audio.
2. Xác thực đơn vị (Hz vs bin vs tần số chuẩn hóa).
3. Áp checklist có cấu trúc trước khi đổ lỗi neural.
4. Nhận thất bại cửa sổ/COLA và đối xứng liên hợp bằng tai và bằng test.
5. Gắn checklist với debug kiểu Mezon/DeepFilterNet mà không bịa nội bộ.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–8 | Dạng war story: triệu chứng → nguyên nhân sai → bug thật |
| 8–30 | Đi checklist master kèm thí nghiệm tư duy |
| 30–45 | Unit test nên giữ trong repo |
| 45–55 | Thứ tự debug Mezon/DeepFilterNet |
| 55–60 | Bài tập |

## Checklist master

1. **Sự thật sample rate** — PCM = rate mô hình (hoặc resampler có tài liệu); có anti-alias khi giảm mẫu; không cứng 48 kHz.
2. **Đơn vị trục tần số** — \(f=k f_s/N\); lọc theo Hz dùng đúng \(f_s\).
3. **Chuẩn hóa FFT / Parseval** — khớp docs thư viện; round-trip STFT→ISTFT giữ năng lượng.
4. **Cửa sổ & COLA** — analysis/synthesis + hop thỏa COLA; khớp training.
5. **Đối xứng liên hợp / packing** — input iFFT thực Hermitian; DC/Nyquist imag ~0.
6. **Bố cục kênh** — interleaved vs planar; chính sách stereo→mono.
7. **Hop / kế toán trễ** — look-ahead ms; đệm ring; warmup metric nhất quán.
8. **DC & rác thấp** — DC blocker nếu lệch mic; đừng nhầm DC với nhiễu mô hình phải xóa.
9. **Hiển thị dB** — nhất quán \(20\log_{10}|X|\); clamp tránh \(\log 0\).
10. **Resampler + miền mô hình** — metric ở rate đã thỏa thuận; không resample kép trong A/B.

## Kịch bản debug

Warble 100 Hz ↔ hop 10 ms + COLA hỏng. “Mô hình cắt phụ âm” ↔ kiểm rate thật có năng lượng >6 kHz không; map bin 48 vs 16. SI-SDR đẹp, user ghét ↔ pha/musical noise (Ch. 08).

## Unit test nên có

Impulse round-trip; Parseval wrapper; sine resample không spur alias; assert downmix mono.

## Thứ tự debug Mezon / DeepFilterNet (công khai)

1. Rate/kênh theo README gói / model card.
2. Giao frame (callback, ring) — chủ đề Ch. 05.
3. Vệ sinh STFT (checklist này).
4. Mới đổi variant mô hình / tùy chọn npm.
5. Trích paper DeepFilterNet công khai; không claim đồ thị Mezon chưa công bố.

## Bẫy thường gặp

1. Đổi ba thứ cùng lúc (rate, hop, model).
2. Tin một demo quán cà phê.
3. Lỡ dùng checkpoint non-causal trong wrapper streaming.
4. Bỏ qua thời gian hop p99.
5. “Sửa” warble bằng NS mạnh hơn.

## Bài tập nhỏ

1. Chọn ba mục checklist; đặt tên unit test cho mỗi mục.
2. Hop 5 ms: tần số warble nếu COLA hỏng?
3. Vì sao sai \(f_s\) trong \(f=kf_s/N\) bắt chước mô hình xấu?
4. Mẫu báo cáo sự cố 6 bước “NS nghe tệ trên Chrome”.
5. Mục nào bắt stereo interleaved đưa vào FFT mono?

## Đọc thêm

- Oppenheim & Schafer — cửa sổ, scale, bẫy DFT.
- Paper DeepFilterNet — cấu hình & ghi chú real-time.
- Tài liệu profile ORT / trình duyệt để tách chi phí STFT vs net.
