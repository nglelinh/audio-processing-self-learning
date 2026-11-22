---
layout: post
title: "06-01 ONNX, tract và ORT"
chapter: "06"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter06
lesson_type: required
draft: false
---

Khử nhiễu trực tiếp trên thiết bị gần như luôn yêu cầu **xuất (export)** đồ thị đã huấn luyện sang một runtime suy luận chuyên biệt. **ONNX** (định dạng trao đổi đồ thị) đóng vai trò tệp trung gian; **ONNX Runtime (ORT)** là engine đa nền tảng phổ biến (bao gồm cả phiên bản Web); còn **tract** là thư viện suy luận viết bằng Rust khi bạn cần một chuỗi thực thi thuần Rust. Gói `deepfilternet3-noise-filter` **1.3.0** không đưa PyTorch vào trình duyệt: ghi chú phát hành công khai cho biết đường thực thi WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) được xây dựng lại với **tract 0.23.3**. Trình duyệt chỉ tải module đã biên dịch cùng tệp nén `DeepFilterNet3_onnx.tar.gz`, chứ không chạy một session Python. Bài học này xác định tiêu chí chọn runtime, hợp đồng đầu vào/đầu ra khi chạy streaming, và các lỗi kích thước tensor (shape) khiến đồ thị chạy được trong notebook nhưng lại lỗi khi đưa vào AudioWorklet (callback xử lý âm thanh trên luồng thời gian thực).

![Đồ thị ONNX được xuất thành module WASM, trình duyệt tải cạnh kho mô hình]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Hình. ONNX là định dạng tệp trao đổi; `tract` hoặc ORT đảm nhiệm việc thực thi; cuối cùng trình duyệt khởi tạo module WASM.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ giải thích được vai trò định dạng trao đổi của ONNX trong tăng cường giọng nói, so sánh được ORT với `tract` cho ứng dụng trình duyệt và tệp thực thi Rust, liệt kê được các lỗi export chỉ bộc lộ khi chạy từng hop, đồng thời phân biệt được tensor ảnh kiểu NCHW với khung đặc trưng kiểu DeepFilter `[1, T, F]` trước khi khởi tạo session.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao AudioWorklet không chứa framework huấn luyện.
- **10–25 phút** — Đồ thị tính toán, initializer, phiên bản opset và bên nào đảm nhiệm STFT.
- **25–40 phút** — So sánh ORT với `tract`, bao gồm phiên bản `tract` cố định ở bản 1.3.0.
- **40–50 phút** — Trục động, tensor trạng thái và kiểm tra shape.
- **50–60 phút** — Thực hành mini-lab, bẫy thường gặp và làm bài tập.

## Giải thích cốt lõi

### Tệp ONNX thực sự chứa gì

Một tệp ONNX biểu diễn đồ thị tính toán gồm các tensor vào/ra có tên, danh sách toán tử (như `Conv`, `GRU`, `MatMul`) và bộ trọng số lưu trong mục initializer. Framework huấn luyện xuất ra tệp này, còn runtime suy luận sẽ tối ưu hóa và thực thi nó. Trong bài toán tăng cường giọng nói, đồ thị có thể tích hợp sẵn bước trích xuất đặc trưng hoặc kỳ vọng ứng dụng tự chạy STFT ở bên ngoài session. Các mô hình họ DeepFilter thường đi theo hướng thứ hai: runtime nhận từng khung phổ làm đầu vào, còn bước cộng chồng lấp (overlap-add) nằm ở phía ngoài. Nếu hai bên lệch nhau về bước nhảy (hop), cửa sổ hoặc số bin tần số, session vẫn trả về tensor hợp lệ nhưng âm thanh đầu ra sẽ bị sai.

### Cố định phiên bản opset và runtime

Tập toán tử của ONNX được đánh số theo **opset**. Một mô hình xuất bằng opset 17 có thể không nạp được trên phiên bản ORT cũ hơn. Do đó, cần cố định đồng thời ba yếu tố: phiên bản opset khi xuất, phiên bản ORT hoặc `tract` đưa vào sản phẩm, và một tác vụ CI kiểm tra nạp đúng tệp `.onnx` trên chính runtime sẽ phát hành. Ghi chú phát hành bản 1.3.0 của `deepfilternet3-noise-filter` nêu rõ phiên bản `tract` **0.23.3** cho bản dựng WASM. Đây là thông tin phát hành thực tế, không phải lý do để bỏ qua bước kiểm tra toán tử: `tract` và ORT không hỗ trợ hoàn toàn cùng một tập toán tử. Một đồ thị mở được bằng `onnxruntime` trong Python vẫn có thể gặp lỗi trên `tract` nếu lớp lọc sâu (deep filter) tùy biến chưa được gộp thành các toán tử được hỗ trợ.

### So sánh ORT và `tract`

| Tiêu chí | ONNX Runtime | tract |
|----------|--------------|-------|
| Ngôn ngữ | C/C++, Python, Java, C#, JS/WASM | Ưu tiên Rust |
| Đường triển khai web | `onnxruntime-web` | Không phải đường trình duyệt mặc định |
| Tối ưu hóa | Tối ưu đồ thị và execution provider | Đồ thị thuần Rust, phù hợp streaming |
| Phù hợp sản phẩm | Đồng nhất trên nhiều nền tảng | Đường Rust được ghi chú WASM 1.3.0 đề cập |
| Độ phủ toán tử | Rộng theo mặc định | Cần kiểm chứng trực tiếp trên bản xuất DeepFilter |

Hãy chọn ORT khi cần một tệp ONNX dễ kiểm chứng từ Python đi kèm backend Web có tài liệu đầy đủ. Hãy chọn `tract` khi sản phẩm phát hành là tệp thực thi Rust và bạn đã kiểm tra xong toàn bộ toán tử. Trên trình duyệt, gói của Mezon sử dụng WASM biên dịch từ ngăn xếp `libDF` của DeepFilter với `tract` được nhắc tới trong changelog 1.3.0. Phần thực hành `df-core` tùy chọn ở Chương 09 là nơi bạn trực tiếp ghép nối với `tract`; không nên biến wrapper npm thành một mô hình thứ hai.

### Quy ước trục dữ liệu khi chạy streaming

Mô hình streaming cần khai báo khung đầu vào có trục thời gian đúng bằng một hop, đi kèm các tensor trạng thái hồi tiếp ở đầu vào và đầu ra. Hợp đồng tiêu chuẩn ở đây là `features` có kích thước `[1, T, F]` với `T = 1` trong callback, cùng cặp `state_in` / `state_out` có kích thước cố định. Trục batch động hữu ích khi chạy kiểm thử offline, nhưng trong callback âm thanh gần như luôn bằng 1. Cần khai báo rõ ràng các trục này khi xuất mô hình; một số kịch bản kiểm thử offline vô tình cố định cứng `T = 100` lúc export, khiến đồ thị vẫn nạp thành công nhưng từ chối mọi hop thời gian thực.

Định dạng NCHW như `[1, 3, 224, 224]` là quy ước cho dữ liệu ảnh. Dù chiều đầu tiên bằng 1, tensor bậc 4 vẫn sai kích thước đối với khung đặc trưng DeepFilter; hợp đồng của bài học chỉ chấp nhận tensor bậc 3 với chiều batch bằng 1. Bước triển khai thực tế sau bài kiểm tra minh họa này là khởi tạo `ort.InferenceSession` và đối chiếu **tên đầu vào** khớp hoàn toàn với đồ thị, chứ không chỉ kiểm tra số chiều.

### Các lỗi thường gặp khi xuất mô hình

1. **Toán tử không được hỗ trợ** trong các lớp deep filter tùy biến: cần gộp thành các toán tử chuẩn của ONNX hoặc đăng ký toán tử mở rộng cho runtime, tránh tự đặt tên toán tử tùy tiện.
2. **Rẽ nhánh điều khiển (control-flow) và thao tác ghi đè (in-place)** cho kết quả khác nhau giữa quá trình huấn luyện và đồ thị đã xuất.
3. **Thiếu cổng truyền trạng thái** của GRU, khiến mô hình trở thành không trạng thái và gây hiện tượng bơm tiếng giữa các hop.
4. **Sót kiểu `float64`:** cần ép toàn bộ về `float32` trước khi lượng tử hóa hoặc biên dịch sang WASM.
5. **Lệch tiền xử lý:** phép tính STFT bằng NumPy lúc huấn luyện không khớp với STFT trong WASM khi chạy sản phẩm.

### Vì sao trình duyệt biên dịch trước một module chuẩn hóa

Gói `deepfilternet3-noise-filter` không yêu cầu trang web tự dựng session ORT. Hàm `DeepFilterNet3Core.initialize()` sẽ tải dữ liệu nhị phân WASM cùng tệp nén mô hình rồi gọi `WebAssembly.compile` trên luồng chính; hàm `createAudioWorkletNode` chỉ chạy sau khi biên dịch xong. Nhờ đó, phần việc nặng được tách hoàn toàn khỏi callback âm thanh (Chương 05). Dù vậy, ORT vẫn là công cụ chuẩn để kiểm tra độ tương đương số học trong Python cũng như cho các sản phẩm gọi trực tiếp `onnxruntime-web`. Khi đánh giá hiệu năng, luôn đo hệ số thời gian thực trên chính bản WASM phát hành vì thời gian chạy ORT trên Python thuộc một môi trường hoàn toàn khác.

## Mini-lab

Nếu đã cài đặt ONNX Runtime, bạn có thể kiểm tra nhanh bằng lệnh tùy chọn `python3 -c "import onnxruntime"`. Phần bắt buộc của bài lab là viết chương trình kiểm tra kích thước tensor: lưu đoạn mã sau thành `shape_check.py` và chạy `python3 shape_check.py`.

```python
def verdict(shape):
    rank = len(shape)
    if rank == 4:
        return "NCHW rejected-by-df-frame"
    if rank == 3 and shape[0] == 1:
        return "DF frame [1, T, F] accepted"
    return "rejected"

for shape in [(1, 3, 224, 224), (1, 1, 96), (96,)]:
    print(f"{list(shape)} -> {verdict(shape)}")
```

**Kết quả kỳ vọng**

```text
[1, 3, 224, 224] -> NCHW rejected-by-df-frame
[1, 1, 96] -> DF frame [1, T, F] accepted
[96] -> rejected
```

**Lỗi thường gặp**

- Coi kết quả “accepted” ở đây là bằng chứng cho thấy đồ thị thực tế sẽ chạy trơn tru; đoạn mã chỉ kiểm tra bậc tensor và chiều batch bằng 1.
- Khi chuyển sang `ort.InferenceSession`, lỗi **lệch tên đầu vào của session (session input name mismatch)** rất hay xảy ra: shape đúng nhưng mã gọi tên `input` trong khi đồ thị đặt là `feat_erb` hoặc tên khác. Hãy luôn kiểm tra bằng `session.get_inputs()`.
- Trục thời gian bị cố định cứng `T = 100` lúc xuất vẫn vượt qua bài kiểm tra bậc lỏng lẻo nhưng sẽ báo lỗi ngay khi nhận hop độ dài 1.

## Bẫy thường gặp

- Phát hành các tệp ONNX khác nhau theo từng hệ điều hành mà không có bài kiểm thử nạp tự động.
- Bật execution provider CUDA cho sản phẩm cần chạy trên laptop chỉ có CPU.
- Mặc định rằng `tract` chạy được mọi mô hình mà ORT chấp nhận.
- Dùng chỉ số hệ số thời gian thực của ORT trên Python để ước lượng cho bản WASM.
- Gọi `createAudioWorkletNode` trước khi `initialize()` biên dịch xong module, khiến lớp core ném ngoại lệ.

## Bài tập

1. Lập bảng mô tả các tensor cho một hop GRU minh họa: nêu rõ tên, bậc tensor và tensor nào đóng vai trò trạng thái.
2. Chọn một phiên bản ORT cụ thể, tra cứu danh sách opset được hỗ trợ trong [tài liệu ONNX Runtime](https://onnxruntime.ai/docs/) và xác định phiên bản opset phù hợp để xuất mô hình.
3. Viết khoảng 150 từ phân tích việc chọn ORT hay `tract` cho một tiện ích mở rộng (extension) trên Chrome, sau đó phân tích lại cho một công cụ dòng lệnh (CLI) khử nhiễu viết bằng Rust.
4. Thiết kế một bước kiểm thử CI tự động báo lỗi khi đầu ra ONNX và bản tham chiếu PyTorch lệch quá ngưỡng SI-SDR quy định trên một đoạn âm thanh chuẩn.
5. Giải thích vì sao không thể đưa tensor kích thước `[1, 3, 224, 224]` vào mô hình xử lý khung âm thanh dù chiều batch bằng 1.

### Gợi ý đáp án

1. Bảng cần có `frame` dạng `[1, 1, F]`, cùng `state_in` và `state_out` có chung kích thước chiều ẩn. Nếu đồ thị không chứa toán tử FFT, ghi rõ bước STFT nằm ngoài session.
2. Phiên bản opset lúc xuất phải nằm trong danh sách mà runtime phát hành hỗ trợ, không tự động lấy opset mới nhất của framework huấn luyện.
3. Với extension trình duyệt: chọn runtime WASM phù hợp với ma trận trình duyệt hỗ trợ. Với CLI viết bằng Rust: chọn `tract` nếu kiểm tra toán tử đạt yêu cầu để tránh phụ thuộc thêm thư viện native. Cả hai phương án đều bắt buộc có bước kiểm chứng toán tử.
4. Cố định sẵn tệp âm thanh chuẩn, độ dài hop và ngưỡng sai số trong job CI; cho job báo lỗi cả khi thiếu tensor trạng thái đầu ra chứ không chỉ khi lệch SI-SDR.
5. Tensor bậc 4 tương ứng định dạng ảnh NCHW, trong khi hợp đồng khung đặc trưng trong mini-lab yêu cầu tensor bậc 3.

## Đọc thêm

- [Tài liệu ONNX Runtime](https://onnxruntime.ai/docs/), bao gồm các phần về lượng tử hóa và triển khai Web dùng ở các bài kế tiếp.
- [tract](https://github.com/sonos/tract), thư viện suy luận viết bằng Rust được đề cập trong ghi chú phát hành bản 1.3.0.
- Gói npm [`deepfilternet3-noise-filter`](https://www.npmjs.com/package/deepfilternet3-noise-filter) và [kho mã nguồn](https://github.com/mezonai/mezon-noise-suppression).
- Các thảo luận về xuất mô hình DeepFilterNet sang ONNX (luôn tự kiểm chứng tệp ONNX từ cộng đồng trước khi sử dụng).

## Video tham khảo

- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, tiếng Anh. **Xem trước.** Video giải thích vai trò tệp trao đổi của ONNX và cách ONNX Runtime thực thi mô hình trên CPU, GPU và thiết bị biên — nền tảng trước khi so sánh với `tract`.
- [Introduction to ONNX Runtime](https://www.youtube.com/watch?v=Wp5PaRpudlk) — NVIDIA Developer, tiếng Anh. Tài liệu giới thiệu chính thức thứ hai về ONNX Runtime, giúp làm rõ cơ chế execution provider trước khi triển khai sang WASM.
