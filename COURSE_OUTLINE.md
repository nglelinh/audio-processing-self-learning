# Course Outline — Audio Noise Suppression Self-Learning

**EN:** Real-Time Audio Noise Suppression: From DSP to DeepFilterNet  
**VI:** Khử nhiễu âm thanh thời gian thực: Từ DSP đến DeepFilterNet  
**Audience:** Vietnamese software engineers (intermediate); Fourier & audio DSP taught in depth from scratch.  
**Author:** Nguyen Le Linh `<nglelinh@gmail.com>`  
**Product alignment:** `mezonai/mezon-noise-suppression` (npm `deepfilternet3-noise-filter`); local `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.  
**Site:** `https://nglelinh.github.io/audio-processing-self-learning/`  

---

## Chapter map (00–10)

| # | EN | VI | Lessons (EN) |
|---|----|----|--------------|
| 00 | Introduction & problem framing | Giới thiệu & định khung bài toán | 4 |
| 01 | Fourier & discrete transforms (deep) | Fourier & biến đổi rời rạc (sâu) | 7 |
| 02 | Audio processing pipeline | Pipeline xử lý âm thanh | 7 |
| 03 | Classical NS / AEC / beamforming | NS / AEC / beamforming cổ điển | 5 |
| 04 | Neural SE & DeepFilterNet family | SE neural & họ DeepFilterNet | 6 |
| 05 | Real-time constraints | Ràng buộc thời gian thực | 4 |
| 06 | On-device inference | Suy luận trên thiết bị | 4 |
| 07 | Product integration | Tích hợp sản phẩm | 4 |
| 08 | Evaluation | Đánh giá | 4 |
| 09 | Capstone: Mezon noise suppression | Capstone: Mezon noise suppression | 5 |
| 10 | References & further paths | Tài liệu tham khảo & hướng đi tiếp | 3 |

**Total:** 53 EN lessons paired with 53 VI lessons (106 files). These are full self-study articles (objectives, teaching prose, figures, mini-labs, exercises with hints), not stubs.

## Chapter 00: Introduction & problem framing / Giới thiệu & định khung bài toán

- **EN** 00-01 Why real-time noise suppression matters  
  **VI** 00-01 Vì sao khử nhiễu thời gian thực quan trọng

- **EN** 00-02 Noise types and speech mixture models  
  **VI** 00-02 Các loại nhiễu và mô hình hỗn hợp tiếng nói

- **EN** 00-03 Real-time vs offline enhancement  
  **VI** 00-03 Khử nhiễu thời gian thực và offline

- **EN** 00-04 Course map and Mezon product context  
  **VI** 00-04 Lộ trình khóa học và ngữ cảnh sản phẩm Mezon


## Chapter 01: Fourier & discrete transforms (deep) / Fourier & biến đổi rời rạc (sâu)

- **EN** 01-01 Continuous Fourier transform intuition  
  **VI** 01-01 Trực giác biến đổi Fourier liên tục

- **EN** 01-02 Sampling, aliasing, and Nyquist  
  **VI** 01-02 Lấy mẫu, aliasing và Nyquist

- **EN** 01-03 DTFT, DFS, and DFT relationships  
  **VI** 01-03 Hệ thống quan hệ DTFT, DFS và DFT

- **EN** 01-04 DFT as matrix / orthonormal basis  
  **VI** 01-04 DFT như ma trận / cơ sở trực chuẩn

- **EN** 01-05 FFT algorithms and complexity  
  **VI** 01-05 Thuật toán FFT và độ phức tạp

- **EN** 01-06 FFT in real-time framed audio  
  **VI** 01-06 FFT trong audio khung thời gian thực

- **EN** 01-07 Fourier pitfalls checklist for engineers  
  **VI** 01-07 Checklist bẫy Fourier cho kỹ sư


## Chapter 02: Audio processing pipeline / Pipeline xử lý âm thanh

- **EN** 02-01 PCM, sample rates, and channels  
  **VI** 02-01 PCM, tốc độ mẫu và kênh

- **EN** 02-02 Frames, hop size, and overlap-add  
  **VI** 02-02 Frame, hop và overlap-add

- **EN** 02-03 Windowing and spectral leakage  
  **VI** 02-03 Cửa sổ hóa và rò phổ

- **EN** 02-04 STFT / ISTFT for speech (DeepFilterNet tie-in)  
  **VI** 02-04 STFT / ISTFT cho tiếng nói (gắn DeepFilterNet)

- **EN** 02-05 Filtering in time vs frequency  
  **VI** 02-05 Lọc miền thời gian vs miền tần số

- **EN** 02-06 Spectrograms: reading speech and noise  
  **VI** 02-06 Spectrogram: đọc tiếng nói và nhiễu

- **EN** 02-07 Pipeline latency–quality tradeoffs  
  **VI** 02-07 Tradeoff độ trễ–chất lượng của pipeline


## Chapter 03: Classical NS / AEC / beamforming / NS / AEC / beamforming cổ điển

- **EN** 03-01 Spectral subtraction  
  **VI** 03-01 Spectral subtraction

- **EN** 03-02 Wiener filtering for speech  
  **VI** 03-02 Bộ lọc Wiener cho tiếng nói

- **EN** 03-03 Kalman-style tracking (intuition)  
  **VI** 03-03 Theo dõi kiểu Kalman (trực giác)

- **EN** 03-04 AEC context and WebRTC APM  
  **VI** 03-04 Ngữ cảnh AEC và WebRTC APM

- **EN** 03-05 Beamforming / GSC / IVA as front-ends  
  **VI** 03-05 Beamforming / GSC / IVA như front-end


## Chapter 04: Neural SE & DeepFilterNet family / SE neural & họ DeepFilterNet

- **EN** 04-01 Neural speech enhancement overview  
  **VI** 04-01 Tổng quan tăng cường tiếng nói bằng mạng nơ-ron

- **EN** 04-02 DeepFilterNet: deep filtering idea  
  **VI** 04-02 DeepFilterNet: ý tưởng deep filtering

- **EN** 04-03 DeepFilterNet2 and DeepFilterNet3  
  **VI** 04-03 DeepFilterNet2 và DeepFilterNet3

- **EN** 04-04 Successors survey: DPDFNet, DeepFilterGAN, HDF-Net  
  **VI** 04-04 Khảo sát kế tục: DPDFNet, DeepFilterGAN, HDF-Net

- **EN** 04-05 Ultra-light streaming models  
  **VI** 04-05 Mô hình streaming siêu nhẹ

- **EN** 04-06 RNNoise as a teaching bridge  
  **VI** 04-06 RNNoise như cầu nối giảng dạy


## Chapter 05: Real-time constraints / Ràng buộc thời gian thực

- **EN** 05-01 RTF and device budgets  
  **VI** 05-01 RTF và ngân sách thiết bị

- **EN** 05-02 AudioWorklet and audio callbacks  
  **VI** 05-02 AudioWorklet và audio callback

- **EN** 05-03 Ring buffers and underruns  
  **VI** 05-03 Ring buffer và underrun

- **EN** 05-04 Streaming model state  
  **VI** 05-04 Trạng thái mô hình streaming


## Chapter 06: On-device inference / Suy luận trên thiết bị

- **EN** 06-01 ONNX, tract, and ORT  
  **VI** 06-01 ONNX, tract và ORT

- **EN** 06-02 Quantization for speech models  
  **VI** 06-02 Lượng tử hóa cho mô hình tiếng nói

- **EN** 06-03 SIMD and WASM deployment  
  **VI** 06-03 SIMD và triển khai WASM

- **EN** 06-04 Packaging models for products  
  **VI** 06-04 Đóng gói mô hình cho sản phẩm


## Chapter 07: Product integration / Tích hợp sản phẩm

- **EN** 07-01 WebRTC insertion points  
  **VI** 07-01 Điểm chèn trong WebRTC

- **EN** 07-02 LiveKit TrackProcessor patterns  
  **VI** 07-02 Pattern TrackProcessor của LiveKit

- **EN** 07-03 CDN model loading  
  **VI** 07-03 Tải mô hình qua CDN

- **EN** 07-04 Mezon npm surface (techniques, not only wrapper)  
  **VI** 07-04 Bề mặt npm Mezon (kỹ thuật, không chỉ wrapper)


## Chapter 08: Evaluation / Đánh giá

- **EN** 08-01 SI-SDR and related intrusive metrics  
  **VI** 08-01 SI-SDR và metric xâm nhập liên quan

- **EN** 08-02 DNSMOS and non-intrusive MOS predictors  
  **VI** 08-02 DNSMOS và bộ dự đoán MOS không xâm nhập

- **EN** 08-03 Listening tests  
  **VI** 08-03 Kiểm thử lắng nghe

- **EN** 08-04 DNS Challenge-style metric suites  
  **VI** 08-04 Bộ metric kiểu DNS Challenge


## Chapter 09: Capstone: Mezon noise suppression / Capstone: Mezon noise suppression

- **EN** 09-01 Mezon NS architecture tour  
  **VI** 09-01 Tour kiến trúc Mezon NS

- **EN** 09-02 Techniques beyond the npm wrapper  
  **VI** 09-02 Kỹ thuật vượt qua npm wrapper

- **EN** 09-03 Optional Rust native (df-core) path  
  **VI** 09-03 Lộ trình Rust native (df-core) tùy chọn

- **EN** 09-04 Capstone project brief  
  **VI** 09-04 Đề bài capstone

- **EN** 09-05 Capstone checklist & demo day  
  **VI** 09-05 Checklist capstone & demo day


## Chapter 10: References & further paths / Tài liệu tham khảo & hướng đi tiếp

- **EN** 10-01 Curated reading list  
  **VI** 10-01 Danh mục đọc có chọn lọc

- **EN** 10-02 Further learning paths  
  **VI** 10-02 Hướng học tiếp

- **EN** 10-03 Maintaining this course  
  **VI** 10-03 Duy trì khóa học này


## Advisor notes

- Chapters **01** and **02** stay heavy (7 lessons each). Do not collapse them into a light “DSP mention.”
- Cite only well-known sources: DeepFilterNet / DeepFilterNet2 / DeepFilterNet3, DNS Challenge, WebRTC APM, SpeexDSP, RNNoise, SI-SDR, DNSMOS, ORT/tract; named survey pointers only (DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet, GTCRN).
- Teach techniques. The npm package `deepfilternet3-noise-filter` **1.3.0** is a vehicle: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor` (LiveKit `TrackProcessor`), `setSuppressionLevel` (0–100), optional `assetConfig.cdnUrl` (example `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`). For package ≥ 1.2.0, including 1.3.0, the client adds a `v2/` prefix itself (`{cdnUrl}/v2/pkg/df_bg.wasm`, `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`). Do not put `v2` inside `cdnUrl`. LiveKit entry points are `DeepFilterNoiseFilterProcessor` and `DeepFilterNoiseFilter` (`audioTrack.setProcessor`). The non-LiveKit core is `DeepFilterNet3Core` (`initialize`, `createAudioWorkletNode`, `setSuppressionLevel`, `destroy`). Examples use sample rate 48000. The model line is Rikorose DeepFilterNet.
- Figures: `img/generated/*.png`, embedded as `{{ site.imgurl }}/generated/<name>.png`. `imgurl` is `/audio-processing-self-learning/img`.
- Local preview: `bundle install && bundle exec jekyll serve` → http://127.0.0.1:4000/audio-processing-self-learning/
- Do not modify `mezon-noise-suppression` product code from course tasks. Instructor checkout (optional): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.
