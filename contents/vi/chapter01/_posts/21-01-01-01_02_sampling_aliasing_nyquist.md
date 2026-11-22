---
layout: post
title: "01-02 Lấy mẫu, aliasing và Nyquist"
chapter: "01"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Mọi track WebRTC và mọi lượt suy luận của DeepFilterNet đều giả định một tần số lấy mẫu (sample rate) cố định. Sai lệch tần số lấy mẫu sẽ tạo ra lỗi chồng phổ (aliasing) âm thầm, biểu hiện bên ngoài rất giống "suy giảm chất lượng mô hình". Bài học này biến định lý lấy mẫu thành một công cụ kiểm tra thực tế cho kỹ sư.

![Phổ bị sao chép theo mỗi sample rate; các bản sao chồng khi tín hiệu quá rộng]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Hình. Quá trình lấy mẫu lặp lại phổ theo chu kỳ \(f_s\) Hz; phần chồng lấn giữa các bản sao là aliasing mà bộ khử nhiễu mạng nơ-ron không thể khôi phục ngược lại.*

## Mục tiêu học tập

1. Phát biểu định lý lấy mẫu, tốc độ Nyquist và tần số Nyquist.
2. Giải thích hiện tượng aliasing thông qua các con số âm thanh cụ thể.
3. Lựa chọn có chủ đích các mức tần số lấy mẫu 8 / 16 / 48 kHz cho pipeline khử nhiễu tiếng nói.
4. Mô tả vai trò của bộ lọc chống aliasing trước ADC và trước bước giảm mẫu (decimation).
5. Liệt kê các bẫy khi lấy mẫu lại (resample) nhằm đồng bộ đồng hồ trình duyệt với tần số lấy mẫu của mô hình mạng nơ-ron.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Phân tích sự cố (postmortem): vì sao chạy mô hình ONNX 16 kHz trực tiếp trên tín hiệu 48 kHz khiến chất lượng sụp đổ |
| 10–25 | Lấy mẫu bằng chuỗi xung, sự lặp lại bản sao phổ và phác họa giới hạn Nyquist |
| 25–40 | Ví dụ số về aliasing, bảng băng thông tiếng nói và tiêu chí chọn tần số lấy mẫu cho sản phẩm |
| 40–52 | Lọc chống aliasing, thiết kế bộ lấy mẫu lại và các lưu ý với WebAudio/WebRTC |
| 52–60 | Các bẫy thường gặp và bài tập nhỏ |

## Giải thích cốt lõi

Lấy mẫu lý tưởng tương đương việc nhân tín hiệu liên tục \(x_c(t)\) với một chuỗi xung chu kỳ \(T=1/f_s\), khiến phổ của tín hiệu **lặp lại** sau mỗi \(f_s\) Hz. Nếu các bản sao phổ chồng lấn lên nhau, hiện tượng **aliasing** sẽ xảy ra và không một bộ lọc số nào có thể tách ngược lại một cách duy nhất.

Trên lưới lấy mẫu \(t=n/f_s\), ta có:

$$
\cos\!\left(2\pi\frac{f}{f_s}n\right)
=\cos\!\left(2\pi\frac{f-mf_s}{f_s}n\right)
$$

vì \(2\pi m n\) là một số nguyên lần chu kỳ. Ta gập tần số đại diện về đoạn \([0,f_s/2]\). Chẳng hạn, một sóng cosine 7 kHz lấy mẫu ở 8 kHz (chọn \(m=1\)) sẽ gập về \(|7000-8000|=1000\,\mathrm{Hz}\): hai sóng cosine này tạo ra chính xác cùng một dãy mẫu. Với hàm sine, dấu sẽ đảo ngược: \(\sin(2\pi\cdot 7n/8)=-\sin(2\pi\cdot 1n/8)\) do tính lẻ của hàm sine dưới phép dịch vòng. Ở đây, "trùng khớp" nghĩa là các giá trị mẫu bằng nhau hoàn toàn, không chỉ "nghe gần giống".

Nếu tín hiệu \(x_c\) có băng thông giới hạn ở \(B\) Hz, ta phải chọn \(f_s>2B\) (**tốc độ Nyquist** là \(2B\), còn **tần số Nyquist** là \(f_s/2\)).

Sau khi lấy mẫu, tần số góc chuẩn hóa là \(\omega=2\pi f/f_s\). Mốc \(\omega=\pi\) luôn tương ứng với tần số Nyquist trên trục số, nhưng giá trị Hz thực tế phụ thuộc vào \(f_s\). Do đó, cùng một tập hệ số bộ lọc FIR sẽ có tần số cắt (Hz) khác nhau khi chạy ở 16 kHz so với 48 kHz.

| Tần số lấy mẫu | Tần số Nyquist | Ứng dụng điển hình |
|------|---------|----------------|
| 8 kHz | 4 kHz | Thoại băng hẹp (telephony) |
| 16 kHz | 8 kHz | Mô hình ML tiếng nói băng rộng (wideband) |
| 48 kHz | 24 kHz | Đồng hồ WebRTC/toàn băng (full-band); mặc định của `deepfilternet3-noise-filter` 1.3.0 |

Trước bộ chuyển đổi ADC luôn cần một bộ lọc thông thấp (LPF) tương tự. Tương tự, trước khi **giảm mẫu (decimation)** từ 48 kHz xuống 16 kHz (hệ số 3), bắt buộc phải lọc thông thấp gần 8 kHz *rồi mới* giữ lại mỗi mẫu thứ ba; bỏ qua bước lọc này là một lỗi kỹ thuật nghiêm trọng.

Đưa trực tiếp dữ liệu PCM 48 kHz vào STFT của một mô hình huấn luyện ở 16 kHz không giúp "tăng độ phân giải cho mạng". Ngược lại, mọi bin tần số đều bị gán sai giá trị Hz, và nếu thiếu bộ lọc thông thấp gần 8 kHz, năng lượng vùng 8–24 kHz sẽ gập thẳng vào dải tần mà mạng nhận diện là tiếng nói. Khi lấy mẫu lại (resample), việc bỏ/lặp mẫu đơn thuần là sai, nội suy tuyến tính có chất lượng kém gần tần số Nyquist, nên môi trường sản phẩm cần dùng bộ lọc đa pha (polyphase) hoặc thư viện tương đương `libsamplerate`. Các mô hình khử nhiễu mạng nơ-ron rất nhạy với lỗi này vì các thành phần alias xuất hiện như một dạng "nhiễu lạ" chưa từng có trong tập huấn luyện.

## Ví dụ có số

Một âm đơn 5 kHz lấy mẫu ở \(f_s=8\,\mathrm{kHz}\) sẽ bị alias thành 3 kHz. Với khung dài 20 ms, số mẫu ở 16 kHz là \(L_{16k}=320\), còn ở 48 kHz là \(L_{48k}=960\). Chi phí tính toán xấp xỉ tỷ lệ thuận với số mẫu mỗi giây — chuyển từ 16 kHz lên 48 kHz có thể làm tăng khoảng 3 lần lưu lượng tính toán STFT nếu giữ nguyên độ dài cửa sổ theo giây.

## Bẫy thường gặp

1. Chạy mô hình huấn luyện ở 16 kHz trực tiếp trên PCM 48 kHz với suy nghĩ "tần số lấy mẫu cao hơn thì tốt hơn".
2. Cho rằng định dạng `float32` không bị aliasing — thực tế aliasing phụ thuộc vào tần số lấy mẫu, không phải độ sâu bit.
3. Trộn tín hiệu 44.1 kHz với 48 kHz mà không qua bước lấy mẫu lại.
4. Lấy mẫu lại bằng FFT nhưng xử lý sai biên khối, gây tiếng lách tách (click).
5. Nhầm lẫn giữa độ sâu bit (quyết định nhiễu lượng tử hóa) và tần số lấy mẫu (quyết định băng thông).

## Mini-lab

**Mục tiêu.** Lấy mẫu sóng cosine 7 kHz ở tần số 8 kHz và kiểm chứng rằng dãy mẫu thu được trùng khớp với sóng cosine 1 kHz.

```python
import numpy as np

fs = 8000
n = np.arange(32)
high = np.cos(2 * np.pi * 7000 * n / fs)
low = np.cos(2 * np.pi * 1000 * n / fs)
err = np.max(np.abs(high - low))
print(f"{err:.3e}")
print(np.round(high[:8], 6).tolist())
```

**Kết quả kỳ vọng.** Sai số nhỏ hơn `1e-12` (thường khoảng `1.354e-14`). Tám mẫu đầu tiên sau khi làm tròn là `[1.0, 0.707107, -0.0, -0.707107, -1.0, -0.707107, -0.0, 0.707107]`.

**Lỗi thường gặp.** So sánh hàm sine nhưng quên dấu trừ; kết luận "không có aliasing" chỉ vì hai mảng đều ở kiểu `float64`; hoặc lọc thông thấp *sau* khi đã lấy mẫu ở 8 kHz với kỳ vọng khôi phục lại được thành phần 7 kHz.

## Bài tập nhỏ

1. Xác định tần số Nyquist tại 48 kHz và 16 kHz.
2. Tìm tần số alias của một âm đơn 10 kHz khi lấy mẫu ở \(f_s=16\,\mathrm{kHz}\).
3. Tính số mẫu trong 10 ms ở các tần số lấy mẫu 8 kHz, 16 kHz và 48 kHz.
4. Viết danh mục kiểm tra 4 bước để chuyển đổi an toàn tín hiệu 48 kHz mono Float32 sang đầu vào cho mô hình 16 kHz.
5. Giải thích vì sao cùng một mốc \(\omega=\pi\) lại tương ứng với các tần số Hz khác nhau khi \(f_s\) thay đổi.

### Gợi ý đáp án

1. Tần số Nyquist bằng \(f_s/2\): đạt 24 kHz ở 48 kHz và 8 kHz ở 16 kHz.
2. Âm 10 kHz tại \(f_s=16\,\mathrm{kHz}\) gập một lần về \(16-10=6\,\mathrm{kHz}\).
3. Khoảng thời gian 10 ms tương ứng với 80, 160 và 480 mẫu.
4. Xác nhận đầu vào là mono `float` 48 kHz; áp dụng lọc thông thấp gần 8 kHz; giảm mẫu theo hệ số 3; kiểm chứng rằng sóng sin 1 kHz vẫn giữ đúng 1 kHz và năng lượng trên 8 kHz đã được triệt tiêu.
5. Mốc \(\omega=\pi\) tương ứng với nửa chu kỳ trên mỗi mẫu, tức \(f_s/2\) Hz. Tần số số \(\omega\) đã được chuẩn hóa theo \(f_s\), còn tần số vật lý (Hz) thì không.

## Đọc thêm

- Oppenheim & Schafer — định lý lấy mẫu và xử lý tín hiệu đa tốc độ.
- Julius O. Smith, *Mathematics of the DFT*, https://www.dsprelated.com/freebooks/mdft/ — quá trình lấy mẫu và trục tần số sử dụng trong FFT.
- Tài liệu Web Audio `sampleRate` và các ràng buộc `getUserMedia` trong WebRTC.

## Video tham khảo

- [Aliasing and the Sampling Theorem Simplified](https://www.youtube.com/watch?v=KuaannH5pnM) — Barry Van Veen, tiếng Anh. **Xem trước.** Minh họa cách phổ liên tục gập vào khoảng \(2\pi\) — chính cơ chế tạo ra lỗi aliasing khi lệch tần số lấy mẫu.
- [Xiph.Org Video Presentations: Digital Show & Tell](https://xiph.org/video/vid2.shtml) — Xiph.Org, tiếng Anh. Trang video chính thức của Xiph.Org giải thích về lấy mẫu, độ sâu bit và khôi phục tín hiệu, giúp phân biệt giới hạn thực của tần số lấy mẫu với hiểu nhầm về dạng sóng "bậc thang".
