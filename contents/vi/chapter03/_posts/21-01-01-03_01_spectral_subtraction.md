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

Trừ phổ (spectral subtraction) là bước nhập môn kinh điển của bài toán khử nhiễu: ước lượng phổ biên độ nhiễu, trừ đi từ phổ tín hiệu quan sát rồi tái tạo lại dạng sóng. Thuật toán đủ gọn để tự cài đặt trong một buổi chiều, nhưng cũng đủ sâu để phơi bày hầu hết các dạng méo âm — đặc biệt là *nhiễu nhạc (musical noise)* — mà các hệ thống mạng nơ-ron hiện đại vẫn phải tìm cách khắc phục. Bài học này xây dựng công thức trừ phổ trên biên độ STFT, trình bày kỹ thuật trừ dư (over-subtraction) và đặt ngưỡng sàn phổ (spectral floor) trong các bộ tiền xử lý thực tế (như SpeexDSP), đồng thời chỉ rõ khi nào trừ phổ vẫn hữu ích làm tầng tiền xử lý nhẹ trước mô hình mạng nơ-ron.

Nếu bạn đứng trong một quán cà phê ồn ào và cố lắng nghe người bạn đối diện, phản xạ tự nhiên nhất của não bộ — và cũng là ý tưởng đầu tiên trong lịch sử khử nhiễu số — là: *đợi lúc bạn mình ngừng nói để "ghi nhớ" tiếng ồn nền, rồi lấy tổng âm thanh trừ bớt tiếng ồn đó đi*. Thoạt nghe tưởng chừng quá đơn giản để có thể sai, nhưng chính phép trừ tưởng như ngây thơ ấy lại mở ra một bài học sâu sắc về thống kê ngẫu nhiên: khi trừ đi một đại lượng trung bình khỏi một tín hiệu nhiễu biến động ngẫu nhiên từng khung một, những đỉnh nhiễu sót lại sẽ kêu lách tách như những nốt nhạc rơi rời rạc — thứ mà giới kỹ sư gọi là **nhiễu nhạc (musical noise)**.

## Kiến thức cần nhớ: Trừ phổ nằm ở đâu trong xử lý tín hiệu thống kê?

### 1. Mô hình cộng tính và giả định độc lập thống kê
Trong phòng kín không vang quá nặng, sóng âm thu được tại micro là tổng tuyến tính $$y[t] = s[t] + n[t]$$. Nhờ tính tuyến tính của biến đổi Fourier thời gian ngắn (STFT), quan hệ này giữ nguyên trên từng ô thời gian–tần số: $$Y(\ell, k) = S(\ell, k) + N(\ell, k)$$. Khi giả định tiếng nói và nhiễu không tương quan nhau, công suất kỳ vọng cộng trực tiếp: $$E[\vert Y \vert^2] = E[\vert S \vert^2] + E[\vert N \vert^2]$$. Trừ phổ thay kỳ vọng lý thuyết bằng phổ tức thời $$\vert Y(\ell, k) \vert$$ và một ước lượng trung bình $$\vert \hat{N}(k) \vert$$ đo được trong các khoảng lặng.

### 2. Bất đối xứng giữa biên độ và pha trong thính giác người
Một số phức STFT gồm biên độ $$\vert Y \vert$$ và pha $$\angle Y$$. Các thực nghiệm tâm âm học kinh điển (Wang & Lim, 1982) cho thấy ở mức SNR trung bình và cao, tai người nhạy cảm với sai số biên độ hơn nhiều so với sai số pha cục bộ. Vì thế, thuật toán trừ phổ cổ điển (Boll, 1979) chỉ sửa biên độ để lấy $$\vert \hat{S} \vert$$ rồi ghép lại với chính pha nhiễu $$\angle Y$$ trước khi biến đổi ngược ISTFT.

### 3. Cơ chế sinh nhiễu nhạc và hai van an toàn $$\alpha, \beta$$
Do nhiễu nền là quá trình ngẫu nhiên, biên độ thực $$\vert N(\ell, k) \vert$$ dao động mạnh quanh mức trung bình $$\vert \hat{N}(k) \vert$$. Nếu trừ đúng $$1\times$$ mức trung bình rồi cắt về $$0$$ khi âm (half-wave rectification), một nửa số bin nhiễu bị xóa sạch về $$0$$, còn nửa kia trồi lên thành những gai nhọn cô lập xuất hiện rồi biến mất sau mỗi $$10\text{ ms}$$. Qua ISTFT, mỗi gai cô lập trở thành một hình sin ngắn nghe như tiếng "bíp" hay tiếng nước nhỏ giọt. Giải pháp kinh điển của Berouti (1979) là trừ dư bằng hệ số $$\alpha > 1$$ để dập các gai cô lập, đồng thời giữ lại một **sàn phổ (spectral floor)** $$\beta \vert Y \vert$$ (hoặc $$\beta \vert \hat{N} \vert$$) nhằm lấp các hố phổ đen kịt bằng một lớp nền dịu đều tai hơn.

### Giải thích: Cầm tay tính 3 bin STFT để thấy rõ sự khác biệt giữa trừ ngây thơ và trừ có $$\alpha, \beta$$

Giả sử bộ ước lượng nhiễu trong khoảng lặng cho $$\vert \hat{N}(k) \vert = 2{,}0$$ tại cả 3 bin tần số xét cùng một khung. Quan sát biên độ đo được $$\vert Y(k) \vert$$ tại 3 bin:
- **Bin A (họa âm tiếng nói mạnh):** $$\vert Y_A \vert = 10{,}0$$.
- **Bin B (đỉnh nhiễu ngẫu nhiên trồi lên trong khoảng lặng):** $$\vert Y_B \vert = 3{,}0$$.
- **Bin C (đáy nhiễu ngẫu nhiên tụt xuống thấp):** $$\vert Y_C \vert = 1{,}2$$.

Ta so sánh trực tiếp hai công thức:
1. **Trừ ngây thơ ($$\alpha = 1{,}0,\; \beta = 0$$):** $$\vert \hat{S} \vert = \max(\vert Y \vert - \vert \hat{N} \vert,\; 0)$$.
2. **Trừ dư kèm sàn phổ ($$\alpha = 2{,}0,\; \beta = 0{,}1$$):** $$\vert \hat{S} \vert = \max(\vert Y \vert - \alpha \vert \hat{N} \vert,\; \beta \vert Y \vert)$$.

| Bin tần số | $$\vert Y \vert$$ | Trừ ngây thơ ($$\alpha=1,\beta=0$$) | Trừ dư + sàn phổ ($$\alpha=2,\beta=0{,}1$$) | Ý nghĩa âm học |
| :--- | :---: | :---: | :---: | :--- |
| **Bin A** (tiếng nói) | $$10{,}0$$ | $$\max(10{,}0 - 2{,}0,\; 0) = 8{,}0$$ | $$\max(10{,}0 - 4{,}0,\; 1{,}0) = 6{,}0$$ | Giữ được họa âm chính (giảm nhẹ biên độ) |
| **Bin B** (gai nhiễu) | $$3{,}0$$ | $$\max(3{,}0 - 2{,}0,\; 0) = 1{,}0$$ | $$\max(3{,}0 - 4{,}0,\; 0{,}3) = 0{,}3$$ | Trừ ngây thơ để lọt gai $$1{,}0$$ gây **nhiễu nhạc**; $$\alpha=2$$ dập gọn xuống $$0{,}3$$ |
| **Bin C** (đáy nhiễu) | $$1{,}2$$ | $$\max(1{,}2 - 2{,}0,\; 0) = 0{,}0$$ | $$\max(1{,}2 - 4{,}0,\; 0{,}12) = 0{,}12$$ | Trừ ngây thơ tạo hố $$0{,}0$$ đột ngột; sàn $$\beta$$ giữ nền êm $$0{,}12$$ |

Nhìn vào cột giữa và cột phải, bạn thấy ngay cái giá phải trả: $$\alpha = 2{,}0$$ dập sạch gai nhiễu ở Bin B (từ $$1{,}0$$ xuống $$0{,}3$$) nhưng đồng thời làm tiếng nói ở Bin A hơi mỏng đi (từ $$8{,}0$$ xuống $$6{,}0$$). Chính sự đánh đổi cố hữu giữa *khử sạch nhiễu* và *méo giọng* này sẽ dẫn ta sang bộ lọc Wiener mượt mà hơn ở bài 03-02.

## Mục tiêu học tập

Sau bài học này, bạn sẽ nắm được mô hình hỗn hợp cộng tính trên miền STFT, viết được giả mã thuật toán trừ phổ biên độ kèm hệ số trừ dư và ngưỡng sàn, giải thích được vì sao các đỉnh nhiễu dư nghe giống tiếng "nhạc", và xác định được khi nào bộ trừ phổ cổ điển nên dùng làm tầng tiền xử lý thay vì chuyển thẳng sang lọc Wiener hoặc mặt nạ mạng nơ-ron.

## Kế hoạch 60 phút

- **0–10 phút** — Mô hình $$Y = S + N$$, so sánh phổ biên độ với phổ công suất và lý do thường tái sử dụng pha của khung nhiễu.
- **10–25 phút** — Ước lượng nền nhiễu (VAD / thống kê cực tiểu) và công thức trừ cơ bản $$|\hat{S}| = |Y| - \alpha |\hat{N}|$$.
- **25–40 phút** — Hệ số $$\alpha$$, ngưỡng sàn $$\beta$$ và ví dụ tính toán trên một vài bin.
- **40–50 phút** — Nhiễu nhạc: cơ chế hình thành, danh mục kiểm tra nghe và bộ tiền xử lý kiểu SpeexDSP.
- **50–60 phút** — Các bẫy thường gặp, bài tập và vai trò tiền xử lý trước DeepFilterNet.

## Giải thích cốt lõi

### Mô hình hỗn hợp và biên độ STFT

Xét tín hiệu quan sát đơn kênh:

$$
y[t] = s[t] + n[t],
$$

trong đó $$s$$ là tiếng nói sạch và $$n$$ là nhiễu cộng tính. Sau khi áp dụng STFT có cửa sổ (Chương 02), ta ký hiệu các phổ phức tương ứng là $$Y(k,\ell)$$, $$S(k,\ell)$$ và $$N(k,\ell)$$. Trừ phổ cổ điển tác động trên **biên độ** (hoặc công suất) và tái sử dụng **pha của tín hiệu nhiễu**:

$$
\hat{S}(k,\ell) = \bigl(|Y(k,\ell)| - \widehat{|N|}(k,\ell)\bigr)_{+} \; e^{j\angle Y(k,\ell)}.
$$

Phép lấy phần dương $$(\cdot)_{+}$$ ngăn biên độ bị âm. Biến thể trên miền công suất trừ ước lượng công suất nhiễu khỏi $$|Y|^2$$ rồi lấy căn bậc hai — cùng một nguyên lý nhưng có sự đánh đổi khác nhau giữa độ chệch (bias) và phương sai (variance).

### Ước lượng nền nhiễu (các giả định)

Thuật toán cần một ước lượng $$\widehat{|N|}(k)$$, thường dựa trên các giả định phổ biến sau:

1. **Nhiễu dừng trong khoảng lặng ban đầu** — lấy trung bình biên độ của $$L_0$$ khung đầu tiên vốn được giả định chỉ chứa nhiễu.
2. **Bộ phát hiện tiếng nói (VAD)** — chỉ cập nhật ước lượng nhiễu trên các khung không có tiếng nói.
3. **Thống kê cực tiểu (min-statistics) / cập nhật đệ quy** — bám theo cực tiểu đã làm mượt của phổ nhiễu (thường thấy trong bộ tiền xử lý kiểu SpeexDSP).

Công thức cập nhật đệ quy trên các khung không có tiếng nói:

$$
\widehat{|N|}(k,\ell) = \lambda \widehat{|N|}(k,\ell-1) + (1-\lambda)\,|Y(k,\ell)|,
$$

trong đó $$\lambda$$ gần bằng 1 nếu cần tốc độ thích nghi chậm và ổn định.

**Giả định then chốt:** Với nhiễu không dừng (tiếng gõ phím, người nói chuyện xung quanh, nhạc nền), ước lượng nền cập nhật chậm sẽ **trừ thiếu** khi nhiễu bùng phát và **trừ dư** ngay sau đó — đây là lý do trừ phổ thuần túy không đáp ứng được yêu cầu VoIP hiện đại.

### Trừ dư (over-subtraction) và ngưỡng sàn phổ (spectral floor)

Các cải tiến theo hướng Berouti bổ sung hai tham số điều chỉnh:

- **$$\alpha \ge 1$$** — trừ *nhiều hơn* ước lượng nhiễu để triệt tiêu các đỉnh nhiễu còn sót.
- **$$\beta \in (0,1)$$** — giữ biên độ không rơi xuống dưới $$\beta\,|Y|$$ nhằm giảm nhiễu nhạc, đánh đổi bằng việc để lại một phần nhiễu nền dư.

$$
|\hat{S}(k,\ell)| = \max\bigl(|Y(k,\ell)| - \alpha\,\widehat{|N|}(k,\ell),\; \beta\,|Y(k,\ell)|\bigr).
$$

Trong thực tế, $$\alpha$$ đôi khi được chọn phụ thuộc vào SNR (tăng $$\alpha$$ khi SNR tiên nghiệm thấp). Cách tiếp cận này mở đường trực tiếp sang **bộ lọc Wiener** ở bài học tiếp theo.

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

Cần giữ kích thước hop, hàm cửa sổ và phép cộng chồng lấp nhất quán với Chương 02 để đảm bảo tái tạo hoàn hảo khi $$\alpha=0$$ và $$\beta=1$$.

### Nhiễu nhạc (musical noise)

Khi ước lượng nhiễu hơi **thấp** hơn thực tế, phổ sau trừ còn sót lại các đỉnh nhọn rời rạc; khi ước lượng **cao** hơn, nó khoét thành các hố phổ bằng 0. Qua các khung liên tiếp, các đỉnh cô lập này bật tắt và dịch chuyển theo tần số, tạo ra âm thanh lách tách giống tiếng hú hoặc tiếng chim hót gọi là **nhiễu nhạc (musical noise)**. Đặt ngưỡng sàn và làm mượt độ lợi giúp giảm hiện tượng này, trong khi tăng mạnh $$\alpha$$ mà không đặt sàn sẽ làm âm thanh tệ hơn.

**Danh mục kiểm tra nghe (khoảng 30 giây mỗi đoạn):**

1. Cân bằng âm lượng (loudness) giữa đầu vào và đầu ra trước khi so sánh.
2. Nghe riêng đoạn chỉ có nhiễu: có xuất hiện tiếng hú hoặc ríu rít không?
3. Nghe riêng đoạn tiếng nói ở SNR thấp: giọng có bị rỗng hay giống robot không?
4. Tăng $$\beta$$: nhiễu nhạc giảm xuống trong khi nhiễu nền dư tăng lên.
5. Tăng $$\alpha$$: mức nhiễu giảm nhưng méo tiếng nói và các âm giả (tonal artifact) thường tăng.

## Ví dụ số (trên vài bin minh họa)

Cho $$|Y| = [5.0,\; 2.0,\; 1.2]$$, $$\widehat{|N|} = [1.0,\; 1.5,\; 1.0]$$, $$\alpha=1.5$$ và $$\beta=0.1$$.

Kết quả sau trừ và áp sàn lần lượt là: bin 0 → $$3.5$$; bin 1 → chạm sàn $$0.2$$; bin 2 → chạm sàn $$0.12$$. Nếu không có ngưỡng sàn, bin 1 và bin 2 sẽ bị cắt thẳng về 0, tạo các hố phổ cứng sau ISTFT.

## Khi nào trừ phổ cổ điển vẫn hữu ích làm tầng tiền xử lý

- Làm cổng giảm nhiễu luôn bật với chi phí rất thấp trên DSP trước tầng mạng nơ-ron nặng hơn.
- Tạo ước lượng khởi tạo SNR tiên nghiệm cho bộ lọc Wiener hoặc MMSE.
- Xuất hiện trong bộ tiền xử lý SpeexDSP và các chuỗi VoIP cổ điển kết hợp AGC + VAD + NS.
- Kiến trúc lai (hybrid): khối cổ điển xử lý tiếng ù HVAC dừng, còn mạng nơ-ron xử lý nhiễu không dừng (Chương 04).

Với bài toán khử nhiễu toàn băng thời gian thực như Mezon, riêng trừ phổ là chưa đủ — nhưng nắm vững cơ chế này giúp bạn hiểu rõ bản chất các mặt nạ học được của DeepFilterNet. Biểu đồ bên trái trong hình dưới minh họa quy tắc này trên miền công suất: cột xanh dương là \(|Y|^2\), đường cam là sàn nhiễu ước lượng, còn cột xanh lá là phần năng lượng giữ lại sau khi áp sàn. Biểu đồ bên phải không phải phép trừ mà là đường độ lợi Wiener mượt của bài kế tiếp.

![Spectral subtraction miền công suất theo từng bin, cạnh đường gain Wiener mà bài này chưa áp]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Hình. Trừ phổ (trái) loại bỏ một nền nhiễu rồi kẹp sàn phần còn lại; đường cong mượt bên phải là độ lợi Wiener khi phép trừ cứng được thay bằng hàm theo SNR.*

## Bẫy thường gặp

- Trộn lẫn công thức miền công suất và miền biên độ mà không điều chỉnh lại $$\alpha, \beta$$.
- Vẫn cập nhật ước lượng nhiễu khi người dùng đang nói → dẫn tới **xóa mất tiếng nói**.
- Đặt $$\beta=0$$ với kỳ vọng nền "sạch tuyệt đối" → gây nhiễu nhạc nặng.
- Quên chuẩn hóa OLA → gây hiện tượng bơm biên độ (pumping).
- Kỳ vọng trừ phổ xử lý được tiếng vọng (thuộc AEC, bài 03-04) hoặc nhiễu có hướng (thuộc beamforming, bài 03-05).

## Mini-lab

**Mục tiêu.** Chạy thuật toán trừ phổ biên độ trên 8 bin mẫu và in danh sách các bin bị kẹp về ngưỡng sàn.

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

**Kết quả kỳ vọng.** `raw` bằng `[-0.8, 1.5, -1.0, 1.8, 0.2, -0.5, -0.9, 0.8]`. Sau khi áp ngưỡng sàn, `magS` bằng `[0.12, 1.5, 0.08, 1.8, 0.22, 0.11, 0.05, 0.8]`. Các bin bị kẹp sàn là `[0, 2, 4, 5, 6]`, trong khi các bin 1, 3 và 7 đi qua nguyên vẹn.

**Lỗi thường gặp.** Áp dụng công thức công suất \(|Y|^2\) lên bộ số biên độ này hoặc quên nhân `beta * magY` sẽ làm sai cả tập bin bị cắt lẫn giá trị sàn; kiểm tra điều kiện `raw < 0` sẽ bỏ sót bin 4 (dù phần dư 0.2 vẫn dương nhưng thấp hơn ngưỡng sàn 0.22); đặt `alpha=1` sẽ cắt ít bin hơn và che mất tác động trừ dư mà ví dụ muốn minh họa.

## Bài tập

1. Chứng minh rằng khi $$|Y| < \alpha\widehat{|N|}$$ thì công thức có ngưỡng sàn trả về $$\beta|Y|$$, và giải thích ý nghĩa vật lý của $$\beta$$.
2. Cài đặt phiên bản ngoại tuyến bằng NumPy, quét các cặp giá trị $$\alpha, \beta$$ và ghi nhận sự đánh đổi giữa nhiễu nhạc và nhiễu dư.
3. Thay nhiễu dừng bằng tiếng gõ bàn phím và giải thích vì sao ước lượng $$\widehat{|N|}$$ cố định thất bại.
4. Viết 5 gạch đầu dòng phân tích khi nào nên giữ tầng tiền xử lý kiểu SpeexDSP trước DeepFilterNet3 WASM và khi nào nên tắt hẳn.

### Gợi ý đáp án

1. Hàm `max` trả về đối số thứ hai khi đối số thứ nhất nhỏ hơn (và rõ ràng khi \(|Y| - \alpha\widehat{|N|} < 0 < \beta|Y|\)); \(\beta|Y|\) chính là tỷ lệ biên độ nhiễu tối thiểu được giữ lại để tránh tạo hố phổ cứng.
2. Ước lượng nền nhiễu từ đoạn đầu chỉ có nhiễu, sau đó nghe kỹ phần đuôi nhiễu khi tăng \(\alpha\) và giảm \(\beta\).
3. Đợt xung cao hơn sàn cố định sẽ bị trừ thiếu và lọt qua, còn các khung sau đó có thể bị trừ quá mức; cần chỉ cập nhật \(\widehat{|N|}\) khi VAD xác nhận không có tiếng nói.
4. Có thể giữ tầng tiền xử lý dừng chi phí thấp khi nhiễu ù rất ổn định và mô hình mạng nơ-ron cần tiết kiệm tải; nên tắt nếu tầng tiền xử lý khoét hố phổ hoặc gây méo khiến mô hình 48 kHz phía sau nhận diện sai cấu trúc tiếng nói.

## Đọc thêm

- S. F. Boll, bài báo kinh điển về trừ phổ, *IEEE TASSP*, 1979.
- Berouti & Makhoul — kỹ thuật trừ dư và ngưỡng sàn (trình bày trong Loizou, *Speech Enhancement*).
- Tài liệu bộ tiền xử lý SpeexDSP (Xiph).
- Đối chiếu thêm: bộ ước lượng Ephraim–Malah / Wiener (bài 03-02) và RNNoise (bài 04-06).

## Video tham khảo

- [Spectral Subtraction In Python - Alexx Mitchell](https://www.youtube.com/watch?v=Xb--68NlxS0) — The Audio Programmer, tiếng Anh. **Xem trước.** Trình bày trực quan luồng thuật toán: ước lượng biên độ nhiễu, trừ rồi áp sàn; minh họa nguyên nhân phát sinh nhiễu nhạc khi xử lý bin âm một cách thô bạo.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Phần mở đầu cho thấy vì sao các sản phẩm gọi thoại sau này thay thế bộ khử cổ điển bằng mô hình học sâu.
- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, tiếng Anh. Nên nghe sau khi nắm sơ đồ trừ phổ để cảm nhận chất lượng đích mà các thuật toán cổ điển khó đạt được.
