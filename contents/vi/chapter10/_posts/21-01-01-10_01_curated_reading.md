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

Đọc kỹ ba nguồn gốc còn hơn đánh dấu hai mươi abstract. Mọi link bên dưới là bài báo, repo, hoặc bộ tài liệu thật dùng trong khóa. Tên khảo sát ở cuối chỉ là tên: DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet, GTCRN. Đừng bịa tiêu đề hay URL của chúng. Nếu thẻ đọc cần một sự kiện bạn chưa mở, ghi “chưa đọc” thay vì một câu nghe hợp lý.

![Đường ERB và deep filter của DeepFilterNet]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. Bức tranh bạn vẽ lại được sau khi đọc Schröter và cộng sự: STFT vào, gain ERB và deep filter, ISTFT và overlap-add ra. Mẫu thẻ bên dưới là cách chứng minh bạn đã đọc.*

## Bạn làm được gì sau bài này

Bạn chọn được ba link trong danh sách, điền thẻ bốn gạch cho mỗi link, và khớp một ví dụ đã điền đủ để người chấm thấy hình dạng. Bạn cũng giữ SI-SDR, DNSMOS, RTF, và TrackProcessor là thuật ngữ tiếng Anh trong ghi chú, kể cả khi phần văn xung quanh viết bằng tiếng Việt.

## Link được trích

Họ DeepFilterNet:

- Schröter, Escalante-B., Rosenkranz, Maier. “DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio based on Deep Filtering.” ICASSP 2022. <https://arxiv.org/abs/2110.05588>
- Schröter và cộng sự. “DeepFilterNet2: Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio.” <https://arxiv.org/abs/2205.05474> (bài Interspeech 2023 sau này trích công trình này là IWAENC 2022).
- Schröter, Escalante-B., Rosenkranz, Maier. “DeepFilterNet: Perceptually Motivated Real-Time Speech Enhancement.” Interspeech 2023. <https://arxiv.org/abs/2305.08227> — đây là trích dẫn mô hình DeepFilterNet3 mà README upstream dùng. Bảng kết quả trong bài gọi tên DeepFilterNet3; tựa bài không thêm số “3”.
- Mã và hướng dẫn archive mô hình: <https://github.com/Rikorose/DeepFilterNet>

Cầu nối giảng và runtime:

- RNNoise: <https://github.com/xiph/rnnoise> và Valin, “A Hybrid DSP/Deep Learning Approach to Real-Time Full-Band Speech Enhancement,” <https://arxiv.org/abs/1709.08243>
- WebRTC APM: <https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/>
- SpeexDSP: <https://github.com/xiph/speexdsp>
- Tài liệu ONNX Runtime: <https://onnxruntime.ai/docs/>
- tract: <https://github.com/sonos/tract>

Đánh giá và sản phẩm:

- Le Roux, Wisdom, Erdogan, Hershey. “SDR – Half-baked or Well Done?” ICASSP 2019. Dùng cho SI-SDR, không thay bài nghe.
- Dữ liệu và baseline DNS Challenge: <https://github.com/microsoft/DNS-Challenge>
- DNSMOS / DNSMOS P.835: Reddy, Gopal, Cutler, Interspeech 2021 và ICASSP 2022. Không xâm nhập. Khóa này không có ngưỡng điểm chính thức.
- Tài liệu LiveKit: <https://docs.livekit.io/>
- npm `deepfilternet3-noise-filter` 1.3.0: <https://www.npmjs.com/package/deepfilternet3-noise-filter>
- Repo sản phẩm (đọc, đừng nộp patch bài khóa vào đây): <https://github.com/mezonai/mezon-noise-suppression>

## Mẫu thẻ

Bốn gạch, không hơn. Đây là hình dạng mini-lab đòi.

```text
Source: <url>
- Claim: một câu từ abstract hoặc README, không phải đoán.
- Streaming / latency: nhân quả hay không, hop hoặc look-ahead nếu nguồn nêu, không thì "not stated".
- What it measures or ships: metric, thư viện, hoặc API. Chỉ dùng SI-SDR, DNSMOS, RTF, TrackProcessor khi nguồn thật sự bàn tới.
- What I will reuse: một việc trong harness hoặc capstone của bạn.
```

Ví dụ đã điền (đừng nộp URL này như một trong ba link trừ khi bạn còn viết hai link khác):

```text
Source: https://arxiv.org/abs/2110.05588
- Claim: DeepFilterNet tăng cường tiếng nói full-band bằng tầng gain ERB cộng deep filtering, độ phức tạp thấp.
- Streaming / latency: Khung hướng tới enhance full-band thời gian thực; hãy kiểm tra bài để lấy cửa sổ, hop, và look-ahead trước khi trích một con số mili giây.
- What it measures or ships: Bài báo cáo metric enhance xâm nhập trên tập test và mô tả bộ lọc hai tầng. Đây không phải TrackProcessor của LiveKit.
- What I will reuse: Tôi sẽ vẽ lại khối ERB cộng deep filter trong phác capstone và sẽ không mô tả npm wrapper như thể nó là thuật toán.
```

Ví dụ từ chối một số độ trễ bịa. Sự từ chối đó là một phần hình dạng. Nếu bạn mở PDF và thấy hop, bạn được thay câu “hãy kiểm tra bài” bằng con số bạn đọc, và nên nói bạn đã đọc.

## Đọc một nguồn trong một giờ

Bắt đầu từ hình, không từ mục related work. Với bài DeepFilterNet, tìm đường ERB và tổng deep filter. Với DNSMOS, xác nhận nó không xâm nhập và ghi protocol nghe mà nó được huấn luyện để bám. Với README npm, chỉ chép tên công khai: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, `setProcessor`, `setSuppressionLevel`, `setEnabled`, `assetConfig.cdnUrl`, và cách thêm tiền tố `v2/` từ ≥ 1.2.0. Với WebRTC APM hoặc SpeexDSP, ghi chúng là baseline cổ điển, không phải weight thả vào CDN Mezon.

Tên khảo sát, liệt kê để bạn nhận ra trong một buổi nói rồi dừng: DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet, GTCRN. Thẻ bịa arXiv id cho một tên trong đó là trượt bài.

## Mini-lab

Chọn **ba** URL trong danh sách trên. Viết `reading_cards.md` với ba thẻ đúng hình bốn gạch. Rồi chạy:

```python
from pathlib import Path
text = Path("reading_cards.md").read_text()
sources = text.count("Source:")
bullets = text.count("\n- ")
print("sources", sources)
print("bullets", bullets)
print("has_url", "https://" in text)
```

Đầu ra kỳ vọng:

```text
sources 3
bullets 12
has_url True
```

Mười hai gạch là ba thẻ nhân bốn gạch. Kiểu hỏng: câu claim trái với tựa bạn chưa mở; URL bịa cho GTCRN hoặc DeepFilterGAN; dùng ví dụ đã điền làm cả ba thẻ; dịch SI-SDR hoặc DNSMOS thành viết tắt khác.

## Bài tập

1. Làm ba thẻ. Có ít nhất một URL DeepFilterNet và một URL không phải bài báo (repo hoặc docs).
2. Sau khi thật sự mở arXiv:2110.05588, thêm ghi chú riêng thứ năm (không thuộc bốn gạch) với hop hoặc look-ahead bạn thấy, hoặc “tôi không thấy”.
3. Mở repo DNS Challenge đủ lâu để gọi tên một thư mục hoặc script thật sự có ở đó. Đặt tên đó vào gạch “ships”.
4. Viết một câu vì sao thẻ DNSMOS của bạn không có ngưỡng chính thức.
5. Liệt kê các tên khảo sát bạn sẽ **không** trích kèm URL.

### Gợi ý đáp án

1. Tối thiểu là một bài cộng một repo. Trang npm và docs LiveKit tính là không phải bài báo.
2. Giữ khế ước bốn gạch. Ghi chú thêm để phía dưới.
3. Đừng mô tả file bạn chưa thấy. “not stated” được phép.
4. Reddy, Gopal và Cutler cho một predictor, không cho vạch ship của Mezon. Lệch miền là kiểu hỏng.
5. DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet, GTCRN.
