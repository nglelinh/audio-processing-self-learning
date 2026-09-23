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

DeepFilterNet2 và DeepFilterNet3 giữ tách ERB cộng deep filter, và đổi loss train, lượng đệm thời gian, một post-filter, cùng một cổng SNR. Bài này chỉ dùng số in trong arXiv:2205.05474 và arXiv:2305.08227. Không bịa tên khối, và không nhận gói npm khớp bit với các checkpoint đó.

![Cùng bộ xương ERB cộng deep filter qua các thế hệ DeepFilterNet]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. Bộ xương giữ nguyên: 32 gain ERB (equivalent rectangular bandwidth, băng thông chữ nhật tương đương) cho đường bao, rồi filter phức 5 tap trên bin thấp của STFT (short-time Fourier transform, biến đổi Fourier thời gian ngắn). Đổi đã công bố giữa các phiên bản là loss và dữ liệu (STFT đa phân giải, DNS4, post-filter), ít đệm thời gian hơn trong mạng, và một cổng SNR có thể bỏ một tầng. Tên module bạn chưa đọc trong paper không thuộc chú thích này.*

## Mục tiêu học tập

Bạn nêu DeepFilterNet2 đổi gì so với mô hình ICASSP 2022 (đệm runtime, loss đa phân giải, post-filter, RTF đã báo cáo), paper Interspeech 2023 thêm cổng SNR cục bộ và một hàng DeepFilterNet3 trên Voicebank+Demand ra sao, và `deepfilternet3-noise-filter` thuộc họ đó mà không phải nguồn sự thật thứ hai cho trọng số.

## Kế hoạch 60 phút

- **0–10 phút** — Nhắc: 32 băng ERB, 5 tap, 20 ms / 10 ms, độ trễ 40 ms.
- **10–25 phút** — DF2: RTF 0,04 đến từ đâu, và không đến từ đâu.
- **25–40 phút** — Cổng 2023 và hàng DF3 trên bảng metric.
- **40–50 phút** — Lệch RIR, export ONNX, bề mặt npm.
- **50–60 phút** — Mini-lab, bài tập.

## Giải thích cốt lõi

### Cùng ADN, checkpoint khác

Cả ba thế hệ nhắm 48 kHz, cửa sổ 20 ms, chồng 50%, 32 băng ERB, và filter 5 tap tới khoảng 5 kHz, với look-ahead hai khung được nêu là độ trễ **40 ms**. Hãy ghim một file trọng số, không ghim chữ “DeepFilterNet”. Checkpoint DF2 trong config DF3 là lỗi shape hoặc lỗi âm sắc.

### DeepFilterNet2 — arXiv:2205.05474

DeepFilterNet2, “Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio” (IWAENC 2022, arXiv:2205.05474), giữ STFT đó. Những đổi làm chất lượng và tốc độ dịch chuyển:

- **Loss.** Warmup 3 epoch rồi cosine decay, cập nhật mỗi bước. Loss phổ đa phân giải sau STFT ngược dùng cửa sổ 5, 10, 20 và 40 ms với nén $$c=0{,}3$$. Hạng $$\alpha$$ của ICASSP bị bỏ; filter 5 tap có thể nghỉ bằng cách đặt phần thực của tap hiện tại bằng 1 và các tap kia bằng 0.
- **Dữ liệu.** DNS4 tiếng Anh, cộng đường méo: target giữ ít vang hơn hỗn hợp, và tiếng bị clip được dựng lại. Đó là cơ chế cho phòng họp, không phải bảo đảm cho phòng của bạn.
- **Ít đệm thời gian hơn.** Kernel thời gian co từ $$2\times 3$$ xuống $$1\times 3$$, trừ một lớp vào nhân quả $$3\times 3$$. Hidden của GRU (gated recurrent unit, đơn vị hồi tiếp có cổng) là 256. Linear có nhóm thành một phép nhân ma trận. Ngữ cảnh thêm là một vòng activation; trên CPU nhỏ, lưu lượng đó át số MAC.
- **Post-filter.** Một biến dạng sin trên gain ERB, $$G \leftarrow G\sin(\pi G/2)$$, giảm mạnh hơn các băng nhiễu. Bước hai trộn một độ mạnh $$\beta$$. Đừng bịa $$\beta$$ mặc định; `--pf` bật post-filter đã công bố.
- **Cùng CPU, RTF khác.** Trên Voicebank+Demand, Core i5-8250U: hàng ICASSP là 1,778 M tham số, 0,348 GMAC, RTF 0,11, PESQ 2,81. Hàng DF2 đã giản là 2,306 M, 0,356 GMAC, **RTF 0,04**, PESQ 3,08 (CSIG 4,30, CBAK 3,40, COVL 3,699, STOI 0,9429). GMAC gần như phẳng; RTF giảm vì kernel và GRU đổi. Hàng post-filter vẫn RTF 0,04 và PESQ **3,03**. PESQ giảm. Chỉ nhìn PESQ sẽ revert một thay đổi làm vì cảm nhận.

Abstract còn nói tốc độ này đủ cho Raspberry Pi 4. Đó vẫn không phải số nhiệt của điện thoại.

### Paper 2023 và DeepFilterNet3 — arXiv:2305.08227

“DeepFilterNet: Perceptually Motivated Real-Time Speech Enhancement” (Interspeech 2023, arXiv:2305.08227) nhắc lại framework và là citation mà README dự án gắn với mô hình **DeepFilterNet3**. Dùng đúng sự gắn đó. Đừng bịa một tiêu đề DF3 thứ hai.

Luật xử lý của demo, làm được mà không cần tên module mới:

- 48 kHz, cửa sổ 20 ms, hop 10 ms, look-ahead 2 khung, độ trễ thuật toán **40 ms**.
- 32 gain ERB cho đường bao.
- Filter phức $$N=5$$ trên **96 bin** thấp nhất (4,8 kHz). Bin cao hơn giữ gain ERB.
- Encoder còn dự đoán SNR cục bộ $$\xi\in[-15,35]$$ dB. Nếu $$\xi<-10$$ dB, cả hai decoder tắt và khung là im lặng. Nếu $$\xi>20$$ dB, decoder deep filter tắt. Ngược lại cả hai tầng chạy.

Tiếng nói vừa dưới −10 dB thành im lặng số. Tiếng nói trên 20 dB không được tầng hài, nên một hum có thể còn giữa các partial. Vòng tract trong paper đó báo **RTF 0,19** trên một luồng i5-8250U. **0,04** của DF2 là binary khác. Đừng lấy trung bình, và đừng gọi số nào là RTF điện thoại.

Hàng Voicebank+Demand ghi DeepFilterNet3 là PESQ 3,17, CSIG 4,34, CBAK 3,61, COVL 3,77, STOI 0,944, so với DF2 ở PESQ 3,08 và bản gốc 2,81. Một tập test.

### Wrapper, ONNX, phòng

`deepfilternet3-noise-filter` 1.3.0 ([mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression)) chạy ONNX/WASM trong AudioWorklet: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, suppression 0–100 qua `setSuppressionLevel`. Đừng nhận khớp bit với CLI hay với bảng paper. Wrapper đổi hop, look-ahead hoặc sample rate là một hệ khác.

Export là PyTorch → ONNX → ONNX Runtime, WASM hoặc tract → AudioWorklet hoặc callback native. State GRU phải là đầu vào và đầu ra của đồ thị. Trục động nuốt cả file là mô hình offline. RT60 mô phỏng của paper đầu dừng ở 1 s. Over-suppression trong phòng thật thường là lỗ dữ liệu đó. Hãy nghe (Chương 08) trước khi phóng to mạng.

## Bẫy thường gặp

- Nạp trọng số DF2 với ngưỡng cổng DF3, hoặc ngược lại.
- Trích PESQ 3,17 như “MOS sản phẩm”.
- Coi RTF 0,04 hoặc 0,19 trên i5 là ngân sách laptop không quạt hoặc điện thoại.
- Bật `--pf`, thấy PESQ tụt từ 3,08 xuống 3,03, rồi revert một đổi cảm nhận bạn chưa nghe.
- Cho rằng `setSuppressionLevel(100)` tái hiện độ suy giảm đầy đủ của paper. Đó là núm sản phẩm, thang 0–100, không phải số dB trong paper.

## Mini-lab

**Mục tiêu.** Chạy CLI hai lần nếu có trọng số, một lần với cờ post-filter, và luôn tính biến dạng sin không thứ nguyên trên bốn gain để lab chạy offline.

```bash
deepFilter --output-dir out/noisy/ noisy.wav
deepFilter --pf --output-dir out/pf/ noisy.wav
python3 - << 'PY'
import numpy as np
G = np.array([0.0, 0.2, 0.5, 1.0])
Gp = G * np.sin(0.5 * np.pi * G)
np.set_printoptions(precision=6, suppress=True)
print(Gp)
PY
```

**Expected**. Khi có trọng số và đầu vào 48 kHz: hai wav đã tăng cường, và log có timing hoặc RTF. Đừng kỳ vọng hai wav trùng nhau. NumPy luôn in `[0. 0.061803 0.353553 1.]`. Gain 0,2 bị kéo xuống mạnh hơn gain 1 — đó là over-attenuation mà post-filter nhằm tới. Bước thứ hai, có trọng số $$\beta$$, cố ý không nằm trong script này.

**Failure modes**. Không có mạng để tải trọng số: giữ kết quả NumPy và ghi lỗi CLI. File không phải 48 kHz vào binary Rust `deep-filter`. So RTF log laptop với điện thoại. Nhận wav `--pf` khớp `setSuppressionLevel` của gói npm.

## Bài tập

1. **Ba hàng.** Với mô hình ICASSP 2022, DeepFilterNet2, và hàng DeepFilterNet3, liệt kê hội nghị, mã arXiv, một đổi cơ chế, và một số bạn chịu bênh.
2. **Cổng.** SNR cục bộ là −12 dB, rồi +25 dB, rồi +5 dB. Tầng nào chạy?
3. **Đọc RTF.** Bảng DF2 nói GMAC 0,356 và RTF 0,04; hàng trước nói GMAC 0,348 và RTF 0,11. Vì sao hàng MAC trông chậm hơn lại nhanh hơn?
4. **Gói.** Nêu hai ký hiệu tác giả app thấy trên `deepfilternet3-noise-filter`, và hai sự thật về hop và state mà gói không miễn cho bạn.

### Gợi ý đáp án

1. ICASSP 2022, 2110.05588: hai tầng ERB + deep filter; PESQ 2,81 / 1,778 M. IWAENC 2022, 2205.05474: ít kernel thời gian hơn, loss đa phân giải, post-filter; RTF 0,04 và PESQ 3,08 trên bảng i5 đó. Interspeech 2023, 2305.08227, README gắn citation này với DF3: cổng SNR và hàng bảng PESQ 3,17. Mọi PESQ là Voicebank+Demand, không phải tập sản phẩm của bạn.
2. −12 dB: cả hai decoder tắt, khung im. +25 dB: chỉ tầng ERB. +5 dB: cả hai tầng.
3. Bảng MAC bỏ qua lưu lượng bộ nhớ. Kernel thời gian nhỏ hơn của DF2 đụng ít activation đệm hơn mỗi hop, nên RTF từ 0,11 xuống 0,04 trong khi GMAC ở quanh 0,35.
4. `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, và `setSuppressionLevel` (0–100) là bề mặt. Bạn vẫn sở hữu hop 10 ms so với quantum 128 mẫu, và state GRU/STFT xuyên callback. Không có cam kết khớp bit với CLI.

## Đọc thêm

- Schröter et al., DeepFilterNet2, IWAENC 2022, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474).
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227), citation DeepFilterNet3 của README.
- [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) cho checkpoint và `deepFilter`.
- [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) chỉ cho phần đóng gói AudioWorklet.
