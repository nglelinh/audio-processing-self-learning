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

Đọc sâu ba tài liệu gốc có giá trị hơn nhiều so với việc lưu hai mươi bài tóm tắt mà không mở ra xem. Mọi liên kết dưới đây đều là bài báo, kho mã nguồn hoặc bộ tài liệu chính thức được dùng xuyên suốt khóa học. Các tên mô hình khảo sát ở cuối danh sách — gồm DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet và GTCRN — chỉ mang tính điểm tên nhận diện; tuyệt đối không tự bịa tiêu đề hay URL cho chúng. Nếu thẻ đọc cần một chi tiết mà bạn chưa trực tiếp mở nguồn để kiểm tra, hãy ghi rõ “chưa đọc” thay vì suy diễn một câu nghe có vẻ hợp lý.

![Đường ERB và deep filter của DeepFilterNet]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. Sơ đồ khối mà bạn cần tự vẽ lại được sau khi đọc các công trình của Schröter và cộng sự: STFT đầu vào → nhánh hệ số ERB và bộ lọc sâu (deep filter) → ISTFT và cộng chồng lấp (overlap-add) ở đầu ra. Mẫu thẻ đọc bên dưới là cách chứng minh bạn đã đọc tài liệu gốc.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ chọn được 3 liên kết từ danh mục chuẩn, hoàn thiện thẻ đọc gồm đúng 4 gạch đầu dòng cho mỗi nguồn theo đúng định dạng kiểm tra, đồng thời giữ nguyên các thuật ngữ tiếng Anh cốt lõi (`SI-SDR`, `DNSMOS`, `RTF`, `TrackProcessor`) trong ghi chú ngay cả khi phần diễn giải viết bằng tiếng Việt.

## Danh mục tài liệu trích dẫn

**Họ mô hình DeepFilterNet:**

- Schröter, Escalante-B., Rosenkranz, Maier. *“DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio based on Deep Filtering.”* ICASSP 2022. <https://arxiv.org/abs/2110.05588>
- Schröter và cộng sự. *“DeepFilterNet2: Towards Real-Time Speech Enhancement on Embedded Devices for Full-Band Audio.”* <https://arxiv.org/abs/2205.05474> (bài báo Interspeech 2023 sau này trích dẫn công trình này theo hội nghị IWAENC 2022).
- Schröter, Escalante-B., Rosenkranz, Maier. *“DeepFilterNet: Perceptually Motivated Real-Time Speech Enhancement.”* Interspeech 2023. <https://arxiv.org/abs/2305.08227> — đây là trích dẫn của mô hình DeepFilterNet3 mà README kho gốc sử dụng (các bảng kết quả bên trong gọi tên DeepFilterNet3 dù tiêu đề bài báo không thêm số “3”).
- Mã nguồn và hướng dẫn gói trọng số mô hình: <https://github.com/Rikorose/DeepFilterNet>

**Các mô hình nền tảng và runtime suy luận:**

- RNNoise: <https://github.com/xiph/rnnoise> và Valin, *“A Hybrid DSP/Deep Learning Approach to Real-Time Full-Band Speech Enhancement,”* <https://arxiv.org/abs/1709.08243>
- WebRTC APM: <https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/>
- SpeexDSP: <https://github.com/xiph/speexdsp>
- Tài liệu ONNX Runtime: <https://onnxruntime.ai/docs/>
- Thư viện suy luận Rust `tract`: <https://github.com/sonos/tract>

**Đánh giá chất lượng và tích hợp sản phẩm:**

- Le Roux, Wisdom, Erdogan, Hershey. *“SDR – Half-baked or Well Done?”* ICASSP 2019 — nền tảng của SI-SDR (không thay thế kiểm thử lắng nghe).
- Dữ liệu và mô hình nền DNS Challenge: <https://github.com/microsoft/DNS-Challenge>
- DNSMOS / DNSMOS P.835: Reddy, Gopal, Cutler (Interspeech 2021 và ICASSP 2022) — bộ dự đoán không xâm nhập; khóa học không đặt ngưỡng điểm đạt chính thức.
- Tài liệu LiveKit: <https://docs.livekit.io/>
- Gói npm `deepfilternet3-noise-filter` 1.3.0: <https://www.npmjs.com/package/deepfilternet3-noise-filter>
- Kho mã nguồn sản phẩm (chỉ dùng để đọc tham khảo, không gửi bản vá bài tập vào đây): <https://github.com/mezonai/mezon-noise-suppression>

## Mẫu thẻ đọc tài liệu

Mỗi thẻ chỉ gồm đúng 4 gạch đầu dòng theo đúng cấu trúc yêu cầu của mini-lab:

```text
Source: <url>
- Claim: một câu từ abstract hoặc README, không phải đoán.
- Streaming / latency: nhân quả hay không, hop hoặc look-ahead nếu nguồn nêu, không thì "not stated".
- What it measures or ships: metric, thư viện, hoặc API. Chỉ dùng SI-SDR, DNSMOS, RTF, TrackProcessor khi nguồn thật sự bàn tới.
- What I will reuse: một việc trong harness hoặc capstone của bạn.
```

Ví dụ một thẻ đọc đã điền hoàn chỉnh (không nộp lại nguyên văn URL này làm một trong 3 thẻ trừ khi bạn tự viết thêm 2 nguồn khác):

```text
Source: https://arxiv.org/abs/2110.05588
- Claim: DeepFilterNet tăng cường tiếng nói full-band bằng tầng gain ERB cộng deep filtering, độ phức tạp thấp.
- Streaming / latency: Khung hướng tới enhance full-band thời gian thực; hãy kiểm tra bài để lấy cửa sổ, hop, và look-ahead trước khi trích một con số mili giây.
- What it measures or ships: Bài báo cáo metric enhance xâm nhập trên tập test và mô tả bộ lọc hai tầng. Đây không phải TrackProcessor của LiveKit.
- What I will reuse: Tôi sẽ vẽ lại khối ERB cộng deep filter trong phác capstone và sẽ không mô tả npm wrapper như thể nó là thuật toán.
```

Lưu ý rằng ví dụ trên cố tình không tự điền một con số độ trễ chưa kiểm chứng — đây là một phần quan trọng của tính kỷ luật khoa học. Khi bạn đã mở tệp PDF và xác nhận chính xác độ dài hop, bạn có thể thay câu lưu ý bằng con số thực tế đọc được.

## Cách đọc hiệu quả một tài liệu trong một giờ

Hãy bắt đầu từ các sơ đồ khối thay vì đọc mục tài liệu liên quan (related work) trước. Với các bài báo DeepFilterNet, hãy tìm ngay nhánh tính hệ số ERB và phép lọc sâu đa khung. Với DNSMOS, cần xác nhận bản chất không xâm nhập và ghi nhận giao thức nghe thử mà mô hình được huấn luyện để bám theo. Với README gói npm, chỉ ghi nhận các tên giao diện công khai (`DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, `setProcessor`, `setSuppressionLevel`, `setEnabled`, `assetConfig.cdnUrl` và quy tắc nối tiền tố `v2/` từ bản ≥ 1.2.0). Với WebRTC APM hay SpeexDSP, hãy xếp chúng vào nhóm nền tảng DSP cổ điển, không phải tệp trọng số để thả vào CDN Mezon.

Nhắc lại danh sách các tên khảo sát chỉ dùng để nhận diện khi đọc thêm: DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet và GTCRN. Thẻ đọc nào tự bịa mã arXiv cho các tên này sẽ bị đánh trượt.

## Mini-lab

Chọn **3** URL trong danh sách chính thức phía trên, soạn tệp `reading_cards.md` gồm 3 thẻ đúng cấu trúc 4 gạch đầu dòng mỗi thẻ, rồi chạy script kiểm tra:

```python
from pathlib import Path
text = Path("reading_cards.md").read_text()
sources = text.count("Source:")
bullets = text.count("\n- ")
print("sources", sources)
print("bullets", bullets)
print("has_url", "https://" in text)
```

**Kết quả kỳ vọng**

```text
sources 3
bullets 12
has_url True
```

Tổng cộng 12 gạch đầu dòng tương ứng 3 thẻ nhân 4 mục.

**Lỗi thường gặp.** Viết phần `Claim` mâu thuẫn với tiêu đề bài báo do chưa mở đọc; tự bịa URL cho GTCRN hoặc DeepFilterGAN; sao chép nguyên ví dụ mẫu làm cả 3 thẻ; hoặc tự ý đổi chữ viết tắt chuẩn của `SI-SDR` và `DNSMOS`.

## Bài tập

1. Hoàn thiện 3 thẻ đọc, trong đó có ít nhất một bài báo thuộc họ DeepFilterNet và ít nhất một nguồn không phải bài báo (kho mã nguồn hoặc tài liệu kỹ thuật).
2. Sau khi mở trực tiếp `arXiv:2110.05588`, thêm một dòng ghi chú riêng bên dưới thẻ (nằm ngoài 4 gạch đầu dòng chuẩn) ghi rõ độ dài hop và look-ahead bạn tìm thấy, hoặc ghi trung thực là chưa tìm thấy.
3. Mở kho DNS Challenge đủ lâu để gọi tên một thư mục hoặc script có thật trong kho đó rồi đưa vào mục `What it measures or ships`.
4. Viết một câu giải thích vì sao thẻ đọc về DNSMOS không ghi ngưỡng điểm đậu chính thức.
5. Liệt kê lại danh sách các tên mô hình khảo sát mà bạn không được phép gắn URL tự bịa.

### Gợi ý đáp án

1. Tối thiểu gồm 1 bài báo khoa học và 1 kho mã nguồn hoặc trang tài liệu (trang npm và tài liệu LiveKit đều tính là nguồn ngoài bài báo).
2. Giữ đúng quy ước 4 gạch đầu dòng bên trong thẻ; mọi ghi chú mở rộng đặt riêng phía dưới.
3. Không mô tả tệp chưa trực tiếp kiểm tra; ghi `"not stated"` khi nguồn không đề cập.
4. Công trình của Reddy, Gopal và Cutler xây dựng bộ dự đoán chất lượng chứ không định nghĩa ngưỡng phát hành cho Mezon, đặc biệt khi có rủi ro lệch miền dữ liệu.
5. DPDFNet, DeepFilterGAN, HDF-Net, FastEnhancer, μNet, Fast-ULCNet và GTCRN.

## Video tham khảo

- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. **Xem trước.** Xem song song với bài báo DeepFilterNet trong danh sách đọc để nắm nhanh sơ đồ khối trước khi đọc kỹ PDF.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Phần trình bày về DNS Challenge và DNSMOS khớp trực tiếp với nhóm tài liệu đánh giá chất lượng.
- [But what is the Fourier Transform?  A visual introduction.](https://www.youtube.com/watch?v=spUNpyF58BY) — 3Blue1Brown, tiếng Anh. Cung cấp trực giác hình học cho biến đổi Fourier trước khi đi sâu vào các công thức DSP.
