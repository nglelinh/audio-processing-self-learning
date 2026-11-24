---
layout: post
title: "02-02 Frame, hop và overlap-add"
chapter: "02"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter02
lesson_type: required
draft: false
---

Pipeline STFT chia tín hiệu âm thanh thành các khung chồng lấp, xử lý từng khung rồi ghép lại bằng kỹ thuật cộng chồng lấp (overlap-add, OLA). Cấu hình sai bước nhảy hop hoặc sai OLA sẽ tạo ra tiếng rung giật (warble) mà việc cập nhật trọng số mạng nơ-ron không thể khắc phục. Bài học này chứng minh điều kiện COLA (constant overlap-add: tổng các hàm cửa sổ chồng lấp bằng hằng số) cho cửa sổ Hann tuần hoàn, đồng thời quy đổi \(L\) và \(R\) sang mili giây — vì thông số "chồng lấp 50%" chưa cho biết độ trễ cho tới khi chia cho \(f_s\).


Khi bạn cắt một đoạn ghi âm thành từng lát 20 ms, nhân mỗi lát với một đường cong hình chuông (như cửa sổ Hann) để hai đầu lát vuốt êm về 0, rồi biến đổi ngược lại miền thời gian — một câu hỏi sống còn lập tức đặt ra: *làm sao ghép các lát hình chuông ấy lại với nhau để giọng nói phát ra không bị lúc to lúc nhỏ nhấp nhô theo nhịp 10 ms?* Bí mật nằm ở thuật toán **Overlap-Add (OLA)** và một điều kiện toán học đẹp như thơ mang tên **COLA (Constant Overlap-Add)**!

---

## Bản đồ kiến thức nền: Chia khung, Bước nhảy và Overlap-Add đứng trên ba trụ cột nào?

### 1. Bộ ba tham số: Frame Length ($$N$$), Hop Size ($$H$$) và Tỉ lệ chồng lấp
Mỗi khung thứ $$m$$ bắt đầu tại vị trí $$mH$$ và lấy $$N$$ mẫu: $$x_m[n] = x[mH + n]\cdot w[n]$$. Tỉ lệ chồng lấp là $$1 - H/N$$ (ví dụ $$N = 960,\ H = 480 \implies$$ chồng lấp **50%**; $$H = 240 \implies$$ chồng lấp **75%**). Giảm $$H$$ giúp bám sát biến đổi nhanh của tiếng nói tốt hơn nhưng làm tăng tuyến tính số khung phải chạy FFT mỗi giây.

### 2. Điều kiện Tái tạo Hoàn hảo COLA (Constant Overlap-Add)
Nếu ta chưa sửa gì trong miền tần số (bộ lọc đồng nhất), tổng các cửa sổ trượt chồng lên nhau phải bằng **đúng một hằng số $$C > 0$$ tại mọi mẫu $$n$$**:

$$
\sum_{m=-\infty}^{\infty} w[n - mH] = C \qquad \forall n \in \mathbb{Z}.
$$

Nếu điều kiện COLA bị vi phạm (ví dụ dùng cửa sổ Hann nhưng lại chọn hop $$H = 0.6 N$$), âm thanh đầu ra sẽ bị điều biến biên độ gợn sóng liên tục!

### 3. Hai biến thể thực thi: OLA (Overlap-Add) vs. WOLA (Weighted Overlap-Add)
Trong **OLA cổ điển**, chỉ nhân cửa sổ ở đầu phân tích (analysis) rồi cộng thẳng ở đầu tổng hợp. Trong **WOLA** (dùng trong DeepFilterNet và hầu hết hệ thống khử nhiễu hiện đại), ta nhân cửa sổ ở *cả hai đầu* phân tích ($$w_a$$) và tổng hợp ($$w_s$$) để làm mượt các bước nhảy do mặt nạ khử nhiễu gây ra — khi đó điều kiện tái tạo hoàn hảo trở thành $$\sum_m w_a[n - mH]\,w_s[n - mH] = C$$!

---

### Khung giải thích: tự tay kiểm chứng điều kiện COLA của cửa sổ Hann với chồng lấp 50% (nên đọc chậm)

Xét cửa sổ **Hann định kỳ (periodic Hann)** độ dài $$N$$ với bước nhảy $$H = N/2$$:

$$
w[n] = \frac{1}{2}\Bigl(1 - \cos\frac{2\pi n}{N}\Bigr), \qquad n = 0, 1, \dots, N - 1.
$$

1. **Chứng minh đại số tổng quát cho mọi $$N$$ chẵn:** Tại bất kỳ vị trí $$n \in [0, N/2 - 1]$$ nào, có đúng 2 khung phủ lên nó (nửa sau của khung trước và nửa đầu của khung hiện tại):
   $$
   w[n] + w\!\Bigl(n + \frac{N}{2}\Bigr) = \frac{1}{2}\Bigl(1 - \cos\frac{2\pi n}{N}\Bigr) + \frac{1}{2}\Bigl(1 - \cos\!\Bigl(\frac{2\pi n}{N} + \pi\Bigr)\Bigr).
   $$
   Nhờ đồng nhất thức lượng giác $$\cos(\theta + \pi) = -\cos\theta$$, hai số hạng cosin **triệt tiêu nhau tuyệt đối**, để lại:
   $$
   w[n] + w\!\Bigl(n + \frac{N}{2}\Bigr) = \frac{1}{2} + \frac{1}{2} = \mathbf{1.0}!
   $$
2. **Kiểm tra bằng số cụ thể với $$N = 4,\ H = 2$$:** Cửa sổ Hann định kỳ là $$w = [0,\ 0.5,\ 1.0,\ 0.5]$$. Xếp chồng 3 khung liên tiếp lệch nhau $$H = 2$$ mẫu:
   - Khung 0: `[0.0, 0.5, 1.0, 0.5,  · ,  · ,  · ,  · ]`
   - Khung 1: `[ · ,  · , 0.0, 0.5, 1.0, 0.5,  · ,  · ]`
   - Khung 2: `[ · ,  · ,  · ,  · , 0.0, 0.5, 1.0, 0.5]`
   - **Cộng từng cột (từ vùng ổn định $$n=2..5$$):** `[1.0, 1.0, 1.0, 1.0]` — phẳng lì tuyệt đối, sai số bằng $$0$$! (Lưu ý bẫy hay gặp: cửa sổ Hann *đối xứng* dùng $$N-1$$ ở mẫu số sẽ **không** thỏa COLA chính xác bằng 1 mà bị gợn nhẹ tại ranh giới!)

---

## Mục tiêu học tập

1. Định nghĩa độ dài khung \(L\), bước nhảy hop \(R\) và tỷ lệ chồng lấp (overlap).
2. Giải thích cơ chế tái tạo OLA và điều kiện COLA.
3. Tính hệ quả về độ trễ thuật toán từ \(L\) và \(R\).
4. Lựa chọn bước nhảy hop cho khử nhiễu tiếng nói dựa trên sự đánh đổi giữa độ trễ và chất lượng.
5. Hình dung rõ cách vận hành của bộ đệm OLA trong chế độ streaming.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Vẽ sơ đồ khung và bước nhảy hop trên bảng |
| 12–28 | Cơ sở toán học của OLA và chứng minh COLA cho cửa sổ Hann |
| 28–42 | Cơ chế bộ đệm streaming và xử lý hiệu ứng biên |
| 42–52 | Các thông số thực tế ở 16 kHz và 48 kHz cho tiếng nói |
| 52–60 | Bài tập nhỏ |

![Các frame phân tích chồng nhau, cửa sổ Hann trượt với hop R, và tổng overlap-add của chúng]({{ site.imgurl }}/generated/stft-ola.png)

*Hình. Khung dài \(L\) trượt tiến từng bước hop \(R\); phép cộng chồng lấp chỉ tái tạo trung thực dạng sóng tại vùng mà tổng các cửa sổ dịch chuyển bằng hằng số.*

## Giải thích cốt lõi

### Chia khung (framing)

Xét cửa sổ có độ dài \(L\) mẫu và bước nhảy hop \(R\) mẫu (\(1\le R\le L\)). Tỷ lệ chồng lấp là:

$$
\rho = 1-\frac{R}{L}
$$

Chồng lấp 50% ứng với \(R=L/2\); chồng lấp 75% ứng với \(R=L/4\). Bước nhảy \(R\) cũng chính là số mẫu mới cần gom thêm trước lần tính FFT kế tiếp:

$$
T_R=\frac{R}{f_s},\qquad \text{hops/s}=\frac{f_s}{R},\qquad T_L=\frac{L}{f_s}.
$$

Trong đó, \(T_L\) là thời lượng âm thanh chứa trong một khung phân tích, còn \(T_R\) là chu kỳ xuất ra một khung mới. Một cửa sổ 20 ms đi kèm hop 10 ms vẫn quan sát đủ 20 ms ngữ cảnh ở mỗi lần chạy.

### Cộng chồng lấp (overlap-add)

Với mỗi khung sau xử lý \(y_m[n]=w_{\mathrm{syn}}[n]\cdot \mathrm{iFFT}(\hat{X}_m)\), tín hiệu đầu ra được tổng hợp theo công thức:

$$
\hat{x}[n]=\sum_m y_m[n-mR]
$$

Nếu \(\hat{X}_m\) là phổ STFT chưa thay đổi của \(x\) và cặp cửa sổ thỏa mãn điều kiện **COLA**, thì \(\hat{x}\) sẽ tái tạo lại chính xác \(x\) (sai khác tối đa một độ trễ và hệ số khuếch đại hằng). Cần phân biệt rõ: bước phân tích đã nhân với \(w_{\mathrm{ana}}\), còn phần nhân thêm sau iFFT là \(w_{\mathrm{syn}}\); viết tường minh cả hai giúp tránh lỗi nhân cửa sổ hai lần.

### Điều kiện COLA

Với bước nhảy hop \(R\), tổng tích của cửa sổ phân tích và cửa sổ tổng hợp dịch theo hop phải bằng một hằng số:

$$
\sum_m w_{\mathrm{ana}}[n-mR]\,w_{\mathrm{syn}}[n-mR] = C
$$

(Cụ thể cách kiểm tra phụ thuộc vào việc pipeline nhân cửa sổ một lần hay hai lần và phải khớp định nghĩa STFT đã dùng.) Cửa sổ Hann với tỷ lệ chồng lấp 50% là lựa chọn COLA kinh điển khi dùng đúng phiên bản tuần hoàn.

**Chứng minh cho cửa sổ Hann tuần hoàn.** Định nghĩa:

$$
w[n]=\frac12-\frac12\cos\frac{2\pi n}{L},\qquad n=0,\ldots,L-1.
$$

Lưu ý mẫu số là \(L\) chứ không phải \(L-1\): đây là dạng Hann *tuần hoàn* (`sym=False`). Phiên bản Hann đối xứng (ép \(w[0]=w[L-1]=0\)) **không** cộng thành hằng số chính xác, và đó là nguyên nhân phổ biến khiến bài kiểm tra "Hann 50%" bị lệch vài phần nghìn.

Chọn \(R=L/2\) và xét một mẫu trong vùng giao của hai cửa sổ kế tiếp. Đặt \(\theta=2\pi n/L\), ta có:

$$
w[n]=\frac12(1-\cos\theta),\qquad
w[n+R]=\frac12(1+\cos\theta).
$$

Suy ra:

$$
w[n]+w[n+R]=1.
$$

Như vậy, nếu \(w_{\mathrm{ana}}=w\) và \(w_{\mathrm{syn}}=1\) (không nhân cửa sổ lần thứ hai sau iFFT), tổng COLA ở vùng ổn định luôn bằng hằng số \(C=1\). Phần Mini-lab dưới đây sẽ kiểm chứng hằng số này.

**Trường hợp không bằng hằng số.** Nếu lấy tổng bình phương của cùng cửa sổ đó ở hop 50%, ta thu được \(\tfrac12(1+\cos^2\theta)\), dao động liên tục giữa \(1/2\) và \(1\). Do đó, việc nhân đầy đủ cửa sổ Hann ở cả đầu vào lẫn đầu ra sẽ khiến biên độ bị nhấp nhô theo tần số \(f_s/R\) Hz. Cách khắc phục chuẩn là dùng \(w_{\mathrm{ana}}=w_{\mathrm{syn}}=\sqrt{w}\): tích hai cửa sổ đúng bằng \(w\) nên tổng chồng lấp lại bằng hằng số như vừa chứng minh. Đó là lý do cửa sổ \(\sqrt{\mathrm{Hann}}\) thường xuyên xuất hiện trong mã nguồn STFT.

### Độ trễ

Tăng \(L\) giúp cải thiện độ phân giải tần số nhưng làm tăng độ trễ đệm. Giảm \(R\) giúp cập nhật mặt nạ dày và mượt hơn nhưng tăng tải CPU vì số hop mỗi giây lớn hơn. Các bộ khử nhiễu sản phẩm thường chọn hop trong khoảng 5–20 ms, nhưng **luôn phải khớp với mô hình**.

Với cửa sổ phân tích nhân quả, độ trễ thuật toán xấp xỉ toàn bộ chiều dài cửa sổ chứ không chỉ bằng bước nhảy hop:

$$
D_{\mathrm{alg}}\approx T_L=\frac{L}{f_s}.
$$

Hệ thống chưa thể lập khung phân tích nếu chưa nhận đủ mẫu cuối cùng của khung đó. Giảm \(R\) từ \(L/2\) xuống \(L/4\) làm tăng gấp đôi số hop mỗi giây nhưng không giúp cắt giảm \(D_{\mathrm{alg}}\) xuống một nửa. Với STFT căn giữa (centered), hệ thống cần thêm khoảng \(T_L/2\) mẫu nhìn trước. Bài 02-07 sẽ tách bạch độ trễ thuật toán này khỏi hệ số thời gian thực (RTF).

### Bộ đệm OLA trong chế độ streaming

Hệ thống cần duy trì một bộ đệm tích lũy (accumulator) có độ dài \(\ge L\). Ở mỗi hop, ta cộng khung vừa tổng hợp vào bộ đệm, xuất ra \(R\) mẫu đã hoàn tất (không còn khung tương lai nào chồng lên nữa), và giữ lại phần đuôi chồng lấp cho hop kế tiếp. \(L-R\) mẫu đầu tiên chưa đủ số cửa sổ chồng lấp để đạt hằng số \(C\), nên cần làm mờ (fade) ở đoạn khởi động. Nếu xóa bộ đệm tích lũy sau mỗi callback, tổng chồng lấp sẽ bị ngắt quãng liên tục và tạo ra hiện tượng rung biên độ (tremolo).

## Ví dụ có số

Với \(f_s=48\,\mathrm{kHz}\), \(L=960\) (20 ms) và \(R=480\) (10 ms), ta có \(\rho=0.5\), tốc độ 100 hop/giây và \(D_{\mathrm{alg}}\approx 20\,\mathrm{ms}\). Đây là lưới phân tích công bố của DeepFilterNet: \(N_{\mathrm{FFT}}=960\) ở 48 kHz với tỷ lệ chồng lấp 50% ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)).

Với \(f_s=16\,\mathrm{kHz}\), \(L=512\) và \(R=256\), ta có \(T_L=512/16000=32\,\mathrm{ms}\), \(T_R=16\,\mathrm{ms}\) và tốc độ 62.5 hop/giây. Cần tránh nhầm lẫn: 512 mẫu ở 16 kHz là 32 ms chứ không phải 16 ms, còn hop 10 ms ở 16 kHz tương ứng \(R=160\) chứ không phải 256.

### Triệu chứng khi vi phạm COLA

Âm thanh xuất hiện hiện tượng rung biên độ (tremolo) ở tần số \(f_s/R\) Hz (ví dụ 100 Hz khi hop bằng 10 ms), thường được người nghe mô tả là tiếng "robot" hoặc "lệch pha". Sai số độ lợi của mạng nơ-ron không cố định chính xác tại \(f_s/R\), nhưng lỗi COLA thì có.

### Giai đoạn khởi động

\(L-R\) mẫu đầu tiên của tệp thường chưa đủ chồng lấp, nên cần loại bỏ hoặc làm mượt trước khi tính chỉ số SI-SDR.

## Bẫy thường gặp

1. Kết hợp cửa sổ phân tích Hann với cửa sổ tổng hợp chữ nhật mà không kiểm tra điều kiện COLA.
2. Thay đổi kích thước hop nhưng giữ nguyên hàm cửa sổ thiết kế cho hop cũ.
3. Xuất ra đủ \(L\) mẫu ở mỗi hop thay vì \(R\) mẫu, gây mất đồng bộ thời gian.
4. Xóa bộ nhớ tích lũy OLA sau mỗi lần gọi callback.
5. Dùng STFT ngoại tuyến (có đệm căn giữa) khi đánh giá nhưng lại dùng STFT streaming nhân quả lúc chạy thật.

## Mini-lab

**Mục tiêu.** Thực hiện cộng chồng lấp cửa sổ Hann tuần hoàn với bước nhảy 50% và kiểm chứng độ phẳng của tổng ở vùng giữa.

```python
import numpy as np

L, R = 256, 128
n = np.arange(L)
w = 0.5 - 0.5 * np.cos(2 * np.pi * n / L)  # Hann tuần hoàn, không phải np.hann mặc định
N = L + 8 * R
acc = np.zeros(N)
for m in range(0, N - L + 1, R):
    acc[m:m + L] += w
mid = acc[L:N - L]
print("COLA constant", float(mid[0]))
print("peak deviation", float(np.max(np.abs(mid - mid[0]))))
```

**Kết quả kỳ vọng.** Hằng số COLA in ra là `1.0`, với độ lệch cực đại cỡ \(10^{-15}\).

**Lỗi thường gặp.** Dùng `np.hann(L)` (dạng đối xứng) sẽ đẩy độ lệch lên khoảng \(10^{-2}\) do cả hai đầu đều bằng 0 khiến tổng từng cặp không còn bằng 1. Nếu cộng `w**2` thay vì `w` ở hop 50%, tổng sẽ dao động giữa 0.5 và 1 — đây chính là gợn biên độ khi nhân cửa sổ hai lần. Với `R = L // 4` (chồng lấp 75%), tổng của `w` vẫn phẳng nhưng bằng hằng số `2.0` (nếu giả định `C = 1` sẽ làm gấp đôi biên độ); còn nếu chọn bước nhảy không phải ước của `L` (chẳng hạn `R = 3 * L // 4`), điều kiện COLA mới thực sự bị phá vỡ và tổng không còn phẳng.

## Bài tập nhỏ

1. Tính tỷ lệ chồng lấp khi \(L=1024\) và \(R=256\).
2. Tính độ dài hop (ms) ở 16 kHz khi \(R=160\).
3. Vì sao giảm kích thước hop lại làm tăng tải CPU?
4. Phác thảo trạng thái bộ đệm OLA sau 3 hop với \(L=8\) và \(R=4\).
5. Nêu một tín hiệu kiểm thử điều kiện COLA (ví dụ xung đơn vị hoặc chirp) và giải thích cách quan sát.

### Gợi ý đáp án

1. \(\rho=1-256/1024=0.75\) (75%).
2. \(160/16000=10\,\mathrm{ms}\).
3. Vì số hop mỗi giây (\(f_s/R\)) tăng lên, kéo theo số lần gọi FFT/iFFT mỗi giây tăng tương ứng.
4. Sau 3 hop, bộ đệm tích lũy có một đoạn giữa dài \(R\) mẫu nơi hai cửa sổ chồng hoàn toàn, cộng thêm phần đuôi đang chờ dài \(L-R\) mẫu.
5. Tín hiệu xung đơn vị (hoặc hằng số) làm lộ ngay tổng COLA không phẳng dưới dạng đường bao biên độ tuần hoàn; tín hiệu chirp giúp phát hiện thêm hiện tượng nhòe theo thời gian.

## Đọc thêm

- Oppenheim & Schafer — STFT, dãy bộ lọc (filterbank) và OLA.
- Julius O. Smith, *Spectral Audio Signal Processing* — điều kiện COLA và các đồng nhất thức của cửa sổ Hann.
- Cấu hình định khung DeepFilterNet: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).

## Video tham khảo

- [Short-Time Fourier Transform Explained Easily](https://www.youtube.com/watch?v=-Yxj3yfvY-4) — Valerio Velardo - The Sound of AI, tiếng Anh. **Xem trước.** Minh họa cách cắt khung, bước nhảy hop và nhân cửa sổ; overlap-add chính là bước ghép các khung đó trở lại thành dạng sóng.
- [Short-time Fourier Transform and the Spectogram](https://www.youtube.com/watch?v=NA0TwPsECUQ) — Barry Van Veen, tiếng Anh. Giải thích lý do các khung liên tiếp phải chồng lấp để phép biến đổi ngắn hạn có thể nghịch đảo chính xác.
- [But what is a convolution?](https://www.youtube.com/watch?v=KuXjwB4LzSA) — 3Blue1Brown, tiếng Anh. Xem phần FFT: tích chập miền thời gian tương đương phép nhân miền tần số, và overlap-add là cách ghép lại tín hiệu dài.
