---
layout: post
title: "01-05 Thuật toán FFT và độ phức tạp"
chapter: "01"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

DFT ngây thơ là \(O(N^2)\). Thoại thời gian thực không chịu nổi mỗi hop trên CPU điện thoại hay trong AudioWorklet. Bài này giải thích vì sao FFT là \(O(N\log N)\), radix-2 mang lại gì, và ràng buộc thực tế trong stack ORT/WASM/native.

![Cùng các tone cơ sở DFT mà FFT vẫn tính; thuật toán chỉ đổi lịch phép tính]({{ site.imgurl }}/generated/dft-basis.png)

*Figure. Radix-2 vẫn tính tích trong với các tone này. Nó chỉ đổi thứ tự phép tính, nên kết quả khớp DFT ngây thơ tới sai số làm tròn.*

## Mục tiêu học tập

1. Giải thích FFT \(O(N\log N)\) so với DFT \(O(N^2)\).
2. Mô tả chia để trị Cooley–Tukey radix-2 ở mức hoạt hình.
3. Liệt kê ràng buộc: kích thước lũy thừa 2, tối ưu real-FFT, tái sử dụng plan.
4. Ước chi phí FFT so với phép neural trong ngân sách hop.
5. Hiểu “gọi FFT” trong đồ thị ONNX vs WASM viết tay.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | Số học độ phức tạp: \(N=1024\) naive vs FFT |
| 10–28 | Ý tưởng butterfly radix-2; nhận thức bit-reversal |
| 28–42 | Real FFT; N không phải lũy thừa 2 (mixed radix / pad) |
| 42–52 | Phong cảnh thư viện: native, WASM SIMD, op FFT ORT |
| 52–60 | Bài tập |

## Giải thích cốt lõi

Mỗi trong \(N\) đầu ra cộng \(N\) MAC phức → \(\Theta(N^2)\). Với \(N=1024\) đã ~\(10^6\) MAC/lượt; nhân FFT+iFFT và số hop/s → dễ đau trên mobile khi cộng neural net.

Cooley–Tukey tách chẵn/lẻ:

$$
X[k]=E[k]+e^{-j2\pi k/N}O[k],\qquad
X[k+N/2]=E[k]-e^{-j2\pi k/N}O[k].
$$

Chi phí thỏa \(T(N)=2T(N/2)+\Theta(N)\). Khai triển ra \(\log_2 N\) thế hệ, mỗi thế hệ cộng lại \(\Theta(N)\), nên \(T(N)=\Theta(N\log N)\). Với \(N=1024\), \(\log_2 N=10\) và tỷ số hạng đầu \(N^2/(N\log_2 N)=102.4\). Đó là khoảng trăm lần ít phép nhân-cộng hơn, trước khi kể real-FFT bỏ nửa phổ thừa. Không phải tuyên bố thời gian tường giảm đúng 102 lần; hằng số, SIMD và overhead Python đổi tỷ số đo — mini-lab để thấy bậc đó. Twiddle là phép quay butterfly. Plan FFT tạo **một lần**; **không allocate** trên audio thread; ưu tiên SIMD (Ch. 06).

Speech PCM thực → real-FFT gần nửa công phức vì phổ Hermitian. Cửa sổ 960 mẫu (20 ms ở 48 kHz full-band của `deepfilternet3-noise-filter`) có \(960=2^6\cdot 3\cdot 5\), nên mixed-radix chạy thẳng, không bắt buộc lũy thừa hai. Pad 1024 vẫn được nhưng đổi tâm bin — **khớp training**. Chạy plan dài 256 chỉ vì “FFT nghĩa là lũy thừa hai” trên khung 48 kHz là đổi \(N\), không phải làm nhanh cùng một DFT.

NS cổ điển nhỏ: FFT có thể chiếm đa số. DeepFilterNet-class: matmul thường chiếm đa số, nhưng FFT vẫn đáng kể ở rate cao / hop nhỏ / build không SIMD.

## Ví dụ có số

Hop 10 ms → 100 cặp FFT+iFFT/s/kênh. \(N=512\) ~ vài nghìn MAC/lượt → ~\(10^6\) MAC/s phía FFT — nhỏ so với conv-RNN nhiều lớp, nhưng hop 2.5 ms + \(N=1024\) tăng nhanh.

## Bẫy thường gặp

1. Dựng lại FFT plan mỗi hop.
2. Dùng API phức trên dữ liệu thực bỏ qua lợi ích packing.
3. Nghĩ \(O(N\log N)\) nghĩa là “miễn phí”.
4. Đổi \(N\) lên lũy thừa 2 kế mà không kiểm tương thích mô hình.
5. So thời gian DEBUG vs Release / thiếu SIMD.

## Mini-lab

**Mục tiêu.** So thời gian tích ma trận DFT trực tiếp với `numpy.fft.fft` ở \(N=256\) và \(N=1024\). Đây là kiểm tra bậc lớn, không phải bài benchmark.

```python
import time
import numpy as np

def naive_dft(x):
    n = np.arange(x.shape[0])
    X = np.empty(x.shape[0], dtype=np.complex128)
    for k in range(x.shape[0]):
        X[k] = np.dot(x, np.exp(-2j * np.pi * k * n / x.shape[0]))
    return X

rng = np.random.default_rng(1)
for N in (256, 1024):
    x = rng.standard_normal(N)
    t0 = time.perf_counter()
    Xn = naive_dft(x)
    t_naive = time.perf_counter() - t0
    t0 = time.perf_counter()
    Xf = np.fft.fft(x)
    t_fft = time.perf_counter() - t0
    err = np.max(np.abs(Xn - Xf))
    print(N, f"naive_s={t_naive:.4f}", f"fft_s={t_fft:.6f}", f"err={err:.2e}")
```

**Expected.** `err` dưới `1e-8` ở cả hai kích thước (thường quanh `1e-12` và `1e-11`). Thời gian naive ở \(N=1024\) lớn hơn vài lần so với \(N=256\), cùng bậc với hệ số \(4^2=16\) của \(N^2\), overhead vòng lặp ăn bớt một phần. FFT vẫn dưới 1 ms. Ở \(N=1024\), lời gọi naive chậm hơn `np.fft.fft` hàng trăm lần. Số giây tuyệt đối không khớp máy bạn học.

**Failure modes.** Lấy một lần đo làm RTF công bố. Quên vòng “naive” này vẫn dùng `np.dot` vector hóa mỗi bin, không phải vòng Python thuần hai lớp. So FFT đã ấm với lần naive đầu tiên còn dựng twiddle, rồi trích tỷ số như hằng số Cooley–Tukey.

## Bài tập nhỏ

1. \(\log_2 1024\) tầng; so thô \(N\log N\) vs \(N^2\).
2. Vì sao real-FFT roughly giảm một nửa công?
3. Ba mối quan tâm FFT trên AudioWorklet/WASM.
4. Hop giảm một nửa, \(N\) cố định → CPU FFT roughly thế nào?
5. Một lý do tránh pad khi dùng STFT front-end pretrained.

### Gợi ý đáp án

1. \(\log_2 1024=10\) tầng. \(N\log_2 N=10240\) so với \(N^2=1048576\), hệ số khoảng 102 ở hạng đầu.
2. Phổ thực đối xứng liên hợp, nên thuật toán đóng gói bỏ nửa bin thừa. Lợi khoảng một nửa, không phải lớp tiệm cận mới.
3. Không cấp phát trên audio thread, tái sử dụng plan, và build có SIMD. Thêm một mục: đừng dựng lại bảng twiddle mỗi hop.
4. Số hop mỗi giây nhân đôi, nên việc FFT mỗi giây cũng gần nhân đôi nếu \(N\) giữ nguyên.
5. Pad dịch tâm bin và đổi độ dài mà trọng số đã thấy. Front-end pretrained đọc sai Hertz cho cùng một chỉ số.

## Đọc thêm

- Tổng quan dòng Cooley–Tukey; mục FFT trong Oppenheim & Schafer.
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — FFT là cách tính DFT nhanh hơn, không phải biến đổi khác.
- Tài liệu toán tử STFT/DFT ONNX khi dùng ORT.
