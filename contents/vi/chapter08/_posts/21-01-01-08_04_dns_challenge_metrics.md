---
layout: post
title: "08-04 Bộ metric kiểu DNS Challenge"
chapter: "08"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter08
lesson_type: required
draft: false
---

Cả nghiên cứu lẫn sản phẩm cần một **bộ** metric, không phải một con số. Truyền thống **DNS Challenge** của Microsoft là khuôn nhiều paper DeepFilterNet và eval công nghiệp noi theo: mixture tổng hợp + metric xâm nhập, ghi âm thật + predictor không xâm nhập, cộng listening. Bài này biến truyền thống đó thành phác harness tái lập và mẫu báo cáo capstone.

## Kế hoạch giảng 60 phút

- 0–10 phút: Vì sao bộ metric thắng một metric.
- 10–25 phút: Track kiểu DNS (tổng hợp / thật / listening).
- 25–40 phút: Kiến trúc harness tối thiểu.
- 40–50 phút: WER ASR tùy chọn.
- 50–60 phút: Điền mẫu báo cáo capstone.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Liệt kê track/metric điển hình kiểu DNS.
- Phác harness đánh giá tái lập tối thiểu.
- Tránh overfit một tập tổng hợp.
- Viết phần báo cáo eval hướng sản phẩm.

## Track điển hình

| Track | Tư liệu | Metric |
|-------|---------|--------|
| Synthetic | cặp ồn/sạch | SI-SDR, (PESQ/STOI nếu chọn), Δ vs baseline |
| Real | không clean | DNSMOS (pin bản), predictor khác tùy chọn |
| Listening | tập con tuyển | AB / MUSHRA-like |
| Stress / systems | stream dài, ma trận thiết bị | RTF p95, glitch, lỗi init |
| Downstream tùy chọn | enhance → ASR | delta WER/CER |

**Ghim** năm challenge / paper khi tuyên bố “DNS metrics”.

## Tổng hợp vs thật

Tổng hợp: kiểm soát SNR, có SI-SDR — nhưng RIR/noise bank có thể lệch phòng thật.  
Thật: gần sản phẩm — không SI-SDR, khó tự động hơn.  
**Quy tắc:** đừng chỉ tune trên SI-SDR tổng hợp; luôn giữ real set đóng băng + subsample listening.

## Phác harness

```text
eval/
  datasets/synthetic|real/
  baselines/raw|apm/
  systems/df3_level80|df3_level60/
  scripts/run_enhance.py compute_si_sdr.py compute_dnsmos.py make_tables.py
  reports/YYYY-MM-DD_capstone.md
```

Checklist tái lập: phiên bản gói + commit, hash model, phiên bản DNSMOS, máy đo RTF, seed nếu có.

## Mẫu báo cáo sản phẩm

```markdown
## NS eval — <ngày>
- Hệ: deepfilternet3-noise-filter <ver> / level <n>
- Thiết bị; RTF p50/p95
### Synthetic | Real (DNSMOS) | Listening (AB)
### Quyết định ship / không / sau flag
### Giới hạn
```

## Chống overfit

Hold-out listening cuối; tách loại nhiễu; theo dõi hồi quy trên tiếng sạch; đo lại sau nâng WASM/SIMD.

## Bài tập

1. Điền mẫu với số giả định nhất quán cho level 60 vs 80.  
2. Viết schema cột `meta.csv`.  
3. Đề xuất ε fail CI cho DNSMOS và ΔSI-SDR.  
4. Hai cách suite overfit audio họp Mezon — và giảm rủi ro.

## Đọc thêm

- Overview / baseline DNS Challenge theo năm  
- Kết hợp SI-SDR + DNSMOS trong paper DeepFilterNet2/3  
- Chương 08-01…08-03; Capstone 09-04/09-05
