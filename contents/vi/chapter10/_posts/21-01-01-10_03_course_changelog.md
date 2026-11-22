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

Khóa học này gồm trọn bộ bài giảng song ngữ Anh – Việt từ Chương 00 đến Chương 10. Theo thời gian, các API bên ngoài sẽ thay đổi: gói npm, cấu trúc CDN `v2/`, bộ trọng số DeepFilterNet và giao diện TrackProcessor của LiveKit đều có thể cập nhật, kéo theo các bài học trích dẫn chúng trở nên lỗi thời. Người bảo trì khóa học cần cập nhật đồng bộ cả hai ngôn ngữ trong cùng một lần thay đổi, sinh lại hình minh họa bằng script thay vì chỉnh sửa thủ công tệp PNG, và luôn coi kho mã nguồn sản phẩm chung là tài liệu nguồn để tham khảo chứ không phải nơi nộp bài tập.

![Hình trực giác Fourier dùng làm ví dụ cho người giữ khóa]({{ site.imgurl }}/generated/fourier-intuition.png)

*Hình. Tổng các sóng đơn tần theo miền thời gian tương ứng với các vạch rời rạc trên miền tần số. Người bảo trì sinh lại tệp PNG này cùng mọi hình minh họa khác bằng lệnh `python3 scripts/generate_course_figures.py`; kết quả được ghi vào `img/generated/` và nhúng trong bài qua `{{ site.imgurl }}/generated/fourier-intuition.png`.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ biết cách cập nhật bài học khi gói `deepfilternet3-noise-filter` hoặc bố trí CDN thay đổi, đồng bộ bản tiếng Việt ngay trong cùng một pull request, bổ sung hình minh họa mà không làm hỏng `baseurl`, mở phiếu theo dõi bảo trì liệt kê đủ cả hai tệp ngôn ngữ, và tự dựng trang web tại máy để kiểm tra cảnh báo từ `bundle exec jekyll build`.

## Những thay đổi nguồn gốc cần theo dõi định kỳ

| Nguồn gốc (Upstream) | Thành phần dễ bị lệch | Vị trí cần cập nhật |
|----------|------------|---------|
| Gói npm `deepfilternet3-noise-filter` (sau 1.3.0) | Tên API công khai hoặc quy tắc tự thêm tiền tố `v2/` | Chương 07 và 09 (cả hai ngôn ngữ) |
| CDN thay đổi cấu trúc `v2/` | Đường dẫn `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` | Bài 07-03 và 09-01 |
| LiveKit cập nhật `setProcessor` | Luồng phát hành track ở bài 09-01 | Đối chiếu lại [docs.livekit.io](https://docs.livekit.io/) và ghi rõ phiên bản |
| Tên tệp gói ONNX mới | Mô tả tài nguyên ở Chương 09 và 10 | Chỉ cập nhật đúng tên tệp sau khi đã trực tiếp xác nhận |
| Checkpoint DNSMOS mới | Các bảng đánh giá ở Chương 08 | Cố định tên checkpoint mới; không gộp chung chuỗi điểm với bản cũ |

Các tên giao diện công khai giữ nguyên cho đến khi chính README gốc thay đổi: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, `setProcessor`, `setSuppressionLevel(0–100)`, `setEnabled` và `assetConfig.cdnUrl`. Không tự ý thêm mô tả các lớp nội bộ.

## Kỷ luật cập nhật và ghi nhận thay đổi (Changelog)

Mỗi khi chỉnh sửa bài tiếng Anh, bắt buộc cập nhật bản tiếng Việt tương ứng trong cùng một pull request: giữ đồng nhất `chapter`, `order` và tên tệp, chỉ khác trường `lang: en` và `lang: vi`. Toàn bộ khối mã nguồn, URL và các số liệu kiểm chứng từ bài lab (như `13.80`, `−10.67`, mảng `[1.237, -0.237, -0.763, 0.263]`) phải giữ nguyên chính xác; phần văn bản viết bằng tiếng Việt tự nhiên nhưng bảo toàn các thuật ngữ chuẩn như `SI-SDR`, `DNSMOS`, `RTF` và `TrackProcessor`.

Khi bổ sung hoặc cập nhật hình vẽ, luôn đặt tệp PNG trong `img/generated/` và nhúng thông qua `{{ site.imgurl }}` thay vì dán ảnh chụp rời rạc vào thư mục mới. Chạy lệnh sinh hình:

```bash
python3 scripts/generate_course_figures.py
```

Lệnh này tự động tạo lại toàn bộ hình ảnh trong `img/generated/` (gồm `fourier-intuition.png`, `eval-metric-map.png`, `livekit-trackprocessor.png`, `deepfilternet-erb.png`, `onnx-wasm-path.png` và `rtf-audioworklet.png`). Hãy commit các tệp PNG mới sinh cùng bài học nhúng chúng; nếu chỉ sửa chú thích hình thì không cần chạy lại script.

Ghi một dòng nhật ký kèm ngày tháng ngay trong nội dung mô tả pull request thay vì chỉ trao đổi trong tin nhắn:

```text
2026-09-23 — Chương 08–10 EN và VI: hình, mini-lab, gợi ý đáp án.
             Bản VI cập nhật trong cùng thay đổi. Không sửa repo sản phẩm.
```

## Dựng và kiểm tra trang web tại máy

Tệp `_config.yml` cấu hình `baseurl: /audio-processing-self-learning` và `imgurl: /audio-processing-self-learning/img`. Chạy kiểm tra cục bộ bằng bộ lệnh:

```bash
bundle install
bundle exec jekyll serve
# http://127.0.0.1:4000/audio-processing-self-learning/
bundle exec jekyll build
```

Địa chỉ trang xuất bản là `https://nglelinh.github.io/audio-processing-self-learning/`. Nếu chèn hình bằng đường dẫn tương đối thay vì `site.imgurl`, ảnh có thể hiển thị trên máy cục bộ nhưng bị lỗi 404 khi xuất bản. Sau khi build xong, hãy mở thử một bài thuộc Chương 08 và một bài thuộc Chương 10 để xác nhận URL ảnh đều chứa `/audio-processing-self-learning/img/generated/`.

## Quản trị nội dung và ranh giới kho sản phẩm

Mọi thay đổi về khung chương trình cần được ghi nhận trong `COURSE_OUTLINE.md`. Quy ước trích dẫn chuẩn được lưu trong `AGENTS.md`, xoay quanh các nguồn chính thức: DeepFilterNet (cùng DeepFilterNet2/3), DNS Challenge, WebRTC APM, SpeexDSP, RNNoise, SI-SDR, DNSMOS, ONNX Runtime và `tract` (các tên mô hình khảo sát chỉ giữ ở mức điểm tên). Các bài học chỉ tham khảo tài liệu công khai của [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) và không nhận bản vá trực tiếp tại đó; mọi thử nghiệm của học viên đều thực hiện trên nhánh fork cá nhân hoặc thư mục `capstone/`.

## Mẫu phiếu theo dõi bảo trì (Issue)

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

Chỉ mở phiếu bảo trì khi đã liệt kê đủ cả tệp tiếng Anh lẫn tiếng Việt; một bản vá chỉ cập nhật riêng tiếng Anh được coi là chưa hoàn tất.

## Mini-lab

Từ thư mục gốc của kho khóa học, kiểm tra sự tồn tại của script sinh hình và xác nhận mọi bài tiếng Anh từ Chương 08 đến Chương 10 đều nhúng ảnh qua `site.imgurl`:

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

**Kết quả kỳ vọng**

```text
script_ok
bad none
```

**Lỗi thường gặp.** Chỉnh sửa trực tiếp tệp PNG bằng phần mềm đồ họa rồi bỏ quên script sinh hình (lần chạy script kế tiếp sẽ ghi đè mất chỉnh sửa đó); cập nhật số liệu lab ở bản tiếng Anh nhưng để sót số cũ ở bản tiếng Việt; sao chép nhầm `baseurl` từ kho khác khiến toàn bộ ảnh bị lỗi 404; hoặc mở pull request “sửa bài học” bằng cách chỉnh sửa kho sản phẩm chung.

## Bài tập

1. Đối chiếu README hiện hành của gói npm với bài 09-01 và chỉ ra một nguy cơ sai lệch thông tin theo thời gian.
2. Tạo thử một sửa lỗi chính tả nhỏ ở bài tiếng Anh trên nhánh cục bộ và đồng bộ sửa đổi tương ứng sang tệp tiếng Việt trong cùng một commit (không đẩy lên kho chính trừ khi bạn đang phụ trách bảo trì).
3. Chạy `bundle exec jekyll build` và ghi lại mọi cảnh báo liên quan đến Chương 08–10.
4. Điền mẫu phiếu bảo trì cho tình huống giả định phiên bản `1.4.0` bỏ tiền tố `v2/`, liệt kê đủ cả tệp EN và VI.
5. Nêu chính xác câu lệnh sinh hình và hai quy tắc đường dẫn bắt buộc khi thêm một hình minh họa mới.

### Gợi ý đáp án

1. Các dạng sai lệch phổ biến là bổ sung phương thức công khai mới hoặc thay đổi tiền tố đường dẫn CDN; cần trích dẫn đúng dòng tương ứng trong README.
2. Gộp cả hai tệp vào cùng một PR và giữ nguyên trường `lang` trong YAML frontmatter.
3. Nếu môi trường máy chưa cài Jekyll, ghi trung thực “jekyll not run” thay vì tự tạo nhật ký build giả.
4. Liệt kê đầy đủ đường dẫn cả bản EN và VI; mục hình ảnh ghi “none” nếu sơ đồ không thay đổi.
5. Chạy `python3 scripts/generate_course_figures.py` để xuất tệp vào `img/generated/<name>.png`, và nhúng trong bài bằng `{{ site.imgurl }}/generated/<name>.png`.

## Video tham khảo

- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, tiếng Anh. **Xem trước.** Các chi tiết về runtime và đóng gói thường xuyên thay đổi — mọi phiên bản được ghim trong bài đều cần được rà soát định kỳ trong changelog.
- [Group calling architectures in WebRTC: MCU, SFU & P2P](https://www.youtube.com/watch?v=d2N0d6CKrbk) — Tsahi Levent-Levi, tiếng Anh. Dù SDK có đổi tên hàm hook, nền tảng kiến trúc SFU, MCU và mesh vẫn là chuẩn mực để đối chiếu độ chính xác của tài liệu.
- [What is a CDN (Content Delivery Network) and How does a CDN Work?](https://www.youtube.com/watch?v=rIAIzf6utOc) — Cloudflare, tiếng Anh. Hành vi lưu đệm tại biên so với máy chủ gốc là phần quan trọng cần lưu ý mỗi khi cập nhật đường dẫn tài nguyên trong changelog.
