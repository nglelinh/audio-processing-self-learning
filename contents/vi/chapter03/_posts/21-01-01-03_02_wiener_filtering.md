---
layout: post
title: "03-02 Bộ lọc Wiener cho tiếng nói"
chapter: "03"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter03
lesson_type: required
draft: false
---

Nếu trừ phổ xử lý theo hướng "trừ rồi kẹp sàn", thì **bộ lọc Wiener** chọn một hệ số độ lợi liên tục trên từng bin dựa trên tỷ số tín hiệu trên nhiễu ước lượng. Đường cong bên phải trong hình dưới minh họa độ lợi Wiener, đặt cạnh các cột trừ phổ mà nó thay thế.

![Gain Wiener theo SNR tiên nghiệm, cạnh các cột spectral subtraction mà nó làm mềm]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Hình. Độ lợi Wiener đạt \(1/2\) (\(-6\,\mathrm{dB}\)) khi công suất tiếng nói và nhiễu bằng nhau, biến thiên mượt mà thay vì tạo các hố phổ cứng như cột trừ phổ bên trái.*

Đây là cầu nối tự nhiên giữa trừ phổ cổ điển và các mô hình tăng cường tiếng nói mạng nơ-ron dựa trên mặt nạ: họ DeepFilterNet có thể được nhìn nhận như phiên bản học sâu của độ lợi Wiener thời gian–tần số với đặc trưng giàu thông tin hơn và bộ lọc đa khung. Bài học này trình bày trực giác MMSE, phân biệt SNR tiên nghiệm và hậu nghiệm, cơ chế theo dõi decision-directed và ứng dụng lọc Wiener trong các hệ thống VoIP.

Nếu trừ phổ giống như cầm chiếc kéo cắt phẳng mọi phần nhô lên khỏi mặt sàn nhiễu, thì **bộ lọc Wiener** lại giống một người thợ chỉnh âm tinh tế vặn chiếc chiết áp liên tục trên từng dải tần: hễ nơi nào tiếng nói áp đảo nhiễu, chiết áp mở gần tối đa; nơi nào nhiễu lấn át tiếng nói, chiết áp hạ êm xuống gần $$0$$ mà không bao giờ tạo ra vết cắt sắc lẹm. Kỳ diệu ở chỗ, công thức độ lợi mượt mà $$G = \frac{\xi}{1+\xi}$$ không phải là một mẹo đặt tay cảm tính, mà là nghiệm tối ưu duy nhất của bài toán bình phương sai số trung bình cực tiểu (MMSE) trong lý thuyết xác suất.

## Kiến thức cần nhớ: Từ hình học không gian Hilbert đến bộ lọc Wiener thời gian–tần số

### 1. Tiêu chí MMSE và nguyên lý trực giao (Orthogonality Principle)
Trong lý thuyết ước lượng thống kê, nếu muốn tìm một hệ số thực $$G$$ sao cho tín hiệu ước lượng $$\hat{S} = G \cdot Y$$ gần tín hiệu sạch $$S$$ nhất theo nghĩa sai số bình phương trung bình $$E[\vert S - G Y \vert^2]$$ nhỏ nhất, điều kiện cần và đủ là sai số $$(S - G Y)$$ phải *trực giao* với dữ liệu quan sát $$Y$$: $$E[(S - G Y) Y^*] = 0$$. Khi $$S$$ và $$N$$ không tương quan, phương trình trực giao này rút gọn chỉ trong hai dòng đại số thành $$G = \frac{E[\vert S \vert^2]}{E[\vert S \vert^2] + E[\vert N \vert^2]} = \frac{\xi}{1 + \xi}$$, với $$\xi = \frac{E[\vert S \vert^2]}{E[\vert N \vert^2]}$$ là **SNR tiên nghiệm (a priori SNR)**.

### 2. Phân biệt rạch ròi SNR tiên nghiệm $$\xi$$ và SNR hậu nghiệm $$\gamma$$
Trong thực tế, ta không bao giờ biết trước công suất tiếng nói sạch $$E[\vert S \vert^2]$$. Thứ duy nhất đo được trực tiếp ở khung hiện tại là **SNR hậu nghiệm (a posteriori SNR)**: $$\gamma(\ell, k) = \frac{\vert Y(\ell, k) \vert^2}{\hat{\lambda}_N(\ell, k)}$$. Nếu vội vàng xấp xỉ $$\hat{\xi} = \max(\gamma - 1, 0)$$, ước lượng sẽ nhảy loạn xạ theo từng đỉnh nhiễu ngẫu nhiên và tái sinh nhiễu nhạc y hệt trừ phổ.

### 3. Cơ chế Decision-Directed của Ephraim–Malah và cầu nối sang Deep Learning
Năm 1984, Ephraim và Malah đưa ra một công thức đệ quy thiên tài gọi là **decision-directed (DD)**: kết hợp $$98\%$$ ước lượng mượt từ khung trước đó với chỉ $$2\%$$ quan sát tức thời ở khung hiện tại:
$$\hat{\xi}(\ell, k) = \alpha\,\frac{\vert \hat{S}(\ell-1, k) \vert^2}{\hat{\lambda}_N(\ell, k)} + (1 - \alpha)\,\max(\gamma(\ell, k) - 1,\; 0), \qquad \alpha \approx 0{,}98.$$
Nhờ bộ nhớ làm mượt này, độ lợi Wiener biến thiên êm ái, gần như triệt tiêu nhiễu nhạc. Và khi bước sang Chương 4, bạn sẽ thấy mặt nạ tỷ số lý tưởng (IRM) hay độ lợi ERB của DeepFilterNet thực chất chính là một mạng nơ-ron học cách dự đoán trực tiếp đường cong $$G(\ell, k)$$ thay vì tự tính $$\hat{\xi}$$ bằng công thức đệ quy.

### Giải thích: Cầm tay tính độ lợi Wiener ở 3 mức SNR và kiểm chứng sức mạnh làm mượt của Decision-Directed

**Phần A — Độ lợi Wiener tại 3 mức SNR tiên nghiệm:** áp dụng $$G = \frac{\xi}{1+\xi}$$ và đổi sang suy hao decibel $$20\log_{10} G$$:

| Trạng thái ô STFT | SNR tiên nghiệm $$\xi$$ | Độ lợi Wiener $$G = \frac{\xi}{1+\xi}$$ | Suy hao biên độ (dB) | Hiệu ứng nghe |
| :--- | :---: | :---: | :---: | :--- |
| Tiếng nói mạnh ($$+10\text{ dB}$$) | $$10$$ | $$\frac{10}{11} \approx 0{,}909$$ | $$-0{,}83\text{ dB}$$ | Gần như nguyên vẹn |
| Tiếng nói ngang nhiễu ($$0\text{ dB}$$) | $$1$$ | $$\frac{1}{2} = 0{,}500$$ | $$-6{,}02\text{ dB}$$ | Hạ đều một nửa biên độ |
| Nhiễu áp đảo ($$-10\text{ dB}$$) | $$0{,}1$$ | $$\frac{0{,}1}{1{,}1} \approx 0{,}091$$ | $$-20{,}83\text{ dB}$$ | Nén sâu xuống dưới nền |

**Phần B — Chuyện gì xảy ra khi một gai nhiễu bất ngờ xuất hiện trong khoảng lặng?**
Giả sử khung trước đó đang yên lặng với $$\hat{\xi}_{\text{trước}} = 0{,}20$$. Đột ngột ở khung hiện tại, nhiễu ngẫu nhiên vọt lên khiến SNR hậu nghiệm đo được là $$\gamma = 4{,}0$$ (nên $$\max(\gamma - 1, 0) = 3{,}0$$):
1. **Nếu tin hoàn toàn khung hiện tại (ML tức thời):**
   $$\hat{\xi}_{\text{ML}} = 3{,}0 \implies G_{\text{ML}} = \frac{3{,}0}{1 + 3{,}0} = 0{,}750.$$
   Bộ lọc đột ngột mở toang $$75\%$$ cho gai nhiễu lọt qua — tạo ngay một tiếng "tích" nhiễu nhạc!
2. **Nếu dùng Decision-Directed với $$\alpha = 0{,}98$$:**
   $$\hat{\xi}_{\text{DD}} = 0{,}98 \times 0{,}20 + 0{,}02 \times 3{,}0 = 0{,}196 + 0{,}060 = 0{,}256 \implies G_{\text{DD}} = \frac{0{,}256}{1{,}256} \approx 0{,}204.$$
   Độ lợi chỉ nhích nhẹ lên $$0{,}204$$ (gần như không nghe thấy gai nhiễu). Nhưng nếu đó thực sự là một âm tiết tiếng nói bắt đầu kéo dài nhiều khung liên tiếp, $$\hat{\xi}_{\text{DD}}$$ sẽ tăng dần đều trong vài chục mili-giây — đổi lấy sự êm tai bằng một chút độ trễ đáp ứng ở đầu âm tiết.

## Mục tiêu học tập

Sau bài học này, bạn sẽ suy ra được độ lợi Wiener miền tần số $$G = \xi/(1+\xi)$$ từ tiêu chí MMSE dưới giả định Gauss, phân biệt rõ SNR tiên nghiệm $$\xi$$ với SNR hậu nghiệm $$\gamma$$, viết được giả mã bộ theo dõi decision-directed và liên hệ độ lợi Wiener với mặt nạ mềm (soft mask) trong mạng nơ-ron tăng cường tiếng nói.

## Kế hoạch 60 phút

- **0–10 phút** — Chuyển từ trừ cứng sang độ lợi mềm; so sánh cảm nhận nghe giữa Wiener và trừ phổ.
- **10–25 phút** — Phác thảo dẫn xuất MMSE → $$G^{\mathrm{Wiener}}=\xi/(\xi+1)$$.
- **25–40 phút** — Ước lượng $$\xi$$, $$\gamma$$ và công thức đệ quy decision-directed (Ephraim–Malah).
- **40–50 phút** — Kỹ thuật thực tế cho tiếng nói: sàn độ lợi và ứng dụng trong SpeexDSP / WebRTC NS.
- **50–60 phút** — Các bẫy thường gặp, bài tập và dẫn sang lọc Kalman (bài 03-03).

## Giải thích cốt lõi

### Công thức độ lợi Wiener

Với mô hình hỗn hợp $$Y=S+N$$ tại một bin STFT (giả sử $$S$$ và $$N$$ có phân bố Gauss, không tương quan và kỳ vọng bằng 0), bộ ước lượng tuyến tính tối ưu theo sai số bình phương trung bình tối thiểu (MMSE) của $$S$$ từ $$Y$$ có dạng nhân với hệ số:

$$
G^{\mathrm{W}} = \frac{P_S}{P_S + P_N} = \frac{\xi}{\xi + 1},
$$

trong đó $$\xi = P_S/P_N$$ là **SNR tiên nghiệm (a priori SNR)** và phổ sau tăng cường là $$\hat{S}=G^{\mathrm{W}} Y$$.

**Cách diễn giải:** Khi $$\xi\to\infty$$ thì $$G\to 1$$ (giữ nguyên tín hiệu); khi $$\xi\to 0$$ thì $$G\to 0$$ (triệt tiêu nhiễu). Ở vùng trung gian, $$G$$ hoạt động như một mặt nạ mềm — đúng dạng hàm mà các mạng dự đoán mặt nạ học từ dữ liệu.

### SNR hậu nghiệm (a posteriori SNR)

$$
\gamma = \frac{|Y|^2}{P_N}.
$$

Ta có thể đo trực tiếp $$\gamma$$ ở mỗi khung nếu biết công suất nhiễu $$P_N$$, nhưng không thể đo trực tiếp $$\xi$$ vì $$P_S$$ bị ẩn. Phần lớn công sức của khử nhiễu cổ điển tập trung vào việc ước lượng $$\xi$$. Ước lượng hợp lý cực đại (ML) thô $$\hat{\xi}=\max(\gamma-1,0)$$ dao động rất mạnh giữa các khung và tạo ra méo âm tương tự trừ phổ cứng.

### Bộ ước lượng decision-directed (Ephraim–Malah)

$$
\hat{\xi}(\ell) = \eta\,\frac{|G(\ell-1) Y(\ell-1)|^2}{P_N} + (1-\eta)\,\max\bigl(\gamma(\ell)-1,\,0\bigr),
$$

với hằng số làm mượt $$\eta$$ thường chọn khoảng $$0.98$$, sau đó tính $$G=\hat{\xi}/(\hat{\xi}+1)$$. Giá trị $$\eta$$ lớn giúp độ lợi mượt và giảm mạnh nhiễu nhạc nhưng dễ gây nhòe đuôi âm; ngược lại, $$\eta$$ nhỏ giúp bám nhiễu không dừng nhanh hơn nhưng dễ làm độ lợi dao động giật.

### Góc nhìn mặt nạ mềm (cầu nối sang Chương 04)

Mặt nạ tỷ số lý tưởng (IRM) trên miền công suất được định nghĩa là:

$$
M^{\mathrm{IRM}} = \frac{|S|^2}{|S|^2+|N|^2} = \frac{\xi}{\xi+1}.
$$

Biểu thức này trùng khớp hoàn toàn với độ lợi Wiener khi $$\xi$$ là SNR thực. Các mạng tăng cường tiếng nói thường huấn luyện để hồi quy $$\hat{M}$$ tiến tới IRM, IBM hoặc cIRM — vì thế nắm vững lọc Wiener giúp việc đọc hiểu DeepFilterNet trở nên trực quan hơn nhiều.

### Giả mã

```text
for each frame ell:
  Y = STFT(y_ell)
  γ = |Y|^2 / P_N
  ξ = η * |S_prev|^2 / P_N + (1-η) * max(γ - 1, 0)
  G = max(ξ / (ξ + 1), G_min)
  S_hat = G * Y
  S_prev = S_hat
  emit ISTFT_OLA(S_hat)
```

## Bảng tham số tinh chỉnh lọc Wiener cho tiếng nói

| Tham số | Khi tăng → | Khi giảm → |
|---------|------------|------------|
| $$\eta$$ | Mượt hơn, ít nhiễu nhạc hơn | Đáp ứng nhanh hơn nhưng dễ giật |
| $$G_{\min}$$ | Còn nhiều nhiễu nền dư hơn | Dễ méo tiếng hoặc tạo hố phổ |
| Tốc độ cập nhật $$P_N$$ | Bám tốt hơn với nhiễu không dừng | Ổn định hơn trong lúc có tiếng nói |

**Kiểm tra nhanh (sanity check):** Khi $$P_N\to 0$$ thì $$G\to 1$$ và đầu ra phải xấp xỉ đầu vào (với OLA đúng chuẩn). Nên viết bài kiểm thử đơn vị cho trường hợp biên này.

## Bẫy thường gặp

- Dùng trực tiếp $$\gamma/(\gamma+1)$$ và coi đó là bộ lọc Wiener chuẩn.
- Đóng băng ước lượng $$P_N$$ mãi mãi sau giây đầu tiên của cuộc gọi.
- Không đặt sàn độ lợi $$G_{\min}$$, khiến độ lợi tụt về 0 đột ngột và sinh nhiễu nhạc.
- Đặt lọc Wiener phía sau khối AGC phi tuyến mà không cập nhật lại mật độ phổ công suất nhiễu.
- Nhầm lẫn giữa **tiếng vọng** (có tín hiệu tham chiếu) với **nhiễu nền** (ước lượng mù) — lọc Wiener NS không thay thế được AEC.

## Mini-lab

**Mục tiêu.** Tính độ lợi Wiener tại ba mức SNR tiên nghiệm là \(-10\), \(0\) và \(+10\,\mathrm{dB}\).

```python
import numpy as np

for snr_db in (-10, 0, 10):
    xi = 10 ** (snr_db / 10.0)
    G = xi / (xi + 1.0)
    print(snr_db, "xi", round(float(xi), 4), "G", round(float(G), 3),
          "G_dB", round(float(20 * np.log10(G)), 2))
```

**Kết quả kỳ vọng.** Tại \(-10\,\mathrm{dB}\) → \(\xi=0.1\), \(G\approx 0.091\) (\(-20.83\,\mathrm{dB}\)); tại \(0\,\mathrm{dB}\) → \(\xi=1\), \(G=0.5\) (\(-6.02\,\mathrm{dB}\)); tại \(+10\,\mathrm{dB}\) → \(\xi=10\), \(G\approx 0.909\) (\(-0.83\,\mathrm{dB}\)). Hàng giữa tương ứng đúng với điểm đánh dấu trên hình minh họa.

**Lỗi thường gặp.** Đưa trực tiếp giá trị dB vào công thức \(\xi/(\xi+1)\) (quên đổi sang tuyến tính qua \(10^{\mathrm{SNR}/10}\)) khiến độ lợi ở \(-10\,\mathrm{dB}\) lớn hơn ở \(+10\,\mathrm{dB}\), làm đảo ngược hoàn toàn đường cong; dùng nhầm \(20\log_{10}\) để đổi công suất SNR sang \(\xi\), hoặc tính \(10\log_{10} G\) thay vì \(20\log_{10} G\), sẽ làm cột dB lệch hệ số 2; lưu ý rằng \(\gamma/(\gamma+1)\) là công thức thế khác và bài thực hành này không ước lượng \(\gamma\).

## Bài tập

1. Chứng minh $$G=\xi/(\xi+1)=1-1/(\xi+1)$$ và giải thích ý nghĩa của $$1-G$$.
2. Tính $$G$$ với $$\xi\in\{0.1,1,10\}$$ theo cả thang tuyến tính và dB; giá trị $$\xi$$ nào cho độ lợi đúng bằng $$-6\,\mathrm{dB}$$?
3. Cài đặt bộ lọc Wiener decision-directed, vẽ bản đồ độ lợi $$G(k,\ell)$$ và so sánh mức nhiễu nhạc với bài 03-01.
4. Viết hai đoạn văn giải thích vì sao mạng nơ-ron ước lượng IRM vượt trội hơn Wiener decision-directed trên nhiễu không dừng dù vẫn giữ cùng trực giác $$\xi/(\xi+1)$$.

### Gợi ý đáp án

1. Biến đổi trực tiếp cho thấy \(1-G=1/(\xi+1)\), đại diện cho tỷ lệ thành phần trong \(Y\) được quy về nhiễu.
2. \(G=1/2\) (tương ứng \(-6.02\,\mathrm{dB}\)) đạt được tại \(\xi=1\); ba giá trị độ lợi tương ứng là \(0.091\), \(0.5\) và \(0.909\).
3. Hãy vẽ trực tiếp \(G\) thay vì \(|Y|\): khi \(\eta\) nhỏ sẽ thấy bản đồ \(G\) lốm đốm, trong khi trừ phổ tạo các vùng khuyết cứng.
4. Mạng nơ-ron vẫn hướng tới ước lượng tỷ số công suất, nhưng nó vượt trội vì khai thác được ngữ cảnh thời gian–tần số rộng hơn nhiều so với một phép đệ quy decision-directed đơn giản, chứ không phải vì phát minh ra một công thức độ lợi hoàn toàn khác.

## Đọc thêm

- N. Wiener — nền tảng lý thuyết lọc tối ưu.
- Ephraim & Malah, *IEEE TASSP*, 1984.
- P. Scalart & J. V. Filho, “Speech enhancement based on a priori signal to noise estimation,” *ICASSP*, 1996 — dạng ước lượng SNR tiên nghiệm dùng trong lọc Wiener tiếng nói.
- Loizou, *Speech Enhancement: Theory and Practice*.
- SpeexDSP và WebRTC APM — các hiện thực kỹ thuật thực tế.

## Video tham khảo

- [Lec 22: Causal IIR Wiener Filter](https://www.youtube.com/watch?v=K_U0yeVdblU) — NPTEL IIT Guwahati, tiếng Anh. **Xem trước.** Minh họa cách độ lợi thay đổi liên tục theo mức nhiễu của phép đo — đúng nguyên lý đằng sau độ lợi theo bin trên STFT thay cho phép trừ cứng.
- [Wiener Filter Demonstration](https://www.youtube.com/watch?v=U71siegOD48) — Greg Malysa, tiếng Anh. Đoạn minh họa ngắn về hành vi của bộ lọc Wiener giúp bạn hình dung trực quan trước khi ánh xạ lên từng bin tiếng nói.
- [Spectral Subtraction In Python - Alexx Mitchell](https://www.youtube.com/watch?v=Xb--68NlxS0) — The Audio Programmer, tiếng Anh. Đặt cạnh bài Wiener để thấy rõ sự khác biệt giữa quy tắc trừ kèm ngưỡng sàn với đường độ lợi liên tục theo SNR.
