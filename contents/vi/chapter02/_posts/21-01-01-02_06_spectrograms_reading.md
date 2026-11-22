---
layout: post
title: "02-06 Spectrogram: đọc tiếng nói và nhiễu"
chapter: "02"
order: 6
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Phổ đồ (spectrogram) là công cụ giao tiếp chung của kỹ sư xử lý tiếng nói. Bài học này hướng dẫn cách đọc cấu trúc tiếng nói, nhận diện các dạng nhiễu và phát hiện méo âm (artifact) sau khử nhiễu, đồng thời tránh bị đánh lừa bởi thang màu dB. Phổ đồ không phải là "bức ảnh tuyệt đối của âm thanh" mà là biểu diễn \(|X(\ell,k)|\) của một cấu hình STFT cụ thể theo thang decibel có ngưỡng sàn; chỉ cần đổi hàm cửa sổ hoặc dải màu là hình ảnh thu được sẽ kể một câu chuyện hoàn toàn khác.

## Mục tiêu học tập

1. Đọc chính xác các trục của phổ đồ (thời gian, tần số và thang màu dB).
2. Nhận diện nguyên âm hữu thanh, formant, phụ âm xát và khoảng lặng.
3. Nhận diện nền nhiễu dừng, nhiễu bùng nổ (burst), babble và nhạc nền.
4. Phát hiện các méo âm phổ biến sau khử nhiễu (nhiễu nhạc, khử quá mức, rung biên độ theo hop).
5. Kết hợp phổ đồ một cách hợp lý cùng đánh giá nghe và các chỉ số định lượng.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Cấu tạo và các thành phần của một biểu đồ phổ đồ |
| 10–28 | Các mẫu đặc trưng của tiếng nói (nhận diện trực quan không cần nghe) |
| 28–42 | Các mẫu nhiễu và cách đọc tín hiệu hỗn hợp |
| 42–52 | So sánh méo âm trước và sau khử nhiễu |
| 52–60 | Bài tập nhỏ |

![Spectrogram tiếng nói: các vạch hài nằm ngang xếp chồng, rồi một burst nhiễu dọc phủ mọi băng]({{ site.imgurl }}/generated/spectrogram-reading.png)

*Hình. Các họa âm hữu thanh hiện lên thành chồng vạch ngang đều đặn; một đợt nhiễu bùng nổ xuất hiện thành dải dọc phủ kín mọi băng tần cùng lúc.*

## Giải thích cốt lõi

### Các trục và thang hiển thị

- **Trục hoành (X):** thời gian (giây) hoặc chỉ số khung.
- **Trục tung (Y):** tần số Hz (tuyến tính) hoặc thang cảm thụ (Mel/ERB).
- **Màu sắc:** thường là \(20\log_{10}|X(\ell,k)|\) kèm ngưỡng sàn.

Mỗi ảnh phổ đồ luôn cần ghi rõ metadata: \(f_s\), hàm cửa sổ, bước nhảy hop, kích thước FFT và dải dB (ví dụ −80..0 dB). Thiếu các thông số này, ảnh chụp màn hình không đủ giá trị làm bằng chứng kỹ thuật.

$$
S(\ell,k)=20\log_{10}\bigl(\max(|X(\ell,k)|,\,\varepsilon)\bigr).
$$

Trong đó \(\varepsilon\) là ngưỡng sàn. Nếu thiếu \(\varepsilon\), một bin bằng 0 tuyệt đối (sau khi áp mặt nạ cứng) sẽ cho giá trị \(-\infty\), kéo giãn thang màu lệch quanh điểm lỗ đó và khiến toàn bộ câu nói biến thành một mảng màu bệt, mất tương phản. Đặt sàn quanh −80 dB so với sóng sin toàn thang (full-scale) giúp khoảng lặng hiển thị tối rõ trong khi các họa âm nguyên âm vẫn sắc nét. Hai ảnh phổ đồ chỉ có thể so sánh công bằng khi có cùng \(\varepsilon\), hàm cửa sổ và bước nhảy hop. Ngoài ra, trục Mel không khớp trực tiếp với lỗi theo bin tuyến tính: bin \(k\) tương ứng với \(k f_s/N\) Hz, còn dãy lọc Mel đã cộng gộp nhiều bin lại với nhau.

### Quy trình đọc phổ đồ chuẩn

Hãy áp dụng quy trình 5 bước sau cho hình minh họa và cho mọi ảnh đính kèm trong phiếu báo lỗi (ticket):

1. **Kiểm tra thông số STFT.** Đọc kỹ \(f_s\), cửa sổ, hop, \(N\) và dải dB trước khi diễn giải màu sắc. Trên hình minh họa, các vạch ngang nằm gần 1.2, 2.4, 3.6, 4.8, 6.0 và 7.2 kHz — tương ứng tần số cơ bản 1.2 kHz cùng các họa âm trên trục Hz tuyến tính.
2. **Xác định khoảng lặng hoặc nền nhiễu.** Vùng tối trước mốc 0.2 s và sau đợt burst là nền nhiễu. Nếu nền hiển thị sáng, có thể micro đang có tiếng rít hoặc thang màu đang phóng đại 20 dB dưới cùng — không nên vội kết luận mô hình "khử chưa đủ" khi chưa kiểm tra thang màu.
3. **Tìm chồng họa âm.** Các vạch ngang cách đều nhau là dấu hiệu của âm hữu thanh (hoặc nhạc), với khoảng cách giữa hai vạch chính là tần số cơ bản \(f_0\). Trong hình minh họa, khoảng cách khoảng 1.2 kHz tương ứng giọng rất cao hoặc một nốt nhạc (giọng nói thông thường nằm quanh 100–200 Hz), nhưng hình học hoàn toàn tương tự.
4. **Tìm các sự kiện theo phương dọc.** Âm bật (plosive) hoặc đợt nhiễu bùng nổ làm sáng đồng loạt nhiều bin trong một đến hai khung. Dải cam quanh mốc 0.85–1.0 s là ví dụ điển hình: năng lượng trải khắp mọi tần số chứ không phải một họa âm mới; tiếng gõ phím hay tiếng ho có hình dạng tương tự nhưng hẹp hơn.
5. **So sánh trước và sau khử nhiễu trên cùng một thang đo.** Các vạch hài bậc cao biến mất báo hiệu khử quá mức (over-suppression); các đốm sáng rời rạc trong vùng tối là nhiễu nhạc (musical noise); các sọc sáng/tối đều đặn khớp đúng nhịp hop là dấu hiệu lỗi COLA hoặc dao động độ lợi, không phải "nhiễu mới sinh".

Cần lưu ý rằng lỗi pha không xuất hiện trên \(S(\ell,k)\). Nếu âm thanh nghe bị méo "ướt" dù phổ đồ biên độ trông rất sạch, nguyên nhân thường là lỗi tái sử dụng pha nhiễu (bài 02-04) — bản thân phổ đồ biên độ sẽ không bộc lộ lỗi này.

### Dấu hiệu đặc trưng của tiếng nói

| Thành phần | Biểu hiện trên phổ đồ |
|------------|-----------------------|
| Nguyên âm hữu thanh | Chuỗi vạch họa âm ngang; các dải đậm (formant) nối qua các vạch |
| Thay đổi cao độ | Vạch họa âm nghiêng lên/xuống, khoảng cách giữa các vạch thay đổi |
| Âm tắc (plosive) | Vệt bùng nổ băng rộng theo phương dọc đi kèm khoảng đóng ngắn |
| Phụ âm xát (fricative) | Đám mây năng lượng dạng nhiễu ở dải tần số cao |
| Khoảng lặng | Gần mức sàn (chỉ còn nhiễu nền của micro) |

### Dấu hiệu đặc trưng của nhiễu

| Dạng nhiễu | Biểu hiện trên phổ đồ |
|------------|-----------------------|
| HVAC | Dải ngang liên tục ở tần số thấp |
| Tiếng rít quạt | Toàn bộ nền băng rộng bị nâng sáng đều |
| Bàn phím | Các vạch dọc rất mảnh |
| Babble | Có cấu trúc hài giống tiếng nói nhưng chồng chéo lộn xộn |
| Nhạc nền | Chuỗi họa âm ổn định, kéo dài, không dịch chuyển formant như tiếng nói |

### Méo âm thường gặp sau khử nhiễu

| Méo âm (artifact) | Biểu hiện thị giác / thính giác |
|-------------------|---------------------------------|
| Nhiễu nhạc (musical noise) | Các đốm bin đơn lẻ bật tắt rải rác theo thời gian |
| Khử quá mức (over-suppression) | Mất đám mây phụ âm xát cao tần; giọng nghe bị bí, nghẹt |
| Rung biên độ theo hop (warble) | Các sọc biên độ tuần hoàn theo đúng chu kỳ hop |
| Vang dư | Vệt nhòe kéo dài theo phương ngang/dọc ngay sau âm tiết |

Phổ đồ chỉ đóng vai trò **bổ trợ** cho đánh giá nghe và các chỉ số như SI-SDR/DNSMOS (Chương 08), không thể thay thế chúng. Một phổ đồ trông rất sạch vẫn có thể nghe khó chịu do lỗi pha vô hình trên đồ thị biên độ.

## Ví dụ có số

Nhãn thông số chuẩn cho một ảnh phổ đồ: `"48 kHz, Hann 20 ms, hop 10 ms, N=1024, dB −70..0"`. Lưu ý \(N=1024\) ở 48 kHz tương ứng khoảng 21.3 ms nếu độ dài cửa sổ bằng FFT, *không* phải lưới 960 điểm của DeepFilterNet — cần ghi rõ trong phiếu báo lỗi để tránh kiểm tra nhầm chỉ số bin.

Tần số tâm của bin thứ \(k\) là \(k f_s/N\). Một họa âm 200 Hz ở \(f_s=8\,\mathrm{kHz}\) với \(N=256\) rơi vào vị trí:

$$
k=\frac{200}{8000/256}=6.4,
$$

do đó năng lượng phân bố giữa bin 6 và bin 7. Họa âm bậc hai (400 Hz) và bậc ba (600 Hz) lần lượt nằm quanh 12–13 và gần 19 (Mini-lab dưới đây sẽ in trực tiếp các bin này). Một báo cáo lỗi ghi "âm đơn ở bin 200" là đang nhầm lẫn giữa tần số Hz và chỉ số bin.

Một dải sáng kéo dài sát đáy tần số thấp thường là thành phần lệch DC chứ không phải "mô hình khử nhiễu thất bại"; hãy lọc thông cao trước khi vẽ nếu đang chẩn đoán NS. Với babble, cả giọng đích lẫn nền đều có cấu trúc hài nhưng giọng đích thường mạnh và gần micro hơn — phổ đồ giúp định lượng giới hạn thực tế của NS đơn kênh.

## Bẫy thường gặp

1. So sánh hai phổ đồ có dải màu dB khác nhau.
2. Dùng phổ đồ thang Mel để gỡ lỗi chỉ số bin của STFT tuyến tính.
3. Vội kết luận đạt chất lượng chỉ vì nền trông tối hơn mà không kiểm tra xem tiếng nói có bị suy hao không.
4. Bỏ qua các méo pha vốn không hiển thị trên phổ biên độ.
5. Chọn cửa sổ quá dài khiến các hiện tượng biến đổi nhanh trông như "nhiễu dừng".

## Mini-lab

**Mục tiêu.** Tính phổ biên độ trên một khung `rfft` của tín hiệu gồm ba họa âm và in danh sách các bin có năng lượng cao nhất.

```python
import numpy as np

fs, L, R = 8000, 256, 128
t = np.arange(int(0.4 * fs)) / fs
f0 = 200.0
x = (np.sin(2 * np.pi * f0 * t)
     + 0.5 * np.sin(2 * np.pi * 2 * f0 * t)
     + 0.25 * np.sin(2 * np.pi * 3 * f0 * t))
w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(L) / L)
frame = x[L:L + L] * w
mag = np.abs(np.fft.rfft(frame))
top = np.argsort(mag)[-6:][::-1]
print("top bins", top.tolist())
for h in (1, 2, 3):
    print(f"harmonic {h} expected k", h * f0 * L / fs)
```

**Kết quả kỳ vọng.** Các vị trí tâm lý thuyết là **6.4, 12.8 và 19.2**. Sáu bin mạnh nhất nằm ở lân cận các tâm đó (thường là 6 và 7 cho 200 Hz, 12 và 13 cho 400 Hz, cùng 19 cho 600 Hz). Cặp bin sáng cạnh nhau là hệ quả tự nhiên của họa âm lệch lưới qua búp chính cửa sổ Hann, không phải nhiễu.

**Lỗi thường gặp.** Chỉ dùng `np.argmax` sẽ chỉ thấy bin 6 và bỏ sót các họa âm bậc cao; dùng `fft` thay cho `rfft` làm nhân đôi phổ và lệch cách đọc chỉ số; bỏ qua hàm cửa sổ khiến búp phụ (bài 02-03) đẩy các bin không liên quan vào nhóm mạnh nhất; và đọc nhầm bin 6 thành 6 Hz thay vì \(6\cdot8000/256=187.5\,\mathrm{Hz}\) là lỗi ghi nhận rất hay gặp trong ticket.

## Bài tập nhỏ

1. Phác họa dạng phổ đồ giản lược của từ "hello" trong môi trường có nhiễu nền.
2. Lỗi COLA với bước nhảy hop 10 ms hiển thị như thế nào trên phổ đồ?
3. Vì sao bắt buộc phải đặt ngưỡng sàn khi chuyển biên độ sang thang logarit?
4. Nêu hai dấu hiệu phân biệt nhạc nền với tiếng nói hữu thanh trên phổ đồ.
5. Liệt kê các thông số metadata bắt buộc phải đi kèm phổ đồ khi gửi báo cáo lỗi.

### Gợi ý đáp án

1. Chuỗi vạch hài ở tần số thấp cho các nguyên âm, đám mây năng lượng cao tần cho phụ âm xát và vệt dọc ngắn cho âm /h/ hoặc âm bật, tất cả nằm trên một nền nhiễu tương đối đều.
2. Xuất hiện các sọc sáng/tối theo phương dọc lặp lại đều đặn mỗi 10 ms (khớp đúng chu kỳ hop), kể cả xuyên qua những đoạn nguyên âm ổn định.
3. Nếu không có sàn, giá trị 0 tuyệt đối sẽ cho \(-\infty\), làm sụp đổ thang màu của toàn biểu đồ.
4. Nhạc nền thường duy trì khoảng cách họa âm cố định và kéo dài ổn định theo thời gian, còn tiếng nói liên tục dịch chuyển dải formant và biến thiên \(f_0\) theo ngữ điệu.
5. Tần số lấy mẫu \(f_s\), hàm cửa sổ, bước nhảy hop, kích thước FFT và dải hiển thị dB.

## Đọc thêm

- Oppenheim & Schafer và loạt bài về phổ của Julius O. Smith — phân tích bản chất vật lý của biên độ ngắn hạn.
- Chương về phổ đồ trong các giáo trình xử lý tiếng nói và DSP.
- Hình minh họa của DNS Challenge và các bài báo DeepFilterNet (luôn đọc kỹ trục tần số trước khi đối chiếu với STFT tuyến tính 48 kHz).

## Video tham khảo

- [The Spectrogram and the Gabor Transform](https://www.youtube.com/watch?v=EfWnEldTyPA) — Steve Brunton, tiếng Anh. **Xem trước.** Minh họa quá trình trượt cửa sổ trên biến đổi Fourier để tạo ra ảnh thời gian–tần số; luôn kiểm tra trục trước khi đọc màu.
- [Speech Acoustics 5 - vowel formants](https://www.youtube.com/watch?v=glnUFa2fLyE) — Listen Lab, tiếng Anh. Tập trung vào các dải đậm formant thay vì từng vạch hài rời rạc — đây chính là cấu trúc tiếng nói mà bộ khử nhiễu phải bảo toàn.
- [Coding Adventure: Analyzing Audio](https://www.youtube.com/watch?v=08mmKNLQVHU) — Sebastian Lague, tiếng Anh. Phần phân tích ngắn hạn minh họa cách cắt khung tiếng nói để vẽ phổ đồ và lý do một phép FFT trên cả tệp làm mất thông tin thời điểm.
