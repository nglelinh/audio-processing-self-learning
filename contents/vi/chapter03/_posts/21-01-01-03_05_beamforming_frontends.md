---
layout: post
title: "03-05 Beamforming / GSC / IVA như front-end"
chapter: "03"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter03
lesson_type: required
draft: false
---

Khi có **hai micro trở lên**, hình học cho đòn bẩy mà NS một kênh không có: chọn lọc không gian. Beamforming, generalized sidelobe cancellation (GSC) và independent vector analysis (IVA) là front-end đa kênh cổ điển có thể nuôi enhancer neural mono. Bài này dạy trực giác kỹ sư—delay-and-sum, cartoon MVDR, GSC blocking matrix, IVA như tách mù—và hybrid như GSC+DeepFilterNet2 hay IVA+GTCRN trong công việc SNR thấp / drone / dual-mic (chỉ con trỏ khảo sát).

## Mục tiêu học tập

Bạn giải thích mục tiêu delay-and-sum và MVDR bằng lời thường, phác thảo GSC (beamformer cố định + blocking matrix + canceller thích nghi), tóm tắt IVA như bộ tách đa kênh mù, và quyết định khi nào front-end không gian + DeepFilterNet mono thắng NS chỉ mono.

## Kế hoạch 60 phút

- **0–10 phút** — Narrative laptop 2 mic: mục tiêu vs nhiễu hướng khác.
- **10–25 phút** — Steering vector, delay-and-sum, mục tiêu MVDR.
- **25–40 phút** — Cấu trúc GSC; nhánh thích nghi hủy gì.
- **40–50 phút** — Con trỏ IVA / BSS; hybrid front-end + neural refine.
- **50–60 phút** — Bẫy, bài tập, thực tế sản phẩm (Mezon thường vẫn mono).

## Giải thích cốt lõi

### Mô hình không gian (phác far-field)

Micro $$m=1\ldots M$$, sóng phẳng hướng $$\theta$$ tần số $$f$$ có **steering vector** $$\mathbf{a}(\theta,f)$$. Phổ xếp chồng:

$$
\mathbf{y}(f,\ell)=\mathbf{a}(\theta,f)\,S(f,\ell)+\mathbf{v}(f,\ell).
$$

Beamformer: $$Z=\mathbf{w}^H\mathbf{y}$$.

### Delay-and-sum

Chọn trễ (pha) để mục tiêu cộng đồng pha rồi trung bình. Có lợi với nhiễu **không kết hợp**; nhiễu giao thoa **kết hợp** từ hướng khác chỉ bị suy giảm một phần. Baseline giảng dạy tốt.

### Cartoon MVDR

$$
\min_{\mathbf{w}}\mathbf{w}^H\mathbf{R}_{yy}\mathbf{w}\quad\text{s.t.}\quad\mathbf{w}^H\mathbf{a}=1.
$$

Nghiệm $$\mathbf{w}\propto\mathbf{R}_{yy}^{-1}\mathbf{a}$$ (đã chuẩn hóa) tạo null về phía nhiễu giao thoa. Ước lượng $$\mathbf{R}$$ bền vững là phần khó—lệch steering gây **tự triệt tiêu mục tiêu**.

### GSC

1. **Fixed beamformer (FBF)** — nhìn mục tiêu.
2. **Blocking matrix (BM)** — chiếu bỏ mục tiêu → tham chiếu “không mục tiêu”.
3. **Adaptive noise canceler** — NLMS/RLS trừ nhiễu ước từ BM khỏi đầu ra FBF.

**Vì sao thích GSC:** lọc thích nghi không ràng buộc trên tham chiếu nhiễu; dễ gắn VAD để đóng băng lúc mục tiêu nói.

### IVA (con trỏ)

**IVA** và BSS liên quan tách nguồn từ hỗn hợp đa mic không cần steering tường minh, dùng độc lập thống kê. Mức dạy:

- Coi IVA là **front-end không gian mù** cho ước lượng thô mục tiêu + nhiễu giao thoa.
- Mạng nhẹ (GTCRN-class) tinh chỉnh đầu ra IVA—pattern paper dual-channel SNR thấp.

### Hybrid + neural mono

- **GSC → DeepFilterNet2**: hủy nhiễu ego có hướng (drone), DF2 dọn nhiễu khuếch tán dư.
- **IVA → GTCRN**: tách mù rồi CRN nhỏ tinh chỉnh.
- **Chỉ DF3 mono**: mặc định đúng khi $$M=1$$ (đa số tab trình duyệt).

**Ghi chú Mezon:** đường npm / WASM thường **mono**. Đa mic là stretch—học front-end để thiết kế pipeline native tương lai mà không viết lại lõi neural.

## Checklist quyết định

- $$M=1$$ → NS mono cổ điển/neural; bỏ beamforming.
- $$M\ge 2$$, biết hướng mục tiêu, nhiễu có hướng mạnh → GSC / MVDR.
- $$M\ge 2$$, hình học không rõ / người nói chuyển động → IVA / BF thích nghi bền + neural.
- CPU rất hẹp → delay-and-sum đơn giản + NS siêu nhẹ hơn IVA đầy đủ.
- `getUserMedia` đôi khi đã downmix mono sau OS—kiểm tra số kênh thật.

## Bẫy thường gặp

- Lệch steering → **hủy mục tiêu** (nghe như NS ăn tiếng nói).
- Thích nghi GSC lúc mục tiêu nói không có VAD → rò tiếng nói vào BM.
- Coi mic stereo laptop đã hiệu chuẩn hình học.
- STFT đa kênh lệch trễ kênh (USB clock).
- Kỳ vọng beamforming xử lý **echo** không có far-end—vẫn cần AEC.

## Bài tập

1. 2 mic $$d=2\,\mathrm{cm}$$, $$f=2\,\mathrm{kHz}$$, $$c=343$$: tính trễ liên mic broadside vs 45°.
2. Vẽ GSC; đánh dấu chỗ gắn postfilter neural.
3. Brief một trang: chế độ dual-mic native tái sử dụng DF3 ONNX mono + chỉ thêm delay-and-sum.
4. Đọc một abstract hybrid (GSC+DF2 hoặc IVA+GTCRN); 3 gạch: giai đoạn cổ điển đóng góp gì vs neural.

## Đọc thêm

- Van Trees, *Optimum Array Processing*.
- Griffiths & Jim — GSC kinh điển.
- Ghi chú kỹ thuật multi-mic WebRTC / mobile.
- Hybrid khảo sát: GSC–DeepFilterNet2, IVA+GTCRN (mức tên).
- DeepFilterNet2 — tầng neural mono thường *sau* làm sạch không gian.
