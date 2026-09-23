---
layout: post
title: "04-06 RNNoise như cầu nối giảng dạy"
chapter: "04"
order: 6
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

**RNNoise** (Jean-Marc Valin, arXiv:1709.08243; [xiph/rnnoise](https://github.com/xiph/rnnoise)) là front-end băng Bark, một lược pitch, và một GRU (gated recurrent unit, đơn vị hồi tiếp có cổng) nhỏ phát 22 gain. Nó không khớp hàng Voicebank+Demand của DeepFilterNet3 (PESQ 3,17 trong arXiv:2305.08227). Nó dạy cùng một hình — băng thô cộng một tầng hài — với những số bạn kiểm bằng tay.

![Đường ERB của DeepFilterNet, dùng để đối chiếu 22 băng Bark và gain GRU của RNNoise]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. Hình của DeepFilterNet: 32 gain ERB (equivalent rectangular bandwidth, băng thông chữ nhật tương đương), rồi filter phức 5 tap trên bin STFT (short-time Fourier transform, biến đổi Fourier thời gian ngắn) thấp. RNNoise là phía đối chiếu, không phải bản vẽ lại hình này: 22 băng thang Bark, một GRU dự đoán các gain đó, và một lược pitch giữa các hài. Cả hai đều hybrid. Băng, tầng hai, và cỡ mạng thì khác.*

## Mục tiêu học tập

Bạn tính gain băng của RNNoise từ IRM, liệt kê 42 đặc trưng và chồng GRU 215 đơn vị trong paper, đối chiếu pipeline đó với 32 băng ERB và 5 tap phức của DeepFilterNet, và nêu thói quen hệ thống (API khung, làm trơn, trọng số vừa cache) chuyển sang AudioWorklet kể cả khi sản phẩm ship DF3.

## Kế hoạch 60 phút

- **0–10 phút** — Nghe sự đối chiếu: gain băng và filter phức nhiều tap.
- **10–25 phút** — 22 băng, công thức gain, lược pitch.
- **25–40 phút** — 42 đặc trưng, GRU, số mũ loss $$\gamma=1/2$$, độ phức tạp.
- **40–50 phút** — Cái gì mang sang cổng WASM, và không được kỳ vọng gì trên PESQ.
- **50–60 phút** — Mini-lab, bài tập.

## Giải thích cốt lõi

### Khung và băng

RNNoise chạy 48 kHz trên cửa sổ **20 ms**, chồng **50%** (hop 10 ms, 480 mẫu), cùng khung với DeepFilterNet. Phân tích và tổng hợp dùng cửa sổ Vorbis

$$
w(n)=\sin\left(\frac{\pi}{2}\sin^{2}\left(\frac{\pi n}{N}\right)\right),
$$

thỏa tiêu chí Princen–Bradley, nên overlap-add hằng của cửa sổ này dựng lại một tín hiệu hằng. Phổ được gom thành **22 băng**: xấp xỉ Bark của codec Opus (bước Bark ở tần số cao, và ít nhất bốn bin DFT mỗi băng ở tần số thấp), với trọng số tam giác $$w_b(k)$$ cộng thành 1 qua các băng. Năng lượng băng là

$$
E(b)=\sum_k w_b(k)\,|X(k)|^{2}.
$$

Mạng không phát 481 mask bin. Nó phát một gain mỗi băng. Target train là căn bậc hai của IRM,

$$
g_b=\sqrt{\frac{E_s(b)}{E_x(b)}},
$$

áp lên bin bằng cách nội suy cùng các tam giác, $$r(k)=\sum_b w_b(k)\,\hat{g}_b$$. Gain nằm trong $$[0,1]$$. Cái hộp đó là lý do mạng nhỏ ổn định: mạng mapping dự đoán biên độ thô không có hộp như vậy.

Tầng đường bao của DeepFilterNet là hậu duệ của ý này trên thang khác: **32 băng ERB** và một gain thực, không phải 22 băng Bark. Tầng hai là chỗ gãy. RNNoise không dự đoán tap STFT phức. Nó chạy một **lược pitch**. Nếu $$P(k)$$ là DFT của tín hiệu trễ đúng chu kỳ pitch $$T$$, filter lập $$X(k)+\alpha_b P(k)$$ rồi chuẩn lại năng lượng từng băng. Hệ số là heuristic của tương quan pitch $$p_b$$ và gain,

$$
\alpha_b=\min\left(\sqrt{\frac{p_b^{2}(1-g_b^{2})}{(1-p_b^{2})g_b^{2}}},\,1\right),
$$

với luật biên $$\alpha_b=1$$ khi $$p_b\ge g_b$$, và $$\alpha_b=0$$ khi $$g_b=1$$ hoặc $$p_b=0$$. Tổng phức 5 tap của DeepFilterNet dựng được một sự củng cố hài tương tự bên trong mạng, với giá MAC cao hơn nhiều, và chỉ tới khoảng 5 kHz. Lược của RNNoise là DSP, rẻ, và chỉ tốt bằng ước lượng pitch.

### Đặc trưng và GRU

42 đầu vào được paper chốt: 22 hệ số cepstrum Bark, đạo hàm bậc một và bậc hai của 6 hệ số đầu (thêm 12), 6 hệ số DCT của tương quan pitch, chu kỳ pitch, và một đặc trưng không dừng. $$22+12+6+1+1=42.$$ Không có chuẩn hóa trung bình cepstrum, nên mức tuyệt đối hiện ra. Đáp ứng micro được train bằng một lọc bậc hai ngẫu nhiên với hệ số trong $$[-3/8,3/8]$$.

Mạng có **215 đơn vị** và **bốn lớp ẩn**, lớp lớn nhất 96 đơn vị. Valin báo GRU nhỉnh hơn LSTM ở bài này và đơn giản hơn. Một đầu ra voice-activity thêm 24 trọng số và giao cho một GRU việc phân biệt tiếng với nhiễu khi train. Loss gain là

$$
L(g_b,\hat{g}_b)=\left(g_b^{\gamma}-\hat{g}_b^{\gamma}\right)^{2},\qquad \gamma=\tfrac{1}{2},
$$

không phải binary cross-entropy. $$\gamma\to 0$$ tiến tới sai số log-năng lượng và khử quá tay; $$\gamma=1/2$$ là điểm vận hành của paper. Băng không tiếng không nhiễu được đánh dấu không xác định và bị loại khỏi loss — cách im lặng và audio đã lọc thấp tránh dạy mạng xuất 0.

Làm trơn gain giới hạn tốc độ một băng được phép giảm,

$$
\tilde{g}_b=\max\left(\lambda \tilde{g}_b^{(\mathrm{prev})},\,\hat{g}_b\right),\qquad \lambda=0{,}6,
$$

và paper đồng nhất $$\lambda=0{,}6$$ ở hop 10 ms với thời gian vang khoảng **135 ms**. $$\lambda$$ nhỏ hơn nghe khô; $$\lambda=1$$ không bao giờ nhả. Sàn một cực này là mẹo chống nhiễu nhạc mà Chương 03 lấy từ sàn phổ.

### Độ phức tạp đặt cạnh DeepFilterNet

Mạng có **87.503** trọng số. Ở 8 bit chúng vừa cache L2; paper báo không mất chất lượng vì lượng tử hóa đó. Một phép nhân-cộng tính hai flop thì khoảng 175.000 flop mỗi khung, **17,5 Mflop/s** ở 100 khung mỗi giây. FFT thêm khoảng 7,5 Mflop/s và tìm pitch 12 kHz khoảng 10, tổng gần **40 Mflop/s**. Mã C không vector hóa dùng khoảng **1,3%** một nhân Haswell i7-4800MQ và khoảng **14%** Cortex-A53 1,2 GHz. Ngân sách đã công bố của DeepFilterNet là ~0,35 GMAC/s, cao hơn 40 Mflop/s rất nhiều. Trên bảng DF2, RNNoise là PESQ **2,33**, RTF **0,027**, so với DF2 giản lược PESQ **3,08**, RTF **0,04**: RTF laptop cùng cỡ, PESQ thấp hơn trên tập đó.

Dữ liệu train khoảng 6 giờ tiếng và 4 giờ nhiễu, nở thành 140 giờ, resample giữa 40 và 54 kHz. Setup DeepFilterNet ICASSP dùng hơn 750 giờ tiếng. Một click hoặc một ngôn ngữ ngoài 6 giờ đó là một lần trượt hợp lệ.

### Cái gì chuyển sang đường sản phẩm

Đường sản phẩm vẫn là AudioWorklet hướng DF3 (`DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`), không phải port RNNoise. Hãy chép thói quen: một hop mỗi lần gọi (480 mẫu; quantum 128 mẫu vẫn cần ring ở 05-03); tính trước cửa sổ và trọng số băng; làm trơn gain ($$\lambda=0{,}6$$ là hằng của RNNoise, không phải mặc định DF3 chưa nghe); lượng tử hóa để trọng số ở trong cache; giữ lược pitch nếu mạng nhỏ cỡ này. GRU không có lược là một thuật toán khác.

## Bẫy thường gặp

- Bỏ mã C vì PESQ 2,33 trên bảng của người khác.
- Kỳ vọng mô hình RNNoise mặc định khớp PESQ 3,17.
- Port GRU và xóa lọc pitch.
- Chỉ dùng RNNoise làm baseline hồi quy DF3 48 kHz. Giữ nó như một sàn (“ta vẫn thắng cái này”), không phải đích.

## Mini-lab

**Mục tiêu.** Kiểm số đặc trưng, ngân sách flop, và một bước gain đã làm trơn với hằng số của paper. Không file audio, không mạng.

```bash
python3 - << 'PY'
bfcc, deriv, pitch_dct, pitch_period, nonstat = 22, 12, 6, 1, 1
features = bfcc + deriv + pitch_dct + pitch_period + nonstat
weights = 87503
flops_per_frame = weights * 2  # multiply-add counted as two flops
mflops = flops_per_frame * 100 / 1e6  # 10 ms hop
g_hat, g_prev, lam = 0.3, 0.9, 0.6
g_smooth = max(lam * g_prev, g_hat)
print(features, flops_per_frame, round(mflops, 1), round(g_smooth, 2))
PY
```

**Expected**. `42 175006 17.5 0.54`. Gain đã làm trơn ở $$0{,}6\times 0{,}9=0{,}54$$ vì ước lượng mới 0,3 sẽ thả băng quá nhanh. Số “175.000” của paper là cùng đại lượng đã làm tròn ($$2\times 87503=175006$$).

**Failure modes**. Quên đạo hàm và báo 22 đặc trưng. Dùng hop 20 ms rồi ra 8,8 Mflop/s. Đặt $$\lambda=0$$ rồi gọi kết quả là “đã làm trơn”. Nhân bản RNNoise vào sản phẩm và nhận ngang DF3.

## Bài tập

1. **Chuỗi.** Vẽ PCM → cửa sổ 960 điểm → 22 băng → 42 đặc trưng → GRU → 22 gain → lược pitch → tổng hợp. Đánh dấu hop 10 ms.
2. **Alpha.** $$g_b=1$$. $$\alpha_b$$ bằng bao nhiêu, và lược làm gì với khung sạch?
3. **Làm trơn.** Gain đã làm trơn trước đó 0,8, ước lượng mới 0,2, $$\lambda=0{,}6$$. Gain ra là bao nhiêu? Bao nhiêu hop ước lượng 0,2 liên tục thì xuống dưới 0,3?
4. **API.** Phác `process_frame(state, in[480], out[480])` và liệt kê ba trường trong `state` phải sống sót sau lời gọi.

### Gợi ý đáp án

1. Hop 480 mẫu ở 48 kHz. GRU thấy 42 đầu vào và phát 22 gain cộng một VAD. Lược dùng chu kỳ pitch $$T$$ và $$\alpha_b$$ từng băng, rồi năng lượng băng được chuẩn lại.
2. Công thức có lính gác: khi $$g_b=1$$ thì $$\alpha_b=0$$. Lược bị bỏ qua để tiếng sạch không bị lọc pitch.
3. $$\max(0{,}6\times 0{,}8,\,0{,}2)=\max(0{,}48,\,0{,}2)=0{,}48$$. Hop sau $$\max(0{,}6\times 0{,}48,\,0{,}2)=0{,}288$$, dưới 0,3. Hai hop.
4. Ít nhất: state ẩn GRU, các gain đã làm trơn $$\tilde{g}_b$$, và lịch sử OLA / pitch. Xóa cái nào giữa stream cũng gây click hoặc mở một chùm nhiễu ngắn (bài 05-04).

## Đọc thêm

- Valin, “A Hybrid DSP/Deep Learning Approach to Real-Time Full-Band Speech Enhancement,” [arXiv:1709.08243](https://arxiv.org/abs/1709.08243). Công bố thành paper IEEE MMSP 2018 mà DeepFilterNet trích.
- Mã nguồn và trọng số 8 bit: [github.com/xiph/rnnoise](https://github.com/xiph/rnnoise).
- Bộ khử MMSE của SpeexDSP, baseline cổ điển trong paper đó.
- Schröter et al., [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) và [arXiv:2205.05474](https://arxiv.org/abs/2205.05474), cho đối chiếu 32 băng ERB và bảng PESQ 2,33 so với 3,08.
