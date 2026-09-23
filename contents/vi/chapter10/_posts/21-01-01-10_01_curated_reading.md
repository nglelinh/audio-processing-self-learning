---
layout: post
title: "10-01 Danh mục đọc có chọn lọc"
chapter: "10"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter10
lesson_type: required
draft: false
---

Danh sách **chọn lọc** ngắn tốt hơn một đống link. Dưới đây là nguồn chuẩn dùng xuyên suốt khóa, tách must-read và con trỏ survey tùy chọn. **Không trích dẫn giả** — thêm paper nào phải xác minh title/authors/venue trước.

## Kế hoạch giảng 60 phút

- 0–10 phút: Cách đọc paper SE cho việc sản phẩm (hình → độ phức tạp → streaming).
- 10–35 phút: Đi must-read; mỗi HV tóm tắt một paper.
- 35–50 phút: Con trỏ successor / ultra-light (chỉ tên đã nêu).
- 50–60 phút: Làm thẻ “năm link” cá nhân cho capstone.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Gom paper/docs chuẩn của khóa.
- Tách must-read vs survey tùy chọn.
- Giữ danh sách không citation bịa.
- Chỉ đúng tài liệu LiveKit/WebRTC, SI-SDR, DNSMOS, DNS Challenge.

## Must-read (lộ trình lõi)

### Họ DeepFilterNet

1. Schröter et al., **DeepFilterNet** — ICASSP 2022; arXiv:[2110.05588](https://arxiv.org/abs/2110.05588).  
2. DeepFilterNet2/3 qua repo [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) và publication được README liệt kê.  
3. Model sản phẩm: `DeepFilterNet3_onnx.tar.gz` trong `models/`.

### Cầu nối cổ điển / giảng dạy

4. **RNNoise** (Jean-Marc Valin).  
5. **SpeexDSP** / tài liệu WebRTC **APM**.  
6. WebRTC samples & MDN media capture.

### Đánh giá

7. **SI-SDR** trong văn liệu BSS/SE (thảo luận biến thể SDR, Le Roux et al.).  
8. Overview **DNS Challenge** (Microsoft) — giao thức + baseline.  
9. Paper **DNSMOS** khớp phiên bản bạn chạy.  
10. ITU-T **P.808** và ITU-R **BS.1534** (tổng quan listening).

### Sản phẩm / runtime

11. Docs client [LiveKit](https://docs.livekit.io/) — track/processor theo SDK.  
12. npm [`deepfilternet3-noise-filter`](https://www.npmjs.com/package/deepfilternet3-noise-filter) + [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression).  
13. **ONNX Runtime** performance; **tract** nếu đi Rust.

## Con trỏ survey tùy chọn (chỉ tên)

- Successor: **DPDFNet**, **DeepFilterGAN**, **HDF-Net**  
- Ultra-light / streaming: **FastEnhancer**, **μNet**, **Fast-ULCNet**, **GTCRN**  

Xác minh trên arXiv/venue trước khi cite trong báo cáo.

## Cách đọc cho kỹ sư (một trang / paper)

1. Streaming? Causal? Lookahead?  
2. Sample rate / độ phức tạp (MAC, RTF, thiết bị).  
3. Metric báo cáo.  
4. Tái sử dụng gì trong sản phẩm kiểu Mezon.

## Bài tập

1. Thẻ năm link cá nhân (DF, DNS eval, WebRTC/LiveKit, runtime, Mezon README).  
2. Tóm tắt 10 dòng arXiv:2110.05588 về ý tưởng deep filtering.  
3. Tìm trang DNS Challenge năm khớp tooling DNSMOS của bạn.  
4. Thêm một successor đã xác minh ID vào ghi chú.

## Đọc thêm

- Chính sách citation trong `COURSE_OUTLINE.md` / `AGENTS.md`  
- Mục papers trên README DeepFilterNet (danh sách sống)
