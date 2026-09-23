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

Đường Mezon được hỗ trợ là hộp WASM trong `deepfilternet3-noise-filter`: weight ONNX, bản WASM SIMD, bố trí CDN mà client đã cài xin (`v3/` trên bản 1.3.0 đã phát hành), và AudioWorklet. Crate Rust bạn có thể gọi `df-core` là **phương án kéo thay cho hộp đó**, cho CLI máy bàn hoặc nhúng native bạn tự dựng trong workspace của mình. Nó không phải sản phẩm thứ hai, không bắt buộc để đậu, và không phải thư mục bạn có quyền tìm dưới `/Users/nguyenlelinh/ncc/mezon-noise-suppression`. Nếu backend đầu chỉ chép mẫu từ vào ra, hãy ghi **passthrough**. Đừng viết “NS works” trên bản passthrough.

![Đường WASM trên thiết bị của deepfilternet3-noise-filter]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Hình. Đường ship là PyTorch sang ONNX sang WASM sang gói hoặc asset CDN (bản 1.3.0 đã phát hành xin `v3/`), rồi AudioWorklet. Rust `df-core` là phương án kéo thay cho hộp WASM này, không phải sản phẩm thứ hai đứng cạnh nó.*

## Bạn làm được gì sau bài này

Bạn nói được đường WASM tải gì (`df_bg.wasm`, `DeepFilterNet3_onnx.tar.gz`), thí nghiệm Rust cá nhân phải khớp gì (hop khung, sample rate, mô hình thật), và cách chứng minh parity mà không nhận bit-exact khi chưa đo. Bạn cũng từ chối coi backend rỗng là enhance.

## Hộp bạn không thay theo mặc định

Gói 1.3.0 đã cài xin `{cdnUrl}/v3/pkg/df_bg.wasm` và `{cdnUrl}/v3/models/DeepFilterNet3_onnx.tar.gz`. Đoạn README “≥ 1.2.0” vẫn in `v2/`. Tiền tố do client thêm, dù là bản nào. Nút công khai vẫn là `DeepFilterNoiseFilterProcessor` hoặc `DeepFilterNet3Core`, `setProcessor`, `setSuppressionLevel(0–100)`, và `setEnabled`. Thí nghiệm Rust không thêm tên công khai mới vào gói npm. Muốn CLI thì dựng cạnh khóa học, trong repo cá nhân.

Các bài DeepFilterNet nói vì sao viết lại native khó tính: audio full-band 48 kHz, STFT với hop cỡ 10 ms, tầng gain ERB, và deep filter có thể dùng look-ahead ngắn. Look-ahead đó là độ trễ thuật toán. Khớp RTF không phải khớp waveform. Bài 08-01 cho thấy trượt một mẫu biến 13.80 dB thành −10.67 dB. Bản Rust “trễ một chút” sẽ tệ trên SI-SDR dù nghe na ná.

## Workspace cá nhân, nếu bạn chọn

Chỉ tạo trong fork hoặc repo mới. Đừng thêm vào cây sản phẩm chung như bài tập.

```text
my-df-stretch/
  df-core/     # API khung của bạn
  df-cli/      # wav vào, wav ra, offline
  README.md    # câu đầu nói passthrough hoặc backend thật
```

Các mốc gợi ý, theo thứ tự:

1. **Backend passthrough.** `process` trả lại mẫu đầu vào. Tiêu đề README nói passthrough. Test kiểm độ dài và bản sao, không kiểm nền nhiễu.
2. **Lỗi asset.** Thiếu đường tar hoặc ONNX thì fail với lỗi rõ. Đừng lặng lẽ cho audio đi qua rồi in “enhanced”.
3. **Tải runtime thật.** [tract](https://github.com/sonos/tract) hoặc ONNX Runtime ([onnxruntime.ai/docs](https://onnxruntime.ai/docs/)) chạy cùng archive DeepFilterNet3 mà CDN phục vụ. [libDF](https://github.com/Rikorose/DeepFilterNet) phía upstream là lựa chọn thật còn lại. Chọn một và ghim phiên bản.
4. **Khung.** Ghi hop, cửa sổ, và sample rate cạnh đường WASM. Đừng bịa API riêng của Mezon để làm việc đó.
5. **File vàng.** Một wav ồn qua đường WASM công khai, một qua CLI của bạn. So SI-SDR **giữa hai ước lượng**, sau khi căn, và báo float. Rồi nghe. SI-SDR cao giữa chúng nghĩa là chúng khớp nhau, không nghĩa là cái nào khớp tiếng sạch.
6. **Điểm dừng.** Nếu bạn chỉ xong bước 1, script demo nói “passthrough, noise suppression is not running”.

Giấy phép theo dự án DeepFilterNet upstream (Apache-2.0 OR MIT, như gói npm). Đừng commit tar.gz. Trỏ bố trí CDN hoặc hướng dẫn `models/` phía upstream.

## Parity không hư cấu

```text
căn delay hop
enh_wasm.wav  từ processor đã phát hành hoặc lượt WASM offline bạn viết script
enh_rust.wav  từ CLI của bạn
in SI-SDR(enh_wasm, enh_rust) sau khi căn
ghi float vào báo cáo
nếu backend là passthrough, bỏ so sánh này và nói vì sao
```

Chưa có bước 3 thì test vàng là **đang chờ**. File passthrough so với enhancer thật sẽ điểm xấu. Điểm xấu đó là mục đích. Đừng nới dung sai cho đến khi số trông hiền.

tract (hoặc ONNX Runtime) với binding tay tới libDF upstream là đánh đổi bạn nên viết một đoạn: runtime ONNX ăn artifact mà CDN đã ship; libDF là engine mà bản WASM được dựng từ đó và có thể bám trạng thái streaming sát hơn. Cách nào cũng phải đo. Chương 06 là nền. Bài này không thêm bảng ký hiệu riêng.

## “Xong” nghĩa là gì với phần kéo

Xong đường tùy chọn là README người lạ build được, nhãn passthrough nếu bạn chỉ có thế, hoặc CLI cộng một float SI-SDR với đầu ra WASM nếu bạn đã tải mô hình. Xong không phải slide nói client native là Mezon production. Client ship vẫn là gói npm trên đường LiveKit ở 09-01.

## Mini-lab

Viết `df_core_status.md` với hai dòng checker nhìn thấy:

```text
backend: passthrough
claim: noise suppression is not running
```

Nếu bạn thật sự tải mô hình, có thể viết `backend: tract` hoặc `backend: onnxruntime` hoặc `backend: libdf`, và `claim: compared to wasm SI-SDR <float>`. Chữ passthrough không được đứng cạnh câu nhận NS chạy.

```python
from pathlib import Path
text = Path("df_core_status.md").read_text().lower()
ok_pass = "passthrough" in text and "not running" in text
ok_real = any(k in text for k in ("tract", "onnxruntime", "libdf")) and "si-sdr" in text
bad = "ns works" in text or "noise suppression works" in text
print("status", "ok" if (ok_pass or ok_real) and not bad else "fix")
```

Đầu ra kỳ vọng cho lab kéo mặc định (chưa có mô hình):

```text
status ok
```

Kiểu hỏng: “NS works” trên vòng chép; commit `DeepFilterNet3_onnx.tar.gz`; bắt đường máy giảng viên; mô tả Rust là sản phẩm và WASM là demo; float parity không ghi căn thời gian.

## Bài tập

1. Viết năm mốc làm được không cần GPU, đánh dấu mốc nào là passthrough.
2. Liệt kê test không cần weight: độ dài khung, chép đồng nhất, và lỗi thiếu file.
3. Một đoạn, so tract (hoặc ONNX Runtime) với libDF upstream làm backend kéo.
4. Quyết đi hay không đi Rust trong capstone của bạn. Nếu không đi, gọi tên việc WASM bạn sẽ làm.
5. Nêu hướng so SI-SDR: ước lượng với ước lượng, không phải ước lượng với khẩu hiệu.

### Gợi ý đáp án

1. Bước 1–2 được phép passthrough. Bước 3 là lần đầu được dùng chữ enhance.
2. Đồng nhất: mẫu ra bằng mẫu vào. Thiếu file: mã thoát khác không và không có wav “enhanced”.
3. Runtime ONNX ăn tar/ONNX CDN đã có. libDF là engine upstream. Cả hai cần file vàng.
4. Không đi vẫn là capstone đủ nếu 09-01 và 09-04 là thật. Nói vậy.
5. SI-SDR(wasm, rust) sau khi bù delay. Lab 13.80 là phương pháp, không phải điểm sản phẩm kỳ vọng.
