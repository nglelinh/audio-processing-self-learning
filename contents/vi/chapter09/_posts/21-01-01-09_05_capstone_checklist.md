---
layout: post
title: "09-05 Checklist capstone & demo day"
chapter: "09"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Ngày demo là năm phút chứng minh đường publish, các metric, và các giới hạn đều có thật. Slide tiêu đề bóng mà không có số RTF và không có bản ghi dự phòng là trượt. Checklist này là sổ chạy hôm trước: lệnh, file, và các lỗi bạn sẽ tiêm có chủ đích.

![RTF so với quantum render của AudioWorklet]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Hình. RTF là thời gian tường của một quantum chia cho độ dài quantum. Trung bình dưới 1 vẫn có thể tràn nếu p95 hoặc p99 làm tràn callback. Hãy log p95, và để lần tải asset lúc khởi động ra ngoài con số đó.*

## Bạn làm được gì sau bài này

Bạn đi được đường audio, đường asset, và các file metric, tập script năm phút, và tiêm lỗi CDN mà cuộc gọi không chết. Bạn cũng trình một ví dụ nghe với tên điều kiện nhìn thấy được.

## Checklist kỹ thuật

Chép vào `capstone/notes/demo_checklist.md` và đánh dấu. Ô trống là fail cho đến khi bạn ghi `n/a` và lý do.

Đường audio:

- Quyền micro chạy trên máy bạn sẽ demo.
- `setEnabled(true)` và `setEnabled(false)` đều để lại track đã publish. Nếu UI phải vào lại phòng, ghi giới hạn đó.
- `noiseSuppression` của trình duyệt được ghi bật hoặc tắt, để bạn không gán công cho `DeepFilterNoiseFilterProcessor` trong khi suppressor của trình duyệt mới là người làm.
- Rời room không rò thêm audio context nghe được ở lần vào sau.

Tải mô hình:

- Lần lạnh lấy `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` với gói ≥ 1.2.0, gồm 1.3.0. Trên panel mạng, xác nhận bạn **không** nhét `v2/` vào trong `assetConfig.cdnUrl`.
- Lần vào thứ hai dùng cache, hoặc bạn ghi là không.
- Khi CDN bị chặn, cuộc gọi vẫn publish audio chưa xử lý và UI hiện lỗi. Ảnh hoặc một dòng log vào `capstone/notes/`.

Metric, từ `capstone/metrics/suite.md`:

- Sáu cột: clip id, condition, SI-SDR hoặc `n/a`, DNSMOS hoặc `n/a`, listening note, RTF p95.
- Ít nhất một hàng thật với SI-SDR `n/a`.
- RTF p95 ghi tên thiết bị. Nếu bạn chỉ dogfood, ô là `n/a`, không phải 0.2 đoán.
- Phiên bản: bản `deepfilternet3-noise-filter`, tên archive mô hình, bản DNSMOS hoặc `not run`.

Vệ sinh demo:

- Bản ghi dự phòng phát được nếu mic sống hỏng.
- Tai nghe để trên bàn.
- Một clip quán hoặc babble, một clip bàn phím, một clip yên.

Rust, nếu bạn đã đụng: câu nói đầu khớp `df_core_status.md`. Passthrough nghĩa là bạn nói “noise suppression is not running”.

## Script năm phút

| Thời gian | Nói gì | File mở được |
|-----------|--------|----------------|
| 0:00–0:40 | Nhiễu uplink, trên thiết bị, publish LiveKit | `design/sketch.md` |
| 0:40–1:20 | Tám bước công khai, không lớp riêng | `publish-path.md` |
| 1:20–2:30 | Phát thô và đã xử lý, gọi tên điều kiện | wav dự phòng |
| 2:30–3:30 | Một hàng suite cải thiện, một hàng không | `metrics/suite.md` |
| 3:30–4:20 | Kết quả giả thuyết, kể cả fail nếu đó là sự thật | `design/hypothesis.md` |
| 4:20–5:00 | Giới hạn: ngôn ngữ, thiết bị, bản DNSMOS, trạng thái Rust | `notes/limits.md` |

Nếu tập vượt năm phút, cắt slide kiến trúc trước khi cắt hàng phản ví dụ. Hàng không cải thiện là bằng chứng bạn hiểu bản đồ.

## Tiêm lỗi

Chặn host CDN (offline trong DevTools, hoặc `cdnUrl` sai) rồi vào phòng. Kỳ vọng: room vẫn có audio; processor không giả mô hình đã chạy; ghi chú nói `setEnabled` còn tới được không. Khôi phục mạng và tải lại. Kỳ vọng: WASM và tar.gz tải từ đường `v2/`. Nếu lần tiêm nào làm khác, hành vi đó là giới hạn, không phải bất ngờ để giấu.

Tiêm RTF, nếu bạn có log: kéo tới quantum tệ nhất, không phải trung bình. Thanh tràn trên hình là kiểu hỏng. p95 bạn chưa tính thì để `n/a`.

## Mini-lab

Đưa file checklist qua checker sau khi bạn đã chép các heading.

```python
from pathlib import Path
text = Path("capstone/notes/demo_checklist.md").read_text().lower()
need = [
    "setenabled",
    "noisesuppression",
    "df_bg.wasm",
    "deepfilternet3_onnx.tar.gz",
    "si-sdr",
    "dnsmos",
    "rtf p95",
    "backup",
    "passthrough",
]
missing = [n for n in need if n not in text]
print("missing", missing or "none")
```

Đầu ra kỳ vọng:

```text
missing none
```

Dùng token `passthrough` kể cả khi dòng của bạn là “Rust: not attempted, so not a passthrough claim.” Checker chỉ cần từ đó để script demo không quên luật phần kéo. Kiểu hỏng: tick RTF mà không có thiết bị; bản ghi dự phòng là câu khác clip sống; gõ `v2/` vào `cdnUrl` trong khi gói cũng thêm, nên request 404; gọi bản Rust passthrough là “NS works”.

## Bài tập

1. Canh một lần tập. Ghi thời gian tường vào `capstone/notes/rehearsal.txt`. Cắt đến khi còn ≤ 5:00.
2. Làm chặn CDN. Dán hành vi publish quan sát được dưới checklist.
3. Đổi phần giới hạn với một bạn. Mỗi người phải tìm một câu nhận quá.
4. Liệt kê file từ 09-04 bạn sẽ zip hoặc push từ fork. Loại repo sản phẩm.
5. Chỉ thanh tràn trên hình RTF và nói bạn sẽ báo gì nếu log chỉ có trung bình.

### Gợi ý đáp án

1. Cắt kiến trúc trước hàng metric xấu.
2. Dòng trung thực kỳ vọng: “audio đã publish, mô hình chưa tải, UI hiện lỗi” hoặc đúng cái bạn thấy.
3. Nhận quá điển hình: ngôn ngữ SI-SDR trên clip thật, hoặc DNSMOS không có phiên bản.
4. `capstone/design`, `audio`, `metrics`, `notes`. Không đường dưới cây Mezon chung.
5. Báo trung bình và đặt RTF p95 là `n/a`. Đừng bịa phân vị.
