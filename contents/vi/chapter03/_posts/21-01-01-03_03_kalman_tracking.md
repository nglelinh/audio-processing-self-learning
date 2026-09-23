---
layout: post
title: "03-03 Theo dõi kiểu Kalman (trực giác)"
chapter: "03"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter03
lesson_type: required
draft: false
---

Kalman không phải “một mask khác”. Đó là **bộ theo dõi Bayesian đệ quy**: dự đoán trạng thái tiếng nói kế tiếp, rồi hiệu chỉnh bằng quan sát nhiễu mới. Trong SE và AEC, tư duy Kalman xuất hiện ở bộ lọc thích nghi, theo dõi echo dư, và hybrid AEC+NS (ví dụ Kalman AEC cổ điển rồi postfilter neural nhỏ). Bài này giữ mức **trực giác và sơ đồ khối**—đủ để đọc paper và debug hybrid—không biến thành giáo trình điều khiển.

## Mục tiêu học tập

Bạn giải thích vòng predict–update với hiệp phương sai nhiễu quá trình/đo, ánh xạ SE sang phác thảo không gian trạng thái, đối chiếu Kalman với gain Wiener từng khung, và nhận diện pattern sản phẩm: Kalman/LMS/RLS làm front-end cho residual suppressor neural.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao theo dõi đệ quy hơn “ước lượng từ đầu mỗi khung”.
- **10–25 phút** — Mô hình trạng thái, predict, trực giác Kalman gain.
- **25–40 phút** — Thể hiện tiếng nói/AEC: theo dõi hệ số AR hoặc đường echo.
- **40–50 phút** — Hybrid: Kalman AEC + neural postfilter (con trỏ khảo sát).
- **50–60 phút** — Bẫy, bài tập, nối WebRTC APM (03-04).

## Giải thích cốt lõi

### Kalman một câu

Giữ niềm tin về trạng thái ẩn $$x_\ell$$ (mẫu tiếng sạch, hệ số LPC, hoặc đáp ứng xung echo). Mỗi khung:

1. **Predict** theo động học: $$x_{\ell|\ell-1}=A x_{\ell-1|\ell-1}$$.
2. **Update** với đo $$y_\ell=H x_\ell+v_\ell$$: kéo dự đoán về quan sát tỷ lệ với độ tin cậy tương đối.

**Kalman gain** $$K_\ell$$ lớn khi đo đáng tin—tin mic hơn—và nhỏ khi đo nhiễu—chạy theo mô hình.

### Cartoon vô hướng

$$
x_\ell = x_{\ell-1}+w_\ell,\quad y_\ell=x_\ell+v_\ell,
$$

$$
K=\frac{p^{-}}{p^{-}+r},\quad \hat{x}=\hat{x}^{-}+K(y-\hat{x}^{-}).
$$

So với Wiener: $$K$$ giống $$\xi/(\xi+1)$$ nếu đọc $$p^{-}/r$$ như SNR tiên nghiệm. Kalman = Wiener **cộng bộ nhớ** qua trạng thái và phương sai dự đoán.

### Vì sao kỹ sư âm thanh quan tâm

| Ứng dụng | Trạng thái $$x$$ | Đo $$y$$ |
|----------|------------------|----------|
| Theo dõi tiếng sạch | mẫu / biên độ phổ | mic nhiễu |
| LPC / formant | hệ số AR | phần dư / phổ |
| Ước lượng đường AEC | $$\mathbf{h}$$ | mic, hồi quy từ far-end |
| PSD echo dư | công suất echo dư | lỗi sau adaptive filter |

**Bộ lọc thích nghi** (NLMS, RLS) trong AEC là anh em gần: ước lượng đệ quy đường echo. Kalman cho lịch gain có thống kê; NLMS cho bước chuẩn hóa rẻ. WebRTC APM / SpeexDSP nghiêng về adaptive filter thực dụng; paper hybrid thường nói “Kalman AEC” theo nghĩa tracker hiệp phương sai.

### Hybrid cổ điển + neural

1. Adaptive filter / Kalman hủy echo **tuyến tính** có tham chiếu far-end.
2. Mạng **nhỏ** (ULCNet / GTCRN / postfilter DF) dọn echo dư + nhiễu mà mô hình tuyến tính không bắt được.

Con trỏ khảo sát: Align-ULCNet và hybrid ULCNet+adaptive filter; GSC+DeepFilterNet2 cho nhiễu ego có hướng.

**Đạo đức kỹ thuật:** đừng bắt mạng học hủy echo tuyến tính thuần nếu đã có tham chiếu—hãy đưa residual đã làm sạch.

## Checklist: khi nào nghĩ kiểu Kalman

- Có **mô hình động học** (đường echo biến chậm; envelope AR).
- Có **tham chiếu** (far-end cho AEC).
- Residual sau canceller tuyến tính vẫn cần cleaner phi tuyến.
- Ngân sách CPU chặt—ưu tiên adaptive cổ điển + NS nhỏ hơn mạng end-to-end khổng lồ.

## Bẫy thường gặp

- Coi Kalman là “khử nhiễu thần kỳ” mà không chỉ rõ trạng thái/đo.
- Sai $$A$$ hoặc $$H$$ → lệch hệ thống.
- Hiệp phương sai phình số (cần dạng ổn định SPD).
- Kalman đầy đủ trên vector STFT khổng lồ trong khi gần đúng chéo / NLMS mới thực tế.
- Quên neural residual thêm latency và state streaming (Ch. 05–06).

## Bài tập

1. Cài predict–update vô hướng; kích $$x$$ bằng sine chậm; quan sát $$K$$ khi đổi $$r$$.
2. Sơ đồ một trang: AEC với state $$=\mathbf{h}$$; đánh dấu postfilter neural.
3. Ba điểm giống / khác giữa Wiener decision-directed và Kalman cho PSD tiếng nói.
4. Brief thiết kế: trình duyệt có echo loa → WebRTC AEC → neural NS dư; nêu trách nhiệm từng khối.

## Đọc thêm

- R. E. Kalman, 1960.
- Haykin, *Adaptive Filter Theory* (NLMS/RLS).
- Tổng quan WebRTC Audio Processing Module.
- Con trỏ hybrid Kalman/ULCNet AENR (Align-ULCNet, mức tên).
