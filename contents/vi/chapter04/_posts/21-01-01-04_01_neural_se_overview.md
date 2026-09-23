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

Tăng cường tiếng nói bằng mạng nơ-ron thay gain chỉnh tay bằng mô hình train trên cặp nhiễu–sạch. Bài này lập bản đồ masking, mapping và generative, đối chiếu mô hình dạng sóng với mô hình short-time Fourier transform (STFT, biến đổi Fourier thời gian ngắn), và chỉ ra loss mà mô hình thực sự tối ưu, để DeepFilterNet (từ 04-02) và RNNoise (04-06) đứng trên một bản đồ bạn bênh được khi review thiết kế. Kiến trúc khóa học sẽ mở là đồ thị hai tầng ở hình dưới.

![Đồ thị DeepFilterNet hai tầng: gain ERB cho đường bao và deep filter phức trên STFT]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. Đồ thị khóa học sẽ mở: tầng equivalent rectangular bandwidth (ERB, băng thông chữ nhật tương đương) thô ước lượng đường bao phổ, rồi một deep filter phức ngắn khôi phục hài. Các bài sau mở từng khối; bài này chỉ chốt bản đồ.*

## Mục tiêu học tập

Bạn đối chiếu masking, mapping và generative; tách loss phổ nén mà DeepFilterNet dùng khi train khỏi SI-SDR mà bài báo chỉ báo cáo; và tách độ trễ thuật toán khỏi real-time factor (RTF, hệ số thời gian thực).

## Kế hoạch 60 phút

- **0–10 phút** — Từ ideal ratio mask (IRM) Wiener đến mask học được.
- **10–25 phút** — Masking, mapping, generative; miền sóng và STFT.
- **25–40 phút** — Hỗn hợp kiểu DNS và loss trong paper DeepFilterNet.
- **40–50 phút** — Ràng buộc streaming; 40 ms độ trễ thuật toán không phải RTF.
- **50–60 phút** — Mini-lab, bẫy, bài tập.

## Giải thích cốt lõi

### Mạng xuất gì

**1. Masking.** Dự đoán $$M(k,\ell)$$ rồi $$\hat{S}=M\odot Y$$. Mask thực giữ pha nhiễu. Complex ratio mask (CRM) nhân phần thực và phần ảo, xoay được pha từng bin, nhưng vẫn là một tap: một hệ số nhân một bin. IRM vọng lại gain Wiener $$\xi/(\xi+1)$$ ở Chương 03. Paper ICASSP 2022 (arXiv:2110.05588) coi CRM là trường hợp riêng của deep filtering khi bậc $$N=1$$ và look-ahead $$\ell=0$$.

**2. Mapping.** Dự đoán trực tiếp biên độ sạch hoặc phổ phức, $$\hat{S}=f_\theta(Y)$$. Không có lực kéo đầu ra về gần $$Y$$, nên loss yếu làm mờ hài thành một đường bao nhòe.

**3. Generative.** GAN hoặc diffusion rút tiếng nói từ một hậu nghiệm. Mạng thứ hai vẫn phải xong trong cùng một hop. DeepFilterGAN (04-04) chỉ là tên khảo sát: khóa học không gán tiêu đề paper hay URL.

### Miền thời gian và spectrogram

| Họ | Đầu vào | Bạn trả | Bạn được |
|----|---------|---------|----------|
| Dạng sóng (kiểu Conv-TasNet) | Khung PCM | Encoder học trên từng mẫu | Pha nằm ẩn; 48 kHz full-band đắt |
| Mask STFT | Spectrogram phức | Một cửa sổ độ trễ | Gain dễ đọc; CRM không dựng lại hài mà cửa sổ đã nhòe |
| Gain ERB + deep filter | 32 băng ERB, rồi vài tap phức | Hai tầng phải hiện thực | Điểm vận hành của DeepFilterNet |

Ở 48 kHz, cửa sổ 20 ms (960 mẫu) có bước bin $$48000/960=50$$ Hz. Mask từng điểm không moi được nhiễu nằm giữa các hài mảnh hơn một bin — đó là lý do có tầng 2. Các mô hình đã công bố là hệ spectrogram cho ngân sách CPU full-band.

### Hỗn hợp kiểu DNS, với số trong paper

Framework ICASSP 2022 train trên dữ liệu Deep Noise Suppression (DNS): hơn 750 giờ tiếng sạch full-band và 180 giờ nhiễu, VCTK và PTDB được oversample 10 lần, tối đa năm nhiễu ở SNR trong $$\{-5,0,5,10,20,40\}$$ dB, lọc bậc hai ngẫu nhiên, gain trong $$\{-6,0,6\}$$ dB, rồi cuộn với đáp ứng phòng. Thêm 10.000 RIR image-source mô phỏng ở 48 kHz, RT60 từ 0,05 s đến 1,00 s. Quán cà phê có RT60 ngoài khoảng đó, hoặc nhiễu không nằm trong 180 giờ kia, chưa từng được giám sát. DNSMOS (Chương 08) chấm kết quả; hạng leaderboard không phải yêu cầu sản phẩm.

### Họ loss, và loss DeepFilterNet thực sự train

Các họ gặp ở chỗ khác: MSE biên độ, sai số phổ phức, SI-SDR miền thời gian, STFT đa phân giải, và critic đối kháng. Công thức ICASSP 2022 **không** train bằng SI-SDR. Nó dùng loss phổ nén với số mũ $$c=0{,}6$$,

$$
\mathcal{L}_{\mathrm{spec}}=\sum_{k,f}\left\||Y|^{c}-|S|^{c}\right\|^{2}+\sum_{k,f}\left\||Y|^{c}e^{j\varphi_Y}-|S|^{c}e^{j\varphi_S}\right\|^{2},
$$

cộng một hạng phụ (trọng số $$0{,}05$$) đẩy trọng số hòa deep filter về 0 khi SNR cục bộ dưới ngưỡng deep-filter thấp hơn $$-10$$ dB, và về 1 khi SNR đó trên $$-5$$ dB. SI-SDR trong paper đó là số **đánh giá**: 16,63 dB cho mô hình đầy đủ trên VCTK/DEMAND, so với 13,81 dB khi bỏ tầng 2. Wideband PESQ trên cùng bảng là 2,81 so với 2,57. Chỉ trích các số đó như số của bảng đó, tập đó, checkpoint đó.

### Streaming là một đồ thị khác

Transformer offline có thể attention cả câu. Một hop VoIP thì không. Demo 2023 (arXiv:2305.08227) dùng cửa sổ 20 ms, hop 10 ms, look-ahead hai khung: **độ trễ thuật toán 40 ms**. Độ trễ đó không phải RTF.

$$
\mathrm{RTF}=\frac{T_{\mathrm{wall}}}{T_{\mathrm{audio}}}.
$$

Hop 10 ms mà CPU đốt 4 ms thì RTF bằng 0,4, trong khi người nghe vẫn chờ 40 ms. Tích chập nhân quả và trạng thái GRU (gated recurrent unit, đơn vị hồi tiếp có cổng) kích thước cố định thay cache attention phình ra. Chương 05 đo đuôi của $$T_{\mathrm{wall}}$$: RTF trung bình 0,4 mà p95 trên 1 vẫn gây click.

### Các hệ có tên nằm ở đâu

```text
 phức tạp thấp                         chất lượng cao hơn trên tập full-band đã công bố
     │                                              │
  RNNoise ── tên siêu nhẹ (04-05) ── DeepFilterNet / 2 / 3 ── tên khảo sát (04-04)
  22 băng Bark + GRU                 32 băng ERB + filter phức 5 tap
```

RNNoise (Valin, arXiv:1709.08243) dự đoán 22 gain băng bằng GRU nhỏ và một lược pitch. DeepFilterNet dự đoán 32 gain ERB rồi năm tap phức ở bin thấp. Gói npm `deepfilternet3-noise-filter` chạy đồ thị ONNX/WASM hướng DF3 trong một AudioWorklet (luồng render của Web Audio); đó không phải cam kết khớp bit với checkpoint paper, và không phải nhánh RNNoise (04-06).

## Bẫy thường gặp

- Xếp PESQ offline cạnh RTF streaming.
- Coi một clip tàu điện −15 dB là lỗi mô hình khi lưới trộn chỉ xuống −5 dB.
- Giữ pha nhiễu rồi bỏ qua lượt nghe.
- Coi npm wrapper là thuật toán. Thuật toán là STFT, gain ERB, các tap, và state xuyên hop.

## Mini-lab

**Mục tiêu.** Tính độ trễ thuật toán và RTF cho cấu hình 20 ms / 10 ms / look-ahead hai khung đã công bố, và thấy chúng là hai đại lượng khác nhau.

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

**Expected**. `algorithmic_latency_ms=40.0`, `rtf=0.40`, `latency_is_rtf False`. Con số 40 ms là độ trễ đã nêu cho cửa sổ và look-ahead này trong paper DeepFilterNet2 và bản demo 2023. 4 ms thời gian tường là giả định của lab, không phải số đo điện thoại.

**Failure modes**. Lấy hop làm độ trễ (báo 10 ms, bỏ cửa sổ 20 ms và hai khung tương lai). Chia thời gian tường cho cửa sổ thay vì hop (RTF nhỏ đi một nửa). Dán RTF laptop vào ngân sách điện thoại.

## Bài tập

1. **Phân loại.** Đặt RNNoise, U-Net IRM biên độ, Conv-TasNet và DeepFilterNet vào masking / mapping / generative và dạng sóng / STFT. Nêu mỗi hệ nhân hay lọc cái gì.
2. **Độ trễ.** Cửa sổ 20 ms, hop 10 ms, look-ahead 2 khung. Độ trễ thuật toán trước mọi số đo neural là bao nhiêu? Thêm bao nhiêu nếu ring tổng hợp giữ thêm một hop?
3. **Loss.** Loss train dùng $$c=0{,}6$$ trên biên độ và một hạng có pha. SI-SDR trên bảng paper là 16,63 dB. Số nào theo dõi lúc train, số nào chỉ trên tập test cố định?
4. **Dữ liệu.** Nêu một lỗi người dùng nghe được cho mỗi trường hợp: SNR chỉ xuống −5 dB, RT60 chỉ tới 1 s, nhiễu lấy từ 180 giờ không có tiếng gõ phím.

### Gợi ý đáp án

1. RNNoise: gain băng thực (masking) trên lưới STFT/Bark, cộng lược pitch DSP. U-Net IRM: masking, STFT. Conv-TasNet: cơ sở dạng sóng học được, gần mapping. DeepFilterNet: mask ERB thực cộng filter phức nhiều tap trên STFT, không phải mô hình sinh.
2. $$20+2\times 10=40$$ ms. Thêm một hop trong ring là thêm 10 ms độ trễ đệm, không đổi RTF.
3. Theo dõi $$\mathcal{L}_{\mathrm{spec}}$$ (và hạng cổng phụ) khi train. Báo SI-SDR chỉ trên tập test đã ghim; paper đó không lấy nó làm mục tiêu train.
4. −15 dB nằm ngoài lưới trộn. Phòng 1,5 s không có trong khoảng RT60 0,05–1,00 s. Click ngắn không giống nhiễu dài trong 180 giờ đó.

## Đọc thêm

- Schröter et al., ICASSP 2022, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588).
- Schröter et al., DeepFilterNet2, IWAENC 2022, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474).
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227); README gắn citation này với DeepFilterNet3. Mã: [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- Valin, [arXiv:1709.08243](https://arxiv.org/abs/1709.08243), [xiph/rnnoise](https://github.com/xiph/rnnoise). Overview DNS Challenge cho quy ước hỗn hợp.
