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

Bộ khử nhiễu Mezon (Mezon noise suppression) đóng vai trò tình huống nghiên cứu thực tế (case study), không phải một giáo trình riêng biệt. Luồng công khai gồm: micro trình duyệt, track âm thanh cục bộ của LiveKit, và `DeepFilterNoiseFilterProcessor` từ gói npm `deepfilternet3-noise-filter` (phiên bản 1.3.0 trong khóa học này). Toàn bộ quá trình suy luận chạy trực tiếp trên thiết bị. Gói sẽ tải module WASM và gói nén ONNX DeepFilterNet3 từ đường dẫn gốc CDN mà bạn truyền qua `assetConfig.cdnUrl`. Từ phiên bản ≥ 1.2.0 (gồm 1.3.0), gói tự động thêm tiền tố `v2/`, nên hai tệp được tải là `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`, với đường dẫn ví dụ `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`. Bộ trọng số sử dụng gói DeepFilterNet3 gốc của Rikorose. Khi làm bài tập, bạn không chỉnh sửa trực tiếp kho sản phẩm chung [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression); hãy làm việc trên nhánh fork cá nhân hoặc thư mục công cụ đánh giá riêng.

![Đường publish LiveKit với DeepFilterNoiseFilterProcessor]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Hình. Luồng phát hành công khai: micro → `setProcessor` → `DeepFilterNoiseFilterProcessor` → mã hóa âm thanh → LiveKit. Tài nguyên CDN cấp cho processor; `setSuppressionLevel` và `setEnabled` là hai điều khiển lúc chạy. Khi tải tài nguyên lỗi, hệ thống vẫn phát hành âm thanh gốc chưa xử lý.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ lần theo được đủ 8 bước công khai từ micro tới khi phát hành track, chỉ sử dụng đúng các API công khai của gói, ánh xạ từng khối kiến trúc về các chương trước, và viết được bản phác thảo kiến trúc rõ ràng để giảng viên hướng dẫn đánh giá mà không cần truy cập mã nội bộ.

## Các tên giao diện công khai

Bề mặt API công khai gồm các thành phần sau:

| Thành phần | Vai trò |
|-----|---------|
| `DeepFilterNoiseFilterProcessor` | Processor dành cho LiveKit, duy trì đồ thị xử lý trên thiết bị |
| `DeepFilterNet3Core` | Lớp lõi mức thấp dùng cho đồ thị Web Audio độc lập ngoài LiveKit |
| `setProcessor` | Gắn processor vào track âm thanh cục bộ trước khi phát hành |
| `setSuppressionLevel(0–100)` | Điều chỉnh cường độ khử nhiễu trong lúc chạy |
| `setEnabled` | Chuyển sang bypass mà không giả vờ mô hình đang hoạt động |
| `assetConfig.cdnUrl` | **Đường dẫn gốc (base)** của CDN; không tự thêm `v2/` |

Mọi thông tin về truyền báo hiệu (signaling) của LiveKit có thể tra cứu tại [docs.livekit.io](https://docs.livekit.io/). Processor không quản lý token, phòng họp hay SFU. Lớp `DeepFilterNet3Core` là lựa chọn thay thế khi bạn không dùng `TrackProcessor` của LiveKit — đây vẫn là một phần chính thức của cùng gói npm.

## Tám bước trong luồng phát hành track

Hãy đọc kỹ một lần rồi đóng lại để tự viết lại trong phần mini-lab:

1. Trang web xin quyền micro và nhận về đối tượng `MediaStream`.
2. Bọc luồng đó thành một track âm thanh cục bộ (local audio track) của LiveKit — đây là đối tượng sẽ tiếp nhận processor.
3. Khởi tạo `DeepFilterNoiseFilterProcessor` (hoặc qua hàm factory `DeepFilterNoiseFilter(options)`) và truyền vào `assetConfig.cdnUrl` ở dạng đường dẫn gốc không có hậu tố `v2/`.
4. Gói phiên bản ≥ 1.2.0 (gồm 1.3.0) tự động tải `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`.
5. Gọi `setProcessor` để gắn processor lên track, đảm bảo tín hiệu được khử nhiễu trước bước mã hóa.
6. Phát hành (publish) track vào phòng họp; SFU chỉ nhận dòng âm thanh đã mã hóa, không nhận thông tin cấu hình CDN.
7. Trong cuộc gọi, dùng `setSuppressionLevel` (từ 0 đến 100) để thay đổi cường độ khử nhiễu mà không phải phát hành lại track.
8. Dùng `setEnabled(false)` để chuyển sang bypass; nếu tải WASM hoặc gói mô hình thất bại, hệ thống vẫn phải phát hành tín hiệu micro thô và hiển thị thông báo lỗi — một nút tham gia phòng bị treo không bao giờ là hành vi chấp nhận được.

Toàn bộ kiến trúc công khai chỉ gói gọn trong 8 bước trên. Module Rust `df-core` không nằm trong sơ đồ này; đó là nhánh mở rộng tùy chọn ở bài 09-03, không phải yêu cầu bắt buộc.

## Vai trò từng tầng và liên kết kiến thức

Tầng ứng dụng đảm nhiệm vòng đời phòng LiveKit (tham gia, tắt tiếng, rời phòng) theo phạm vi Chương 07. Tầng processor là `DeepFilterNoiseFilterProcessor` cùng luồng callback âm thanh phải hoàn thành trong giới hạn render quantum (Chương 05). Tầng tài nguyên gồm module WASM và gói nén ONNX đặt trên CDN (Chương 06 và 07). Kiến trúc mô hình bên trong thuộc dòng DeepFilterNet3 từ [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet), kết hợp tầng hệ số ERB và bộ lọc sâu trên phổ STFT (Chương 02 và 04). Hai điểm điều khiển chính là `setEnabled` và `setSuppressionLevel`, còn việc đánh giá chất lượng tuân theo Chương 08: SI-SDR khi có bản gốc sạch, DNSMOS khi không có, ghi chú nghe thử và RTF p95.

Lưu ý rằng bộ khử nhiễu và khử vọng tích hợp sẵn của trình duyệt vẫn tồn tại song song với processor này. Nếu bật đồng thời cả hai bộ khử nhiễu, bạn sẽ không thể xác định bên nào đang làm mất phụ âm. Hãy luôn ghi rõ trạng thái ràng buộc `noiseSuppression` của trình duyệt trong bảng kiểm tra.

## Mẫu phác thảo kiến trúc gửi giảng viên hướng dẫn

```markdown
## Mezon NS — architecture sketch
- Goal: khử nhiễu uplink trên thiết bị cho họp LiveKit
- Data path: mic → setProcessor(DeepFilterNoiseFilterProcessor) → publish
- Asset của bản ≥ 1.2.0 gồm 1.3.0: {cdnUrl}/v2/pkg/df_bg.wasm và {cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz
- Controls: setEnabled, setSuppressionLevel(0–100)
- Eval: SI-SDR trên cặp tổng hợp, DNSMOS hoặc n/a trên clip thật, ghi chú AB, RTF p95
- Non-goals: tải PCM lên mây để suy luận; sửa repo sản phẩm chung
- Stretch (tùy chọn): harness Rust df-core cá nhân, ghi passthrough cho đến khi có backend thật
```

| Chương | Câu hỏi bản phác thảo cần làm rõ |
|--------|------------------------|
| 02 | Tần số lấy mẫu và cấu hình khung/hop (không tự suy diễn API bộ đệm ẩn) |
| 03 | Có đang bật song song AEC/NS của trình duyệt hay không |
| 04 | Lý do chọn DeepFilterNet3 và sự đánh đổi của thanh mức khử nhiễu |
| 05 | Cách xử lý khi callback vượt hạn render quantum |
| 06 | Cấu trúc WASM cùng gói ONNX, và quy tắc tự nối `v2/` từ bản ≥ 1.2.0 |
| 07 | Quy trình gắn `setProcessor` và cấu hình `assetConfig.cdnUrl` |
| 08 | Chỉ số nào bắt buộc ghi `n/a` trên bản ghi thực tế |

## Mini-lab

Soạn tệp `publish-path.md` liệt kê đúng 8 bước đánh số từ bước lấy micro đến bước phát hành track, chỉ sử dụng các tên API công khai, sau đó chạy script kiểm tra:

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

**Kết quả kỳ vọng**

```text
steps 8
missing none
```

**Lỗi thường gặp.** Thêm bước thứ 9 gọi tới một lớp nội bộ không công khai; đưa sẵn `v2/` vào giá trị `cdnUrl`; cho cuộc gọi dừng hẳn khi tải tài nguyên lỗi; mô tả Rust `df-core` như yêu cầu bắt buộc; hoặc trỏ bài lab vào kho sản phẩm chung như một phần bài tập.

## Bài tập

1. Viết lại bản phác thảo kiến trúc một trang bằng văn phong của riêng bạn, ghi đầy đủ URL tài nguyên.
2. Vẽ nhánh xử lý tình huống CDN bị chặn; ở nhánh này, luồng âm thanh nào vẫn được phát hành vào phòng?
3. Liệt kê 3 sự kiện telemetry hữu ích không chứa dữ liệu PCM (ví dụ mã phản hồi HTTP khi tải tài nguyên, thời gian khởi tạo theo mili giây, số lần bật/tắt `setEnabled`).
4. Phân biệt rõ trường hợp nào trong thiết kế nên dùng `DeepFilterNet3Core` và trường hợp nào dùng `DeepFilterNoiseFilterProcessor`.
5. Giải thích vì sao mọi thực nghiệm cần thực hiện trên fork cá nhân thay vì kho GitHub sản phẩm chung.

### Gợi ý đáp án

1. Ghi đủ cả hai tệp dưới nhánh `v2/` và nêu rõ tiền tố này do gói tự động bổ sung.
2. Khi tải tài nguyên thất bại, ứng dụng phát hành trực tiếp tín hiệu micro gốc chưa lọc kèm thông báo lỗi, không chặn thao tác vào phòng.
3. Chỉ thu thập bộ đếm và thời lượng xử lý; tuyệt đối không gửi mẫu sóng hay bản ghi giọng nói trong cuộc họp.
4. Luồng phát hành trên LiveKit dùng `DeepFilterNoiseFilterProcessor` với `setProcessor`; ứng dụng Web Audio tự dựng có thể gọi trực tiếp `DeepFilterNet3Core`.
5. Bài học chỉ dựa trên README và API công khai; các thay đổi thử nghiệm phải tách riêng trong fork cá nhân hoặc thư mục harness độc lập.

## Video tham khảo

- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. **Xem trước.** Video trình bày kiến trúc STFT trên thiết bị và hệ số thời gian thực — chính là mô hình cốt lõi chạy bên trong đường truyền công khai của Mezon.
- [Group calling architectures in WebRTC: MCU, SFU & P2P](https://www.youtube.com/watch?v=d2N0d6CKrbk) — Tsahi Levent-Levi, tiếng Anh. Giải thích cách SFU chuyển tiếp các track đã phát hành ở phía máy chủ.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Minh họa các yêu cầu thực tế mà một hệ thống khử nhiễu “trên thiết bị, trước mã hóa” phải đáp ứng trong sản phẩm gọi thoại.
