---
layout: post
title: "09-03 Lộ trình Rust native (df-core) tùy chọn"
chapter: "09"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter09
lesson_type: required
draft: false
---

Luồng chạy chính thức được hỗ trợ của Mezon là gói WASM bên trong `deepfilternet3-noise-filter`: gồm trọng số ONNX, bản dựng WASM SIMD, cấu trúc CDN `v2/` (được gói tự động thêm từ bản ≥ 1.2.0, bao gồm 1.3.0) và AudioWorklet. Crate Rust tạm gọi là `df-core` chỉ là **nhánh mở rộng tùy chọn thay thế cho hộp WASM đó**, phục vụ công cụ dòng lệnh (CLI) trên máy tính hoặc tích hợp native trong không gian làm việc cá nhân của bạn. Đây không phải sản phẩm thứ hai, không phải yêu cầu bắt buộc để hoàn thành khóa học và không nằm trong kho mã nguồn sản phẩm. Nếu phiên bản backend ban đầu chỉ sao chép thẳng mẫu đầu vào sang đầu ra, bắt buộc phải ghi rõ là **passthrough**, tuyệt đối không ghi “NS works” cho một bộ chép thẳng.

![Đường WASM trên thiết bị của deepfilternet3-noise-filter]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Hình. Luồng phát hành sản phẩm đi từ PyTorch sang ONNX, biên dịch thành WASM phân phối qua CDN `v2/` rồi chạy trong AudioWorklet. Nhánh Rust `df-core` chỉ là phương án mở rộng thay cho hộp WASM này, không phải một sản phẩm song song.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ nêu chính xác những tài nguyên luồng WASM tải về (`df_bg.wasm`, `DeepFilterNet3_onnx.tar.gz`), xác định các tham số mà bản thử nghiệm Rust cá nhân cần đồng bộ (độ dài khung/hop, tần số lấy mẫu, mô hình thực), biết cách kiểm chứng độ tương đương (parity) mà không tuyên bố khớp từng bit khi chưa đo, và giữ nguyên tắc không bao giờ đánh đồng backend rỗng với bộ khử nhiễu thực sự.

## Thành phần mặc định không cần thay thế

Phiên bản 1.3.0 (giống mọi bản ≥ 1.2.0) tải `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`, trong đó client tự nối `v2/` còn bạn chỉ truyền đường dẫn gốc (ví dụ `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`). Các điểm điều khiển công khai vẫn giữ nguyên: `DeepFilterNoiseFilterProcessor` hoặc `DeepFilterNet3Core`, `setProcessor`, `setSuppressionLevel(0–100)` và `setEnabled`. Việc thử nghiệm bằng Rust không bổ sung thêm API công khai nào vào gói npm; nếu muốn xây dựng CLI, hãy đặt độc lập trong kho cá nhân.

Các bài báo DeepFilterNet cho thấy việc cài đặt lại trên native đòi hỏi độ chính xác rất cao: âm thanh toàn dải 48 kHz, STFT với hop khoảng 10 ms, tầng hệ số ERB và bộ lọc sâu có thể kèm cửa sổ nhìn trước (look-ahead) ngắn tạo ra độ trễ thuật toán. Đạt cùng RTF không đồng nghĩa khớp dạng sóng: như bài 08-01 đã chứng minh, chỉ cần lệch 1 mẫu cũng khiến SI-SDR tụt từ 13.80 dB xuống −10.67 dB. Do đó, một bản Rust “hơi trễ một chút” sẽ cho điểm SI-SDR rất kém dù nghe qua có vẻ tương tự.

## Tổ chức không gian làm việc cá nhân (nếu chọn thực hiện)

Chỉ khởi tạo thư mục này trong fork hoặc kho cá nhân mới, không đặt vào kho sản phẩm chung:

```text
my-df-stretch/
  df-core/     # API khung của bạn
  df-cli/      # wav vào, wav ra, offline
  README.md    # câu đầu nói passthrough hoặc backend thật
```

Các mốc triển khai gợi ý theo thứ tự:

1. **Backend passthrough.** Hàm `process` trả về nguyên vẹn mẫu đầu vào. Dòng đầu tệp README ghi rõ trạng thái `passthrough`; các bài kiểm thử chỉ xác nhận độ dài và tính toàn vẹn bản sao, không kiểm tra mức giảm nhiễu.
2. **Bắt lỗi thiếu tài nguyên.** Khi thiếu đường dẫn tệp `.tar.gz` hoặc `.onnx`, chương trình phải dừng và báo lỗi rõ ràng, không âm thầm cho âm thanh đi thẳng rồi in thông báo “enhanced”.
3. **Nạp runtime suy luận thực.** Dùng [tract](https://github.com/sonos/tract) hoặc ONNX Runtime ([onnxruntime.ai/docs](https://onnxruntime.ai/docs/)) để chạy cùng gói mô hình DeepFilterNet3 mà CDN phục vụ; lựa chọn thực tế còn lại là [libDF](https://github.com/Rikorose/DeepFilterNet) từ kho nguồn gốc. Hãy chọn một phương án và cố định phiên bản.
4. **Đồng bộ cấu hình khung.** Ghi rõ độ dài hop, kích thước cửa sổ và tần số lấy mẫu song song với bản WASM, không tự đặt thêm API nội bộ cho Mezon.
5. **Đối chiếu trên tệp chuẩn.** Cho cùng một tệp WAV nhiễu đi qua luồng WASM công khai và qua CLI Rust của bạn, căn chỉnh độ trễ rồi tính SI-SDR **giữa hai tín hiệu đầu ra**, báo cáo giá trị thực và nghe thử. Lưu ý: SI-SDR cao giữa hai bản đầu ra chỉ chứng minh chúng khớp nhau, chưa tự chứng minh bản nào khớp giọng sạch.
6. **Điểm dừng trung thực.** Nếu bạn chỉ hoàn thành tới bước 1, kịch bản demo phải nói rõ “passthrough, noise suppression is not running”.

Về giấy phép, cần tuân thủ giấy phép gốc của DeepFilterNet (Apache-2.0 hoặc MIT, tương đồng với gói npm). Không commit trực tiếp tệp `.tar.gz` vào Git; thay vào đó hãy trỏ tới cấu trúc CDN hoặc hướng dẫn tải `models/` từ kho nguồn gốc.

## Kiểm chứng độ tương đương (parity) một cách trung thực

```text
căn delay hop
enh_wasm.wav  từ processor đã phát hành hoặc lượt WASM offline bạn viết script
enh_rust.wav  từ CLI của bạn
in SI-SDR(enh_wasm, enh_rust) sau khi căn
ghi float vào báo cáo
nếu backend là passthrough, bỏ so sánh này và nói vì sao
```

Khi chưa hoàn thành bước 3, bài kiểm tra đối chiếu được ghi nhận ở trạng thái **đang chờ**. Một đầu ra passthrough so với bộ khử nhiễu thực chắc chắn sẽ cho điểm rất thấp — và đó chính là dấu hiệu đúng của phép kiểm tra; không được nới lỏng dung sai để làm đẹp con số.

Sự đánh đổi giữa `tract` (hoặc ONNX Runtime) với việc gọi trực tiếp `libDF` nên được phân tích ngắn gọn trong báo cáo: runtime ONNX sử dụng trực tiếp tệp tài nguyên sẵn có trên CDN, còn `libDF` là engine gốc tạo ra bản WASM nên có thể bám sát trạng thái streaming hơn. Dù chọn hướng nào đều phải đo kiểm thực tế dựa trên nền tảng Chương 06.

## Tiêu chuẩn hoàn thành cho nhánh mở rộng

Nhánh mở rộng tùy chọn được coi là hoàn tất khi có tệp README đủ rõ để người khác tự biên dịch được, ghi nhãn trung thực `passthrough` nếu mới dừng ở bước khung, hoặc cung cấp CLI kèm chỉ số SI-SDR đối chiếu với đầu ra WASM nếu đã nạp mô hình thực. Lưu ý không trình bày client native như sản phẩm chính của Mezon — sản phẩm đang vận hành vẫn là gói npm trên luồng LiveKit ở bài 09-01.

## Mini-lab

Tạo tệp `df_core_status.md` chứa hai dòng trạng thái để script kiểm tra đọc:

```text
backend: passthrough
claim: noise suppression is not running
```

Nếu bạn đã nạp thành công mô hình thực, có thể thay bằng `backend: tract`, `backend: onnxruntime` hoặc `backend: libdf`, kèm dòng `claim: compared to wasm SI-SDR <float>`. Tuyệt đối không đặt `passthrough` cạnh tuyên bố rằng khử nhiễu đang chạy.

```python
from pathlib import Path
text = Path("df_core_status.md").read_text().lower()
ok_pass = "passthrough" in text and "not running" in text
ok_real = any(k in text for k in ("tract", "onnxruntime", "libdf")) and "si-sdr" in text
bad = "ns works" in text or "noise suppression works" in text
print("status", "ok" if (ok_pass or ok_real) and not bad else "fix")
```

**Kết quả kỳ vọng** (cho trạng thái mặc định chưa nạp mô hình):

```text
status ok
```

**Lỗi thường gặp.** Ghi “NS works” cho vòng lặp sao chép thẳng; commit tệp `DeepFilterNet3_onnx.tar.gz` vào kho Git; phụ thuộc vào đường dẫn cục bộ trên máy khác; mô tả Rust là bản sản phẩm còn WASM chỉ là bản demo; hoặc báo cáo số SI-SDR đối chiếu mà không ghi bước căn chỉnh thời gian.

## Bài tập

1. Liệt kê 5 mốc thực hiện nhánh Rust mà không cần GPU, đánh dấu rõ mốc nào vẫn ở trạng thái `passthrough`.
2. Đề xuất các bài kiểm thử đơn vị (unit test) không cần trọng số mô hình: kiểm tra độ dài khung, tính đồng nhất khi sao chép và xử lý lỗi thiếu tệp.
3. Viết một đoạn ngắn so sánh `tract` (hoặc ONNX Runtime) với `libDF` gốc khi làm backend cho nhánh mở rộng.
4. Quyết định rõ bạn có thực hiện nhánh Rust trong dự án cuối khóa hay không; nếu không, hãy nêu cụ thể hạng mục WASM bạn chọn thay thế.
5. Nêu đúng chiều so sánh SI-SDR trong bài kiểm tra độ tương đương: so sánh hai tín hiệu ước lượng với nhau, không so với khẩu hiệu.

### Gợi ý đáp án

1. Bước 1 và 2 là `passthrough`; từ bước 3 (nạp runtime thực) mới được sử dụng thuật ngữ “enhance”.
2. Kiểm tra tính đồng nhất: mẫu đầu ra bằng đúng mẫu đầu vào; kiểm tra thiếu tệp: chương trình thoát với mã lỗi khác 0 và không tạo tệp WAV “enhanced”.
3. Runtime ONNX dùng trực tiếp tệp mô hình phân phối qua CDN, còn `libDF` là engine gốc của tác giả; cả hai hướng đều bắt buộc đối chiếu trên tệp chuẩn.
4. Không chọn nhánh Rust vẫn hoàn thành trọn vẹn dự án cuối khóa miễn là các phần 09-01 và 09-04 được thực hiện đầy đủ và trung thực.
5. Tính `SI-SDR(wasm, rust)` sau khi đã bù độ trễ; giá trị `13.80` ở bài lab chỉ minh họa phương pháp, không phải mức điểm mục tiêu của sản phẩm.

## Video tham khảo

- [Zoom on Web: getting connected with advanced web technology](https://www.youtube.com/watch?v=nhTxJBgTywc) — Chrome for Developers, tiếng Anh. **Xem trước.** Xem phần về Rust `simd128` và cờ biên dịch — mốc hiệu năng WASM mà bất kỳ nhánh `df-core` native nào cũng cần so sánh cùng.
- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, tiếng Anh. Giới thiệu engine ONNX Runtime cho cùng loại đồ thị mà nhánh Rust phải nạp.
- [Sonic Boom! Audio Programming on Android and Chrome (Google I/O'19)](https://www.youtube.com/watch?v=EeQr0zfvF04) — Google for Developers, tiếng Anh. Ràng buộc thời gian của callback âm thanh vẫn giữ nguyên bất kể mã nguồn viết bằng JS hay Rust.
