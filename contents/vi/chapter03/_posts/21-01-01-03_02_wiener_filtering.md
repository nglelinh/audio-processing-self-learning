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

Spectral subtraction quyết định “trừ rồi sàn”; **bộ lọc Wiener** chọn gain liên tục theo từng bin từ ước lượng tỉ số tín hiệu–nhiễu. Đường bên phải của hình là gain đó; các cột bên trái là subtractor mà nó thay.

![Gain Wiener theo SNR tiên nghiệm, cạnh các cột spectral subtraction mà nó làm mềm]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Hình. Gain Wiener bằng \(1/2\) (\(-6\,\mathrm{dB}\)) khi công suất tiếng nói và nhiễu bằng nhau, và nó không thành các hố cứng của cột trừ phổ bên trái.*

Đây là cầu nối giữa subtractor cổ điển và enhancer neural dựa trên mask: họ DeepFilterNet có thể đọc như họ hàng học được của gain Wiener thời–tần, với đặc trưng phong phú hơn và bộ lọc đa khung. Bài này xây trực giác MMSE, SNR tiên nghiệm / hậu nghiệm, theo dõi decision-directed, và biến thể Wiener tiếng nói trong stack VoIP.

## Mục tiêu học tập

Bạn suy ra gain Wiener miền tần số $$G = \xi/(1+\xi)$$ từ lập luận MMSE dưới giả định Gauss, phân biệt SNR tiên nghiệm $$\xi$$ và hậu nghiệm $$\gamma$$, cài tracker decision-directed ở mức giả mã, và nối gain Wiener với soft mask trong SE neural.

## Kế hoạch 60 phút

- **0–10 phút** — Từ trừ cứng sang gain mềm; nghe Wiener vs subtractor.
- **10–25 phút** — Phác thảo MMSE → $$G^{\mathrm{Wiener}}=\xi/(\xi+1)$$.
- **25–40 phút** — Ước lượng $$\xi$$, $$\gamma$$; đệ quy decision-directed (Ephraim–Malah).
- **40–50 phút** — Thủ thuật tiếng nói: sàn gain; SpeexDSP / WebRTC NS.
- **50–60 phút** — Bẫy, bài tập, mở Kalman (03-03).

## Giải thích cốt lõi

### Gain Wiener một dòng

Với $$Y=S+N$$ trong một bin STFT, ước lượng tuyến tính MMSE của $$S$$ cho $$Y$$ (Gauss, không tương quan, kỳ vọng không) là nhân với

$$
G^{\mathrm{W}} = \frac{P_S}{P_S + P_N} = \frac{\xi}{\xi + 1},
$$

$$\xi = P_S/P_N$$ là **SNR tiên nghiệm**. Phổ tăng cường $$\hat{S}=G^{\mathrm{W}} Y$$.

**Đọc:** $$\xi\to\infty$$ thì $$G\to 1$$; $$\xi\to 0$$ thì $$G\to 0$$. Ở giữa là soft mask—đúng hình dạng mạng mask học từ dữ liệu.

### SNR hậu nghiệm

$$
\gamma = \frac{|Y|^2}{P_N}.
$$

$$\gamma$$ đo được mỗi khung nếu biết $$P_N$$; $$\xi$$ thì không vì $$P_S$$ ẩn. SE cổ điển đổ công sức vào ước lượng $$\xi$$. Ước lượng ML thô $$\hat{\xi}=\max(\gamma-1,0)$$ nhiễu theo khung và tạo artifact giống subtraction mạnh.

### Decision-directed (Ephraim–Malah)

$$
\hat{\xi}(\ell) = \eta\,\frac{|G(\ell-1) Y(\ell-1)|^2}{P_N} + (1-\eta)\,\max\bigl(\gamma(\ell)-1,\,0\bigr),
$$

$$\eta$$ thường $$0.98$$, rồi $$G=\hat{\xi}/(\hat{\xi}+1)$$. $$\eta$$ cao: mượt, ít musical noise, dễ “váng”; $$\eta$$ thấp: bám nhiễu không dừng tốt hơn nhưng giật.

### Nhìn soft mask (cầu Chương 04)

IRM miền công suất:

$$
M^{\mathrm{IRM}} = \frac{|S|^2}{|S|^2+|N|^2} = \frac{\xi}{\xi+1}.
$$

Đúng gain Wiener khi $$\xi$$ là SNR thật. Mạng SE thường hồi quy $$\hat{M}$$ về IRM / IBM / cIRM. Đọc DeepFilterNet dễ hơn khi đã “nằm lòng” Wiener.

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

## Checklist chỉnh Wiener tiếng nói

| Núm | Tăng → | Giảm → |
|-----|--------|--------|
| $$\eta$$ | mượt, ít tonal | nhanh, giật |
| $$G_{\min}$$ | nhiễu dư nhiều | méo / hố |
| Tốc độ cập nhật $$P_N$$ | bám nhiễu không dừng | ổn định lúc nói |

**Sanity:** $$P_N\to 0$$ ⇒ $$G\to 1$$, output ≈ input (OLA chuẩn). Hãy unit-test đường này.

## Bẫy thường gặp

- Dùng $$\gamma/(\gamma+1)$$ như thể là Wiener.
- Đóng băng $$P_N$$ mãi sau giây đầu cuộc gọi.
- Không sàn gain → về 0 đột ngột → musical noise.
- Wiener sau AGC phi tuyến mà không cập nhật PSD nhiễu.
- Nhầm **echo** (có tham chiếu) với **nhiễu** (mù)—Wiener NS không phải AEC.

## Mini-lab

**Mục tiêu.** Tính gain Wiener tại SNR tiên nghiệm \(-10\), \(0\) và \(+10\,\mathrm{dB}\).

```python
import numpy as np

for snr_db in (-10, 0, 10):
    xi = 10 ** (snr_db / 10.0)
    G = xi / (xi + 1.0)
    print(snr_db, "xi", round(float(xi), 4), "G", round(float(G), 3),
          "G_dB", round(float(20 * np.log10(G)), 2))
```

**Kỳ vọng.** \(-10\,\mathrm{dB}\) → \(\xi=0.1\), \(G\approx 0.091\) (\(-20.83\,\mathrm{dB}\)). \(0\,\mathrm{dB}\) → \(\xi=1\), \(G=0.5\) (\(-6.02\,\mathrm{dB}\)). \(+10\,\mathrm{dB}\) → \(\xi=10\), \(G\approx 0.909\) (\(-0.83\,\mathrm{dB}\)). Hàng giữa là điểm đánh dấu trên hình.

**Khi hỏng.** Đưa decibel thẳng vào \(\xi/(\xi+1)\) (quên \(10^{\mathrm{SNR}/10}\)) làm gain ở \(-10\,\mathrm{dB}\) lớn hơn gain ở \(+10\,\mathrm{dB}\), tức đường cong bị lộn. Dùng \(20\log_{10}\) để đổi SNR sang \(\xi\), hoặc báo \(10\log_{10} G\) thay vì \(20\log_{10} G\), sẽ lệch cột decibel khoảng một hệ số hai. \(\gamma/(\gamma+1)\) là plug-in khác; lab này không ước lượng \(\gamma\).

## Bài tập

1. Chứng minh $$G=\xi/(\xi+1)=1-1/(\xi+1)$$; diễn giải $$1-G$$.
2. Tính $$G$$ với $$\xi\in\{0.1,1,10\}$$ (tuyến tính và dB); $$\xi$$ nào cho $$-6\,\mathrm{dB}$$?
3. Cài decision-directed Wiener; vẽ bản đồ $$G(k,\ell)$$; so musical noise với 03-01.
4. Hai đoạn văn: vì sao ước lượng IRM neural thắng Wiener decision-directed trên nhiễu không dừng mà vẫn giữ trực giác $$\xi/(\xi+1)$$.

### Gợi ý đáp án

1. Trừ hai dạng; \(1-G=1/(\xi+1)\) là phần của \(Y\) bạn gán cho nhiễu.
2. \(G=1/2\) (tức \(-6\,\mathrm{dB}\)) khi \(\xi=1\). Ba gain được hỏi khoảng \(0.091\), \(0.5\) và \(0.909\).
3. Vẽ \(G\), không vẽ \(|Y|\). \(\eta\) giật thì ảnh lốm đốm; spectral subtraction trông như các hố.
4. Mạng vẫn nhắm một tỉ số công suất. Nó thắng vì ước lượng tỉ số đó từ nhiều ngữ cảnh hơn một vòng đệ quy decision-directed, không phải vì bịa một dạng gain khác.

## Đọc thêm

- N. Wiener — nền tảng lọc tối ưu.
- Ephraim & Malah, *IEEE TASSP*, 1984.
- P. Scalart và J. V. Filho, “Speech enhancement based on a priori signal to noise estimation,” *ICASSP*, 1996 — dạng SNR tiên nghiệm dùng trong Wiener tiếng nói.
- Loizou, *Speech Enhancement: Theory and Practice*.
- SpeexDSP / WebRTC APM — hiện thực kỹ thuật.
