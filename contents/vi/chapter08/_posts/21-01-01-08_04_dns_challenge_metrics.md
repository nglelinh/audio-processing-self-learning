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

Một trung bình SI-SDR là cách bài báo được trích và cách sản phẩm bị bất ngờ. Microsoft DNS Challenge ([microsoft/DNS-Challenge](https://github.com/microsoft/DNS-Challenge)) là khuôn công khai khóa này chép ở kích thước nhỏ: cặp tổng hợp nơi metric xâm nhập hợp lệ, ghi thật nơi chúng không hợp lệ, một lát nghe, và một cột hệ thống để phần mềm thời gian thực không núp sau bảng chất lượng. Từng kỳ challenge đổi thực đơn metric. Ghim năm hoặc bài báo bạn theo. Đừng nhận “thắng DNS Challenge” nếu bạn không chạy blind set năm đó với protocol năm đó.

![Bản đồ đánh giá cho cả bộ metric]({{ site.imgurl }}/generated/eval-metric-map.png)

*Hình. Bộ metric là cả bản đồ, không phải một ô. SI-SDR, DNSMOS, nghe, và RTF trả lời các câu khác nhau. Ô trống ghi `n/a`, không điền bù.*

## Bạn làm được gì sau bài này

Bạn dựng được phiếu sáu cột, một hàng một clip, chạy checker từ chối cột thiếu, và giải thích ô nào phải là `n/a`. Bạn cũng tách epsilon hồi quy của lab khỏi mọi con số xuất hiện trong bài báo.

## Các track đáng giữ

| Track | Vật liệu | Metric hợp lệ |
|-------|----------|----------------|
| Tổng hợp | Cặp ồn/sạch bạn sinh | SI-SDR, PESQ/STOI nếu chọn, delta so với bypass |
| Thật | Ghi kiểu họp, không file sạch | DNSMOS nếu ghim checkpoint, không thì `n/a` |
| Nghe | Cùng điều kiện, clip ngắn | Ghi chú AB: thắng, thua, hoặc hòa |
| Hệ thống | Máy sẽ demo | RTF p95, cộng init hoặc fallback nếu đã đo |
| Hạ nguồn tùy chọn | Một bản ASR cố định | Delta WER hoặc CER, không thay MOS |

Dữ liệu tổng hợp cho bạn núm SNR và một tham chiếu. Nó cũng nói dối khi ngân hàng nhiễu sạch hơn phòng thật. Dữ liệu thật là sản phẩm và từ chối SI-SDR. Luật là không chỉnh trên một cột. Đóng băng một tập nghe cuối mà bạn không mở khi còn đang đổi mức.

## Bố trí harness

Để harness trong thư mục của bạn hoặc fork. Đừng đặt vào cây sản phẩm chung `mezonai/mezon-noise-suppression`, và đừng bắt checkout giảng viên tại `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.

```text
eval/
  datasets/synthetic/   # clean/, noisy/, meta.csv
  datasets/real/
  systems/bypass/
  systems/level60/
  systems/level80/
  scripts/compute_si_sdr.py
  reports/YYYY-MM-DD.md
```

`meta.csv` cần ít nhất `clip_id,condition,snr_db,clean_path,noisy_path`. Hàng thật để `clean_path` trống. Tái lập được là phần đầu báo cáo: phiên bản gói (npm `deepfilternet3-noise-filter` 1.3.0 nếu đó là bản bạn chạy), tên archive `DeepFilterNet3_onnx.tar.gz`, tên checkpoint DNSMOS hoặc `not run`, OS, và thiết bị đo RTF. Nếu enhance tất định, nói vậy. Nếu không, ghi seed.

Không có ngưỡng SI-SDR hay DNSMOS chính thức để chép vào CI. Bạn có thể chọn epsilon lab sau khi có baseline trên đúng tập này, và phải ghi đó là nội bộ. Bảng trong bài báo không phải epsilon đó.

ASR tùy chọn: chọn một phiên bản engine, phiên âm bản ồn và bản enhance cùng cấu hình, báo delta. Enhance giúp DNSMOS mà hại WER là sự thật sản phẩm, không phải mâu thuẫn để giấu.

## Khung báo cáo

```markdown
## NS eval — <date>
- System: deepfilternet3-noise-filter <version>, setSuppressionLevel <n>
- RTF p95: <số và thiết bị> hoặc n/a

### Per clip
(bảng sáu cột từ mini-lab)

### Decision
Ship, không ship, hoặc ship sau cờ — và cột nào ép quyết định.

### Limits
Ngôn ngữ, thiết bị, và metric bạn không chạy.
```

Overfit lộ ra khi bộ chỉ có giọng bạn, một quán, và một trung bình không có hàng theo điều kiện. Chạy lại sau khi đổi WASM hoặc SIMD. Bằng mẫu hiếm khi sống sót sau khi đổi runtime, nên metric phải đi cùng binary.

## Mini-lab

Tạo `suite.md` với bảng markdown **sáu hàng dữ liệu**. Header phải có các cột: clip id, condition, SI-SDR hoặc `n/a`, DNSMOS hoặc `n/a`, listening note, RTF p95. Dùng `n/a` khi metric không hợp lệ hoặc chưa chạy. Ít nhất một hàng là clip thật (`n/a` ở SI-SDR) và ít nhất một hàng là tổng hợp. Ghi chú nghe ngắn (`new`, `old`, `tie`, hoặc `not listened`). RTF p95 là số bạn đo hoặc `n/a` nếu chưa đo.

Checker `check_suite.py`:

```python
from pathlib import Path
lines = Path("suite.md").read_text().splitlines()
tables = [ln for ln in lines if ln.strip().startswith("|")]
header = tables[0].lower()
need = ["clip id", "condition", "si-sdr", "dnsmos", "listening note", "rtf p95"]
missing = [n for n in need if n not in header]
data = [ln for ln in tables[2:] if ln.strip().strip("|").strip()]
print("missing", missing or "none")
print("data_rows", len(data))
```

Đầu ra kỳ vọng:

```text
missing none
data_rows 6
```

Ví dụ hình dạng (sáu hàng của bạn phải là clip của bạn; một hàng này chỉ cho thấy các ô):

```markdown
| clip id | condition | SI-SDR or n/a | DNSMOS or n/a | listening note | RTF p95 |
| --- | --- | --- | --- | --- | --- |
| syn_fan_01 | synthetic fan, 10 dB | 13.80 | n/a | tie | 0.35 |
```

Số 13.80 ở đây là float lab bài 08-01, dán để kiểu cột rõ. Nó không phải số đo DeepFilterNet. Kiểu hỏng: header ghi “quality” thay vì sáu tên; năm hàng; ghi thật với SI-SDR bịa; một số RTF chép vào mọi hàng mà không nói đó là số cả phiên; ngưỡng trông chính thức kiểu “DNSMOS phải vượt 3.5”.

## Bài tập

1. Điền đủ sáu hàng, trộn điều kiện tổng hợp và thật. Chạy checker đến khi in `data_rows 6`.
2. Viết header `meta.csv` cùng một hàng tổng hợp và một hàng thật.
3. Đề xuất luật fail CI mà không giả làm ngưỡng DNSMOS chính thức.
4. Nêu hai cách bộ metric overfit audio họp Mezon, và tập giữ lại chặn mỗi cách.
5. Thêm cột ASR tùy chọn. Nói vì sao nó không được thay ghi chú nghe.

### Gợi ý đáp án

1. Hàng thật: SI-SDR là `n/a`. Hàng chưa chạy DNSMOS: DNSMOS là `n/a`.
2. Hàng thật: đường clean để trống. Đừng bịa file tham chiếu.
3. Ví dụ chính sách: “trên golden set 12 clip này, fail nếu trung bình DNSMOS theo điều kiện giảm quá epsilon đã ghi trong báo cáo.” Epsilon là của bạn.
4. Chỉ giọng tác giả; chỉ quán. Giữ ngoài những người nói khác và một điều kiện bàn phím hoặc quạt bạn không chỉnh trên đó.
5. WER có thể tăng khi bộ khử hại phụ âm mà metric thích. Giữ ghi chú nghe.
