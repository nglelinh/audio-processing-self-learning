---
layout: post
title: "04-02 DeepFilterNet: ý tưởng deep filtering"
chapter: "04"
order: 2
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

**DeepFilterNet** (Schröter et al., ICASSP 2022, arXiv:2110.05588) là bộ tăng cường full-band dồn phần lớn dung lượng vào đường bao thính giác thô và một filter phức ngắn, không phải một mạng dày trên cả 481 bin. Bài này viết tổng filter và chạy nó trên phổ đồ chơi hai tap, kể cả khi trọng số pretrained không tải được.

![Sơ đồ hai tầng DeepFilterNet: gain ERB trên đường bao, deep filter trên hài tần số thấp]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. Tầng 1 dự đoán gain thực trên 32 băng ERB (equivalent rectangular bandwidth, băng thông chữ nhật tương đương) và nhân lên toàn STFT (short-time Fourier transform, biến đổi Fourier thời gian ngắn). Tầng 2 dự đoán filter phức 5 tap và chỉ áp lên tần số thấp, nơi phần lớn năng lượng tiếng nói tuần hoàn nằm. Bin cao giữ gain ERB.*

## Mục tiêu học tập

Bạn tính một lần áp gain ERB và một tổng deep filter đa khung trên bin phức; giải thích vì sao filter 5 tap tới khoảng 5 kHz rẻ hơn CRM trên mọi bin ở 48 kHz; nêu STFT đã công bố (cửa sổ 20 ms, hop 10 ms) và độ trễ thuật toán 40 ms gồm hai khung look-ahead; rồi chạy CLI `deepFilter` hoặc đường NumPy bên dưới.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao 481 bin ở 48 kHz không được cùng một ngân sách MAC.
- **10–25 phút** — Tầng ERB: 32 gain thực, nhân từng điểm.
- **25–40 phút** — Tổng deep filter so với gain Wiener hoặc CRM một tap.
- **40–50 phút** — Look-ahead, nhân quả, và repo chính thức.
- **50–60 phút** — Mini-lab (CLI hoặc NumPy), bài tập.

## Giải thích cốt lõi

### Hai tầng, với kích thước đã công bố

Tai phân giải tần số mịn hơn ở tần số thấp. DeepFilterNet dùng sự kiện đó hai lần.

1. **Tầng đường bao.** Ngân hàng ERB chữ nhật nén log-công suất xuống $$N_{\mathrm{ERB}}=32$$ băng. Mạng dự đoán 32 gain thực, ngân hàng ngược trải chúng lên bin STFT, rồi nhân với phổ nhiễu. Đặc trưng dùng chuẩn hóa trung bình mũ với suy giảm 1 s, nên một cú nhảy gain micro không bị đọc thành nhiễu mới.
2. **Tầng tuần hoàn.** Năm tap phức chỉ chạy tới $$f_{\mathrm{DF}}=5$$ kHz (ICASSP và DeepFilterNet2). Demo 2023 (arXiv:2305.08227) nói 96 bin thấp nhất: FFT 960 điểm ở 48 kHz có bin 50 Hz, và $$96\times 50\,\mathrm{Hz}=4{,}8$$ kHz. Trên ngưỡng đó, đầu ra là gain ERB.

Các bảng so sánh dùng 48 kHz, $$N_{\mathrm{FFT}}=960$$ (20 ms), chồng 50% (hop 480 mẫu = 10 ms). DeepFilterNet2 và demo 2023 dùng look-ahead hai khung và nêu **độ trễ thuật toán 40 ms**. Công thức độ trễ ICASSP là độ trễ cửa sổ cộng $$\max(l_{\mathrm{DNN}}, l_{\mathrm{DF}})$$; setup train dùng $$l_{\mathrm{DNN}}=2$$ và $$l_{\mathrm{DF}}=1$$. Các khung tương lai đó là độ trễ, phải đếm trước khi ai nói “thời gian thực”.

Trên bảng VCTK/DEMAND của paper ICASSP, mô hình đầy đủ có 1,778 triệu tham số và 0,348 GMAC/s, WB-PESQ 2,81, SI-SDR 16,63 dB. Bỏ tầng 2 còn 0,885 triệu tham số, 0,251 GMAC/s, PESQ 2,57, SI-SDR 13,81 dB. Tầng 2 chiếm khoảng nửa số tham số và phần lớn việc khôi phục hài.

### Filter không phải mask

Mask một tap, kể cả gain Wiener dưới mô hình Gauss, là

$$
\hat{S}(k,\ell)=M(k,\ell)\,Y(k,\ell).
$$

Deep filtering (Mack và Habets, và tuyến CLC mà paper ICASSP dựa vào) dự đoán các tap $$W_i$$ rồi cộng một đoạn lịch sử ngắn. Với filter 5 tap và look-ahead tùy chọn $$\ell$$,

$$
\hat{S}(t,f)=\sum_{i=0}^{4} W_i(t,f)\,X(t-i+\ell,f).
$$

Bản ICASSP đánh chỉ số bậc $$N=5$$ bằng tổng $$\sum_{i=0}^{N}$$; demo 2023 viết véctơ $$N=5$$ tap $$W_0,\ldots,W_{N-1}$$. Hãy dạy tổng năm hệ số. Cách đọc nào cũng là FIR theo thời gian trên từng bin, không phải một phép nhân. Lab dưới dùng hai tap cho phép tính vừa một dòng; ba tap còn lại là cùng một mẫu.

Tap phức xoay được một bin nhờ khung quá khứ — việc mask biên độ không làm được. Nhiều véctơ tap cho cùng một đầu ra, nên paper train chúng bằng loss phổ nén của bài 04-01 ($$c=0{,}6$$), không bằng một filter lý tưởng dạng đóng. Mô hình ICASSP còn học trọng số hòa $$\alpha(k)$$ giữa đầu ra deep filter và đầu ra ERB. Demo 2023 dùng cổng SNR (04-03). Đừng gộp hai cơ chế đó thành một khối.

### Vì sao số MAC giảm

Bộ giải mã đường bao phát 32 gain, không phải 481 ($$32/481\approx 0{,}067$$). Tầng tinh là 5 tap phức trên 96 bin, không phải CRM trên mọi bin. Mạng ICASSP còn tách lớp tuyến tính và GRU (gated recurrent unit, đơn vị hồi tiếp có cổng) thành $$P=8$$ nhóm, hidden $$512/8=64$$. Tên lớp đổi giữa các phiên bản; ngân sách này thì không.

### Nhân quả và repo

Tap chỉ được chạm các khung trong look-ahead đã khai. State GRU, bộ chuẩn hóa 1 s, và các phổ quá khứ là state streaming (05-04). Xóa chúng giữa cuộc gọi là một click hoặc một chùm nhiễu ngắn.

Cấu hình và trọng số: [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet). CLI `deepFilter` của gói `deepfilternet` mặc định trọng số DeepFilterNet3. Binary Rust `deep-filter` cần wav 48 kHz. Gói npm `deepfilternet3-noise-filter` ([mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression)) chạy ONNX/WASM trong AudioWorklet (`DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`) và không khớp bit với CLI.

## Checklist trước khi gọi đó là DeepFilterNet

1. STFT full-band 48 kHz, không phải mạng offline 16 kHz.
2. 32 gain ERB cho đường bao.
3. Filter phức nhiều tap chỉ trên bin thấp.
4. Look-ahead nằm trong nhóm độ trễ 40 ms, tách khỏi RTF.
5. State nhân quả được mang qua các hop.
6. Trọng số ghim bằng tên file hoặc commit, rồi mới export (Chương 06).

## Bẫy thường gặp

- Gọi mọi mạng mask là “DeepFilterNet”.
- Áp filter 5 tap lên cả 481 bin rồi hỏi ngân sách GMAC đi đâu.
- Chấm PESQ 16 kHz rồi nhận bảng 48 kHz.
- Quên cửa sổ 20 ms trong câu chuyện “khung 10 ms”.
- Tráo checkpoint DF, DF2 và DF3 trong một config (bài sau).

## Mini-lab

**Mục tiêu.** Tăng cường một file bằng CLI chính thức. Nếu không tải được trọng số, vẫn tính một tổng deep filter trong NumPy và so với mask một tap.

```bash
pip install deepfilternet
deepFilter --output-dir out/ noisy.wav
```

Cờ đã được tài liệu hóa: `--model-base-dir` (trọng số cục bộ), `--pf` (post-filter, bài 04-03), `--output-dir`, `--compensate-delay`. Đầu vào của binary Rust `deep-filter` là wav 48 kHz.

Đường offline, hai tap của tổng ở trên:

```bash
python3 - << 'PY'
import numpy as np
Y_now = np.complex64(1.0 + 0.5j)
Y_prev = np.complex64(0.2 - 0.1j)
H0 = np.complex64(0.8 + 0.0j)
H1 = np.complex64(0.1 - 0.2j)
deep = H0 * Y_now + H1 * Y_prev
mask = np.complex64(0.8) * Y_now
print(deep)
print(mask)
print(round(abs(deep), 6), round(abs(mask), 6))
PY
```

**Expected**. CLI: một wav đã tăng cường trong `out/` và một dòng log có timing hoặc RTF. NumPy, luôn luôn: kết quả deep filter `(0.8+0.35j)`, mask một tap `(0.8+0.4j)`, mô-đun khoảng `0.873212` và `0.894427`. Phần ảo đổi vì $$H_1$$ dùng $$Y_{\mathrm{prev}}$$; mask không làm được việc đó.

**Failure modes**. Không có mạng nên CLI không tải được trọng số — chạy đường NumPy và ghi lại lỗi, đừng bịa file wav. Đưa file không phải 48 kHz vào binary Rust. Đọc RTF laptop trên log rồi gọi đó là RTF điện thoại. Quên `--output-dir` rồi tìm wav ở nhầm thư mục.

## Bài tập

1. **Đặt cạnh nhau.** Viết gain Wiener một tap và tổng 5 tap. Khoanh đại lượng học được và đại lượng mà bộ theo dõi nhiễu sẽ ước lượng.
2. **Bin.** Ở 48 kHz với FFT 960 điểm, chỉ số bin cuối cùng của ngưỡng 4,8 kHz là bao nhiêu? Với 5 tap thì có bao nhiêu tap phức mỗi khung?
3. **Phác MAC.** Đầu đường bao phát 32 số thay vì 481. Tính tỉ số. Vì sao đó chưa phải toàn bộ câu chuyện GMAC?
4. **Kiểm độ trễ.** Hop 10 ms, look-ahead 2 khung, cửa sổ 20 ms. Bạn nêu độ trễ thuật toán nào, và cờ CLI nào chỉ dịch căn chỉnh file chứ không xóa độ trễ đó?

### Gợi ý đáp án

1. Wiener: $$M=\xi/(\xi+1)$$, một phép nhân thực (hoặc phức), $$\xi$$ từ bộ theo dõi nhiễu. Deep filter: năm $$W_i$$ phức từ mạng, tích vô hướng với năm khung $$X$$. Học được: $$W_i$$ và gain ERB. Hệ cổ điển ước lượng: $$\xi$$ hoặc PSD nhiễu.
2. Bước bin 50 Hz, nên chỉ số 96 rơi vào 4,8 kHz — đúng số “96 bin thấp nhất” của demo 2023. $$96\times 5=480$$ tap phức mỗi khung, trước các bin cao chỉ nhận một gain thực.
3. $$32/481\approx 0{,}0665$$. STFT, trải ngược ERB, và phép nhân 5 tap trên 96 bin còn nằm ngoài. Bài DF2 cho thấy nhóm hóa và hình kernel đổi RTF tường kể cả khi GMAC gần như đứng yên.
4. 40 ms. `--compensate-delay` căn lại file cho chấm offline; nó không bỏ look-ahead khỏi cuộc gọi trực tiếp.

## Đọc thêm

- Schröter et al., ICASSP 2022, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588). Gain ERB, deep filtering, bảng 1,778 M / 0,348 GMAC.
- Mack và Habets, “Deep Filtering,” IEEE Signal Processing Letters, 2020, như paper đó trích: filter phức đa khung mà DeepFilterNet nhận.
- README [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) cho CLI `deepFilter` và model card.
- Bài sau: DeepFilterNet2 và citation 2023 gắn với DeepFilterNet3 đổi gì, ở cùng mức cao.
