---
layout: post
title: "04-04 Khảo sát kế tục: DPDFNet, DeepFilterGAN, HDF-Net"
chapter: "04"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

DPDFNet, DeepFilterGAN và HDF-Net chỉ là **con trỏ khảo sát**. Bài này không cho chúng tiêu đề paper, năm, hội nghị hay URL. Chưa mở PDF thì bạn chưa có dòng thư mục, và không được bịa. Giờ học là đặt một kế tục cạnh bộ xương ERB cộng deep filter, rồi quyết định bản triển khai DF3 có nên đổi hay không.

![Bộ xương ERB cộng deep filter mà mọi tên kế tục vẫn phải thắng trên RTF và lượt nghe]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. DPDFNet, DeepFilterGAN và HDF-Net chỉ là con trỏ khảo sát: tên trên danh sách đọc, không phải checkpoint tải được từ trang này. Cái nào cũng phải giữ hop STFT (short-time Fourier transform, biến đổi Fourier thời gian ngắn) nhân quả, state bị chặn, và RTF (real-time factor, hệ số thời gian thực) dưới 1 trên CPU đích. Bài này không nêu tiêu đề, năm hay URL cho ba tên đó.*

## Mục tiêu học tập

Bạn gắn một câu cho mỗi tên DPDFNet, DeepFilterGAN và HDF-Net; từ chối tiêu đề hoặc năm không chép từ PDF; và quyết định ship, theo dõi, hay bỏ qua từ RTF, độ phủ ONNX, và một lỗi nghe bạn tái hiện được.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao một cái tên không phải kế hoạch di cư.
- **10–25 phút** — Thẻ bốn ô, chỉ điền những gì bạn chỉ được.
- **25–40 phút** — “Dual-path”, “tầng GAN” và “filter phân cấp” tốn gì trong AudioWorklet.
- **40–50 phút** — Over-attenuation là lỗi sản phẩm, độc lập với một paper.
- **50–60 phút** — Mini-lab và vệ sinh trích dẫn.

## Giải thích cốt lõi

### Bài khảo sát được phép nhận điều gì

Bài 04-02 và 04-03 trích bảng vì các bảng đó nằm trong arXiv:2110.05588, arXiv:2205.05474 và arXiv:2305.08227. Bài này không có giấy phép đó. Bản đồ đọc của khóa dùng ba tên:

- **DPDFNet** — tên người ta tra khi phàn nàn là ngữ cảnh dài và over-attenuation, trên xương kiểu DeepFilterNet2.
- **DeepFilterGAN** — tên người ta tra khi một tầng dự đoán kiểu DeepFilterNet được theo sau bởi một tầng sinh, cố trả lại tiếng mà tầng dự đoán đã xóa.
- **HDF-Net** — tên người ta tra khi deep filtering bị tách phân cấp theo thời gian và tần số, thay vì một đầu filter.

Ba câu đó là bản đồ, không phải abstract. Chúng không cho phép một số tham số, một delta PESQ, một hình, hay một link. Tên lân cận, cũng không citation ở đây: pDeepFilterNet2 (điều kiện người nói) và DFingerNet (điều kiện vân nhiễu). Cá nhân hóa nằm ngoài phạm vi trừ khi capstone nói khác.

### Thẻ bốn ô

Với mỗi PDF bạn thực sự mở, viết đúng bốn ô:

1. **Bài toán** tác giả đo (over-attenuation, một hài mất, một số độ trễ).
2. **Cơ chế** với đúng danh từ khối in trong PDF đó.
3. **Triển khai được không:** số tham số nếu PDF in, đồ thị có nhân quả không, có ONNX hoặc RTF không.
4. **Hành động:** bỏ qua, theo dõi, hoặc prototype. Prototype cần hop, thiết bị, và một clip nghe.

Ô 3 trống vì PDF không nhắc streaming thì hành động không phải “ship”. Mô hình bảng xếp hạng có lớp hai chiều sẽ không chạy trong `process()`.

### Mỗi ý tốn gì, mà không giả vờ đã đọc PDF

Giữ mục này ở thể điều kiện. Đây là bản dịch kỹ thuật của **cái tên**, để lập ngân sách một spike. Không phải tóm tắt kết quả.

Khối **dual-path**, mẫu mà tên DPDFNet chỉ tới, chạy một chuỗi theo thời gian và một chuỗi theo tần số. Trên hop 10 ms, nhánh thời gian hoặc là state GRU (gated recurrent unit, đơn vị hồi tiếp có cổng) cố định, hoặc là chờ các hop tương lai. Bốn hop tương lai là thêm 40 ms chồng lên 40 ms đã công bố của DeepFilterNet2, thành 80 ms độ trễ. Tổng đó không phải RTF. Hai GRU cũng có thể nhân đôi p95. Over-attenuation thì không cần paper: phụ âm xát nhẹ biến mất. Một loss sàn gain là giả thuyết, không phải kết quả để trích.

**Bộ tái sinh GAN**, mẫu mà tên DeepFilterGAN chỉ tới, là mạng thứ hai trên một tầng dự đoán. Hai session ONNX, hoặc một đồ thị hợp nhất, thêm MAC và một tầng khó giữ tất định trong `process()`. Suppression trên bề mặt npm đã là số nguyên 0–100 qua `setSuppressionLevel`. Hãy vặn xuống trước khi thêm GAN.

**Deep filter phân cấp**, mẫu mà tên HDF-Net chỉ tới, vẫn tính

$$
\hat{S}(t,f)=\sum_{i} W_i(t,f)\,X(t-i+\ell,f),
$$

với hơn một đầu. Năm tap trên 96 bin đã là 480 phép nhân phức mỗi khung (04-02). Một đầu theo trục tần số nhìn được bin lân cận; đầu trong một PDF có nhân quả hay không là câu hỏi cho hình của PDF đó, không phải cho trang này.

### Phân loại sản phẩm, với hàng DF3 bạn thực sự trích được

Hàng metric DeepFilterNet3 duy nhất được trích là Voicebank+Demand trong arXiv:2305.08227: PESQ 3,17, CSIG 4,34, CBAK 3,61, COVL 3,77, STOI 0,944, cạnh DF2 ở PESQ 3,08. RTF được trích là 0,04 (DF2, i5 laptop) và 0,19 (vòng tract 2023 trên i5-8250U). Một kế tục chỉ đáng một spike nếu clip của bạn lộ lỗi mà các checkpoint đó bỏ sót, và một đồ thị nhân quả sống được trong hop 10 ms (một quantum 2,67 ms là ngân sách sai).

| Tên | Ý được lặp lại | Ship từ bài này? | Vì sao |
|-----|----------------|------------------|--------|
| DPDFNet | Ngữ cảnh dual-path; over-attenuation là chủ đề cần tra | Không | Không tiêu đề, năm, URL ở đây |
| DeepFilterGAN | Tầng dự đoán cộng tầng sinh | Không | Mạng thứ hai; RTF và tính tất định chưa biết cho đến khi đọc |
| HDF-Net | Deep filter phân cấp | Không | Như trên |
| Baseline DeepFilterNet3 | 32 ERB + filter 5 tap, citation 2023 mà README gắn | Có, như baseline khóa học | Số nằm ở 04-03 |

Front-end không gian ở Chương 03 (GSC vào enhancer mono, IVA vào enhancer mono) là một kiểu “kế tục” khác: chúng đổi số micro. Vẫn là hybrid mức khảo sát, không phải lý do bỏ DF3.

## Bẫy thường gặp

- Viết lại đồ thị ONNX sau một abstract.
- Gõ tiêu đề, năm hoặc mã arXiv từ trí nhớ cho DPDFNet, DeepFilterGAN hoặc HDF-Net.
- Cho rằng tầng GAN vừa p95 của tầng dự đoán.
- Import một op filter tùy biến mà tract hoặc ONNX Runtime WASM không có, rồi phát hiện trên luồng audio.

## Mini-lab

**Mục tiêu.** Lập thẻ bốn ô với các ô **không** được bịa để trống, và kiểm tra ghi chú không chứa citation bịa.

```bash
python3 - << 'PY'
names = ["DPDFNet", "DeepFilterGAN", "HDF-Net"]
# Fill only from a PDF you opened. Leave unknown fields as None.
cards = {
    name: {"problem": None, "mechanism": None, "params": None,
           "causal": None, "url": None, "year": None, "title": None}
    for name in names
}
for name, card in cards.items():
    missing = [k for k, v in card.items() if v is None]
    print(f"{name}: missing={missing}")
print("survey_pointers_only=True")
PY
```

**Expected**. Mỗi tên in `missing=['problem', 'mechanism', 'params', 'causal', 'url', 'year', 'title']` cho đến khi bạn thay `None` từ một PDF. Dòng cuối là `survey_pointers_only=True`.

**Failure modes**. Dán tiêu đề hoặc năm từ snippet tìm kiếm bạn chưa mở. Điền `params` bằng số không có trong PDF. Coi ô `causal` trống là “đủ nhân quả”. Gắn URL mà bài này không cung cấp.

## Bài tập

1. **Thẻ.** Sau khi tự mở từng PDF, điền bốn ô. Không mở được thì để trống và nói vậy.
2. **Over-attenuation, không cần paper.** Thu mười giây có phụ âm xát nhẹ (“see”, “fish”), mức thoải mái và mức nhỏ, qua đường DF3 ở suppression 30 và 90. Viết khác biệt nghe được trong hai câu.
3. **Ngân sách độ trễ.** Một chunk dual-path chờ 4 hop 10 ms, và độ trễ đã công bố của DeepFilterNet2 là 40 ms. Tổng là bao nhiêu, và tổng đó có phải RTF không?
4. **Ghi nhớ.** Trong 150 từ, nói với tech lead ở lại baseline DF3 hoặc xếp một spike đọc. Chỉ được trích arXiv:2110.05588, arXiv:2205.05474 và arXiv:2305.08227.

### Gợi ý đáp án

1. Thẻ trống điểm cao hơn tiêu đề bịa. Chữ cơ chế phải dùng danh từ của PDF.
2. Bạn nghe phụ âm bị xóa và đuôi “khô” hoặc bơm, không nghe một số MOS. Suppression là 0–100 qua `setSuppressionLevel`, không phải dB của paper.
3. $$40+4\times 10=80$$ ms độ trễ thuật toán nếu chunk là look-ahead thêm. RTF là thời gian tường trên thời gian audio, có thể 0,2 hoặc 1,4 độc lập với 80 ms đó.
4. Baseline bênh được là hàng DF3 của citation 2023 và các số 40 ms / RTF đã công bố. Spike là bài đọc cộng một smoke test ONNX nhân quả, không phải viết lại.

## Đọc thêm

- Bài 04-02 và 04-03, trích [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [arXiv:2205.05474](https://arxiv.org/abs/2205.05474) và [arXiv:2305.08227](https://arxiv.org/abs/2305.08227).
- PDF bạn tự kiếm cho DPDFNet, DeepFilterGAN và HDF-Net. Trang này cố ý không có link cho chúng.
- Chương 05 cho ràng buộc RTF và AudioWorklet mà mọi kế tục vẫn phải đạt.
