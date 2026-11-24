---
layout: post
title: "01-07 Checklist bẫy Fourier cho kỹ sư"
chapter: "01"
order: 7
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Khi bộ khử nhiễu cho ra âm thanh lỗi, phản xạ phổ biến của nhiều kỹ sư là đem mô hình đi huấn luyện lại ngay lập tức. Bài học này cung cấp danh mục kiểm tra Fourier/STFT trước khi triển khai — bao gồm đơn vị, hàm cửa sổ, tính đối xứng, hệ số chuẩn hóa, lấy mẫu lại và DC/Nyquist — để chỉ nghi ngờ mạng nơ-ron sau khi đã loại trừ toàn bộ lỗi pipeline.

![Các bản sao phổ khi lấy mẫu — hình đứng sau một bin Nyquist bị gán sai]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Hình. Bẫy phổ biến nhất trong bài học này là sai trục tần số: Nyquist luôn ở \(f_s/2\), và một bin lệch đi một chỉ số đã tương ứng với giá trị Hz khác chứ không phải sai số làm tròn.*


Một trong những lỗi âm thanh khó chịu nhất khi lập trình DSP không phải là chương trình bị crash, mà là chương trình *vẫn chạy êm ru và phát ra tiếng* — nhưng tiếng bị méo nhẹ, âm lượng sai đúng 6 dB, hoặc xuất hiện tiếng "tách tách" mơ hồ ở rìa mỗi khung! Thủ phạm hầu như luôn nằm trong một nhóm nhỏ các **bẫy Fourier kinh điển**: nhầm tích chập vòng với tích chập tuyến tính, quên hệ số 2 của phổ một phía `rfft`, hay quên chuẩn hóa năng lượng cửa sổ.

---

## Bản đồ kiến thức nền: Ba nhóm bẫy Fourier kinh điển mà kỹ sư âm thanh hay vấp phải là gì?

### 1. Tích chập vòng (Circular) vs. Tích chập tuyến tính (Linear Convolution)
Định lý tích chập của DFT nói rằng nhân hai phổ cỡ $$N$$ tương đương **tích chập vòng modulo $$N$$** trong miền thời gian! Nếu tín hiệu dài $$L$$ và bộ lọc dài $$M$$, kết quả tích chập tuyến tính thực sự dài $$L + M - 1$$ mẫu. Nếu bạn dùng FFT cỡ $$N < L + M - 1$$ mà không đệm đủ số 0, phần đuôi thừa sẽ **quấn ngược vòng lên đầu khung** gây chồng lấp miền thời gian (time-domain aliasing)!

### 2. Quy ước chuẩn hóa và Phổ một phía (`rfft` vs. `fft`)
Giữa NumPy, PyTorch, SciPy và RustFFT, quy ước chia $$1/N$$ có thể đặt ở IFFT, chia $$1/\sqrt{N}$$ cho cả hai chiều, hoặc không chia ở đâu cả! Ngoài ra, khi dùng `rfft` cho tín hiệu thực để tính phổ công suất (PSD), mỗi bin trung gian $$1 \le k < N/2$$ đại diện cho cả tần số dương $$+f_k$$ lẫn âm $$-f_k$$ nên năng lượng phải nhân **hệ số 2** (trừ bin DC $$k=0$$ và Nyquist $$k=N/2$$).

### 3. Đứt gãy pha (Phase Discontinuity) và Méo ranh giới khung
Thay đổi biên độ hoặc pha đột ngột giữa hai khung liên tiếp mà không dùng cửa sổ mượt và kỹ thuật chồng lấp (Overlap-Add / Overlap-Save) sẽ tạo ra bước nhảy biên độ ở ranh giới mỗi 10 ms — tai người lập tức nghe thành tiếng rè 100 Hz cực kỳ khó chịu!

---

### Khung giải thích: tự tay bắt tại trận lỗi "Tích chập vòng quấn ngược" với dãy 3 mẫu (nên đọc chậm)

Xét tín hiệu $$x = [1, 1, 1]$$ (độ dài $$L = 3$$) lọc qua bộ lọc $$h = [1, 1, 1]$$ (độ dài $$M = 3$$):

1. **Kết quả tích chập tuyến tính ĐÚNG** (độ dài phải là $$L + M - 1 = 3 + 3 - 1 = \mathbf{5\text{ mẫu}}$$):
   $$
   y_{\text{linear}} = [1,\ 2,\ 3,\ 2,\ 1].
   $$
2. **Sai lầm khi dùng FFT cỡ $$N = 4$$ (quên đệm đủ lên $$N \ge 5$$):**
   - Đệm thành $$x_4 = [1, 1, 1, 0]$$ và $$h_4 = [1, 1, 1, 0]$$, rồi tính $$\text{IFFT}_4(\text{FFT}_4(x_4) \cdot \text{FFT}_4(h_4))$$.
   - Phần tử thứ 5 (chỉ số $$n = 4$$, giá trị $$1$$) không có chỗ chứa trong mảng 4 phần tử nên bị **quấn modulo 4** về chỉ số $$4 \bmod 4 = \mathbf{0}$$ và cộng đè lên $$y[0] = 1$$!
   - Kết quả sai thu được là:
     $$
     y_{\text{circular}, 4} = [1 + 1,\ 2,\ 3,\ 2] = [\mathbf{2},\ 2,\ 3,\ 2] \neq [1,\ 2,\ 3,\ 2,\ 1]!
     $$
3. **Cách sửa duy nhất đúng:** Luôn đệm số 0 cho cả $$x$$ và $$h$$ tới kích thước $$N_{\text{FFT}} \ge L + M - 1$$ (ở đây là $$N = 5$$, hoặc lũy thừa 2 gần nhất $$N = 8$$) thì tích chập vòng mới trùng khít 100% với tích chập tuyến tính!

---

## Mục tiêu học tập

1. Chẩn đoán các lỗi biến đổi Fourier và DFT phổ biến trong pipeline âm thanh.
2. Xác thực đơn vị tần số (Hz, chỉ số bin và tần số chuẩn hóa).
3. Áp dụng danh mục kiểm tra có hệ thống trước khi quy kết lỗi cho mô hình mạng nơ-ron.
4. Nhận diện lỗi cửa sổ/COLA và lỗi đối xứng liên hợp bằng cả thính giác lẫn kiểm thử tự động.
5. Áp dụng danh mục kiểm tra vào quy trình gỡ lỗi kiểu Mezon/DeepFilterNet mà không suy đoán chi tiết nội bộ.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–8 | Tình huống thực tế (war story): từ triệu chứng → suy đoán sai → nguyên nhân gốc |
| 8–30 | Rà soát toàn bộ danh mục kiểm tra kèm thí nghiệm phân tích |
| 30–45 | Các bài kiểm thử đơn vị (unit test) cần duy trì trong kho mã |
| 45–55 | Trình tự gỡ lỗi cho Mezon/DeepFilterNet |
| 55–60 | Bài tập nhỏ |

## Danh mục kiểm tra chính

1. **Tính chính xác của tần số lấy mẫu** — tần số PCM phải khớp với tần số mô hình (hoặc đi qua bộ lấy mẫu lại có tài liệu rõ ràng); bắt buộc lọc chống aliasing khi giảm mẫu; không gán cứng 48 kHz.
2. **Đơn vị trục tần số** — tuân thủ \(f=k f_s/N\); mọi bộ lọc định nghĩa theo Hz phải dùng đúng \(f_s\).
3. **Chuẩn hóa FFT và Parseval** — đối chiếu tài liệu thư viện; phép biến đổi khứ hồi STFT → ISTFT phải bảo toàn năng lượng.
4. **Cửa sổ và điều kiện COLA** — cặp cửa sổ phân tích/tổng hợp cùng bước nhảy hop phải thỏa điều kiện COLA và khớp cấu hình huấn luyện.
5. **Đối xứng liên hợp và đóng gói phổ** — đầu vào của iFFT tín hiệu thực phải có tính đối xứng Hermitian; phần ảo tại DC và Nyquist xấp xỉ 0.
6. **Bố cục kênh (channel layout)** — phân biệt xen kẽ (interleaved) với tách mặt phẳng (planar) và xác định rõ quy tắc gộp kênh stereo → mono.
7. **Tính toán bước nhảy hop và độ trễ** — ghi nhận rõ độ trễ look-ahead (ms), bộ đệm vòng và khoảng khởi động (warmup) nhất quán khi đo chỉ số.
8. **Thành phần DC và nhiễu tần số cực thấp** — dùng bộ chặn DC nếu micro có độ lệch tĩnh; không kỳ vọng mô hình khử nhiễu tự xử lý phần DC này.
9. **Hiển thị thang dB** — dùng nhất quán \(20\log_{10}|X|\) cho biên độ và giới hạn cận dưới để tránh \(\log 0\).
10. **Bộ lấy mẫu lại và miền đánh giá** — tính chỉ số chất lượng ở tần số lấy mẫu đã thống nhất; tránh lấy mẫu lại hai lần trong bài kiểm thử A/B.

### Minh họa số cho hai bẫy điển hình

**Bin Nyquist là một chỉ số nguyên phụ thuộc vào \(f_s\).** Với \(N\) chẵn, bin Nyquist nằm tại \(k=N/2\), tương ứng tần số \(f_s/2\). Xét \(N=512\) và \(f_s=16\,\mathrm{kHz}\): bin đúng là \(k=256\) tại \(8000\,\mathrm{Hz}\). Nếu lệch một chỉ số xuống \(k=255\), tần số tương ứng chỉ là \(255\times 16000/512=7968.75\,\mathrm{Hz}\); một mặt nạ đặt ngưỡng ở bin 255 sẽ bỏ sót bin Nyquist, trong khi bài test viết sơ sài ("một bin cao nào đó có thay đổi") vẫn báo đạt. Nghiêm trọng hơn, nếu gán nhầm mảng 16 kHz sang nhãn 48 kHz thì bin 256 sẽ bị hiểu là \(256\times 48000/512=24000\,\mathrm{Hz}\) — bạn tưởng đang xử lý vùng gần 24 kHz trong khi tín hiệu thực chỉ chứa năng lượng đến 8 kHz. Khi đó, `setSuppressionLevel(0–100)` sẽ điều chỉnh độ sâu khử trên một trục tần số sai. Hãy kiểm tra tần số lấy mẫu và bảng ánh xạ bin trước khi động vào `DeepFilterNet3Core`.

**Tráo đổi phần thực và phần ảo.** Phổ DFT của một khung PCM thực luôn thỏa tính đối xứng liên hợp \(X[k]=X^*[(N-k)\bmod N]\), đồng thời bin DC và bin Nyquist đều là số thực thuần. Nếu vô tình tráo phần thực và phần ảo, đẳng thức đối xứng sẽ bị phá vỡ với sai số cùng bậc độ lớn của phổ. Khi tính biến đổi nghịch, kết quả xuất hiện phần ảo khác không; việc ép lấy phần thực rồi tiếp tục sẽ che giấu lỗi thành âm thanh đục và lệch pha. Phần Mini-lab dưới đây dùng câu lệnh `assert` để bắt cả hai lỗi này.

## Kịch bản gỡ lỗi nhanh

- Tiếng rung giật (warble) chu kỳ 100 Hz → kiểm tra hop 10 ms và lỗi điều kiện COLA.
- "Mô hình cắt mất phụ âm" → kiểm tra tín hiệu thực có năng lượng trên 6 kHz hay không và đối chiếu ánh xạ bin giữa 48 kHz với 16 kHz.
- Chỉ số SI-SDR tốt nhưng người nghe phàn nàn → kiểm tra lỗi pha và nhiễu nhạc (Chương 08).

## Các bài kiểm thử đơn vị nên duy trì

Cần giữ sẵn các bài test tự động cho: khứ hồi xung đơn vị (impulse round-trip), đẳng thức Parseval cho hàm bọc FFT, lấy mẫu lại sóng sin không sinh thành phần alias giả, và kiểm chứng độ dài/biên độ sau bước gộp kênh mono.

## Trình tự gỡ lỗi cho Mezon / DeepFilterNet (thông tin công khai)

1. Xác minh tần số lấy mẫu và số kênh theo README của gói hoặc model card.
2. Kiểm tra khâu truyền khung (callback và bộ đệm vòng) — nội dung Chương 05.
3. Rà soát độ chính xác của STFT theo danh mục kiểm tra của bài này.
4. Sau cùng mới thay đổi biến thể mô hình hoặc tùy chọn của gói npm.
5. Khi lập luận về thuật toán, trích dẫn các bài báo DeepFilterNet công khai; không suy đoán cấu trúc đồ thị nội bộ chưa công bố của Mezon.

## Bẫy thường gặp

1. Thay đổi đồng thời ba yếu tố (tần số lấy mẫu, bước nhảy hop và mô hình).
2. Kết luận chất lượng chỉ dựa trên một đoạn demo quán cà phê.
3. Vô tình đưa checkpoint không nhân quả vào wrapper streaming.
4. Bỏ qua phân vị đuôi p99 của thời gian xử lý mỗi hop.
5. Cố "khắc phục" tiếng rung giật bằng cách tăng cường độ khử nhiễu.

## Mini-lab

**Mục tiêu.** Viết câu lệnh `assert` để phát hiện phổ bị tráo phần thực/ảo và chứng minh bin Nyquist bị lệch một chỉ số sẽ không còn là 8 kHz.

```python
import numpy as np

def hermitian_error(X):
    n = np.arange(X.shape[0])
    mirror = np.conj(X[(X.shape[0] - n) % X.shape[0]])
    return np.max(np.abs(X - mirror))

x = np.array([1.0, 0.5, -0.2, 0.1, 0.0, -0.3, 0.4, 0.2])
X = np.fft.fft(x)
swapped = X.imag + 1j * X.real

def nyquist_hz(n_fft, fs):
    return (n_fft // 2) * fs / n_fft

print(f"good={hermitian_error(X):.3e}")
print(f"swapped={hermitian_error(swapped):.3f}")
print(f"nyquist={nyquist_hz(512, 16000):.2f}")
print(f"off_by_one={(512 // 2 - 1) * 16000 / 512:.2f}")
assert hermitian_error(X) < 1e-8
assert hermitian_error(swapped) > 1e-3
assert nyquist_hz(512, 16000) == 8000.0
```

**Kết quả kỳ vọng.** `good=0.000e+00`, `swapped=3.400`, `nyquist=8000.00`, `off_by_one=7968.75`, cả ba câu lệnh `assert` đều đạt. Nếu bỏ `assert` kiểm tra phổ bị tráo, dữ liệu hỏng sẽ lọt qua; nếu đổi `nyquist_hz` thành \(N/2-1\), `assert` cuối sẽ báo lỗi ngay lập tức.

**Lỗi thường gặp.** Kiểm tra tính đối xứng bằng `np.allclose(X, np.conj(X[::-1]))` mà quên rằng chỉ số 0 phải ánh xạ vào chính nó (công thức chuẩn dùng \((N-k)\bmod N\) để bin DC khớp với DC); hoặc chấp nhận 7968.75 Hz là "đủ gần Nyquist" trong bài kiểm thử đơn vị.

## Bài tập nhỏ

1. Chọn ba mục trong danh mục kiểm tra chính và đặt tên bài kiểm thử đơn vị tương ứng cho từng mục.
2. Với hop 5 ms, lỗi COLA sẽ tạo ra tiếng rung giật ở tần số xấp xỉ bao nhiêu Hz?
3. Vì sao dùng sai giá trị \(f_s\) trong công thức \(f=kf_s/N\) lại tạo ra triệu chứng giống như mô hình kém chất lượng?
4. Xây dựng mẫu báo cáo sự cố 6 bước cho lỗi "khử nhiễu nghe kém trên Chrome".
5. Mục nào trong danh mục kiểm tra sẽ phát hiện lỗi đưa dữ liệu stereo xen kẽ (interleaved) trực tiếp vào FFT mono?

### Gợi ý đáp án

1. Đặt tên bài kiểm thử gắn trực tiếp với lỗi cần bắt: `test_cola_impulse_roundtrip`, `test_parseval_scale`, `test_downmix_length`.
2. Lỗi COLA ở hop 5 ms sẽ gây điều biến biên độ ở tần số gần \(1/0.005=200\,\mathrm{Hz}\).
3. Mọi nhãn tần số của bin đều tỷ lệ thuận với \(f_s\); một mô hình 16 kHz khi nhận dữ liệu 48 kHz sẽ hoạt động như bộ lọc thông thấp dù trọng số mô hình không hề thay đổi.
4. Ghi nhận theo thứ tự: tần số lấy mẫu, số kênh, bước nhảy hop (ms), phân vị p95 của thời gian callback, kết quả kiểm tra xung COLA, rồi mới tới mã định danh mô hình; mỗi lần thử nghiệm chỉ thay đổi đúng một biến.
5. Mục bố cục kênh (mục 6): tín hiệu stereo xen kẽ nếu bị đọc như mono sẽ trộn mẫu kênh trái và kênh phải thành các mẫu thời gian liên tiếp.

## Đọc thêm

- Oppenheim & Schafer — hàm cửa sổ, hệ số tỷ lệ và các bẫy phổ biến của DFT.
- DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — cấu hình STFT và lưu ý thời gian thực; Julius O. Smith, https://ccrma.stanford.edu/~jos/mdft/, cho các tính chất đối xứng DFT được kiểm chứng bằng `assert`.
- Tài liệu đo hiệu năng (profiling) của ONNX Runtime và trình duyệt để tách riêng chi phí STFT với chi phí mạng nơ-ron.

## Video tham khảo

- [11: Spectral Analysis Part 1 - Intro to Neural Computation](https://www.youtube.com/watch?v=4ip-4ai6kN8) — MIT OpenCourseWare, tiếng Anh. **Xem trước.** Nhấn mạnh rằng gọi FFT rất dễ sai ngầm; nên xem các cảnh báo về trục tần số, hệ số chuẩn hóa và hàm cửa sổ trước khi nghĩ đến việc huấn luyện lại mô hình.
- [Lecture 13: Spectral Leakage, Windowing, with Examples of Hanning and Hamming Windows](https://www.youtube.com/watch?v=tCWU9C-LdJQ) — Bahga Lab IIT Delhi, tiếng Anh. So sánh búp phụ của cửa sổ Hann với cửa sổ chữ nhật, minh họa phần rò phổ trong danh mục kiểm tra.
- [Xiph.Org Video Presentations: Digital Show & Tell](https://xiph.org/video/vid2.shtml) — Xiph.Org, tiếng Anh. Video chính thức của Xiph.Org về lấy mẫu và tái tạo tín hiệu, hữu ích khi cần phân biệt lỗi lệch trục tần số do tần số lấy mẫu với lỗi của mạng nơ-ron.
