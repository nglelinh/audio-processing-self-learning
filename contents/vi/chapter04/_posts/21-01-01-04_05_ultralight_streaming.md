---
layout: post
title: "04-05 Mô hình streaming siêu nhẹ"
chapter: "04"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

Không phải sản phẩm nào cũng cần dung lượng kiểu DeepFilterNet3. SE streaming **siêu nhẹ** nhắm hàng chục MMAC và bộ nhớ rất nhỏ cho DSP, hearable và điện thoại tầm thấp. Bài khảo sát này dạy tiêu chí chọn—đặc biệt **số MAC ≠ RTF tường**—và nêu con trỏ đã biết: **GTCRN**, **FastEnhancer**, **μNet**, **Fast-ULCNet** (và họ ULCNet). Dùng như từ vựng shortlist, không phải lệnh viết lại bắt buộc.

## Mục tiêu học tập

Bạn giải thích vì sao chọn toán tử và traffic bộ nhớ chi phối RTF, nêu các mô hình trên với vai trò một dòng, liệt kê tiêu chí shortlist NS on-device, và quyết định khi nào ưu DF3 vs siêu nhẹ.

## Kế hoạch 60 phút

- **0–10 phút** — Kịch bản: hearable vs tab trình duyệt laptop.
- **10–25 phút** — MAC vs RTF vs bộ nhớ; op thân thiện CPU.
- **25–40 phút** — Tour con trỏ: GTCRN, FastEnhancer, μNet, Fast-ULCNet.
- **40–50 phút** — Trôi state streaming (mức cao).
- **50–60 phút** — Checklist quyết định; bài tập.

## Giải thích cốt lõi

### Chủ đề công nghiệp

Paper siêu nhẹ tối ưu: **params**, **MAC/khung**, **latency nhân quả**, benchmark nhúng (Cortex-A, HiFi DSP, Pi, CPU điện thoại). Có thể thua DF3 về chất lượng full-band phong phú—nhưng thắng khi lựa chọn còn lại là “tắt NS”.

### MAC ≠ RTF tường

Công trình kiểu FastEnhancer nhấn: toán tử grouped/subband phức có thể trông rẻ trên bảng MAC nhưng chậm trên CPU vì gather/scatter, cache kém, kernel không thân thiện trong ORT. Ngược lại, encoder–decoder “trơn” MAC hơi cao hơn + GEMM fuse có thể thắng RTF.

**Quy tắc đo (Ch. 05):** báo RTF đơn luồng trên thiết bị đích với warm cache **và** nhịp audio-callback—không chỉ MAC paper.

### Con trỏ khảo sát

| Mô hình | Vai trò một dòng |
|---------|------------------|
| **GTCRN** | Baseline CRN nhóm siêu nhẹ được trích dẫn rộng |
| **FastEnhancer** | SE streaming hướng tốc độ; tư duy RTF ONNX |
| **μNet** | Hồ sơ DSP / hearable bộ nhớ cực thấp |
| **Fast-ULCNet** | Kế ULCNet; ghi nhận vấn đề state RNN dài |
| **ULCNet** (họ) | SE full-band nhẹ / bạn đồng hành hybrid AENR |

Tên liên quan cùng cụm: UL-UNAS, AdaptCRN, CoFi-Lite, FSPEN—đọc sâu tùy chọn.

### Trôi state streaming (xem trước 05-04)

RNN nhỏ chạy hàng giờ có thể **trôi**: state ẩn lệch dần. Giảm nhẹ: reset mềm lúc silence, chuẩn hóa bị chặn, test stream **≥ 30 phút**.

### Khi nào DF3 vs siêu nhẹ

**DF3-class:** desktop/laptop WASM SIMD; chất lượng full-band là khác biệt; tải vài MB chấp nhận được.  
**Siêu nhẹ:** DSP/hearable/CPU rất yếu; latency thuật toán vài ms; bộ nhớ ≪ DF3; chấp nhận nhiễu dư nhiều hơn.  
**Hybrid:** AEC cổ điển + NS siêu nhẹ trên nhúng; DF3 trên Electron/web desktop.

## Checklist shortlist

1. Nhân quả? Số khung look-ahead?
2. Sample rate 16 vs 48 kHz?
3. RTF đo trên **hạng thiết bị của bạn** (ORT/WASM).
4. Kích thước mô hình + thời gian cold-start.
5. Kế hoạch ổn định stream dài.
6. Giấy phép weight/code.
7. Độ phủ op ONNX trong runtime.

## Bẫy thường gặp

- Chọn mô hình chỉ từ bảng MAC.
- Port convolution nhóm không có kernel SIMD.
- Bỏ test stream dài.
- Nhét weight 16 kHz siêu nhẹ vào pipeline 48 kHz không có chính sách resample.

## Bài tập

1. Chọn DF3 vs siêu nhẹ cho (a) DSP kiểu AirPods, (b) Chrome laptop tầm trung, (c) loa Pi—5 gạch mỗi trường hợp.
2. Phác harness đo: warm-up, p50/p95 RTF, ghi chú affinity luồng.
3. Đề xuất thí nghiệm phát hiện suy giảm dần trong 45 phút.
4. Đọc abstract FastEnhancer và GTCRN; chỉ lấy latency/hạng tính toán **có trong abstract**.

## Đọc thêm

- GTCRN (dòng CRN siêu nhẹ ICASSP).
- FastEnhancer paper / code.
- μNet, Fast-ULCNet / ULCNet.
- DeepFilterNet2/3 — baseline phía chất lượng.
