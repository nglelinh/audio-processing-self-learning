---
layout: post
title: "02-03 Cửa sổ và rò phổ"
chapter: "02"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Cửa sổ cân bằng giữa rò phổ (spectral leakage: năng lượng một tone lan sang bin khác) và độ rộng búp chính. Trong NS, cửa sổ sai — hoặc cặp phân tích/tổng hợp không khớp — tạo musical noise và warble theo hop. Con số nên nhớ theo dB: cửa sổ chữ nhật để sidelobe đầu khoảng \(-13\,\mathrm{dB}\), Hann đẩy sidelobe đó xuống khoảng \(-31\,\mathrm{dB}\).

## Mục tiêu học tập

1. Giải thích rò phổ do cắt hình chữ nhật.
2. So sánh định tính các cửa sổ thường gặp (Hann, Hamming, Blackman).
3. Nối độ rộng búp chính với phân giải tần số và định vị thời gian.
4. Nêu cách cửa sổ tương tác với COLA và mask NS.
5. Chọn cửa sổ khớp front-end STFT đã huấn luyện.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Minh họa rò cửa sổ chữ nhật |
| 12–28 | Bảng cửa sổ; sidelobe và búp chính |
| 28–42 | COLA và chọn cửa sổ; nhân cửa sổ hai lần |
| 42–52 | Musical noise và huyền thoại “bin độc lập” |
| 52–60 | Bài tập |

![Cửa sổ chữ nhật so với Hann: biến đổi chữ nhật giữ đuôi sinc dài, Hann hạ sidelobe và làm rộng búp chính]({{ site.imgurl }}/generated/window-leakage.png)

*Hình. Biên độ chuẩn hóa đỉnh của một tone đã nhân cửa sổ: chữ nhật rò một đuôi sidelobe chậm, Hann đổi búp chính rộng hơn để lấy sàn thấp hơn nhiều.*

## Giải thích cốt lõi

### Cơ chế rò

Nhân với \(w[n]\) là chập DTFT với \(W(e^{j\omega})\). Cửa sổ chữ nhật có sidelobe cao → bin xa bị nhiễm. Cửa sổ thuôn hạ sidelobe, làm rộng búp chính → các bin gần bị nhòe vào nhau.

Một frame hữu hạn đã là phép nhân với hình chữ nhật, kể cả khi bạn “không áp cửa sổ”. DTFT của hình đó là nhân Dirichlet. Sidelobe đầu thấp hơn búp chính khoảng **13 dB**, và đuôi giảm chậm. Tone lệch tâm bin — mọi hài tiếng nói thật rồi cũng lệch — đổ năng lượng hàng chục bin xa, mức mà bộ theo dõi nhiễu có thể tưởng là nhiễu.

Hann tuần hoàn của bài 02-02,

$$
w[n]=\frac12-\frac12\cos\frac{2\pi n}{L},
$$

triệt đuôi chậm đó: sidelobe đầu xuống khoảng **−31 dB**, yên hơn chừng 18 dB, và các sidelobe xa tiếp tục giảm. Cái giá là độ rộng búp chính, khoảng bốn bin từ null đến null thay vì hai. Kéo dài \(L\) và đổi sang Hann là hai núm khác nhau.

Đọc trục hình theo dB so với đỉnh.

### So sánh định tính

| Cửa sổ | Sidelobe | Búp chính | Ghi chú |
|--------|----------|-----------|---------|
| Chữ nhật | kém (sidelobe đầu ≈ −13 dB) | hẹp nhất (~2 bin) | tò mò phân tích; đây là cửa sổ ngầm nếu bạn bỏ qua |
| Hann | tốt (sidelobe đầu ≈ −31 dB) | rộng hơn (~4 bin) | lựa chọn STFT; COLA @ 50% với dạng tuần hoàn |
| Hamming | tương tự | tương tự | sàn sidelobe khác; không cùng đồng nhất thức COLA |
| Blackman | sidelobe thấp hơn | rộng hơn | mượt hơn; đừng thay vào mô hình train bằng Hann |

Hệ số lấy từ tài liệu DSP, đừng bịa. Đầu Hamming không về 0, nên không thay thế được cặp COLA của Hann dù đồ thị “na ná”.

### Đánh đổi phân giải

Phân giải tần số hiệu dụng \(\sim \alpha f_s/L\) với \(\alpha>1\) tùy cửa sổ. Định vị thời gian \(\sim L/f_s\). NS tiếng nói cần đủ phân giải để tách formant khỏi sàn nhiễu, và đủ cục bộ thời gian cho phụ âm — cửa sổ vài chục ms, không phải 1 ms hay 1 s.

Ở 48 kHz với \(L=960\), búp chính Hann khoảng bốn bin rộng \(4\cdot48000/960=200\,\mathrm{Hz}\). Nó không tách các hài của giọng trầm, và nó nhòe một plosive 5 ms trên cả cửa sổ 20 ms. Muốn bin mịn hơn thì kéo \(L\) và trả bằng độ trễ. Muốn ít rò sang sàn xa thì đổi cửa sổ, không phải zero-pad: pad nội suy \(W(e^{j\omega})\), không làm nó hẹp lại.

### Cửa sổ và mask

Gain nhảy lung tung giữa các bin kề nhau thì chống lại độ mượt vốn có của cửa sổ — hoặc tạo musical noise khi coi các bin là độc lập. Mask mượt theo tần số và thời gian hợp vật lý hơn. Phân tích chữ nhật làm giả định “bin độc lập” càng sai: bin \(k+8\) vẫn chứa tone của bin \(k\) ở mức nghe được. Gate cứng các “bin nhiễu” sẽ chặt sidelobe của nguyên âm và để lại búp chính.

### Phân tích và tổng hợp

Có pipeline chỉ nhân \(w\) lúc phân tích và dùng cửa sổ tổng hợp khác cho COLA. Có pipeline dùng \(\sqrt{\text{Hann}}\) cả hai phía. **Khớp lúc train.** Đổi sang Blackman “cho hay” sẽ vỡ tái dựng. Bình phương Hann không phải COLA: tích \(w\cdot w\) gợn giữa \(1/2\) và \(1\). Căn bậc hai chia cửa sổ để mỗi phía đều thuôn mà tích vẫn cộng phẳng.

Hann có trung bình \(1/2\), nên phân tích chưa chuẩn hóa làm công suất băng rộng tụt khoảng 6 dB trước cả suppressor. SI-SDR so với tham chiếu miền thời gian sẽ nhìn như một lỗ hệ thống cho đến khi chia cho hằng COLA.

## Ví dụ có số

16 kHz, \(L=512\), tone đúng bin 32 so với bin 32.5. Chữ nhật: lệch bin thì lan rộng. Hann: sidelobe giảm, búp chính rộng — cả bin 32 và 33 đều sáng. Tone đúng bin có thể trông gần như lý tưởng (sidelobe ở sàn số) và giấu một cửa sổ xấu. Hãy luôn thử lệch nửa bin. Mini-lab in sidelobe đo được; nó không trùng khít −13 / −31 dB trong sách vì đỉnh nằm giữa hai bin và phép đo bỏ một vành bảo vệ. Khoảng cách giữa chữ nhật và Hann vẫn là bài học của hình.

Spectral subtraction với sàn từng bin độc lập để lại các đỉnh lẻ — birdies. Làm mượt thì đỡ nhưng làm mờ tiếng nói. Đó là sức căng cổ điển trước SE neural.

## Bẫy thường gặp

1. Áp cửa sổ hai lần (API đã nhân cửa sổ + nhân tay).
2. Dùng chữ nhật vì “FFT cần thế”.
3. Quên gain cửa sổ khi kiểm Parseval / SI-SDR.
4. Cửa sổ train khác cửa sổ serve.
5. Kỳ vọng cửa sổ tự chữa aliasing (không chữa được).

## Mini-lab

**Mục tiêu.** FFT một sine lệch bin, lần lượt với cửa sổ chữ nhật và Hann tuần hoàn, in mức sidelobe theo dB so với đỉnh.

```python
import numpy as np

fs, N = 16000, 512
n = np.arange(N)
f = 32.5 * fs / N  # giữa bin 32 và 33
x = np.sin(2 * np.pi * f * n / fs)
hann = 0.5 - 0.5 * np.cos(2 * np.pi * n / N)

def sidelobe_db(mag, guard=3):
    mag = mag / mag.max()
    k = int(np.argmax(mag))
    side = np.concatenate([mag[: max(0, k - guard)], mag[k + guard + 1 :]])
    return 20 * np.log10(side.max())

rect = np.abs(np.fft.rfft(x))
han = np.abs(np.fft.rfft(x * hann))
print("rect sidelobe dB", round(float(sidelobe_db(rect)), 1))
print("hann sidelobe dB", round(float(sidelobe_db(han)), 1))
```

**Kỳ vọng.** Sidelobe chữ nhật gần **−17 dB**, Hann gần **−40 dB** (vành 3 bin quanh đỉnh lệch bin). Hann thấp hơn, và búp chính của nó rộng hơn nếu bạn vẽ cả hai.

**Khi hỏng.** Bin nguyên (`32 * fs / N`) đẩy cả hai sidelobe xuống sàn số (dưới −200 dB) và không dạy được gì. `np.hann` so với công thức tuần hoàn đổi nhẹ số Hann nhưng không khép khoảng cách. Quên chia `mag.max()` thì in đơn vị FFT tuyệt đối, không phải dB so với đỉnh. Vành bằng 0 sẽ gọi vai của búp chính là “sidelobe”, và cả hai cửa sổ trông cùng tệ.

## Bài tập nhỏ

1. Vì sao cửa sổ taper giảm sidelobe?
2. \(L\) gấp đôi ⇒ độ rộng búp chính roughly thế nào?
3. Hop thân thiện COLA phổ biến với Hann?
4. Mask per-bin hung hãn tạo musical noise thế nào?
5. Một lý do \(\sqrt{\mathrm{Hann}}\) xuất hiện trong codebase STFT?

### Gợi ý đáp án

1. Biến đổi \(W\) của cửa sổ có sidelobe nhỏ hơn, và nhân \(w\) là chập tone với \(W\).
2. Độ rộng theo hertz tỉ lệ \(f_s/L\), nên giảm một nửa; độ rộng theo bin của Hann vẫn khoảng 4.
3. \(R=L/2\) với Hann tuần hoàn (bài 02-02).
4. Các số 0 cứng giữa các bin chặt sidelobe của một hài thật và để lại đỉnh lẻ, sau ISTFT thành tiếng chim.
5. Để phân tích và tổng hợp đều thuôn mà tích của chúng vẫn thỏa COLA.

## Đọc thêm

- Oppenheim & Schafer — cửa sổ và phân tích phổ.
- Julius O. Smith, *Spectral Audio Signal Processing* — mức sidelobe và độ rộng búp chính.
- Cấu hình STFT DeepFilterNet: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588).
