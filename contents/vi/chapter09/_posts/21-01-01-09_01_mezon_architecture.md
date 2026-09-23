---
layout: post
title: "09-01 Tour kiến trúc Mezon NS"
chapter: "09"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Mezon noise suppression là case study sản phẩm, không phải giáo trình thứ hai. Đường công khai là micro trình duyệt, track cục bộ của LiveKit, và `DeepFilterNoiseFilterProcessor` từ gói npm `deepfilternet3-noise-filter` (bản 1.3.0 trong khóa này). Suy luận ở trên thiết bị. Gói tải bản WASM và archive ONNX DeepFilterNet3 từ CDN base bạn truyền trong `assetConfig.cdnUrl`. README vẫn nói mọi bản từ 1.2.0 trở đi tự thêm `v2/`. Client 1.3.0 đã phát hành thì không: `AssetLoader.getAssetUrls()` xin `{cdnUrl}/v3/pkg/df_bg.wasm` và `{cdnUrl}/v3/models/DeepFilterNet3_onnx.tar.gz` (ghi chú phát hành “bump assets cdn version to v3”, 2026-06-26). Bạn học đường đó. Bạn không sửa repo chung [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) như bài tập. Fork cá nhân hoặc harness bên ngoài là workspace. Cây giảng viên tại `/Users/nguyenlelinh/ncc/mezon-noise-suppression` là tùy chọn, không bắt buộc để xong lab.

![Đường publish LiveKit với DeepFilterNoiseFilterProcessor]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Hình. Chỉ đường publish công khai: mic, `setProcessor`, `DeepFilterNoiseFilterProcessor`, audio đã mã hóa, LiveKit. Asset CDN nuôi processor. `setSuppressionLevel` và `setEnabled` là nút lúc chạy. Khi asset lỗi, vẫn publish audio chưa xử lý.*

## Bạn làm được gì sau bài này

Bạn truy được tám bước công khai từ micro tới track đã publish, chỉ gọi API mà khóa này coi là công khai, và ánh xạ từng hộp về chương trước. Bạn cũng viết được phác kiến trúc để advisor chấm mà không mở mã riêng.

## Tên công khai được dùng

Ở trên bề mặt này:

| Tên | Vai trò |
|-----|---------|
| `DeepFilterNoiseFilterProcessor` | Processor LiveKit, giữ đồ thị trên thiết bị |
| `DeepFilterNet3Core` | Lõi thấp hơn cho đồ thị WebAudio không phải LiveKit |
| `setProcessor` | Gắn processor vào track cục bộ trước khi publish |
| `setSuppressionLevel(0–100)` | Mức mạnh lúc chạy |
| `setEnabled` | Bypass, không giả vờ mô hình đã chạy |
| `assetConfig.cdnUrl` | **Base** CDN. Đừng tự nối `v2/` hay `v3/` |

Tài liệu LiveKit là chỗ tra signaling: [docs.livekit.io](https://docs.livekit.io/). Processor không giữ token, room, hay SFU. `DeepFilterNet3Core` là lối thoát khi bạn không ở trong TrackProcessor của LiveKit. Nó vẫn là cùng gói sản phẩm, không phải lớp riêng bạn bịa.

## Tám bước đường publish

Đọc một lần, rồi đóng lại và viết lại trong mini-lab.

1. Trang xin micro và nhận `MediaStream`.
2. Bạn bọc stream đó thành local audio track của LiveKit. Track là đối tượng nhận processor.
3. Bạn tạo `DeepFilterNoiseFilterProcessor` và truyền `assetConfig.cdnUrl` là base CDN, không có hậu tố `v2/` hay `v3/`.
4. Gói 1.2.x, theo README, xin `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`. Bản 1.3.0 đã cài xin cùng hai tên file dưới `v3/`. Hãy theo `getAssetUrls()` của đúng bản bạn cài.
5. Bạn gọi `setProcessor` với processor đó để mẫu được enhance trước khi mã hóa.
6. Bạn publish track lên room. SFU nhận audio đã mã hóa, không nhận thông tin CDN của bạn.
7. Sau đó `setSuppressionLevel` từ 0 đến 100 đổi mức mạnh mà không publish lại.
8. `setEnabled(false)` bỏ qua mô hình. Nếu WASM hoặc archive không tải được, bạn vẫn publish micro chưa xử lý và hiện lỗi. Nút join chết không phải tính năng khử nhiễu.

Đó là cả câu chuyện công khai. Rust `df-core` không nằm trên sơ đồ này. Nó là phần kéo tùy chọn ở bài 09-03, không phải sản phẩm thứ hai bạn phải vẽ mới đậu.

## Từng lớp để làm gì

Lớp ứng dụng là room LiveKit: vào, mute, rời. Chương 07 giữ ranh giới đó. Lớp processor là `DeepFilterNoiseFilterProcessor` cùng callback audio phải xong trong quantum render (chương 05). Lớp asset là module WASM và tar ONNX trên CDN (chương 06 và 07). Mô hình các asset đó chạy là dòng DeepFilterNet3 từ [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet): tầng gain ERB cộng deep filter trên STFT, nên chương 02 và 04 là điều kiện. Nút là `setEnabled` và `setSuppressionLevel`. Đánh giá là chương 08: SI-SDR khi có tham chiếu sạch, DNSMOS khi không, ghi chú nghe, và RTF p95.

Khử nhiễu và khử echo của trình duyệt vẫn đứng cạnh processor này. Nếu cả hai chạy, bạn không biết cái nào ăn phụ âm. Ghi ràng buộc `noiseSuppression` bạn đã đặt. Đó là mục checklist, không phải lớp riêng.

## Phác cho advisor

```markdown
## Mezon NS — architecture sketch
- Goal: khử nhiễu uplink trên thiết bị cho họp LiveKit
- Data path: mic → setProcessor(DeepFilterNoiseFilterProcessor) → publish
- Asset của bản 1.3.0 đã cài: {cdnUrl}/v3/pkg/df_bg.wasm và {cdnUrl}/v3/models/DeepFilterNet3_onnx.tar.gz (README vẫn ghi v2/ cho ≥ 1.2.0)
- Controls: setEnabled, setSuppressionLevel(0–100)
- Eval: SI-SDR trên cặp tổng hợp, DNSMOS hoặc n/a trên clip thật, ghi chú AB, RTF p95
- Non-goals: tải PCM lên mây để suy luận; sửa repo sản phẩm chung
- Stretch (tùy chọn): harness Rust df-core cá nhân, ghi passthrough cho đến khi có backend thật
```

| Chương | Câu phác phải trả lời |
|--------|------------------------|
| 02 | Sample rate và frame/hop, không bịa API buffer ẩn |
| 03 | AEC/NS của trình duyệt có bật cùng lúc không |
| 04 | Vì sao mô hình là DeepFilterNet3 và núm mức đánh đổi gì |
| 05 | Callback trễ quantum thì sao |
| 06 | WASM và archive ONNX, gồm tiền tố mà client đã cài thêm (`v3/` trên 1.3.0) |
| 07 | `setProcessor` và `assetConfig.cdnUrl` |
| 08 | Metric nào là `n/a` trên ghi thật |

## Mini-lab

Viết `publish-path.md` với đúng tám bước đánh số từ micro tới publish. Chỉ dùng tên công khai. Rồi chạy:

```python
import re
from pathlib import Path
text = Path("publish-path.md").read_text()
steps = re.findall(r"(?m)^\s*(\d+)\.\s+\S", text)
need = [
    "DeepFilterNoiseFilterProcessor",
    "setProcessor",
    "setSuppressionLevel",
    "setEnabled",
    "cdnUrl",
    "df_bg.wasm",
    "DeepFilterNet3_onnx.tar.gz",
]
missing = [n for n in need if n not in text]
print("steps", len(steps))
print("missing", missing or "none")
```

Đầu ra kỳ vọng:

```text
steps 8
missing none
```

Kiểu hỏng: bước thứ chín gọi lớp riêng; nhét `v2/` vào chính `cdnUrl`; dừng cuộc gọi khi asset lỗi; mô tả Rust `df-core` là bắt buộc; trỏ lab vào `/Users/nguyenlelinh/ncc/mezon-noise-suppression` như thể cây đó là một phần bài.

## Bài tập

1. Điền phác advisor bằng lời bạn, một trang, URL asset viết đủ.
2. Vẽ nhánh CDN bị chặn. Nhánh thành công vẫn publish audio. Audio nào?
3. Liệt kê ba sự kiện telemetry không tải PCM (ví dụ mã HTTP asset, mili giây init, số lần lật `setEnabled`).
4. Nói chỗ nào trong thiết kế được dùng `DeepFilterNet3Core`, và chỗ nào bắt buộc `DeepFilterNoiseFilterProcessor`.
5. Giải thích vì sao fork cá nhân là workspace còn repo GitHub chung thì không.

### Gợi ý đáp án

1. Gồm cả hai file dưới tiền tố mà client đã cài thêm (`v3/` trên 1.3.0) và nói tiền tố là của gói, không phải của bạn.
2. Khi lỗi, publish mic chưa xử lý và hiện lỗi. Đừng chặn room.
3. Chỉ bộ đếm và thời gian. Không mẫu, không bản ghi lời trong room.
4. Đường publish LiveKit dùng processor và `setProcessor`. Trang WebAudio tự viết có thể dùng core. Đừng bịa thêm phương thức.
5. Bài khóa đọc README và API công khai. Thí nghiệm nằm ở fork hoặc harness của bạn.
