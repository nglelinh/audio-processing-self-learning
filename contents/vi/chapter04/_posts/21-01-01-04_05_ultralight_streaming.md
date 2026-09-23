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

Một số sản phẩm không tiêu được ngân sách laptop của DeepFilterNet2. Các tên **GTCRN**, **FastEnhancer**, **μNet** và **Fast-ULCNet** là từ vựng shortlist cho enhancer streaming siêu nhẹ. Bài này **không** gắn tiêu đề paper, năm hay URL cho chúng. Bài dạy phép đo quyết định shortlist: bảng MAC và RTF (real-time factor, hệ số thời gian thực) thời gian tường tách nhau, và state GRU (gated recurrent unit, đơn vị hồi tiếp có cổng) chạy một giờ là một lỗi khác với hop chậm.

![RTF đối chiếu quantum AudioWorklet: thời gian tường mỗi khối audio, không phải bảng MAC]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Figure. RTF là thời gian tường chia thời gian audio. Một quantum AudioWorklet (luồng render của Web Audio) 128 mẫu ở 48 kHz dài khoảng 2,67 ms. Mô hình siêu nhẹ là mô hình có p95 thời gian tường vừa hop bạn thực sự chạy, trên CPU bạn thực sự ship. GTCRN, FastEnhancer, μNet và Fast-ULCNet chỉ là tên trên hình này — không paper, năm hay URL.*

## Mục tiêu học tập

Bạn giải thích, với bảng DeepFilterNet2 làm ví dụ tính được, vì sao GMAC và RTF có thể đi ngược nhau; đặt bốn tên siêu nhẹ lên checklist chọn mà không bịa kết quả của chúng; và thiết kế một kiểm tra state dài không phụ thuộc paper nào trong số đó.

## Kế hoạch 60 phút

- **0–10 phút** — DSP tai nghe và tab laptop: hai ngân sách.
- **10–25 phút** — Số DF2 như chứng minh MAC lệch RTF.
- **25–40 phút** — Bốn tên, mỗi tên một dòng, và thứ bạn vẫn phải đo.
- **40–50 phút** — Trôi state qua hàng chục phút.
- **50–60 phút** — Mini-lab, checklist, bài tập.

## Giải thích cốt lõi

### Hai ngân sách không phải bảng DF2

DeepFilterNet2 (arXiv:2205.05474) báo RTF **0,04** ở **0,356 GMAC** trên Core i5-8250U laptop, so với hàng ICASSP 0,348 GMAC và RTF **0,11**. Vòng tract 2023 báo RTF **0,19** trên i5-8250U. RNNoise, trên bảng DF2 đó, khoảng 0,06 M tham số, RTF 0,027, PESQ 2,33, so với PESQ 3,08 của DF2. Đó là những số compute duy nhất bài này coi là đã in. Tai nghe hoặc điện thoại là máy khác: RTF laptop không phải RTF điện thoại. Đồ thị siêu nhẹ nhắm bộ nhớ nhỏ hơn nhiều và một hop ngắn, và thường rơi gần PESQ 2,33 hơn 3,17. Điều đó chấp nhận được khi phương án kia là underrun.

### Vì sao bảng MAC nói dối

Số MAC giả định mọi phép nhân-cộng có cùng thời gian tường. Không phải vậy.

- Gather theo nhóm hoặc theo băng nhảy trong bộ nhớ. ALU chờ cache. FastEnhancer là tên người ta nhắc khi lập luận này; trang này không trích paper đó.
- Một GEMM dày hơi lớn hơn, được runtime hợp nhất, có thể xong sớm hơn một conv nhóm khéo mà kernel ONNX Runtime không vector hóa.
- Kernel thời gian giữ một vòng activation quá khứ. DF2 cắt kernel từ $$2\times 3$$ xuống $$1\times 3$$ (trừ lớp vào) và RTF từ 0,11 xuống 0,04 trong khi GMAC đứng yên. Đó là cơ chế mang sang cách bạn đọc mọi đồ thị siêu nhẹ: đếm byte di chuyển mỗi hop, không chỉ MAC.

**Luật đo (Chương 05).** Một luồng, bỏ warm-up, p50 và p95 của thời gian tường mỗi hop, chia cho độ dài hop. Chạy trên thiết bị đích theo nhịp callback. Cột MAC của paper là một giả thuyết.

### Bốn tên, và chỉ là tên

| Tên | Vai trên shortlist khóa học | Bài này sẽ không nói |
|-----|-----------------------------|----------------------|
| **GTCRN** | Mạng hồi tiếp tích chập có nhóm, siêu nhẹ, được nhắc nhiều | Không tiêu đề, năm, URL, MAC, MOS |
| **FastEnhancer** | Tên gắn với “nhanh trên thiết bị”, kể cả đo ONNX Runtime | Không số kết quả |
| **μNet** | Tên gắn với bộ nhớ cực thấp (DSP, tai nghe) | Không số kết quả |
| **Fast-ULCNet** | Tên gắn với tuyến ULCNet và state RNN của stream dài | Không số kết quả |

Các chuỗi cùng cụm — ULCNet, UL-UNAS, AdaptCRN, CoFi-Lite, FSPEN — là từ vựng tùy chọn. Không phải nội dung thi, và không có citation ở đây.

### State chạy lâu hơn clip demo

Clip 3 giây giấu trôi GRU. Ở hop 10 ms, 45 phút là $$45\times 60\times 100=270\,000$$ lần cập nhật. Lượng tử hóa, cổng không ổn, hoặc khoảng im lặng chưa thấy sẽ đẩy state ra khỏi vùng train. Bạn nghe nhiễu nhạc tăng chậm hoặc tiếng bị dúi chậm, không phải click tại $$t=0$$. Fast-ULCNet chỉ là tên shortlist gắn với thảo luận đó; trang này không nêu cách chữa từ paper. Phép thử không cần citation:

- Trong im lặng đã phát hiện, hòa state GRU về 0 trong vài trăm mili giây, không trong một hop. Zero cứng là click hoặc chùm nhiễu của bài 05-04.
- Chặn chuẩn state nếu kiến trúc cho phép một tỷ lệ không đổi gain.
- Ghi histogram gain ở phút 1 và phút 40. Lệch ở cùng mức vào là trôi.

### Khi đường DF3 vẫn thắng

Ưu tiên mô hình gắn DeepFilterNet3 trên trình duyệt laptop khi WASM SIMD giữ được hop và vài megabyte trọng số chấp nhận được. Ưu tiên một tên siêu nhẹ trên DSP hoặc CPU rất nhỏ, nơi nhiễu dư được phép. Một cách chia mạch lạc: AEC cổ điển cộng suppressor dư rất nhỏ trên thiết bị, DF3 trong trình duyệt. File trọng số 16 kHz trong đồ thị 48 kHz không phải DF3 nhẹ; hãy resample có chủ đích.

## Checklist shortlist

1. Nhân quả, và bao nhiêu khung look-ahead?
2. 16 kHz hay 48 kHz, và resampler nằm ở đâu?
3. RTF p95 trên **thiết bị của bạn**, một luồng, cache nóng, nhịp callback.
4. Byte trọng số và thời gian cold-start, tách khỏi RTF.
5. Một lần chạy ít nhất 30 phút có đoạn im.
6. Giấy phép của trọng số.
7. Mọi toán tử có trong bản ONNX Runtime hoặc tract của bạn.

## Bẫy thường gặp

- Chọn người thắng từ cột MAC.
- Port tích chập nhóm mà runtime WASM chạy thành vòng scalar.
- Bỏ lần chạy 30 phút.
- Đưa PCM 48 kHz vào mô hình có STFT train ở 16 kHz.

## Mini-lab

**Mục tiêu.** Tái hiện so sánh DF2 “GMAC phẳng, RTF không phẳng” từ số đã công bố, rồi áp cùng phép thử tỷ số cho một cặp siêu nhẹ giả để thấy một quyết định trông thế nào trước khi có paper không được nêu tên.

```bash
python3 - << 'PY'
# Numbers from the DeepFilterNet2 paper's Voicebank table (notebook i5).
rows = [
    ("DF ICASSP row", 0.348, 0.11),
    ("DF2 simplified", 0.356, 0.04),
]
for name, gmac, rtf in rows:
    print(f"{name}: gmac={gmac:.3f} rtf={rtf:.2f} rtf_per_gmac={rtf/gmac:.3f}")
# Hypothetical shortlist. These MACs are lab fiction, not paper results.
fake = [("modelA", 0.05, 0.30), ("modelB", 0.08, 0.12)]
best = min(fake, key=lambda r: r[2])
print("lower_p95_rtf", best[0])
PY
```

**Expected**. `DF ICASSP row: gmac=0.348 rtf=0.11 rtf_per_gmac=0.316` và `DF2 simplified: gmac=0.356 rtf=0.04 rtf_per_gmac=0.112`. Rồi `lower_p95_rtf modelB`. Model B nhiều MAC hơn mà RTF thấp hơn — đó là luật chọn.

**Failure modes**. Coi cặp giả là kết quả GTCRN hoặc FastEnhancer. Trích 0,04 như RTF điện thoại. Xếp hạng chỉ theo `rtf_per_gmac` khi p95, không phải trung bình, trượt hop.

## Bài tập

1. **Tình huống.** Với DSP đeo tai, laptop tầm trung trong Chrome, và loa họp cỡ Raspberry Pi, chọn DF3 hoặc “một tên siêu nhẹ” và nêu lý do ngân sách trong một câu.
2. **Phác harness.** Số hop warm-up, độ dài hop, và phân vị bạn dùng làm cổng. Vì sao trung bình không phải cổng?
3. **Trôi.** Hop 10 ms, 40 phút. Bao nhiêu lần cập nhật GRU? Bạn so cái gì ở đầu và ở cuối?
4. **Tên.** Viết một câu cho mỗi GTCRN, FastEnhancer, μNet và Fast-ULCNet, không chữ số và không năm.

### Gợi ý đáp án

1. DSP: siêu nhẹ, vì RTF 0,04 của DF2 đo trên Core i5. Chrome laptop: DF3, nếu WASM SIMD giữ p95 trong hop và cỡ tải chấp nhận được. Board cỡ Pi: paper DF2 nhận thời gian thực trên Pi 4 cho **mô hình đó**; một tên siêu nhẹ là phương án dự phòng nếu p95 bản build của bạn không đạt.
2. Bỏ 50 hop đầu, hop = 10 ms = 0,01 s, cổng trên p95 (và nhìn p99). Trung bình giấu khung trễ gây underrun. Chương 05 tính đúng việc này.
3. $$40\times 60\times 100=240\,000$$ lần cập nhật. So histogram gain băng hoặc chuẩn state trên một clip hiệu chuẩn lặp lại, không so cả waveform của cuộc gọi.
4. Chỉ dùng vai một dòng trong bảng trên. Có chữ số nghĩa là bạn đã bịa một kết quả.

## Đọc thêm

- Schröter et al., DeepFilterNet2, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474), cho hai hàng RTF 0,11 và 0,04. Đó là ví dụ MAC lệch RTF.
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227), cho số RTF 0,19 của vòng tract.
- Valin, [arXiv:1709.08243](https://arxiv.org/abs/1709.08243), baseline hybrid nhỏ (bài 04-06).
- Nguồn gốc bạn tự mở cho GTCRN, FastEnhancer, μNet và Fast-ULCNet. Không cái nào được link ở đây.
