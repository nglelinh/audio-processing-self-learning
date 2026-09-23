---
layout: post
title: "10-03 Duy trì khóa học này"
chapter: "10"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter10
lesson_type: required
draft: false
---

Khóa này là bộ bài tiếng Anh và tiếng Việt đầy đủ từ chương 00 đến 10. API vẫn dịch chuyển. Gói npm, bố trí CDN `v2/`, weight DeepFilterNet, và móc TrackProcessor của LiveKit sẽ trôi, và bài trích chúng sẽ trôi theo. Người giữ khóa sửa cặp ngôn ngữ trong cùng một thay đổi, sinh lại hình thay vì sửa PNG bằng tay, và coi repo sản phẩm chung là tài liệu upstream để đọc, không phải cây bài tập.

![Hình trực giác Fourier dùng làm ví dụ cho người giữ khóa]({{ site.imgurl }}/generated/fourier-intuition.png)

*Hình. Tổng các tone theo thời gian thành các vạch theo tần số. Người giữ khóa sinh lại PNG này, và mọi hình khác của khóa, bằng `python3 scripts/generate_course_figures.py`. Đầu ra vào `img/generated/`. Bài nhúng bằng `{{ site.imgurl }}/generated/fourier-intuition.png`.*

## Bạn làm được gì sau bài này

Bạn vá được bài khi `deepfilternet3-noise-filter` hoặc bố trí CDN đổi, cập nhật bản tiếng Việt trong cùng pull request, thêm hình mà không gãy `baseurl`, và mở phiếu bảo trì liệt kê cả hai file ngôn ngữ. Bạn cũng build site tại máy và gọi tên lỗi nếu `bundle exec jekyll build` cảnh báo.

## Cần theo dõi gì

| Upstream | Cái gì gãy | Sửa đâu |
|----------|------------|---------|
| npm `deepfilternet3-noise-filter` trên 1.3.0 | Tên công khai hoặc tiền tố asset (`v2/` trong README, `v3/` trong bản 1.3.0 đã cài) | Chương 07 và 09, cả hai ngôn ngữ |
| CDN rời `v2/` | URL `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` | 07-03 và 09-01 |
| LiveKit `setProcessor` | Đường publish ở 09-01 | Đọc lại [docs.livekit.io](https://docs.livekit.io/) và trích phiên bản |
| Tên archive ONNX mới | Câu asset ở 09 và 10 | Chỉ tên file, sau khi bạn thấy nó |
| Checkpoint DNSMOS | Bảng chương 08 | Ghim tên mới; đừng so điểm cũ như một chuỗi |

Tên công khai giữ cho đến khi chính README đổi: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, `setProcessor`, `setSuppressionLevel(0–100)`, `setEnabled`, `assetConfig.cdnUrl`. Đừng mô tả lớp riêng cho có vẻ chính xác.

## Kỷ luật changelog

Khi bạn sửa bài tiếng Anh, cập nhật bản tiếng Việt trong cùng pull request. Cùng `chapter`, cùng `order`, cùng thân tên file, `lang: en` một bên và `lang: vi` bên kia. Khối mã, URL, và float lab đã in (13.80 và −10.67, danh sách mixer `[1.237, -0.237, -0.763, 0.263]`) giữ nguyên. Văn là tiếng Việt tự nhiên. Giữ thuật ngữ tiếng Anh SI-SDR, DNSMOS, RTF, và TrackProcessor.

Khi thêm hình, đặt PNG trong `img/generated/` và tham chiếu bằng `{{ site.imgurl }}`. Đừng dán ảnh chụp một lần vào thư mục mới. Lệnh sinh:

```bash
python3 scripts/generate_course_figures.py
```

Lệnh đó viết lại PNG trong `img/generated/`, gồm `fourier-intuition.png`, `eval-metric-map.png`, `livekit-trackprocessor.png`, `deepfilternet-erb.png`, `onnx-wasm-path.png`, và `rtf-audioworklet.png`. Commit PNG vừa sinh cùng bài nhúng nó. Nếu chỉ đổi chú thích, không cần sinh lại.

Một dòng có ngày thuộc thân PR, không chỉ trong chat:

```text
2026-09-23 — Chương 08–10 EN và VI: hình, mini-lab, gợi ý đáp án.
             Bản VI cập nhật trong cùng thay đổi. Không sửa repo sản phẩm.
```

## Build site

`_config.yml` đặt `baseurl: /audio-processing-self-learning` và `imgurl: /audio-processing-self-learning/img`. Xem tại máy:

```bash
bundle install
bundle exec jekyll serve
# http://127.0.0.1:4000/audio-processing-self-learning/
bundle exec jekyll build
```

Site đã xuất bản là `https://nglelinh.github.io/audio-processing-self-learning/`. Hình dùng đường tương đối mà không qua `site.imgurl` sẽ chạy trên một host và 404 trên host kia. Sau build, mở một trang chương 08 và một trang chương 10 và xác nhận URL ảnh chứa `/audio-processing-self-learning/img/generated/`.

## Vòng advisor và ranh giới sản phẩm

Ghi yêu cầu giáo trình vào `COURSE_OUTLINE.md`. Luật trích dẫn nằm ở `AGENTS.md`: DeepFilterNet cùng DeepFilterNet2/3, DNS Challenge, WebRTC APM, SpeexDSP, RNNoise, SI-SDR, DNSMOS, ONNX Runtime, và tract. Tên khảo sát giữ là tên. Bài khóa đọc [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression). Chúng không bắt `/Users/nguyenlelinh/ncc/mezon-noise-suppression`, và không nhận patch ở đó. Học viên thí nghiệm trong fork cá nhân hoặc trong `capstone/`.

## Mẫu issue bảo trì

```markdown
Title: [course] Update Ch09 CDN paths for package x.y.z
- Upstream version:
- Broken lesson paths:
- EN files:
- VI files:
- Figure touched (img/generated name) or none:
- jekyll build: pass/fail
- Verified image URL contains site imgurl: yes/no
```

Chỉ mở issue khi cả hai file ngôn ngữ được liệt kê. Bản sửa chỉ rơi tiếng Anh là chưa xong.

## Mini-lab

Từ gốc repo, xác nhận script sinh hình còn đó và mọi bài tiếng Anh chương 08–10 vẫn nhúng hình qua `site.imgurl`:

```bash
test -f scripts/generate_course_figures.py && echo script_ok
python3 - << 'PY'
from pathlib import Path
bad = []
paths = list(Path("contents/en").glob("chapter0[89]/_posts/*.md"))
paths += list(Path("contents/en").glob("chapter10/_posts/*.md"))
for p in paths:
    if "site.imgurl" not in p.read_text():
        bad.append(p.name)
print("bad", bad or "none")
PY
```

Đầu ra kỳ vọng:

```text
script_ok
bad none
```

Kiểu hỏng: sửa PNG trong trình ảnh rồi bỏ script, lần sinh sau sẽ xóa chỉnh đó; đổi float lab tiếng Anh mà để bản tiếng Việt ở số cũ; `baseurl` chép từ tên repo khác nên mọi ảnh 404; pull request “sửa” bài bằng cách sửa repo sản phẩm.

## Bài tập

1. So README npm với bài 09-01 và liệt kê một rủi ro trôi.
2. Tạo một lỗi chính tả một từ tiếng Anh trên nhánh cục bộ, sửa, và chiếu sửa sang file tiếng Việt trong cùng commit. Đừng push trừ khi bạn đang trực giữ khóa.
3. Chạy `bundle exec jekyll build` và chép cảnh báo nào nhắc chương 08–10.
4. Điền mẫu issue cho bản 1.4.0 giả định bỏ tiền tố `v2/`. Ghi cả file EN và VI.
5. Gọi lệnh sinh hình và hai luật đường dẫn cho một hình mới.

### Gợi ý đáp án

1. Trôi hay gặp: thêm phương thức công khai, hoặc đổi tiền tố CDN. Trích dòng README bạn thấy.
2. Một PR, hai file. `lang` trong front matter giữ nguyên.
3. Nếu chưa cài build, ghi “jekyll not run” thay vì bịa log sạch.
4. Cả đường EN và VI. Dòng hình là “none” trừ khi sơ đồ đổi.
5. `python3 scripts/generate_course_figures.py` ghi `img/generated/<name>.png`. Bài dùng `{{ site.imgurl }}/generated/<name>.png`.
