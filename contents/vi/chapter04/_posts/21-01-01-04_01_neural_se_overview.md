---
layout: post
title: "04-01 Tổng quan tăng cường tiếng nói bằng mạng nơ-ron"
chapter: "04"
order: 1
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

Tăng cường tiếng nói bằng mạng nơ-ron thay thế các công thức độ lợi chỉnh tay bằng mô hình học từ các cặp dữ liệu nhiễu–sạch. Bài học này hệ thống hóa ba hướng tiếp cận chính — tạo mặt nạ (masking), ánh xạ trực tiếp (mapping) và mô hình sinh (generative) — đối chiếu xử lý trên miền dạng sóng với miền biến đổi Fourier thời gian ngắn (STFT), đồng thời phân tích hàm mất mát mà mô hình thực sự tối ưu. Qua đó, DeepFilterNet (từ bài 04-02) và RNNoise (bài 04-06) được đặt trên cùng một bản đồ kiến trúc rõ ràng để bạn có cơ sở lập luận khi đánh giá thiết kế. Kiến trúc trọng tâm của khóa học là sơ đồ hai tầng ở hình dưới.

![Đồ thị DeepFilterNet hai tầng: gain ERB cho đường bao và deep filter phức trên STFT]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. Kiến trúc hai tầng trọng tâm của khóa học: tầng đầu sử dụng băng thông chữ nhật tương đương (equivalent rectangular bandwidth, ERB) để ước lượng đường bao phổ thô, sau đó một bộ lọc sâu (deep filter) phức ngắn khôi phục cấu trúc họa âm. Các bài sau sẽ đi sâu vào từng khối; bài này tập trung dựng bản đồ tổng thể.*

Sau ba chương đi từ biến đổi Fourier đến trừ phổ, Wiener và Kalman, ta nhận ra một giới hạn chung của trường phái cổ điển: chúng đều phải đặt ra các giả định thống kê đơn giản (nhiễu dừng, phân bố Gauss, pha nhiễu giữ nguyên) để viết được công thức đóng. Nhưng thế giới thực lại đầy rẫy tiếng gõ phím cơ, tiếng chó sủa, tiếng xe cộ biến đổi từng phần trăm giây — những thứ không vừa với bất kỳ phương trình giải tích gọn gàng nào. **Tăng cường tiếng nói bằng mạng nơ-ron (Neural Speech Enhancement)** lật ngược cách tiếp cận: thay vì tự viết công thức độ lợi, ta cho mạng nơ-ron nghe hàng nghìn giờ cặp âm thanh *nhiễu – sạch* để nó tự học cấu trúc họa âm phức tạp của giọng người và tách nhiễu ngay cả trong những tình huống phi dừng khắc nghiệt nhất.

## Bản đồ kiến thức nền: Ba hệ hình học sâu cho âm thanh và bài toán pha

### 1. Masking, Mapping và Generative — ba cách đặt đầu ra của mạng
- **Masking (Tạo mặt nạ):** mạng dự đoán một tỷ lệ (thực như IRM hoặc phức như CRM) rồi nhân với tín hiệu đầu vào $$Y$$. Vì mặt nạ bị chặn trong phạm vi nhỏ và tận dụng sẵn cấu trúc của $$Y$$, mô hình học nhanh, nhẹ và ít bị "bịa" giọng lạ.
- **Mapping (Ánh xạ trực tiếp):** mạng dự đoán thẳng phổ sạch $$\hat{S}$$ hoặc dạng sóng sạch $$\hat{s}[t]$$. Linh hoạt hơn nhưng dễ bị mờ chi tiết tần số cao khi SNR thấp.
- **Generative (Mô hình sinh — Diffusion / Flow / Codec):** sinh lại giọng nói sạch có điều kiện trên bản ghi nhiễu. Nghe rất tự nhiên ngay cả ở SNR cực âm, nhưng thường nặng, độ trễ cao và có nguy cơ "ảo giác" phát âm sai từ nếu không kiểm soát chặt.

### 2. Tại sao hàm mất mát (Loss) quan trọng không kém kiến trúc mạng?
Nếu huấn luyện mạng chỉ bằng sai số bình phương (MSE) trên biên độ STFT thô, các bin năng lượng lớn ở tần số thấp sẽ thống trị toàn bộ gradient, khiến mạng bỏ mặc các phụ âm xát yếu ở tần số cao (như "s", "x", "th"). Vì vậy, các hệ thống hiện đại như DeepFilterNet dùng **hàm mất mát phổ nén (compressed spectral loss)** với lũy thừa $$c \approx 0{,}3\text{–}0{,}6$$ ($$\vert S \vert^c$$) kết hợp cả thành phần biên độ lẫn thành phần phức để cân bằng giữa năng lượng lớn và chi tiết thính giác tinh tế — khác hẳn với chỉ số đánh giá SI-SDR thường dùng khi báo cáo kết quả.

### 3. Mặt nạ thực (IRM) bất lực trước sai số pha — lý do mặt nạ phức (CRM) ra đời
Ở SNR cao, pha nhiễu $$\angle Y$$ gần với pha sạch $$\angle S$$. Nhưng khi nhiễu mạnh bằng hoặc lớn hơn tiếng nói ($$\text{SNR} \le 0\text{ dB}$$), vector nhiễu $$N$$ kéo lệch góc pha của $$Y = S + N$$ đi hàng chục độ. Một mặt nạ thực chỉ có thể kéo dài hoặc rút ngắn vector $$Y$$ dọc theo đúng hướng sai đó, không bao giờ xoay nó trở về đúng góc của $$S$$ được!

### Khung giải thích: Cầm tay so sánh Mặt nạ thực (IRM) và Mặt nạ phức (CRM) trên một bin STFT nhiễu (nên đọc chậm)

Xét đúng một ô thời gian–tần số STFT nơi tiếng nói sạch và nhiễu là hai số phức:
- Tiếng nói sạch: $$S = 3 + 4j$$ (biên độ $$\vert S \vert = \sqrt{3^2 + 4^2} = 5$$, pha $$\approx 53{,}1^\circ$$).
- Nhiễu tại ô đó: $$N = 1 - 4j$$ (biên độ $$\vert N \vert = \sqrt{17} \approx 4{,}12$$, SNR cục bộ khoảng $$+1{,}7\text{ dB}$$).
- Quan sát micro thu được:
  $$Y = S + N = (3 + 1) + (4 - 4)j = 4 + 0j \qquad (\vert Y \vert = 4,\; \angle Y = 0^\circ).$$

Hãy thử khôi phục $$S$$ bằng hai loại mặt nạ lý tưởng (oracle):
1. **Mặt nạ biên độ thực tốt nhất (Oracle Real Mask):**
   Để khớp đúng biên độ $$\vert S \vert = 5$$ từ $$\vert Y \vert = 4$$, hệ số thực duy nhất là $$M_{\text{real}} = \frac{5}{4} = 1{,}25$$.
   - Kết quả khôi phục: $$\hat{S}_{\text{real}} = 1{,}25 \times (4 + 0j) = 5 + 0j$$.
   - Sai số phức còn lại:
     $$\vert S - \hat{S}_{\text{real}} \vert = \vert (3 + 4j) - (5 + 0j) \vert = \vert -2 + 4j \vert = \sqrt{4 + 16} = \sqrt{20} \approx 4{,}47!$$
   Dù đã biết trước biên độ sạch một cách hoàn hảo, sai số vẫn lên tới $$4{,}47$$ (gần bằng cả biên độ tiếng nói $$5$$!) chỉ vì mặt nạ thực không thể xoay góc pha từ $$0^\circ$$ lên $$53{,}1^\circ$$.

2. **Mặt nạ tỷ số phức (Oracle Complex Ratio Mask — CRM):**
   $$M_{\text{CRM}} = \frac{S}{Y} = \frac{3 + 4j}{4} = 0{,}75 + 1{,}00j.$$
   - Kết quả khôi phục:
     $$\hat{S}_{\text{CRM}} = (0{,}75 + 1{,}00j) \times 4 = 3 + 4j = S \implies \vert S - \hat{S}_{\text{CRM}} \vert = 0.$$

Phép nhân số phức đơn giản này là cốt lõi của cả kỷ nguyên tăng cường tiếng nói hiện đại: muốn khử nhiễu sâu ở SNR thấp mà giọng vẫn trong, mạng nơ-ron phải can thiệp được vào **cả biên độ lẫn pha** — và DeepFilterNet ở bài 04-02 sẽ còn tiến thêm một bước bằng cách dùng bộ lọc phức *đa khung*.

## Mục tiêu học tập

Sau bài học này, bạn sẽ phân biệt được masking, mapping và generative; tách bạch hàm mất mát phổ nén mà DeepFilterNet dùng khi huấn luyện với chỉ số SI-SDR dùng để báo cáo đánh giá; đồng thời phân biệt rõ độ trễ thuật toán với hệ số thời gian thực (real-time factor, RTF).

## Kế hoạch 60 phút

- **0–10 phút** — Bước chuyển từ mặt nạ tỷ số lý tưởng (IRM) kiểu Wiener sang mặt nạ học sâu.
- **10–25 phút** — So sánh masking, mapping và generative; đối chiếu miền dạng sóng và miền STFT.
- **25–40 phút** — Quy trình trộn dữ liệu kiểu DNS và hàm mất mát trong bài báo DeepFilterNet.
- **40–50 phút** — Ràng buộc streaming: phân biệt độ trễ thuật toán 40 ms với RTF.
- **50–60 phút** — Mini-lab, các bẫy thường gặp và bài tập.

## Giải thích cốt lõi

### Mạng nơ-ron dự đoán đại lượng nào

**1. Tạo mặt nạ (Masking).** Mạng dự đoán mặt nạ $$M(k,\ell)$$ rồi tính $$\hat{S}=M\odot Y$$. Mặt nạ thực giữ nguyên pha của tín hiệu nhiễu. Mặt nạ tỷ số phức (Complex Ratio Mask, CRM) nhân cả phần thực lẫn phần ảo nên xoay được pha từng bin, nhưng vẫn chỉ là bộ lọc một tap (một hệ số tác động lên một bin). IRM phản ánh trực tiếp độ lợi Wiener $$\xi/(\xi+1)$$ ở Chương 03. Bài báo ICASSP 2022 (arXiv:2110.05588) xem CRM như trường hợp riêng của deep filtering khi bậc $$N=1$$ và độ nhìn trước $$\ell=0$$.

**2. Ánh xạ trực tiếp (Mapping).** Mạng dự đoán thẳng biên độ sạch hoặc phổ phức $$\hat{S}=f_\theta(Y)$$. Vì không có cơ chế neo đầu ra quanh $$Y$$, hàm mất mát thiếu chặt chẽ dễ làm mờ các họa âm thành một đường bao nhòe.

**3. Mô hình sinh (Generative).** Các mô hình GAN hoặc khuếch tán (diffusion) lấy mẫu tiếng nói từ phân bố hậu nghiệm. Dù chất lượng cảm thụ có thể cao, toàn bộ mạng vẫn phải hoàn tất trong cùng một ngân sách hop khi chạy streaming. DeepFilterGAN (bài 04-04) chỉ được đề cập ở mức tên khảo sát trong khóa học này.

### Miền thời gian và miền phổ đồ

| Họ mô hình | Đầu vào | Chi phí phải trả | Lợi thế đạt được |
|------------|---------|------------------|------------------|
| Miền dạng sóng (kiểu Conv-TasNet) | Khung PCM | Bộ mã hóa học trực tiếp trên từng mẫu | Xử lý pha ngầm; chi phí rất cao ở 48 kHz toàn băng |
| Mặt nạ STFT | Phổ đồ phức | Độ trễ tối thiểu một cửa sổ | Độ lợi dễ diễn giải; CRM khó tái tạo hài đã bị cửa sổ làm nhòe |
| Độ lợi ERB + deep filter | 32 băng ERB, kèm vài tap phức | Phải triển khai kiến trúc hai tầng | Điểm cân bằng hiệu quả của DeepFilterNet |

Ở tần số lấy mẫu 48 kHz, cửa sổ 20 ms (960 mẫu) cho khoảng cách giữa các bin là $$48000/960=50$$ Hz. Mặt nạ từng điểm đơn thuần không thể tách nhiễu nằm xen giữa các họa âm mảnh hơn một bin — đó là lý do tầng thứ hai ra đời. Các mô hình toàn băng đã công bố chủ yếu chọn miền phổ đồ để phù hợp với ngân sách CPU.

### Quy trình trộn dữ liệu kiểu DNS (theo số liệu bài báo)

Framework ICASSP 2022 huấn luyện trên dữ liệu Deep Noise Suppression (DNS): hơn 750 giờ tiếng nói sạch toàn băng và 180 giờ nhiễu (VCTK và PTDB được lấy mẫu lặp 10 lần), trộn tối đa năm nguồn nhiễu tại các mức SNR trong $$\{-5,0,5,10,20,40\}$$ dB, áp dụng bộ lọc bậc hai ngẫu nhiên, thay đổi độ lợi trong $$\{-6,0,6\}$$ dB rồi tích chập với đáp ứng xung phòng. Tập huấn luyện bổ sung 10.000 đáp ứng xung phòng (RIR) mô phỏng theo phương pháp nguồn ảnh ở 48 kHz với RT60 từ 0,05 s đến 1,00 s. Do đó, một quán cà phê có RT60 vượt khoảng này hoặc một loại nhiễu không xuất hiện trong 180 giờ nói trên nằm ngoài phân bố đã học. DNSMOS (Chương 08) dùng để chấm điểm kết quả, nhưng thứ hạng bảng xếp hạng không đồng nghĩa với tiêu chuẩn triển khai sản phẩm.

### Các họ hàm mất mát và hàm mất mát thực tế của DeepFilterNet

Các họ hàm mất mát phổ biến trong lĩnh vực này gồm MSE biên độ, sai số phổ phức, SI-SDR miền thời gian, STFT đa phân giải và bộ phân biệt đối kháng (adversarial critic). Lưu ý rằng công thức trong bài báo ICASSP 2022 **không** huấn luyện trực tiếp bằng SI-SDR, mà sử dụng hàm mất mát phổ nén với số mũ $$c=0{,}6$$:

$$
\mathcal{L}_{\mathrm{spec}}=\sum_{k,f}\left\||Y|^{c}-|S|^{c}\right\|^{2}+\sum_{k,f}\left\||Y|^{c}e^{j\varphi_Y}-|S|^{c}e^{j\varphi_S}\right\|^{2},
$$

kèm một hạng phụ (trọng số $$0{,}05$$) kéo trọng số pha trộn của deep filter về 0 khi SNR cục bộ thấp hơn $$-10$$ dB và về 1 khi SNR vượt trên $$-5$$ dB. Trong bài báo đó, SI-SDR chỉ là chỉ số **đánh giá**: đạt 16,63 dB cho mô hình đầy đủ trên VCTK/DEMAND so với 13,81 dB khi bỏ tầng 2 (WB-PESQ tương ứng là 2,81 so với 2,57). Chỉ trích dẫn các con số này gắn đúng với bảng kết quả, tập dữ liệu và checkpoint tương ứng.

### Streaming là một đồ thị xử lý khác biệt

Một mô hình Transformer ngoại tuyến có thể áp dụng attention trên toàn bộ câu nói, nhưng một hop VoIP thì không. Bản demo năm 2023 (arXiv:2305.08227) dùng cửa sổ 20 ms, bước nhảy hop 10 ms và hai khung nhìn trước, tương ứng **độ trễ thuật toán 40 ms**. Độ trễ này tách biệt hoàn toàn với RTF:

$$
\mathrm{RTF}=\frac{T_{\mathrm{wall}}}{T_{\mathrm{audio}}}.
$$

Nếu CPU tiêu tốn 4 ms cho một hop 10 ms thì RTF bằng 0,4, trong khi người nghe vẫn chịu độ trễ thuật toán 40 ms. Tích chập nhân quả và trạng thái đơn vị hồi tiếp có cổng (GRU) kích thước cố định thay thế bộ nhớ đệm attention tăng dần theo độ dài câu. Chương 05 sẽ phân tích phân vị đuôi của $$T_{\mathrm{wall}}$$: RTF trung bình 0,4 nhưng phân vị p95 vượt quá 1 vẫn gây vỡ tiếng.

### Bản đồ vị trí các hệ thống tiêu biểu

```text
 phức tạp thấp                         chất lượng cao hơn trên tập full-band đã công bố
     │                                              │
  RNNoise ── tên siêu nhẹ (04-05) ── DeepFilterNet / 2 / 3 ── tên khảo sát (04-04)
  22 băng Bark + GRU                 32 băng ERB + filter phức 5 tap
```

RNNoise (Valin, arXiv:1709.08243) dự đoán 22 hệ số độ lợi theo băng Bark bằng mạng GRU nhỏ kết hợp bộ lọc lược theo cao độ (pitch comb filter). DeepFilterNet dự đoán 32 độ lợi ERB rồi áp bộ lọc phức 5 tap trên các bin tần số thấp. Gói npm `deepfilternet3-noise-filter` vận hành đồ thị ONNX/WASM theo nhánh DF3 bên trong AudioWorklet (luồng render của Web Audio); gói này không cam kết khớp từng bit với checkpoint trong bài báo và không thuộc nhánh RNNoise (bài 04-06).

## Bẫy thường gặp

- Đặt điểm PESQ ngoại tuyến bên cạnh chỉ số RTF thời gian thực như hai thước đo cùng điều kiện.
- Quy kết một đoạn ghi âm tàu điện ở −15 dB là lỗi mô hình khi tập huấn luyện chỉ trộn xuống tới −5 dB.
- Chỉ kiểm tra phổ biên độ mà bỏ qua việc nghe thử để phát hiện lỗi giữ pha nhiễu.
- Đồng nhất gói bọc npm với thuật toán cốt lõi — thực chất thuật toán nằm ở STFT, độ lợi ERB, các hệ số tap và quản lý trạng thái xuyên hop.

## Mini-lab

**Mục tiêu.** Tính độ trễ thuật toán và RTF cho cấu hình công bố (cửa sổ 20 ms, hop 10 ms, nhìn trước 2 khung) để thấy rõ đây là hai đại lượng độc lập.

```bash
python3 - << 'PY'
window_ms, hop_ms, lookahead_frames = 20.0, 10.0, 2
# Published overall delay for this configuration: window plus two hops.
algo_ms = window_ms + lookahead_frames * hop_ms
wall_ms = 4.0  # one hop of steady compute on a laptop you just timed
rtf = wall_ms / hop_ms
print(f"algorithmic_latency_ms={algo_ms:.1f}")
print(f"rtf={rtf:.2f}")
print("latency_is_rtf", algo_ms == wall_ms)
PY
```

**Kết quả kỳ vọng.** `algorithmic_latency_ms=40.0`, `rtf=0.40`, `latency_is_rtf False`. Mốc 40 ms là độ trễ tổng thể công bố cho cấu hình cửa sổ và look-ahead này trong bài báo DeepFilterNet2 và bản demo 2023; mức thời gian xử lý thực tế 4 ms chỉ là con số giả định minh họa cho máy tính xách tay, không phải số đo trên điện thoại.

**Lỗi thường gặp.** Coi bước nhảy hop là toàn bộ độ trễ (báo 10 ms mà bỏ qua cửa sổ 20 ms và 2 khung nhìn trước); chia thời gian xử lý thực tế cho độ dài cửa sổ thay vì cho hop (làm RTF giảm sai một nửa); hoặc mang RTF đo trên laptop áp vào ngân sách điện thoại.

## Bài tập

1. **Phân loại.** Xếp RNNoise, U-Net IRM biên độ, Conv-TasNet và DeepFilterNet vào các nhóm masking / mapping / generative và miền dạng sóng / STFT; nêu rõ mỗi hệ nhân hay lọc đại lượng nào.
2. **Độ trễ.** Với cửa sổ 20 ms, hop 10 ms và nhìn trước 2 khung, độ trễ thuật toán trước khi đo thời gian chạy mạng nơ-ron là bao nhiêu? Nếu bộ đệm vòng tổng hợp giữ thêm một hop thì tăng thêm bao nhiêu?
3. **Hàm mất mát.** Quá trình huấn luyện dùng số mũ nén $$c=0{,}6$$ trên biên độ kèm thành phần pha, trong khi bảng bài báo ghi SI-SDR đạt 16,63 dB. Chỉ số nào dùng để theo dõi khi huấn luyện, chỉ số nào chỉ dùng trên tập kiểm thử cố định?
4. **Dữ liệu.** Nêu một hiện tượng lỗi người dùng nghe thấy ứng với từng giới hạn dữ liệu: SNR chỉ xuống tới −5 dB, RT60 chỉ tới 1 s, và tập 180 giờ nhiễu thiếu tiếng gõ bàn phím.

### Gợi ý đáp án

1. RNNoise: độ lợi băng thực (masking) trên lưới STFT/Bark kèm bộ lọc lược cao độ DSP; U-Net IRM: masking trên STFT; Conv-TasNet: cơ sở dạng sóng học được, gần hướng mapping; DeepFilterNet: mặt nạ ERB thực kết hợp bộ lọc phức nhiều tap trên STFT (không phải mô hình sinh).
2. Độ trễ thuật toán là $$20+2\times 10=40$$ ms. Giữ thêm một hop trong bộ đệm vòng cộng thêm 10 ms độ trễ đệm nhưng không làm thay đổi RTF.
3. Theo dõi $$\mathcal{L}_{\mathrm{spec}}$$ (cùng hạng phụ cổng) trong quá trình huấn luyện; chỉ báo cáo SI-SDR trên tập kiểm thử cố định vì bài báo đó không lấy SI-SDR làm hàm mục tiêu huấn luyện.
4. Nhiễu −15 dB rơi ngoài phạm vi trộn huấn luyện; phòng vang 1,5 s vượt quá dải RT60 0,05–1,00 s; xung gõ phím ngắn khác biệt với các đoạn nhiễu kéo dài trong tập 180 giờ.

## Đọc thêm

- Schröter et al., ICASSP 2022, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588).
- Schröter et al., DeepFilterNet2, IWAENC 2022, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474).
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227) (README dự án gắn trích dẫn này với DeepFilterNet3). Kho mã nguồn: [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Valin, [arXiv:1709.08243](https://arxiv.org/abs/1709.08243), [xiph/rnnoise](https://github.com/xiph/rnnoise); tài liệu tổng quan DNS Challenge cho quy ước trộn dữ liệu.

## Video tham khảo

- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. **Xem trước.** Trình bày quá trình chuyển dịch từ bộ khử DSP sang mô hình học sâu, bao gồm hàm mất mát và quy trình kiểm thử chất lượng thực tế.
- [RNNoise, Neural Speech Enhancement, and the Browser](https://www.youtube.com/watch?v=nsscrYdrGRE) — W3C, tiếng Anh. Minh họa mô hình lai giữa đặc trưng DSP và mạng hồi tiếp nhỏ, đại diện cho đầu gọn nhẹ trên bản đồ masking so với mapping.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Trình bày sự kết hợp giữa độ lợi đường bao thực và bộ lọc phức — hai cơ chế tăng cường mạng nơ-ron trọng tâm của bài.
