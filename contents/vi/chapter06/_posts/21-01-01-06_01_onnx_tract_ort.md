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

Khử nhiễu trên thiết bị gần như luôn **xuất** đồ thị đã train sang một runtime suy luận. **ONNX** (định dạng trao đổi đồ thị) là file trung gian. **ONNX Runtime (ORT)** là engine đa nền phổ biến, kể cả bản Web. **tract** là thư viện suy luận viết bằng Rust khi bạn muốn đường thuần Rust. Gói `deepfilternet3-noise-filter` **1.3.0** không đưa PyTorch vào trình duyệt. Ghi chú phát hành công khai nói đường WASM (WebAssembly — mã nhị phân chạy trong trình duyệt) được dựng lại với **tract 0.23.3**. Trình duyệt nhận module đã biên dịch cùng kho `DeepFilterNet3_onnx.tar.gz`, không nhận một session Python. Bài này chốt tiêu chí chọn runtime, hợp đồng vào/ra khi stream, và lỗi shape khiến đồ thị chạy trong notebook nhưng gãy trong AudioWorklet (callback xử lý âm thanh trên luồng realtime).

![Đồ thị ONNX được xuất thành module WASM, trình duyệt tải cạnh kho mô hình]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. ONNX là file trao đổi; tract hoặc ORT thực thi; trình duyệt cuối cùng khởi tạo WASM.*

## Mục tiêu học tập

Bạn giải thích ONNX như định dạng trao đổi cho tăng cường tiếng nói, so ORT với tract cho sản phẩm trình duyệt và cho binary Rust, liệt kê bẫy export chỉ lộ khi chạy từng hop, và kiểm tra một tensor là blob ảnh kiểu NCHW hay frame kiểu DeepFilter `[1, T, F]` trước khi ai đó mở session.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao AudioWorklet không chứa framework train.
- **10–25 phút** — Đồ thị, initializer, opset, và phía nào sở hữu STFT.
- **25–40 phút** — ORT đối với tract, gồm pin tract của bản 1.3.0.
- **40–50 phút** — Trục động, tensor state, và bài kiểm shape.
- **50–60 phút** — Mini-lab, bẫy, bài tập.

## Giải thích cốt lõi

### File thực sự chứa gì

File ONNX là một đồ thị tính: tensor vào/ra có tên, toán tử như `Conv`, `GRU`, `MatMul`, và trọng số nằm trong initializer. Framework train ghi file. Runtime tối ưu rồi chạy. Với tăng cường tiếng nói, đồ thị hoặc chứa phép biến đổi đặc trưng, hoặc giả định bạn tự chạy STFT bên ngoài session. Mô hình họ DeepFilter thường thuộc kiểu thứ hai: runtime ăn một frame phổ, overlap-add đứng cạnh nó. Nếu hai phía lệch hop, cửa sổ, hoặc số bin tần số, session vẫn trả tensor nhưng tiếng nghe sai.

### Ghim opset và runtime

Toán tử được đánh số bằng **opset**. Export opset 17 có thể từ chối nạp trên bản ORT cũ. Ghim ba thứ cùng nhau: opset lúc export, phiên bản ORT hoặc tract trong sản phẩm, và một job CI nạp đúng file `.onnx` trên runtime bạn ship. Ghi chú phát hành 1.3.0 của `deepfilternet3-noise-filter` nêu tract **0.23.3** cho bản WASM. Đó là sự kiện sản phẩm trong changelog, không phải lý do bỏ qua kiểm tra toán tử. Tract và ORT không triển khai mọi op giống nhau. Đồ thị mà `onnxruntime` mở được trong Python vẫn có thể gãy trên tract nếu lớp deep-filter tùy biến chưa được hợp thành op được hỗ trợ.

### ORT đối với tract

| Tiêu chí | ONNX Runtime | tract |
|----------|--------------|-------|
| Ngôn ngữ | C/C++, Python, Java, C#, JS/WASM | Ưu tiên Rust |
| Đường web | `onnxruntime-web` | Không phải đường trình duyệt chính |
| Tối ưu | Tối ưu đồ thị, execution provider | Đồ thị Rust, hợp streaming |
| Khớp sản phẩm | Parity nhiều nền | Đường Rust được ghi chú WASM 1.3.0 nhắc tới |
| Độ phủ op | Mặc định rộng | Phải kiểm trên export DeepFilter thật |

Chọn ORT khi cần một file ONNX được kiểm từ Python và một backend Web đã có tài liệu. Chọn tract khi binary ship là Rust và bạn đã kiểm toán tử. Đường trình duyệt của gói Mezon là WASM dựng từ stack `libDF` của DeepFilter, tract được changelog 1.3.0 nêu tên. Thí nghiệm `df-core` tùy chọn ở Chương 09 mới là chỗ bạn tự nối tract. Đừng biến wrapper npm thành một mô hình thứ hai.

### Trục khi stream

Mô hình stream nên khai báo frame có trục thời gian đúng một hop, cùng state hồi tiếp vào và ra. Hợp đồng để học: `features` dạng `[1, T, F]` với `T = 1` trong callback, cộng `state_in` / `state_out` kích thước cố định. Batch động hữu ích khi chạy offline và gần như luôn bằng 1 trong callback âm thanh. Hãy export các trục đó tường minh. Một số export nướng `T = 100` từ script kiểm offline. Đồ thị vẫn nạp, rồi từ chối mọi hop realtime.

Layout NCHW kiểu `[1, 3, 224, 224]` là quy ước ảnh. Tensor hạng 4 là sai shape cho frame DeepFilter dù con số trông có vẻ “có batch”. Hạng 3 với chiều đầu bằng 1 là hợp đồng bài này chấp nhận. Bước thật sau bài cartoon là `ort.InferenceSession`, rồi kiểm **tên input** khớp đồ thị, không chỉ khớp hạng.

### Bẫy khi export

1. **Op không hỗ trợ** trong lớp deep-filter tùy biến. Hợp chúng thành op thân thiện với ONNX, hoặc đăng ký op riêng của runtime. Đừng bịa tên op rồi hy vọng CI bỏ qua.
2. **Control-flow và in-place** lệch giữa bước train và đồ thị đã export.
3. **Thiếu cổng state** của GRU, mô hình trông phi trạng thái và bị bơm tiếng từ hop này sang hop kia.
4. **Sót float64.** Ép float32 trước khi lượng tử hóa hoặc biên dịch WASM.
5. **Lệch tiền xử lý.** STFT NumPy lúc train khác STFT WASM lúc chạy sản phẩm.

### Vì sao trình duyệt chuẩn hóa một module đã biên dịch

Gói không bắt trang tự dựng session ORT. `DeepFilterNet3Core.initialize()` tải byte WASM và kho mô hình, rồi `WebAssembly.compile` trên luồng chính. `createAudioWorkletNode` chỉ chạy sau lần biên dịch đó. Việc nặng nằm ngoài callback âm thanh (Chương 05). ORT vẫn là công cụ đúng để kiểm parity trong Python và cho sản phẩm gọi `onnxruntime-web` trực tiếp. Hãy đo hệ số realtime trên đúng bản WASM bạn ship. Thời gian ORT trong Python là một máy khác.

## Mini-lab

Nếu đã cài ONNX Runtime, lệnh tùy chọn là `python3 -c "import onnxruntime"`. Bài bắt buộc là kiểm shape. Lưu thành `shape_check.py` và chạy `python3 shape_check.py`.

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

**Expected**

```text
[1, 3, 224, 224] -> NCHW rejected-by-df-frame
[1, 1, 96] -> DF frame [1, T, F] accepted
[96] -> rejected
```

**Failure modes**

- Coi “accepted” ở đây là bằng chứng đồ thị thật sẽ chạy. Bài chỉ kiểm hạng và batch đầu bằng 1.
- `ort.InferenceSession` là bước kế tiếp thật. **Session input name mismatch** là lỗi thường gặp: shape đúng nhưng code gọi input tên `input` trong khi đồ thị đặt `feat_erb` hoặc tên khác. Đọc `session.get_inputs()`.
- Trục động để `T = 100` lúc export vẫn qua kiểm hạng lỏng và vẫn từ chối hop dài 1.

## Bẫy thường gặp

- Ship file ONNX khác nhau theo hệ điều hành mà không có bài nạp.
- Bật execution provider CUDA cho sản phẩm phải chạy laptop chỉ có CPU.
- Giả định tract chạy được mọi mô hình ORT chấp nhận.
- Mang số hệ số realtime của ORT Python sang bản WASM.
- Gọi `createAudioWorkletNode` trước khi `initialize()` biên dịch xong module. Core sẽ ném lỗi.

## Bài tập

1. Lập bảng tensor cho một hop GRU đồ chơi: tên, hạng, tensor nào là state.
2. Cho một phiên bản ORT, tra opset được hỗ trợ trong [tài liệu ONNX Runtime](https://onnxruntime.ai/docs/) và chọn opset export.
3. Khoảng 150 từ: chọn ORT hoặc tract cho một extension Chrome, rồi chọn lại cho CLI enhancer viết bằng Rust.
4. Thiết kế bước CI fail khi ONNX và tham chiếu PyTorch lệch quá ngưỡng SI-SDR đã nêu trên một clip vàng.
5. Giải thích vì sao không được đưa `[1, 3, 224, 224]` vào mô hình frame dù batch bằng 1.

### Gợi ý đáp án

1. Có `frame` dạng `[1, 1, F]`, `state_in` và `state_out` cùng kích thước ẩn. Nếu đồ thị không có op FFT thì ghi STFT nằm ngoài session.
2. Opset export phải là opset runtime ship công bố, không phải opset mới nhất mà trainer đưa ra.
3. Extension: runtime WASM với ma trận trình duyệt đã biết. CLI: tract nếu kiểm op đạt, vì bạn tránh thêm một thư viện native. Cả hai câu trả lời đều cần bước kiểm toán tử.
4. Ghim clip, hop và ngưỡng trong job. Fail cả khi thiếu output state, không chỉ khi lệch SI-SDR.
5. Hạng 4 là NCHW. Hợp đồng frame trong mini-lab là hạng 3.

## Đọc thêm

- [Tài liệu ONNX Runtime](https://onnxruntime.ai/docs/), gồm lượng tử hóa và Web dùng ở các bài sau.
- [tract](https://github.com/sonos/tract), thư viện suy luận Rust được ghi chú 1.3.0 của gói nêu tên.
- npm [`deepfilternet3-noise-filter`](https://www.npmjs.com/package/deepfilternet3-noise-filter) và [kho mã](https://github.com/mezonai/mezon-noise-suppression). Checkout tùy chọn của giảng viên, không phải đích sửa của khóa: `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.
- Thảo luận export DeepFilterNet. Hãy xác minh mọi file ONNX cộng đồng trước khi phụ thuộc vào nó.
