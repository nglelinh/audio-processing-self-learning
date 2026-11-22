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

Hàm cửa sổ cân bằng sự đánh đổi giữa hiện tượng rò phổ (spectral leakage: năng lượng của một thành phần tần số lan sang các bin khác) và độ rộng búp chính (main lobe). Trong bài toán khử nhiễu, chọn sai hàm cửa sổ — hoặc dùng cặp cửa sổ phân tích/tổng hợp không khớp nhau — sẽ sinh ra nhiễu nhạc (musical noise) và tiếng rung giật theo nhịp hop. Hai con số mốc cần nhớ theo dB là: cửa sổ chữ nhật có búp phụ (sidelobe) đầu tiên ở mức khoảng \(-13\,\mathrm{dB}\), trong khi cửa sổ Hann đẩy búp phụ này xuống khoảng \(-31\,\mathrm{dB}\).

## Mục tiêu học tập

1. Giải thích cơ chế phát sinh rò phổ khi cắt đoạn bằng cửa sổ chữ nhật.
2. So sánh định tính các hàm cửa sổ thông dụng (Hann, Hamming, Blackman).
3. Liên hệ độ rộng búp chính với độ phân giải tần số và khả năng định vị thời gian.
4. Trình bày sự tương tác giữa hàm cửa sổ, điều kiện COLA và mặt nạ khử nhiễu.
5. Chọn hàm cửa sổ khớp chính xác với phần tiền xử lý STFT của mô hình đã huấn luyện.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Minh họa hiện tượng rò phổ của cửa sổ chữ nhật |
| 12–28 | Bảng so sánh cửa sổ: mức búp phụ và độ rộng búp chính |
| 28–42 | Điều kiện COLA, lựa chọn cửa sổ và lỗi nhân cửa sổ hai lần |
| 42–52 | Nhiễu nhạc và ngộ nhận về "các bin tần số độc lập" |
| 52–60 | Bài tập nhỏ |

![Cửa sổ chữ nhật so với Hann: biến đổi chữ nhật giữ đuôi sinc dài, Hann hạ sidelobe và làm rộng búp chính]({{ site.imgurl }}/generated/window-leakage.png)

*Hình. Phổ biên độ đã chuẩn hóa đỉnh của một âm đơn qua cửa sổ: cửa sổ chữ nhật để lại đuôi búp phụ suy giảm chậm, còn cửa sổ Hann đánh đổi búp chính rộng hơn để đạt nền búp phụ thấp hơn đáng kể.*

## Giải thích cốt lõi

### Cơ chế rò phổ

Nhân tín hiệu với hàm cửa sổ \(w[n]\) ở miền thời gian tương đương với phép tích chập DTFT của tín hiệu với đáp ứng phổ \(W(e^{j\omega})\). Cửa sổ chữ nhật có búp phụ cao nên làm nhiễm năng lượng sang các bin ở xa. Các cửa sổ vuốt thuôn hai đầu (tapered) giúp hạ thấp búp phụ nhưng làm rộng búp chính, khiến các bin sát nhau bị nhòe vào nhau nhiều hơn.

Bản thân việc cắt một khung hữu hạn đã ngầm nhân tín hiệu với cửa sổ chữ nhật, ngay cả khi bạn "không áp hàm cửa sổ nào". DTFT của cửa sổ chữ nhật là nhân Dirichlet: búp phụ đầu tiên chỉ thấp hơn đỉnh chính khoảng **13 dB** và phần đuôi tắt rất chậm. Khi một thành phần tần số rơi lệch tâm bin — điều luôn xảy ra với họa âm tiếng nói thực — năng lượng của nó lan ra hàng chục bin lân cận với mức đủ lớn để bộ theo dõi nhiễu nhận nhầm thành nhiễu nền.

Cửa sổ Hann tuần hoàn ở bài 02-02:

$$
w[n]=\frac12-\frac12\cos\frac{2\pi n}{L},
$$

giúp triệt tiêu phần đuôi tắt chậm đó: búp phụ đầu tiên hạ xuống khoảng **−31 dB** (thấp hơn khoảng 18 dB), và các búp phụ xa tiếp tục suy giảm nhanh. Cái giá phải trả là độ rộng búp chính tăng lên khoảng bốn bin (tính từ điểm 0 đến điểm 0) thay vì hai bin. Lưu ý rằng kéo dài độ dài cửa sổ \(L\) và đổi sang cửa sổ Hann là hai tham số điều chỉnh độc lập nhau.

Khi đọc biểu đồ minh họa, luôn chú ý trục tung tính theo dB tương đối so với đỉnh.

### So sánh định tính các hàm cửa sổ

| Cửa sổ | Búp phụ (sidelobe) | Búp chính (main lobe) | Ghi chú |
|--------|--------------------|-----------------------|---------|
| Chữ nhật | Kém (búp phụ đầu ≈ −13 dB) | Hẹp nhất (~2 bin) | Chủ yếu có giá trị phân tích lý thuyết; là cửa sổ ngầm nếu bỏ qua bước nhân cửa sổ |
| Hann | Tốt (búp phụ đầu ≈ −31 dB) | Rộng hơn (~4 bin) | Lựa chọn phổ biến cho STFT; thỏa COLA ở chồng lấp 50% với dạng tuần hoàn |
| Hamming | Tương tự | Tương tự | Mức nền búp phụ xa khác; không thỏa cùng đồng nhất thức COLA như Hann |
| Blackman | Thấp hơn nữa | Rộng hơn nữa | Rất mượt nhưng không được tự ý thay vào mô hình huấn luyện bằng Hann |

Các hệ số chuẩn cần tra cứu từ tài liệu DSP chứ không tự ước đoán. Vì hai đầu của cửa sổ Hamming không về 0 nên nó không thể thay thế trực tiếp cặp COLA của Hann dù hình dạng trông gần giống.

### Đánh đổi về độ phân giải

Độ phân giải tần số hiệu dụng tỷ lệ với \(\sim \alpha f_s/L\) (trong đó \(\alpha>1\) phụ thuộc dạng cửa sổ), còn độ phân giải định vị thời gian tỷ lệ với \(\sim L/f_s\). Khử nhiễu tiếng nói cần độ phân giải tần số đủ mịn để tách formant khỏi nền nhiễu, đồng thời đủ ngắn theo thời gian để bám sát phụ âm — do đó cửa sổ thường nằm trong khoảng vài chục mili giây thay vì 1 ms hay 1 giây.

Ở 48 kHz với \(L=960\), búp chính của cửa sổ Hann rộng khoảng bốn bin, tương ứng \(4\cdot48000/960=200\,\mathrm{Hz}\). Độ rộng này chưa đủ tách riêng các họa âm sát nhau của giọng trầm và làm nhòe một âm bật (plosive) dài 5 ms ra toàn bộ cửa sổ 20 ms. Muốn thu hẹp búp chính theo Hz phải tăng \(L\) và chấp nhận tăng độ trễ; muốn giảm rò phổ sang các bin xa phải đổi hàm cửa sổ chứ không phải đệm số 0 — vì zero-padding chỉ nội suy dày thêm đường cong \(W(e^{j\omega})\) chứ không thu hẹp nó.

### Tương tác giữa cửa sổ và mặt nạ khử nhiễu

Hệ số độ lợi nhảy đột ngột giữa các bin kề nhau sẽ đi ngược lại độ mượt vốn có của hàm cửa sổ và tạo ra nhiễu nhạc khi xem các bin như hoàn toàn độc lập. Mặt nạ biến thiên mượt theo cả thời gian và tần số phù hợp với bản chất vật lý hơn. Dùng cửa sổ chữ nhật khiến giả định "bin độc lập" càng sai lệch nặng: bin \(k+8\) vẫn chứa năng lượng rò từ bin \(k\) ở mức nghe rõ, nên việc đóng cổng cứng các "bin nhiễu" sẽ cắt búp phụ của nguyên âm nhưng để sót búp chính.

### Cửa sổ phân tích và cửa sổ tổng hợp

Một số pipeline chỉ nhân \(w\) ở bước phân tích và dùng cửa sổ tổng hợp tương ứng cho COLA; số khác dùng \(\sqrt{\text{Hann}}\) ở cả hai phía. Nguyên tắc bắt buộc là **khớp đúng cấu hình lúc huấn luyện** — tự ý đổi sang Blackman sẽ phá vỡ điều kiện tái tạo. Bình phương cửa sổ Hann không thỏa COLA ở mức chồng lấp 50% vì tích \(w\cdot w\) dao động giữa \(1/2\) và \(1\); phép lấy căn bậc hai chia đều độ thuôn cho cả hai phía mà vẫn giữ tổng tích phẳng.

Do giá trị trung bình của cửa sổ Hann là \(1/2\), phép phân tích chưa chuẩn hóa sẽ làm công suất băng rộng giảm khoảng 6 dB trước cả khi qua bộ khử nhiễu. Nếu tính SI-SDR so với tín hiệu tham chiếu miền thời gian mà quên chia cho hằng số COLA, kết quả sẽ xuất hiện sai lệch hệ thống.

## Ví dụ có số

Ở 16 kHz với \(L=512\), so sánh một âm đơn nằm đúng bin 32 với âm nằm giữa hai bin tại 32.5. Với cửa sổ chữ nhật, trường hợp lệch bin làm năng lượng lan rộng; với cửa sổ Hann, búp phụ hạ mạnh còn búp chính rộng ra nên cả bin 32 và 33 đều nổi rõ. Lưu ý rằng âm đơn rơi đúng bin có thể tạo phổ trông gần như lý tưởng (búp phụ nằm ở mức sai số máy) và che giấu lỗi cửa sổ — vì vậy luôn cần kiểm thử bằng âm lệch nửa bin. Trong Mini-lab dưới đây, giá trị búp phụ đo được không trùng khớp tuyệt đối với mốc −13 / −31 dB trong sách do đỉnh nằm giữa hai bin và phép đo có chừa vành bảo vệ, nhưng khoảng cách chênh lệch giữa cửa sổ chữ nhật và Hann vẫn thể hiện rõ.

Trừ phổ cổ điển áp ngưỡng độc lập trên từng bin thường để lại các đỉnh cô lập gây tiếng lách tách kiểu "chim hót" (birdies / musical noise). Làm mượt sẽ giảm hiện tượng này nhưng lại làm nhòe tiếng nói — đó chính là giới hạn kinh điển thúc đẩy các phương pháp tăng cường tiếng nói bằng mạng nơ-ron.

## Bẫy thường gặp

1. Áp dụng hàm cửa sổ hai lần (thư viện đã tự nhân cửa sổ nhưng mã người dùng lại nhân thêm lần nữa).
2. Dùng cửa sổ chữ nhật vì lầm tưởng "FFT yêu cầu như vậy".
3. Quên hệ số khuếch đại của cửa sổ khi kiểm tra Parseval hoặc tính SI-SDR.
4. Dùng cửa sổ lúc triển khai khác với cửa sổ lúc huấn luyện.
5. Kỳ vọng hàm cửa sổ có thể khắc phục lỗi aliasing (điều này không thể xảy ra).

## Mini-lab

**Mục tiêu.** Tính FFT cho một sóng sin rơi lệch bin dưới cửa sổ chữ nhật và cửa sổ Hann tuần hoàn, sau đó in mức búp phụ tính theo dB so với đỉnh.

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

**Kết quả kỳ vọng.** Búp phụ của cửa sổ chữ nhật xấp xỉ **−17 dB**, còn cửa sổ Hann xấp xỉ **−40 dB** (với vành bảo vệ 3 bin quanh đỉnh lệch bin). Cửa sổ Hann cho nền búp phụ thấp hơn rõ rệt, đổi lại búp chính rộng hơn khi vẽ cả hai phổ lên cùng đồ thị.

**Lỗi thường gặp.** Chọn tần số đúng bin nguyên (`32 * fs / N`) sẽ đẩy búp phụ của cả hai cửa sổ xuống mức sai số số học (dưới −200 dB) và không minh họa được sự khác biệt; dùng `np.hann` thay cho công thức tuần hoàn chỉ làm thay đổi nhẹ giá trị của Hann chứ không thu hẹp khoảng cách; quên chia cho `mag.max()` sẽ in ra biên độ FFT tuyệt đối thay vì dB tương đối; và đặt `guard=0` sẽ tính nhầm sườn búp chính là búp phụ khiến cả hai cửa sổ đều trông kém như nhau.

## Bài tập nhỏ

1. Giải thích vì sao cửa sổ vuốt thuôn hai đầu (tapered) giúp giảm búp phụ.
2. Khi tăng gấp đôi độ dài cửa sổ \(L\), độ rộng búp chính thay đổi xấp xỉ như thế nào?
3. Bước nhảy hop nào thỏa mãn điều kiện COLA phổ biến nhất với cửa sổ Hann?
4. Mặt nạ cắt mạnh theo từng bin độc lập gây ra nhiễu nhạc theo cơ chế nào?
5. Nêu một lý do khiến cửa sổ \(\sqrt{\mathrm{Hann}}\) thường xuất hiện trong các kho mã STFT.

### Gợi ý đáp án

1. Biến đổi Fourier \(W\) của cửa sổ vuốt thuôn có búp phụ nhỏ hơn nhiều, mà phép nhân với \(w\) tương đương tích chập phổ tín hiệu với \(W\).
2. Độ rộng theo Hz tỷ lệ với \(f_s/L\) nên giảm đi một nửa; còn độ rộng tính theo số bin của cửa sổ Hann vẫn vào khoảng 4 bin.
3. \(R=L/2\) khi dùng cửa sổ Hann tuần hoàn (như đã chứng minh ở bài 02-02).
4. Các giá trị 0 đột ngột giữa các bin lân cận cắt mất phần búp phụ của một họa âm thực nhưng để sót các đỉnh cô lập, sau ISTFT chuyển thành các âm sắc ngắn nghe như tiếng chim hót.
5. Giúp cả bước phân tích lẫn bước tổng hợp đều được vuốt thuôn ở hai biên trong khi tích hai cửa sổ vẫn thỏa điều kiện COLA.

## Đọc thêm

- Oppenheim & Schafer — hàm cửa sổ và phân tích phổ.
- Julius O. Smith, *Spectral Audio Signal Processing* — mức búp phụ và độ rộng búp chính của các hàm cửa sổ.
- Cấu hình STFT của DeepFilterNet: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588).

## Video tham khảo

- [Lecture 13: Spectral Leakage, Windowing, with Examples of Hanning and Hamming Windows](https://www.youtube.com/watch?v=tCWU9C-LdJQ) — Bahga Lab IIT Delhi, tiếng Anh. **Xem trước.** So sánh búp phụ của cửa sổ chữ nhật với Hann và Hamming, làm rõ trực tiếp sự đánh đổi giữa búp chính và rò phổ.
- [The more general uncertainty principle, regarding Fourier transforms](https://www.youtube.com/watch?v=MBnnXbOM5S4) — 3Blue1Brown, tiếng Anh. Phần nguyên lý bất định giải thích vì sao rút ngắn thời gian quan sát bắt buộc phải làm rộng búp chính theo tần số.
- [Short-Time Fourier Transform Explained Easily](https://www.youtube.com/watch?v=-Yxj3yfvY-4) — Valerio Velardo - The Sound of AI, tiếng Anh. Minh họa trực tiếp bước nhân cửa sổ vuốt thuôn trên khung tiếng nói — nơi rò phổ có thể dẫn tới nhiễu nhạc ở các bước xử lý sau.
