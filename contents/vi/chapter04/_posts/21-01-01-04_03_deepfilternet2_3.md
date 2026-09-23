---
layout: post
title: "04-03 DeepFilterNet2 và DeepFilterNet3"
chapter: "04"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

**DeepFilterNet2** và **DeepFilterNet3** tinh chỉnh công thức deep filtering gốc cho trade-off chất lượng–hiệu năng tốt hơn và bền vững thực tế hơn. Bài giữ trung thực: tóm tắt **nâng cấp thực dụng thường gắn** với DF2/DF3 từ paper và hệ sinh thái đã công bố, nối triển khai kiểu DF3 với `deepfilternet3-noise-filter` / Mezon, và nêu **độ nhạy dữ liệu train / RIR** mà không bịa số benchmark.

## Mục tiêu học tập

Bạn liệt kê headline DF → DF2 → DF3 ở mức kỹ sư sản phẩm, giải thích vì sao xuất ONNX quan trọng hơn FPS demo Python, nối npm package với họ mô hình (wrapper ≠ thuật toán), và nêu RIR chân thực lúc train ảnh hưởng deploy thế nào.

## Kế hoạch 60 phút

- **0–10 phút** — Ôn lõi DF; động lực đánh số phiên bản.
- **10–25 phút** — Narrative DF2: hiệu năng, train, tính thực dụng streaming.
- **25–40 phút** — Narrative DF3: tinh chỉnh thêm; đóng gói sản phẩm.
- **40–50 phút** — Độ nhạy dữ liệu / RIR; điều không được over-claim.
- **50–60 phút** — Bài tập; checklist căn chỉnh Mezon.

## Giải thích cốt lõi

### Cách đọc nhảy phiên bản

DF / DF2 / DF3 là **các thế hệ cùng họ thiết kế**:

- DNA chung: full-band, realtime, ERB + deep filtering.
- Khác recipe train, độ rộng/sâu mạng, đôi khi loss / pipeline dữ liệu.
- Artifact triển khai (ONNX, weight lượng tử) có thể lệch tên paper—**luôn pin SHA / tên file** trong tài liệu sản phẩm.

### DeepFilterNet2 — chủ đề kỹ thuật

Từ paper DF2 và hệ sinh thái (trích paper; không bịa metric):

- Tập trung mạnh hơn vào **CPU realtime** với chất lượng cạnh tranh.
- Tiếp tục xử lý đa tầng / đa phân giải trong tinh thần họ DF.
- Được dùng rộng như **baseline** trong paper kế (DPDFNet xây trên backbone kiểu DF2—04-04).

### DeepFilterNet3 — chủ đề sản phẩm

DF3 tiếp tục họ hướng chất lượng và độ bền full-band hiện đại. Trong căn chỉnh sản phẩm khóa học:

- Tên npm **`deepfilternet3-noise-filter`** báo hiệu đường runtime **hướng DF3** (WASM / ONNX on-device—chi tiết Ch. 06–07, 09).
- Nhiệm vụ học viên: hiểu **kỹ thuật** framing, state nhân quả, I/O mô hình, RTF—không chỉ `npm install`.

**Wrapper vs mô hình:** package nạp weight, suy luận thân thiện audio callback, lộ API kiểu TrackProcessor. Nó **không** miễn cho bạn biết hop STFT, reset state streaming, hay RTF cold-start.

### Đường xuất ONNX

```text
train (PyTorch) → đồ thị ONNX → ORT / WASM / tract → AudioWorklet hoặc native
```

Bẫy (mở rộng Ch. 06): op không hỗ trợ, dynamic axes cho khung stream, state RNN như I/O đồ thị, float32 vs int8.

### Độ nhạy RIR (không bịa số)

Enhancer dễ overfit cách bạn **mô phỏng phòng**. RIR image-source kiểu DNS khác đo thật hoặc mô phỏng sóng/hình học lai. Công trình follow-on train DeepFilterNet với âm học phòng chính xác hơn (paper liên quan DF3 đã xác minh—gán khi giao đọc) báo hành vi tốt hơn trên phòng thật / ASR hạ nguồn—bài học định tính cho Mezon:

- User kêu “NS nuốt tiếng trong phòng họp” → nghi **lệch âm học train/test**, không chỉ kích thước mô hình.
- Ưu tiên đánh giá trên **bản ghi thật** (nghe + DNSMOS, Ch. 08) bên cạnh mix DNS tổng hợp.

**Không** trích delta PESQ cụ thể trừ khi tự tái hiện từ bảng paper đã pin.

### Checklist căn chỉnh Mezon

1. Tên thế hệ mô hình thật sự ship (weight DF3? fine-tune riêng?).
2. Pin sample rate (thường 48 kHz) và chính sách downmix mono.
3. Đo RTF trên thiết bị đích (Ch. 05).
4. Tài liệu hóa cold start vs steady-state.
5. Giữ AEC cổ điển (trình duyệt/WebRTC) phía trước khi có echo (03-04).

## Bẫy thường gặp

- Trộn file weight DF2/DF3 với sai config.
- Nhận “chất lượng DF3” sau khi đổi hop STFT trong wrapper.
- Chỉ đánh giá tập kiểu VCTK-DEMAND cho sản phẩm ngôn ngữ SEA.
- Bỏ qua khiếu nại over-attenuation (một số successor thêm loss tường minh—04-04).

## Bài tập

1. Bảng 3 hàng DF/DF2/DF3: năm/venue (từ trích dẫn thật), claim một câu, artifact tải được.
2. Đọc README `deepfilternet3-noise-filter`; liệt kê API app thấy vs phần lõi vẫn phải hiểu.
3. Hai failure mode nhìn thấy khi RIR train quá khô vs quá vang.
4. Phác thảo tensor I/O ONNX cho một khung stream + state RNN (tên placeholder được).

## Đọc thêm

- Paper DeepFilterNet2 (Schröter et al.).
- DeepFilterNet3 / tag release repo chính thức.
- Công trình train-acoustics DF3 đã xác minh (gán arXiv cụ thể khi đã kiểm).
- README mezon-noise-suppression / `deepfilternet3-noise-filter`.
