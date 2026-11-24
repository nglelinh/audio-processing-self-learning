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

Hãy thử tưởng tượng một buổi họp duyệt phát hành sản phẩm: kỹ sư ML tự tin chiếu lên màn hình một biểu đồ duy nhất — *"Bản mới tăng +1,2 dB SI-SDR so với bản cũ, đề nghị ship ngay chiều nay!"* Nhưng khi đưa lên bảng tổng hợp đa chiều kiểu DNS Challenge, câu chuyện lập tức đảo ngược: bản mới làm **tỉ lệ lỗi nhận dạng giọng nói (WER) tăng vọt**, thua nghe thử ở phòng yên tĩnh và đẩy **RTF p95 lên 0,92** sát ngưỡng vỡ tiếng! Trong kỹ thuật âm thanh thực chiến, không có một chỉ số vạn năng nào — chỉ có một **hệ thống bảng đo đa trục** đặt tất cả sự đánh đổi lên cùng một mặt bàn.

Chỉ dựa vào một con số trung bình SI-SDR là cách nhiều bài báo được trích dẫn nhưng cũng là lý do khiến sản phẩm thực tế gặp sự cố ngoài dự kiến. Cuộc thi Microsoft DNS Challenge ([microsoft/DNS-Challenge](https://github.com/microsoft/DNS-Challenge)) cung cấp khuôn mẫu đánh giá công khai mà khóa học mô phỏng lại ở quy mô gọn nhẹ: gồm cặp dữ liệu tổng hợp (nơi các chỉ số xâm nhập có hiệu lực), bản ghi thực tế (nơi chỉ số xâm nhập không áp dụng được), lát cắt kiểm thử lắng nghe và cột hiệu năng hệ thống để chi phí thời gian thực không bị che khuất sau bảng chất lượng âm thanh. Do mỗi năm cuộc thi lại điều chỉnh danh mục chỉ số, bạn cần ghi rõ năm hoặc bài báo đang tham chiếu, và không tuyên bố “đạt chuẩn DNS Challenge” nếu chưa chạy đúng tập kiểm thử mù và quy trình của năm đó.

**Mạch bài học:** Cái bẫy ra quyết định bằng một con số duy nhất → Bản đồ kiến thức nền (Đánh giá đa nhánh kiểu DNS Challenge, Kỷ luật trung thực `n/a` & Tái lập thực nghiệm, Tương tác với hệ thống hạ nguồn ASR & Cổng kiểm duyệt RTF) → 5 hạng mục đánh giá & Tổ chức thư mục `eval/` → Khung giải thích phân tích bảng đối chiếu 2 bản dựng thực chiến (vì sao bản SI-SDR cao hơn vẫn bị loại) → Khung báo cáo, Mini-lab và Bài tập.

![Bản đồ đánh giá cho cả bộ metric]({{ site.imgurl }}/generated/eval-metric-map.png)

*Hình. Hệ thống đánh giá là toàn bộ bản đồ chứ không phải một ô đơn lẻ: SI-SDR, DNSMOS, kiểm thử lắng nghe và RTF trả lời những câu hỏi khác nhau. Ô nào không áp dụng được thì ghi `n/a`, tuyệt đối không điền số ước đoán.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ xây dựng được bảng báo cáo 6 cột (mỗi hàng một đoạn âm thanh), chạy script kiểm tra tự động để bắt lỗi thiếu cột, giải thích chính xác ô nào bắt buộc ghi `n/a`, và phân biệt rõ ngưỡng sai số hồi quy nội bộ (epsilon) của phòng lab với các con số xuất hiện trong bài báo.

## Bản đồ kiến thức nền: Thiết kế hệ thống đánh giá toàn diện (Evaluation Harness)

### 1. Kiến trúc đa nhánh kiểu DNS Challenge (Synthetic + Real + Listening + Systems)
- **Là gì:** Khuôn khổ đánh giá kết hợp bốn góc nhìn không thể thay thế lẫn nhau: dữ liệu tổng hợp (đo SI-SDR/$$\Delta$$SI-SDR), dữ liệu thu thực tế (đo DNSMOS), nghe mù của con người (AB) và chi phí vận hành thời gian thực (RTF p95, thời gian khởi động lạnh).
- **Nghiên cứu gì:** Phát hiện mọi xung đột tối ưu hóa (ví dụ khử nhiễu quá tay giúp đẹp SI-SDR trên nhiễu dừng nhưng hỏng giọng thực tế hoặc vượt ngân sách CPU).

### 2. Tính tái lập (Reproducibility) và Kỷ luật `n/a`
- **Là gì:** Lưu cố định dữ liệu (`meta.csv`), phiên bản gói (`1.3.0`), tệp nhị phân WASM/ONNX, checkpoint DNSMOS, hạt giống ngẫu nhiên và thiết bị đo; ghi tường minh `n/a` cho mọi ô không hợp lệ (như SI-SDR trên bản ghi thật).
- **Nghiên cứu gì:** Đảm bảo hai bảng báo cáo cách nhau 3 tháng vẫn so sánh được chính xác từng hàng, không bị nhiễm số liệu bịa hay lẫn phiên bản runtime.

### 3. Đánh giá hạ nguồn (Downstream ASR — WER/CER) và Chống quá khớp tập Holdout
- **Là gì:** Đo thêm tác động của bộ khử nhiễu lên tỉ lệ lỗi từ (WER) hoặc lỗi ký tự (CER) của một bộ nhận dạng giọng nói cố định, đồng thời giữ riêng một tập holdout gồm người nói và bối cảnh chưa từng mở ra khi tinh chỉnh.
- **Nghiên cứu gì:** Bảo vệ các ứng dụng có phụ đề tự động / ghi chú họp AI khỏi những bộ lọc làm mượt tai người nhưng vô tình xóa mất âm cuối làm hỏng phiên âm.

## Các hạng mục đánh giá cần duy trì

| Hạng mục (Track) | Dữ liệu đầu vào | Chỉ số hợp lệ |
|-------|----------|----------------|
| Tổng hợp | Cặp tín hiệu ồn/sạch tự tạo | SI-SDR, PESQ/STOI (tùy chọn), mức cải thiện so với bypass |
| Thực tế | Bản ghi cuộc họp thực, không có bản sạch | DNSMOS (khi cố định checkpoint), nếu chưa chạy thì ghi `n/a` |
| Lắng nghe | Cùng các điều kiện nhiễu, đoạn ngắn | Ghi chú kết quả AB: thắng, thua hoặc hòa |
| Hệ thống | Thiết bị dùng để trình diễn (demo) | RTF p95, kèm thời gian khởi tạo hoặc fallback nếu có đo |
| Hạ nguồn (tùy chọn) | Một phiên bản nhận dạng giọng nói (ASR) cố định | Độ chênh lệch WER hoặc CER (không thay thế MOS) |

Dữ liệu tổng hợp mang lại khả năng điều chỉnh SNR linh hoạt và có tín hiệu tham chiếu chính xác, nhưng dễ tạo ảo giác lạc quan khi kho nhiễu quá “sạch” so với môi trường thật. Ngược lại, bản ghi thực tế phản ánh đúng sản phẩm nhưng không thể tính SI-SDR. Nguyên tắc cốt lõi là không tối ưu mô hình chỉ dựa trên một cột duy nhất, đồng thời đóng băng riêng một tập nghe thử cuối cùng mà bạn không mở ra trong lúc tinh chỉnh tham số.

## Khung giải thích: Đọc bảng quyết định phát hành giữa hai bản dựng thực chiến (nên đọc chậm)

Giả sử nhóm của bạn đang cân nhắc giữa **Bản A (mặc định hiện tại, `level = 60`)** và **Bản B (ứng viên mới, `level = 85` + mô hình nặng hơn chút)**. Dưới đây là kết quả gom đủ 5 trục (số liệu minh họa):

| Tiêu chí đánh giá | Bản A (`level 60`) | Bản B (`level 85`) | Chênh lệch (B so với A) |
| :--- | :--- | :--- | :--- |
| Tổng hợp — Quạt 10 dB (SI-SDR) | $$14{,}50\text{ dB}$$ | $$15{,}70\text{ dB}$$ | **$$+1{,}20\text{ dB}$$** (B thắng) |
| Thực tế — Quán cà phê (SI-SDR) | `n/a` | `n/a` | Đúng quy tắc (không có bản sạch) |
| Thực tế — Quán cà phê (DNSMOS BAK / SIG) | $$3{,}75\text{ / }3{,}50$$ | $$4{,}00\text{ / }3{,}15$$ | BAK $$+0{,}25$$, nhưng SIG **$$-0{,}35$$** |
| Nghe thử AB — Phòng yên ($$N = 10$$) | Thắng 6, Hòa 2 | Thắng 2, Hòa 2 | **B thua 2–6** (cắt giọng sạch!) |
| Hạ nguồn ASR (WER) | $$8{,}0\%$$ | $$11{,}5\%$$ | Tăng **$$+3{,}5\%$$** tuyệt đối (tăng $$43{,}8\%$$ tương đối!) |
| Hệ thống — Laptop đích (RTF p95) | $$0{,}58$$ (dư $$4{,}2\text{ ms}$$) | $$0{,}92$$ (chỉ dư $$0{,}8\text{ ms}$$) | **Cực sát trần underrun!** |

**Kết luận ra quyết định (`Decision`):** **KHÔNG SHIP Bản B** làm mặc định! Dù Bản B đẹp hơn ở cột SI-SDR tổng hợp (`+1,20 dB`) và nền quán cà phê yên hơn (`BAK +0,25`), bốn cột còn lại đồng loạt bật đèn đỏ: giọng phòng yên bị méo (`AB 2–6`), phụ đề tự động lỗi tăng gần gấp rưỡi (`WER 8% → 11,5%`) và ngân sách thời gian thực chỉ còn đúng `0,8 ms` dự phòng cho hệ điều hành. Nếu không có bảng đa trục, một nhóm chỉ nhìn SI-SDR sẽ ship ngay một bản cập nhật tệ hơn cho người dùng!

## Tổ chức thư mục bộ công cụ đánh giá (harness)

Hãy đặt bộ công cụ đánh giá trong kho cá nhân hoặc nhánh fork của riêng bạn, không đưa vào kho sản phẩm chung `mezonai/mezon-noise-suppression`:

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

Tệp `meta.csv` cần tối thiểu các cột `clip_id,condition,snr_db,clean_path,noisy_path`, trong đó các hàng bản ghi thực tế để trống cột `clean_path`. Để đảm bảo khả năng tái lập, phần đầu báo cáo phải ghi rõ phiên bản gói (ví dụ `deepfilternet3-noise-filter` 1.3.0), tên tệp nén mô hình `DeepFilterNet3_onnx.tar.gz`, tên checkpoint DNSMOS (hoặc `not run`), hệ điều hành và thiết bị đo RTF. Nếu quá trình xử lý mang tính tất định (deterministic), cần nêu rõ; nếu không, phải ghi lại giá trị hạt giống (seed).

Không tồn tại ngưỡng SI-SDR hay DNSMOS chính thức nào để sao chép thẳng vào CI. Sau khi có số liệu nền (baseline) trên chính tập dữ liệu của mình, bạn có thể đặt một ngưỡng epsilon nội bộ cho kiểm thử hồi quy và ghi chú rõ nguồn gốc nội bộ đó — bảng số liệu trong bài báo khoa học không phải epsilon cho dự án của bạn.

Với nhánh đánh giá ASR tùy chọn: cố định một phiên bản engine ASR, phiên âm cả bản gốc nhiễu lẫn bản đã khử nhiễu theo cùng cấu hình rồi báo cáo mức chênh lệch. Việc bộ khử nhiễu giúp tăng điểm DNSMOS nhưng lại làm xấu đi tỉ lệ lỗi từ (WER) là một thực tế sản phẩm quan trọng, không phải mâu thuẫn cần che giấu.

## Khung báo cáo đánh giá

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

Hiện tượng quá khớp (overfit) lộ rõ khi tập kiểm thử chỉ gồm giọng của chính tác giả, một bối cảnh quán cà phê duy nhất và một con số trung bình gộp không phân tách theo điều kiện. Ngoài ra, bất cứ khi nào thay đổi tệp WASM hoặc cấu hình SIMD, bạn phải chạy lại toàn bộ bộ đánh giá: kết quả khớp từng mẫu hiếm khi giữ nguyên khi đổi runtime, nên chỉ số chất lượng phải luôn gắn liền với đúng tệp nhị phân phát hành.

## Mini-lab

Tạo tệp `suite.md` chứa bảng Markdown gồm đúng **6 hàng dữ liệu**. Hàng tiêu đề bắt buộc có đủ 6 cột: `clip id`, `condition`, `SI-SDR` (hoặc `n/a`), `DNSMOS` (hoặc `n/a`), `listening note`, và `RTF p95`. Ghi `n/a` ở những ô không hợp lệ hoặc chưa chạy; đảm bảo có ít nhất một hàng là bản ghi thực tế (ghi `n/a` ở cột SI-SDR) và ít nhất một hàng là cặp tổng hợp. Cột ghi chú lắng nghe dùng nhãn ngắn (`new`, `old`, `tie` hoặc `not listened`), còn cột RTF p95 điền giá trị đo thực tế hoặc `n/a` nếu chưa đo.

Kiểm tra tệp bằng script `check_suite.py`:

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

**Kết quả kỳ vọng**

```text
missing none
data_rows 6
```

Ví dụ minh họa cấu trúc một hàng (6 hàng trong bài làm phải là dữ liệu của riêng bạn):

```markdown
| clip id | condition | SI-SDR or n/a | DNSMOS or n/a | listening note | RTF p95 |
| --- | --- | --- | --- | --- | --- |
| syn_fan_01 | synthetic fan, 10 dB | 13.80 | n/a | tie | 0.35 |
```

Con số `13.80` ở đây được lấy từ bài lab 08-01 nhằm minh họa định dạng cột, không phải số đo thực của DeepFilterNet.

**Lỗi thường gặp.** Đổi tên tiêu đề cột thành nhãn chung chung kiểu “quality” thay vì 6 tên quy định; điền thiếu số hàng (chỉ có 5 hàng); bịa số SI-SDR cho bản ghi thực tế; sao chép cùng một chỉ số RTF cho mọi hàng mà không ghi chú đó là số đo chung cả phiên; hoặc đặt ra ngưỡng nghe có vẻ chính thức kiểu “DNSMOS phải vượt 3,5”.

## Bài tập

1. Hoàn thiện đủ 6 hàng trong `suite.md` kết hợp cả điều kiện tổng hợp và thực tế, sau đó chạy `check_suite.py` cho đến khi kết quả trả về `data_rows 6`.
2. Viết dòng tiêu đề cho tệp `meta.csv` kèm một dòng dữ liệu tổng hợp và một dòng dữ liệu thực tế.
3. Đề xuất một quy tắc báo lỗi (fail) trong CI mà không ngụy tạo thành ngưỡng chuẩn chính thức của DNSMOS.
4. Chỉ ra hai cách bộ chỉ số đánh giá dễ bị quá khớp với âm thanh cuộc họp Mezon, và nêu cách thiết lập tập kiểm thử giữ lại (holdout set) để ngăn chặn từng cách.
5. Bổ sung cột đánh giá ASR tùy chọn vào bảng và giải thích vì sao cột này vẫn không thể thay thế cột ghi chú lắng nghe.

### Gợi ý đáp án

1. Hàng bản ghi thực tế bắt buộc ghi `n/a` ở cột SI-SDR; hàng chưa chạy mô hình DNSMOS thì ghi `n/a` ở cột DNSMOS.
2. Với hàng bản ghi thực tế, để trống trường đường dẫn bản sạch (`clean_path`) thay vì tự tạo tệp tham chiếu giả.
3. Ví dụ quy tắc minh bạch: “Trên tập golden set 12 đoạn này, báo lỗi CI nếu điểm trung bình DNSMOS theo từng điều kiện giảm quá mức epsilon đã ghi trong báo cáo” — khẳng định rõ epsilon là quy ước nội bộ.
4. Hai dạng quá khớp phổ biến là chỉ dùng giọng của tác giả và chỉ thử trên bối cảnh quán cà phê; khắc phục bằng cách giữ riêng một tập holdout gồm nhiều người nói khác cùng điều kiện bàn phím hoặc quạt không dùng trong lúc tinh chỉnh.
5. Tỉ lệ lỗi từ (WER) có thể tăng lên khi bộ khử nhiễu cắt hỏng phụ âm dù các chỉ số âm học khác vẫn cao; do đó vẫn cần duy trì cột ghi chú lắng nghe.

## Video tham khảo

- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. **Xem trước.** Phần giới thiệu cuộc thi DNS Challenge cho thấy cặp dữ liệu tổng hợp, kiểm thử lắng nghe và mô hình dự đoán khách quan luôn được báo cáo đồng thời thay vì dừng ở một điểm SI-SDR trung bình.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Phần trình bày về dữ liệu huấn luyện minh họa cách một mô hình cụ thể vận hành trên bộ dữ liệu DNS — chỉ nên xem là một dòng kết quả trong toàn bộ bảng đánh giá.
