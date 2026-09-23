---
layout: post
title: "10-02 Hướng học tiếp"
chapter: "10"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter10
lesson_type: required
draft: false
---

Sau capstone, chọn một hướng và ba mươi ngày luyện tạo ra file, không phải danh sách đọc bạn sẽ không mở. Ba hướng dưới đây dùng lại bản đồ đánh giá: SI-SDR xâm nhập khi có tham chiếu sạch, DNSMOS hoặc `n/a` trên audio thật, ghi chú nghe, và RTF khi việc là thời gian thực. Chủ đề kề được gọi tên để bạn chọn thí nghiệm cuối tuần. Chúng không phải khóa thứ hai bạn phải học xong.

![Bản đồ đánh giá để chọn dự án tiếp]({{ site.imgurl }}/generated/eval-metric-map.png)

*Hình. Hướng nào bạn chọn, bản đồ vẫn đúng. Một bộ lọc cổ điển, một lần tái hiện bài báo, và một chính sách LiveKit đều được chấm theo cột chúng thật sự dịch chuyển.*

## Bạn làm được gì sau bài này

Bạn chọn được DSP cổ điển, tăng cường tiếng nói bằng mạng, hoặc sản phẩm hóa, viết lịch ba mươi ngày với một file sẽ commit mỗi tuần, và gọi một chủ đề kề với lệnh hoặc phép đo cuối tuần cụ thể. Bạn cũng biến cây `capstone/` thành món portfolio không phụ thuộc repo sản phẩm chung.

## Hướng A — đào sâu cổ điển

Viết lại overlap-add đến khi một sine khôi phục trong dung sai bạn in ra. Đọc SpeexDSP (<https://github.com/xiph/speexdsp>) hoặc WebRTC APM (<https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/>) đủ để nói khối khử nhiễu chịu trách nhiệm gì, tách khỏi AEC. Trên file stereo bạn tự ghi, mô tả một lỗi beamforming (người nói lệch bên, mic tham chiếu ồn) mà không nhận một thuật toán mới.

Vé ra: ghi chú `path-a/when-classical.md` cho một clip mà cổng phổ đơn giản hoặc gain kiểu Wiener thắng mô hình nặng về RTF và không làm xấu ghi chú nghe. Chỉ đưa SI-SDR nếu bạn còn tham chiếu sạch.

## Hướng B — tăng cường tiếng nói bằng mạng

Mỗi tuần đọc một bài gốc từ bài 10-01, bắt đầu với arXiv:2110.05588, arXiv:2205.05474, và arXiv:2305.08227. Tái hiện một lần đo thời gian ONNX Runtime hoặc tract trên CPU laptop và viết RTF là thời gian tường chia thời lượng audio, kèm tên CPU. Nếu bạn so DeepFilterNet3 với một tên siêu nhẹ (FastEnhancer, μNet, Fast-ULCNet, GTCRN), giữ so sánh trên clip **của bạn** và đừng bịa URL bài báo. Các tên kế tục DPDFNet, DeepFilterGAN, và HDF-Net cùng loại: chỉ là tên cho đến khi trích dẫn thật nằm trước mặt.

Vé ra: `path-b/table.md` với sáu cột của bài 08-04 và một đoạn giới hạn. Không ngôn ngữ bảng xếp hạng.

## Hướng C — sản phẩm hóa

Ở trên đường LiveKit công khai: mic, `DeepFilterNoiseFilterProcessor`, `setProcessor`, publish. Đo thời gian khởi động lạnh của `{cdnUrl}/v2/pkg/df_bg.wasm` và `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` (tiền tố mà 1.3.0 tự thêm từ ≥ 1.2.0) trên mạng bạn thật sự có, rồi lặp khi CDN bị chặn. Rust `df-core` tùy chọn vẫn là phương án kéo thay hộp WASM. Nếu backend là passthrough, README portfolio nói vậy.

Vé ra: `path-c/design.md` với thời gian init, RTF p95 hoặc `n/a`, và log lỗi từ CDN bị chặn.

## Cuối tuần kề

| Chủ đề | Artifact cuối tuần |
|--------|---------------------|
| AEC | Một bản ghi echo át nhiễu, cộng ghi chú rằng NS sẽ không xóa echo |
| Nhiều mic | Một file stereo và một đoạn kênh nào bạn tin |
| Người nói đích | Một clip babble nơi DNSMOS và tai bạn bất đồng |
| Codec | Cùng một câu qua Opus bitrate thấp, trước và sau NS |
| Phụ đề | WER hoặc đếm lỗi tay trên mười câu, không nhận MOS |

## Lịch ba mươi ngày

| Ngày | File thêm | Xong khi |
|------|-----------|----------|
| 1–3 | `notes/si_sdr.py` chạy lại lab 13.80 / −10.67 | Cả hai float khớp bài 08-01 |
| 4–7 | `audio/CLIPS.txt` với 20 tên file | File chưa có điểm |
| 8–14 | MVP hướng (`path-a`, `path-b`, hoặc `path-c`) | README có một lệnh |
| 15–21 | `metrics/suite.md` và một ghi chú nghe của bạn cùng nhóm | Checker 08-04 in 6 hàng dữ liệu, hoặc bạn ghi ít hơn và vì sao |
| 22–26 | `DEMO.md` dưới năm phút | Audio dự phòng có tên |
| 27–30 | Vá tài liệu trong fork **của bạn**, hoặc ADR ở chỗ làm | Không commit vào repo sản phẩm Mezon chung trừ khi đó là việc ngoài khóa |

## Nội dung portfolio

Đưa phác kiến trúc, bảng metric, protocol AB tiếng Anh và tiếng Việt, bản demo không quá ba phút, và thẻ đọc từ 10-01. Gỡ đường tuyệt đối máy cục bộ. Checkout giảng viên tùy chọn không thuộc portfolio công khai.

## Mini-lab

Tạo `path_plan.md`:

```text
path: A
week1_file: notes/si_sdr.py
weekend: aec
command: python3 notes/si_sdr.py
```

Dùng `A`, `B`, hoặc `C`. `weekend` phải là một trong `aec`, `multimic`, `target`, `codec`, `captions`.

```python
from pathlib import Path
text = Path("path_plan.md").read_text().lower()
path_ok = any(f"path: {p}" in text for p in "abc")
weekend_ok = any(w in text for w in ("aec", "multimic", "target", "codec", "captions"))
print("path", "ok" if path_ok else "fix")
print("weekend", "ok" if weekend_ok else "fix")
print("command", "ok" if "command:" in text else "fix")
```

Đầu ra kỳ vọng:

```text
path ok
weekend ok
command ok
```

Kiểu hỏng: ba hướng trong một tháng; chủ đề cuối tuần không có artifact; mục tiêu RTF không có thiết bị; kế hoạch bắt đầu bằng cách không fork gì mà sửa cây sản phẩm chung.

## Bài tập

1. Điền `path_plan.md` cho hướng bạn sẽ làm thật. Chạy checker.
2. Viết tên file từng tuần vào cùng file, dưới header bốn dòng.
3. Gọi một lỗ tài liệu upstream (trang processor LiveKit, README npm, hoặc README DeepFilterNet) bạn vá được bằng một đoạn, và câu claim của đoạn đó.
4. Phác mục README portfolio liên kết năm artifact. Nếu có Rust, gồm luật passthrough.
5. Nêu cột nào trên bản đồ đánh giá hướng của bạn sẽ để `n/a` và vì sao.

### Gợi ý đáp án

1. Một chữ. Đổi hướng ngày 20 là kế hoạch mới, không phải điểm thưởng.
2. Tên file phải tạo được trên máy bạn. Đừng trỏ thư mục nhà của giảng viên.
3. Lỗ thật: tiền tố `v2/`, hoặc khác nhau giữa `setEnabled(false)` và tải asset thất bại.
4. Liên kết file, không phải repo riêng bạn không chia sẻ được.
5. Audio thật để SI-SDR là `n/a`. Lab khôi phục DSP thuần có thể để DNSMOS là `n/a`.
