---
layout: post
title: "03-01 Spectral subtraction"
chapter: "03"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter03
lesson_type: required
draft: false
---

Spectral subtraction là cánh cửa cổ điển vào khử nhiễu: ước lượng phổ biên độ nhiễu, trừ khỏi phổ tiếng nói nhiễu, rồi dựng lại dạng sóng. Thuật toán đủ đơn giản để cài trong một buổi chiều, nhưng đủ sâu để dạy mọi artifact—đặc biệt *musical noise*—mà hệ neural hiện đại vẫn cố tránh. Bài này xây công thức trên STFT biên độ, các heuristic over-subtraction / spectral floor dùng trong preprocessor sản xuất (kiểu SpeexDSP), và bản đồ khi nào subtraction vẫn còn là front-end rẻ trước enhancer neural.

## Mục tiêu học tập

Cuối bài, bạn nêu được mô hình hỗn hợp cộng trong miền STFT, viết spectral subtraction biên độ kèm over-subtraction và flooring ở mức giả mã, giải thích vì sao đỉnh dư nghe như tiếng “nhạc”, và quyết định khi nào subtractor cổ điển hữu ích như tiền xử lý so với khi nên chuyển thẳng sang Wiener hoặc mask neural.

## Kế hoạch 60 phút

- **0–10 phút** — Mô hình $$Y = S + N$$, phổ biên độ vs công suất, vì sao thường giữ pha của khung nhiễu.
- **10–25 phút** — Ước lượng nhiễu (VAD / min-statistics) và subtractor cơ bản $$|\hat{S}| = |Y| - \alpha |\hat{N}|$$.
- **25–40 phút** — Hệ số $$\alpha$$, sàn $$\beta$$, ví dụ số trên vài bin.
- **40–50 phút** — Musical noise: cơ chế, checklist nghe, SpeexDSP preprocessor.
- **50–60 phút** — Bẫy thường gặp, bài tập, khi nào subtraction còn là front-end trước DeepFilterNet.

## Giải thích cốt lõi

### Mô hình hỗn hợp và biên độ STFT

Quan sát một kênh

$$
y[t] = s[t] + n[t],
$$

với $$s$$ là tiếng nói, $$n$$ là nhiễu cộng. Sau STFT có cửa sổ (Chương 02), viết phổ phức $$Y(k,\ell)$$, $$S(k,\ell)$$, $$N(k,\ell)$$. Spectral subtraction cổ điển làm việc trên **biên độ** (hoặc công suất) và tái sử dụng **pha nhiễu**:

$$
\hat{S}(k,\ell) = \bigl(|Y(k,\ell)| - \widehat{|N|}(k,\ell)\bigr)_{+} \; e^{j\angle Y(k,\ell)}.
$$

Phần dương $$(\cdot)_{+}$$ tránh biên độ âm. Biến thể miền công suất trừ ước lượng công suất nhiễu khỏi $$|Y|^2$$ rồi lấy căn—cùng triết lý, trade-off bias/variance khác nhau.

### Ước lượng nền nhiễu (giả định)

Cần $$\widehat{|N|}(k)$$. Các giả định giảng dạy phổ biến:

1. **Nhiễu dừng trong khoảng lặng ban đầu** — trung bình biên độ $$L_0$$ khung đầu coi là chỉ nhiễu.
2. **VAD** — chỉ cập nhật khi không có tiếng nói.
3. **Min-statistics / đệ quy** — bám cực tiểu làm mượt của phổ nhiễu (xuất hiện trong SpeexDSP-style preprocessor).

Cập nhật đệ quy khi không nói:

$$
\widehat{|N|}(k,\ell) = \lambda \widehat{|N|}(k,\ell-1) + (1-\lambda)\,|Y(k,\ell)|,
$$

với $$\lambda$$ gần 1 nếu muốn thích nghi chậm.

**Giả định then chốt:** nhiễu không dừng (gõ phím, người nói cạnh, nhạc) khiến sàn chậm bị **thiếu trừ** lúc bùng phát và **trừ quá** sau đó—lý do subtraction thuần thất bại trong VoIP hiện đại.

### Over-subtraction và spectral floor

Các tinh chỉnh kiểu Berouti đưa hai nút:

- **$$\alpha \ge 1$$** — trừ *nhiều hơn* ước lượng để giảm đỉnh dư.
- **$$\beta \in (0,1)$$** — không cho biên độ xuống dưới $$\beta\,|Y|$$, giảm musical noise với giá phải trả là nhiễu dư.

$$
|\hat{S}(k,\ell)| = \max\bigl(|Y(k,\ell)| - \alpha\,\widehat{|N|}(k,\ell),\; \beta\,|Y(k,\ell)|\bigr).
$$

Đôi khi $$\alpha$$ phụ thuộc SNR: $$\alpha$$ lớn khi SNR tiên nghiệm thấp. Heuristic đó đã hướng tới **bộ lọc Wiener** (bài sau).

### Giả mã (STFT biên độ)

```text
for each frame ell:
  Y = STFT_frame(y_ell)
  magY = |Y|
  if is_noise_frame(ell):
      Nhat = λ * Nhat + (1-λ) * magY
  magS = max(magY - α * Nhat, β * magY)
  S_hat = magS * exp(j * angle(Y))
  emit ISTFT_OLA(S_hat)
```

Giữ hop, cửa sổ, overlap-add nhất quán Chương 02 để tái tạo hoàn hảo khi $$\alpha=0$$, $$\beta=1$$.

### Musical noise

Khi ước lượng nhiễu hơi **thấp**, còn đỉnh mỏng; khi **cao**, tạo hố phổ. Qua các khung, đỉnh dư trôi tần số nghe như tiếng hú/chim—**musical noise**. Flooring và làm mượt gain giảm artifact; $$\alpha$$ mạnh không flooring làm tệ hơn.

**Checklist nghe (khoảng 30 giây/clip):**

1. So khớp loudness input và output.
2. Solo vùng chỉ nhiễu: có hú/whistle không?
3. Solo tiếng nói SNR thấp: có bị rỗng/robot không?
4. Tăng $$\beta$$: musical noise giảm, nhiễu nền tăng.
5. Tăng $$\alpha$$: nhiễu giảm, méo tiếng nói và tonal artifact thường tăng.

## Ví dụ số (toy bins)

$$|Y| = [5.0,\; 2.0,\; 1.2]$$, $$\widehat{|N|} = [1.0,\; 1.5,\; 1.0]$$, $$\alpha=1.5$$, $$\beta=0.1$$.

Bin 0 → $$3.5$$; bin 1 → sàn $$0.2$$; bin 2 → sàn $$0.12$$. Không có sàn thì bin 1–2 về 0 tạo hố cứng sau ISTFT.

## Khi subtraction cổ điển vẫn là front-end

- Cổng luôn-bật rất rẻ trên DSP trước giai neural nặng.
- Khởi tạo SNR tiên nghiệm cho Wiener / MMSE.
- SpeexDSP preprocessor và chuỗi VoIP: subtraction / noise gate cùng AGC + VAD + NS.
- Hybrid: khối cổ điển bỏ Hum HVAC dừng; neural dọn nhiễu không dừng (Chương 04).

Với NS full-band realtime kiểu Mezon, subtraction một mình không đủ — nhưng hiểu nó thì mask học được của DeepFilterNet bớt bí. Panel trái của hình là quy tắc này trong miền công suất: cột xanh là \(|Y|^2\), đường cam là sàn nhiễu, cột xanh lá là phần sống sót sau sàn. Panel phải không phải phép trừ; đó là gain Wiener mềm của bài sau.

![Spectral subtraction miền công suất theo từng bin, cạnh đường gain Wiener mà bài này chưa áp]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Hình. Spectral subtraction (trái) bỏ một sàn nhiễu rồi chặn phần còn lại; đường trơn bên phải là gain Wiener khi phép trừ được thay bằng SNR.*

## Bẫy thường gặp

- Trộn công thức công suất và biên độ mà không chỉnh $$\alpha,\beta$$.
- Cập nhật nhiễu lúc đang nói → **xóa tiếng nói**.
- $$\beta=0$$ “cho sạch” → musical noise nặng.
- Quên chuẩn hóa OLA → pumping.
- Kỳ vọng subtraction xử lý echo (AEC, 03-04) hoặc nhiễu có hướng (beamforming, 03-05).

## Mini-lab

**Mục tiêu.** Chạy spectral subtraction biên độ trên tám bin và in những bin chạm sàn.

```python
import numpy as np

magY = np.array([1.2, 3.5, 0.8, 4.0, 2.2, 1.1, 0.5, 2.8])
Nhat = np.array([1.0, 1.0, 0.9, 1.1, 1.0, 0.8, 0.7, 1.0])
alpha, beta = 2.0, 0.1
raw = magY - alpha * Nhat
magS = np.maximum(raw, beta * magY)
clipped = np.where(raw < beta * magY)[0]
print("raw", np.round(raw, 2))
print("magS", np.round(magS, 2))
print("clipped bins", clipped.tolist())
```

**Kỳ vọng.** `raw` là `[-0.8, 1.5, -1.0, 1.8, 0.2, -0.5, -0.9, 0.8]`. Sau sàn, `magS` là `[0.12, 1.5, 0.08, 1.8, 0.22, 0.11, 0.05, 0.8]`. Bin bị cắt là `[0, 2, 4, 5, 6]`. Bin 1, 3 và 7 đi qua không bị cắt.

**Khi hỏng.** Dùng công suất \(|Y|^2\) với các số biên độ này, hoặc quên `beta * magY`, sẽ đổi cả tập bin bị cắt lẫn giá trị sàn. Test `raw < 0` bỏ sót bin 4: phần dư vẫn dương nhưng thấp hơn sàn. `alpha=1` cắt ít bin hơn và giấu over-subtraction mà ví dụ muốn chỉ.

## Bài tập

1. Chứng minh khi $$|Y| < \alpha\widehat{|N|}$$ thì quy tắc floored trả $$\beta|Y|$$; diễn giải $$\beta$$.
2. Cài offline NumPy; quét $$\alpha,\beta$$; ghi chú musical noise vs nhiễu dư.
3. Thay nhiễu dừng bằng gõ phím; giải thích vì sao $$\widehat{|N|}$$ cố định thất bại.
4. Viết 5 gạch đầu dòng: khi nào giữ SpeexDSP-style trước DeepFilterNet3 WASM, khi nào tắt hẳn.

### Gợi ý đáp án

1. `max` trả đối số thứ hai đúng khi đối số thứ nhất nhỏ hơn; \(\beta|Y|\) là phần biên độ nhiễu bạn từ chối xóa sạch.
2. Giữ ước lượng nhiễu từ đoạn đầu chỉ có nhiễu, rồi nghe đuôi nhiễu khi \(\alpha\) tăng và \(\beta\) giảm.
3. Burst cao hơn sàn đóng băng thì bị trừ thiếu; các frame sau đó bị trừ thừa. Chỉ cập nhật \(\widehat{|N|}\) khi VAD báo nhiễu.
4. Giữ front-end dừng, rẻ, khi mô hình neural là chặng đắt và hum ổn định; tắt khi nó đã đục lỗ mà mô hình 48 kHz sẽ coi là cấu trúc tiếng nói.

## Đọc thêm

- S. F. Boll, spectral subtraction, *IEEE TASSP*, 1979.
- Berouti / Makhoul — over-subtraction & floor (xem Loizou, *Speech Enhancement*).
- Tài liệu SpeexDSP preprocessor (Xiph).
- Đối chiếu: ước lượng Ephraim–Malah / Wiener (03-02), RNNoise (04-06).
