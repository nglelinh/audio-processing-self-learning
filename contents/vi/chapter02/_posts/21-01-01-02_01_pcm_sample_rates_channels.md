---
layout: post
title: "02-01 PCM, tốc độ mẫu và kênh"
chapter: "02"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Bộ khử nhiễu mạng nơ-ron nhận đầu vào là tensor, trong khi micro cung cấp luồng PCM. Định dạng bộ đệm, tần số lấy mẫu và cách bố trí kênh là những điểm tích hợp dễ gặp lỗi nhất ngay cả trước khi mô hình chạy. Sai \(f_s\) không chỉ làm âm thanh "tối" đi mà còn khiến năng lượng bị gập qua tần số Nyquist: một âm đơn 7 kHz lấy mẫu ở 8 kHz sẽ trùng khớp hoàn toàn về giá trị mẫu với âm 1 kHz, và không mặt nạ STFT nào có thể gỡ ngược phép gập đó.


Trước khi bất kỳ thuật toán FFT hay mạng nơ-ron nào chạm tới giọng nói của bạn, micro và mạch chuyển đổi tương tự–số (ADC) đã phải biến sóng áp suất không khí liên tục thành một dòng các con số rời rạc gọi là **PCM (Pulse-Code Modulation)**. Nếu bạn chọn sai định dạng PCM — chẳng hạn gộp sai kênh stereo, quên chuẩn hóa số nguyên 16-bit `int16` về số thực `float32` trong đoạn $$[-1, 1]$$, hoặc trộn nhầm tệp 16 kHz vào mô hình 48 kHz — toàn bộ hệ thống khử nhiễu phía sau sẽ phát ra tiếng ré chói tai hoặc giọng trầm chậm đi đúng 3 lần!

---

## Kiến thức cần nhớ: Biểu diễn Âm thanh số PCM đứng trên ba trụ cột nào?

### 1. Rời rạc hóa thời gian (Sample Rate) và Rời rạc hóa biên độ (Bit Depth)
PCM thực hiện hai phép rời rạc hóa độc lập: **lấy mẫu theo thời gian** ở tần số $$f_s$$ (8 kHz điện thoại cổ điển, 16 kHz chuẩn ASR băng rộng, 48 kHz chuẩn WebRTC/Video) và **lượng tử hóa biên độ** bằng $$B$$ bit (phổ biến là `int16` có $$2^{16} = 65\,536$$ mức từ $$-32\,768$$ đến $$+32\,767$$, hoặc `float32` chuẩn hóa trong $$[-1.0,\ +1.0]$$).

### 2. Nhiễu lượng tử hóa và Quy tắc vàng 6 dB/bit (SQNR)
Làm tròn biên độ thực về mức lượng tử gần nhất sinh ra sai số nhỏ gọi là **nhiễu lượng tử hóa**. Với mô hình sai số phân bố đều trong bước nhảy $$\Delta = 2 / 2^B$$, tỉ số tín hiệu trên nhiễu lượng tử hóa cho sóng sin toàn thang đạt công thức kinh điển:

$$
\text{SQNR}_{\text{dB}} \approx 6.02\,B + 1.76\text{ dB}.
$$

Mỗi khi tăng thêm **1 bit** độ sâu, dải động sạch của bản ghi tăng thêm khoảng **6 dB**!

### 3. Bố cục đa kênh (Mono vs. Stereo Interleaved/Planar) và Clipping
Âm thanh đa kênh có thể lưu kiểu **xen kẽ (interleaved: `L0, R0, L1, R1, ...`)** hoặc **tách mảng (planar: `[L0, L1, ...], [R0, R1, ...]`)**. Nếu vượt biên $$[-1.0, +1.0]$$ trước khi xuất ra DAC, tín hiệu bị **cắt ngọn (clipping)** tạo ra sóng vuông đầy hài bậc lẻ cực kỳ chói tai!

---

### Giải thích: tự tay tính Bitrate, dung lượng và SQNR của chuẩn PCM 48 kHz / 16-bit

1. **Tính tốc độ bit (Bitrate) và dung lượng file WAV không nén** cho âm thanh Stereo ($$C = 2$$ kênh), $$f_s = 48\,000\text{ Hz}$$, độ sâu $$B = 16\text{ bit}$$:
   $$
   \text{Bitrate} = f_s \times B \times C = 48\,000 \times 16 \times 2 = 1\,536\,000\text{ bit/giây} = \mathbf{1.536\text{ Mbps}}.
   $$
   Đổi ra byte mỗi phút: $$\frac{1\,536\,000}{8} \times 60 = 11\,520\,000\text{ byte} \approx \mathbf{11.0\text{ MiB/phút}}$$!
2. **So sánh dải động SQNR giữa 8-bit và 16-bit:**
   - **8-bit:** $$\text{SQNR} \approx 6.02(8) + 1.76 = \mathbf{49.9\text{ dB}}$$ (nền nhiễu lượng tử nghe rất rõ trong đoạn im lặng).
   - **16-bit (chuẩn CD/WebRTC):** $$\text{SQNR} \approx 6.02(16) + 1.76 = \mathbf{98.1\text{ dB}}$$ (vượt xa độ động của hầu hết micro và phòng thu thông thường!).
3. **Chuẩn hóa `int16` ↔ `float32` không lệch trục:** Chuyển `int16` sang `float32` phải chia cho $$32\,768.0$$ ($$2^{15}$$), không chia cho $$32\,767$$, để giá trị nhỏ nhất $$-32\,768$$ ánh xạ đúng về $$-1.0$$ mà không gây tràn số!

---

## Mục tiêu học tập

1. Mô tả các định dạng mã hóa PCM phổ biến trên trình duyệt và hệ thống native (`s16`, `f32`, bố cục planar và interleaved).
2. Chuyển đổi thành thạo giữa số mẫu, thời lượng (giây) và kích thước byte.
3. Xử lý bố cục mono/stereo đúng cách trước khi đưa vào mô hình khử nhiễu mono.
4. Giải thích sự sai lệch đồng hồ thiết bị và `AudioContext.sampleRate`.
5. Đối chiếu yêu cầu định dạng với đường tích hợp WebRTC / Mezon công khai.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Đọc tệp dữ liệu thô: giải mã chuỗi byte theo định dạng `s16` LE mono ở 16 kHz |
| 10–25 | Định dạng mã hóa, thứ tự byte (endian), thang chuẩn `float` Full Scale và hiện tượng cắt đỉnh (clipping) |
| 25–40 | Bố cục kênh (interleaved/planar) và quy tắc gộp kênh (downmix) |
| 40–52 | Đồng hồ lấy mẫu và vị trí đặt bộ lấy mẫu lại trong đồ thị xử lý |
| 52–60 | Bài tập nhỏ |

![Lấy mẫu 8 kHz: sine 1 kHz là duy nhất, sine 7 kHz rơi đúng các mẫu đó và alias thành 1 kHz]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Hình. Với \(f_s=8\,\mathrm{kHz}\), tần số gập là 4 kHz, nên âm 7 kHz và âm 1 kHz tạo ra cùng một dãy mẫu.*

## Giải thích cốt lõi

### PCM

**PCM** (pulse-code modulation) biểu diễn tín hiệu bằng chuỗi giá trị biên độ lấy mẫu cách đều nhau theo thời gian.

| Định dạng | Miền giá trị | Ghi chú |
|-----------|--------------|---------|
| `int16` (`s16`) | \([-32768,32767]\) | Phổ biến trong WebRTC, tệp WAV; cần lưu ý thứ tự byte (endian) |
| `float32` | Thường trong \([-1,1]\) FS | Chuẩn của `AudioBuffer` trong Web Audio |
| `int32` / 24-bit trong container | Ít dùng trên nhánh xử lý thời gian thực | Nên chuyển đổi một lần ở biên hệ thống |

$$
x_{f32} \approx \frac{x_{s16}}{32768}
$$

Một số thư viện chia cho 32767. Hãy thống nhất một quy ước ở biên đồ thị và tránh trộn lẫn hai công thức trong cùng pipeline STFT. Tín hiệu đã bị cắt đỉnh (clip) ngay từ driver không đơn thuần là "tiếng nói to": đó là méo phi tuyến cứng tạo ra các họa âm rơi vào đúng vùng bin của phụ âm xát. Nên chừa vài dB khoảng dự trữ (headroom) trước khi đưa tín hiệu vào bộ khử nhiễu.

### Thời gian, số mẫu và kích thước byte

$$
N_{\mathrm{samples}} = t\cdot f_s,\qquad
N_{\mathrm{bytes}} = N_{\mathrm{samples}}\cdot C\cdot B
$$

Trong đó \(C\) là số kênh và \(B\) là số byte trên mỗi mẫu (2 với `s16`, 4 với `f32`).

**Ví dụ:** Một đoạn 20 ms ở 48 kHz, stereo `s16` có kích thước \(0.02\cdot48000\cdot2\cdot2=3840\) byte. Đoạn 20 ms mono `float32` cũng có đúng 3840 byte — cùng kích thước bộ đệm nhưng khác hoàn toàn bố cục dữ liệu; nếu chỉ kiểm tra `byteLength`, cả hai đều vượt qua. Một quantum 128 mẫu của Web Audio kéo dài \(2.67\,\mathrm{ms}\) ở 48 kHz và \(8\,\mathrm{ms}\) ở 16 kHz, không phải "10 ms".

### Tần số Nyquist và lý do 16 kHz không phải phép giảm mẫu miễn phí

Theo định lý lấy mẫu (Oppenheim & Schafer), tín hiệu giới hạn băng thông với phổ triệt tiêu từ \(f_s/2\) trở lên mới được xác định duy nhất từ các mẫu rời rạc. Hình minh họa cho thấy trường hợp vi phạm: ở \(f_s=8\,\mathrm{kHz}\), ta có:

$$
\sin(2\pi\cdot 7000\cdot n/f_s)=-\sin(2\pi\cdot 1000\cdot n/f_s).
$$

Sau khi đã lấy mẫu, cả bộ lọc Wiener, trừ phổ lẫn DeepFilterNet đều không thể tách biệt hai tần số này.

| Tần số lấy mẫu | Tần số Nyquist | Phạm vi thông tin giữ lại |
|----------------|----------------|---------------------------|
| 8 kHz | 4 kHz | Thoại băng hẹp; năng lượng phụ âm xát gần như mất hết |
| 16 kHz | 8 kHz | Thoại băng rộng (wideband); chuẩn cổ điển và DNS Challenge |
| 48 kHz | 24 kHz | Toàn băng (full-band); tần số công bố của DeepFilterNet và mặc định của `deepfilternet3-noise-filter` 1.3.0 |

Hạ tần số từ 48 kHz xuống 16 kHz chỉ hợp lệ sau khi đã lọc thông thấp để chặn hoàn toàn phần phổ trên 8 kHz. Cách làm "lấy mỗi mẫu thứ ba" sẽ gập dải 8–24 kHz xuống 0–8 kHz; tăng mẫu lại (upsample) sau đó cũng không khôi phục được băng tần đã mất. Đường xử lý toàn băng của Mezon giữ nguyên ở 48 kHz, trừ khi bạn chủ đích chọn mô hình 16 kHz kèm bộ lọc chống aliasing.

### Bố cục interleaved và planar

- **Stereo interleaved:** mẫu hai kênh xen kẽ `LRLRLR...`
- **Planar:** toàn bộ kênh trái L nối tiếp bởi kênh phải R (hoặc lưu qua hai con trỏ riêng biệt)

Đưa thẳng dữ liệu stereo interleaved vào FFT mono sẽ sinh ra các tần số giả theo đúng cơ chế gập phổ ở hình minh họa, vì dãy xen kẽ `L,R,L,R` dồn năng lượng về gần \(f_s/2\). Cần tách kênh hoặc gộp kênh tường minh trước khi nhân hàm cửa sổ.

### Gộp kênh (downmix) cho khử nhiễu tiếng nói

Cần chọn một quy tắc nhất quán và ghi rõ trong tài liệu:

1. **Trung bình cộng:** \(m=(L+R)/2\) (lưu ý trường hợp hai kênh tương quan hoặc ngược pha nhau).
2. **Chọn riêng kênh trái hoặc phải:** phù hợp khi biết rõ vị trí phần cứng micro của sản phẩm.
3. **Trộn theo năng lượng:** ít dùng trong xử lý thời gian thực.

Không nên tính trung bình sau khi đã chạy khử nhiễu độc lập trên hai kênh L và R nếu không có cơ chế xử lý không gian, vì pha giữa hai kênh sẽ bị lệch. Đặc biệt, với tín hiệu stereo ngược pha \(L=-R\) (thường gặp trong tín hiệu kiểm thử hoặc một số cấu hình micro mid-side), phép lấy trung bình cho kết quả bằng 0 tuyệt đối — mô hình "xử lý xong" nhưng đầu ra hoàn toàn im lặng.

### Đồng hồ lấy mẫu

`AudioContext.sampleRate` trên trình duyệt có thể là 44100 Hz, 48000 Hz hoặc giá trị khác, còn track từ `getUserMedia` có thể đã qua bước lấy mẫu lại của trình duyệt. Hãy luôn **đọc trực tiếp** `sampleRate` thay vì gán cứng, và đặt một bộ lấy mẫu lại chất lượng tốt ở biên khối khử nhiễu để đưa về đúng tần số lấy mẫu của mô hình.

Tần số 44.1 kHz là bẫy phổ biến trên các DAC tiêu dùng. Nếu dữ liệu 44.1 kHz bị gắn nhãn nhầm là 48 kHz, toàn bộ phổ sẽ bị dịch theo tỷ lệ \(44100/48000\approx 0.919\), khiến các họa âm rơi sai băng ERB. Giải pháp đúng là đọc tần số lấy mẫu thực của context và lấy mẫu lại đúng một lần.

### Kỳ vọng định dạng của Mezon / WebRTC (thông tin công khai)

Tích hợp trên trình duyệt thường nhận luồng `Float32` từ Web Audio, phổ biến ở 48 kHz và ở dạng mono sau khi downmix. DeepFilterNet được công bố ở cấu hình toàn băng 48 kHz ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)). Khi triển khai thực tế, luôn đối chiếu README hiện hành của `deepfilternet3-noise-filter` thay vì đóng cứng giả định từ bài học.

## Ví dụ có số

Một giây âm thanh mono `f32` ở 16 kHz chiếm \(16000\cdot4=64000\) byte. Một đoạn 10 ms mono `s16` ở 16 kHz chiếm \(0.010\cdot16000\cdot2=320\) byte, tương đương 160 mẫu — đây là kích thước hop cổ điển, khác với quantum 128 mẫu.

Các mẫu `s16` sát ngưỡng ±32767 dễ sinh họa âm méo mà bộ khử nhiễu có thể nhận nhầm là tiếng nói hoặc nhiễu; do đó nên giữ khoảng dự trữ biên độ trước khối NS.

Nếu 960 khung stereo interleaved ở 48 kHz bị đọc nhầm thành 960 mẫu mono, hệ thống sẽ xử lý 10 ms dữ liệu L/R xen kẽ như thể đó là 20 ms tín hiệu mono. Lưu ý rằng 960 mẫu ở 48 kHz đúng bằng độ dài cửa sổ phân tích của DeepFilterNet — chỉ cần sai bước nhảy (stride) một lần sẽ làm lệch toàn bộ các hop kế tiếp.

## Bẫy thường gặp

1. Mặc định thứ tự byte luôn là little-endian (LE) khi đọc tệp thô.
2. Để giá trị `float` vượt ngoài đoạn \([-1,1]\) sau xử lý, gây méo tín hiệu ở đầu ra (sink).
3. Gán cứng tần số lấy mẫu 48 kHz trong mã nguồn.
4. Đầu vào stereo bị cắt bỏ ngầm một nửa bộ đệm do tính sai kích thước.
5. Nhầm phần tiêu đề (header) của tệp WAV với dữ liệu PCM thô từ callback.

## Mini-lab

**Mục tiêu.** Kiểm chứng sóng sin 7 kHz lấy mẫu ở 8 kHz trùng khớp với sóng sin 1 kHz đảo dấu, đồng thời tính lại hai kích thước bộ đệm phổ biến.

```python
import numpy as np

fs = 8000
n = np.arange(int(0.004 * fs))  # 4 ms, cùng ý với hình
s1 = np.sin(2 * np.pi * 1000 * n / fs)
s7 = np.sin(2 * np.pi * 7000 * n / fs)
alias_err = np.max(np.abs(s7 + s1))
print("max |s7 - (-s1)|", alias_err)

def nbytes(seconds, fs, channels, bytes_per_sample):
    return int(round(seconds * fs)) * channels * bytes_per_sample

print("20 ms stereo s16 @ 48 kHz", nbytes(0.020, 48000, 2, 2))
print("10 ms mono s16 @ 16 kHz", nbytes(0.010, 16000, 1, 2))
```

**Kết quả kỳ vọng.** `alias_err` cỡ \(10^{-14}\) (xấp xỉ 0), còn hai kích thước bộ đệm lần lượt là `3840` và `320` byte.

**Lỗi thường gặp.** Dùng `linspace` khiến điểm cuối bị lệch hoặc trùng sẽ đẩy sai số alias từ mức làm tròn số lên \(O(1)\); quên nhân số kênh `channels` hoặc dùng nhầm 4 byte cho `s16` sẽ cho ra 7680 hoặc 640 và gây lệch kích thước giữa WAV với worklet; nếu `alias_err` ra khoảng 2, nghĩa là bạn đã so `s7` với `s1` mà quên dấu trừ của phép gập pha — giá trị mẫu trùng khớp về độ lớn nhưng ngược dấu, đó chính là aliasing.

## Bài tập nhỏ

1. Tính số byte của đoạn âm thanh 10 ms mono `s16` ở 16 kHz.
2. Viết mã giả (pseudocode) gộp kênh stereo interleaved sang mono bằng trung bình cộng.
3. Giải thích vì sao tín hiệu stereo ngược pha \((L=-R)\) gây sự cố với phép gộp kênh trung bình.
4. Nêu ba vị trí trên đường truyền WebRTC nơi `sampleRate` có thể khác nhau.
5. Chuyển đổi giá trị `s16` bằng −16000 sang chuẩn `float` Full Scale bằng phép chia cho 32768.

### Gợi ý đáp án

1. Số mẫu là \(0.010\times16000=160\), nhân với 2 byte mỗi mẫu cho 320 byte.
2. Đọc từng cặp mẫu `(L, R)` đã giải mã và xuất `(L+R)/2` ở kiểu số thực; không tính trung bình trực tiếp trên từng byte thô.
3. Trung bình của hai kênh ngược pha bằng 0 tại mọi mẫu, khiến mô hình chỉ nhận được khoảng lặng.
4. Thiết bị thu (micro/driver), `AudioContext` của trình duyệt và tần số lấy mẫu gốc của mô hình (48 kHz, 16 kHz hoặc 44.1 kHz).
5. \(-16000/32768\approx -0.488\).

## Đọc thêm

- Oppenheim & Schafer, *Discrete-Time Signal Processing* — lấy mẫu và tần số Nyquist.
- Tài liệu Web Audio về `AudioBuffer` và bộ đệm trong `AudioWorkletProcessor`.
- Ràng buộc media track của WebRTC và tài liệu định dạng PCM.
- Cấu hình định khung toàn băng của DeepFilterNet: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).

## Video tham khảo

- [Xiph.Org Video Presentations: Digital Show & Tell](https://xiph.org/video/vid2.shtml) — Xiph.Org, tiếng Anh. **Xem trước.** Video chính thức của Xiph.Org về PCM, độ sâu bit và khôi phục tín hiệu — nên xem trước khi gỡ lỗi tensor 16 kHz nhận từ callback 48 kHz.
- [Aliasing and the Sampling Theorem Simplified](https://www.youtube.com/watch?v=KuaannH5pnM) — Barry Van Veen, tiếng Anh. Cơ chế gập Nyquist minh họa rõ dạng lỗi âm thầm khi một kênh bị lấy mẫu lại sai tần số.
