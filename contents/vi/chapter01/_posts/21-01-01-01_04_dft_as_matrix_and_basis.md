---
layout: post
title: "01-04 DFT như ma trận / cơ sở trực chuẩn"
chapter: "01"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter01
lesson_type: required
draft: false
---

Debug NS đòi hỏi coi DFT như đổi cơ sở có metric (Parseval), không chỉ như đồ thị màu. Bài này nối trực giao, dạng ma trận, chỉ số bin, và rò phổ.

![Tám tone cơ sở DFT: hệ tọa độ của biến đổi dài N]({{ site.imgurl }}/generated/dft-basis.png)

*Figure. Mỗi hàng của ma trận DFT là một tone phức trong hình; một bin là tích trong của khung với hàng đó.*

## Mục tiêu học tập

1. Nhìn DFT như hình chiếu lên mũ phức.
2. Viết DFT như ma trận; biết quy ước unitary vs không chuẩn hóa.
3. Dùng kiểm tra năng lượng kiểu Parseval khi xác thực STFT/ISTFT.
4. Đổi fluently giữa chỉ số bin, Hz, và tần số chuẩn hóa.
5. Dự đoán và nhận ra rò phổ khi sinusoid lệch bin.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–12 | Mũ trực giao; góc nhìn tích trong |
| 12–28 | Ma trận \(\mathbf{F}\); scale unitary; quy ước thư viện |
| 28–42 | Bin↔Hz; DC/Nyquist; tần số âm |
| 42–52 | Rò lệch bin; phác lab tone+nhiễu |
| 52–60 | Bài tập / checklist |

## Giải thích cốt lõi

\(w_k[n]=e^{j2\pi kn/N}\) trực giao với \(\langle w_k,w_\ell\rangle=N\delta_{k\ell}\). Tổng hình học \(\sum_{n=0}^{N-1}e^{j2\pi(k-\ell)n/N}\) bằng \(N\) khi \(k\equiv\ell\pmod N\) và bằng 0 nếu không — đó chính là tích trong. Phân tích: \(X[k]=\langle x,w_k\rangle\). Tổng hợp chia cho \(N\).

$$
\mathbf{X}=\mathbf{F}\mathbf{x},\quad F_{kn}=e^{-j2\pi kn/N}
$$

Nhiều API FFT: thuận không chia, nghịch chia \(1/N\) (hoặc ngược) — **bug scale ISTFT** là sát thủ chất lượng im lặng. Đặt \(\mathbf{U}=\mathbf{F}/\sqrt{N}\). Trực chuẩn cho \(\|\mathbf{Ux}\|=\|\mathbf{x}\|\). DFT không chuẩn hóa của NumPy là \(\mathbf{X}=\sqrt{N}\,\mathbf{Ux}\), nên

$$
\sum_n|x[n]|^2=\frac{1}{N}\sum_k|X[k]|^2.
$$

Nếu nghịch đảo đã chia \(N\) mà đường OLA lại chia \(N\) lần nữa, sóng 48 kHz full-band nhỏ dần mỗi hop. `setSuppressionLevel` trên `DeepFilterNoiseFilterProcessor` không kiểm bug đó: thanh trượt chỉ scale độ khử, không audit Parseval của STFT bạn tự viết cạnh gói.

$$
f_k=\frac{k}{N}f_s
$$

\(k=0\) là DC. \(k=N/2\) (N chẵn) là Nyquist. \(k>N/2\) là tần số âm của tín hiệu thực. Sinusoid không đủ số chu kỳ nguyên trong khối thì gián đoạn khi nối vòng → sidelobe (rò phổ, leakage); cửa sổ làm giảm sidelobe, nới lobe chính (Ch. 02).

## Ví dụ có số

48 kHz, \(N=1024\), \(\Delta f\approx46.875\,\mathrm{Hz}\). HVAC ~100 Hz gần bin 2–3. Mask chỉ xóa bin 2 mà để bin 3–10 thì gần như không làm gì; gain phải mượt sang hàng xóm.

Nhiễu trắng đơn vị dài 256: năng lượng thời gian ~256; \(\sum|X|^2\approx 65536\) với DFT không chuẩn hóa, chia \(N=256\) thì khớp Parseval.

Vector \(x=[1,0,-1,0]\) là \(\cos(2\pi n/4)\): đúng một chu kỳ trong bốn mẫu, tức bin \(k=1\). DFT không chuẩn hóa cho \(X[1]=X[3]=2\), hai bin kia bằng 0. Năng lượng thời gian bằng 2, năng lượng tần số \((4+4)/4=2\). Bài tập 1 vẫn yêu cầu viết cả ma trận; đoạn này chỉ kiểm hai đỉnh và Parseval.

## Bẫy thường gặp

1. Áp \(1/N\) hai lần.
2. Đọc nửa phổ gương như nội dung độc nhất gấp đôi.
3. Sửa nửa phổ không gương liên hợp.
4. So chuẩn FFT khác ngôn ngữ (NumPy vs FFTW…).
5. Dùng `|X|**2` không chuẩn hóa công suất cửa sổ khi ước PSD.

## Mini-lab

**Mục tiêu.** Dựng ma trận DFT dài 8 và kiểm đối xứng liên hợp cùng Parseval trên một vector thực.

```python
import numpy as np

N = 8
n = np.arange(N)
F = np.exp(-2j * np.pi * np.outer(n, n) / N)
x = np.array([1.0, -0.5, 0.25, 0.0, 0.1, -0.2, 0.3, -0.1])
X = F @ x
sym = np.max(np.abs(X - np.conj(X[(N - n) % N])))
energy_time = np.sum(np.abs(x) ** 2)
energy_freq = np.sum(np.abs(X) ** 2) / N
print(f"sym={sym:.3e}")
print(f"time={energy_time:.6f} freq={energy_freq:.6f}")
```

**Expected.** `sym` dưới `1e-12` (khoảng `1.200e-15`). Cả hai năng lượng in `1.462500`.

**Failure modes.** Dùng \(e^{+j2\pi kn/N}\) rồi so với `numpy.fft.fft` mà không ghi chú dấu (lab này không gọi FFT của NumPy; đối xứng và Parseval vẫn đúng với \(F\) này). Quên `/ N` trong Parseval rồi “sửa” bằng cách chia năng lượng thời gian. Sửa `X[1]` mà không sửa cặp liên hợp `X[7]`, rồi kỳ vọng nghịch đảo thực.

## Bài tập nhỏ

1. Với \(N=4\), viết \(\mathbf{F}\) tường minh.
2. \(k=32\), \(f_s=16\,\mathrm{kHz}\), \(N=256\) → Hz?
3. Vì sao tone lệch bin trông băng rộng dưới cửa sổ chữ nhật?
4. Thiết kế unit test 5 dòng Parseval cho wrapper FFT.
5. Bin DC khổng lồ ⇒ triệu chứng miền thời gian?

### Gợi ý đáp án

1. Phần tử hàng \(k\), cột \(n\) là \(e^{-j2\pi kn/4}\). Hàng 0 toàn số 1. Hàng 2 là \([1,-1,1,-1]\).
2. \(f=32\times 16000/256=2000\,\mathrm{Hz}\).
3. Nối vòng bị nhảy ở biên khối, nên tone không trùng một vector cơ sở. Sinc của cửa sổ chữ nhật trải nó ra.
4. Lấy vector thực, so \(\sum|x|^2\) với \((\sum|X|^2)/N\), assert độ lệch tuyệt đối dưới `1e-6` theo scale thư viện ghi.
5. Bin DC lớn là trung bình lớn. Sóng lệch khỏi 0; chỗ đầu tiên cần xem là DC blocker hoặc bias của mic.

## Đọc thêm

- Oppenheim & Schafer — tính chất DFT, Parseval.
- Tài liệu thư viện FFT (cờ chuẩn hóa).
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — ma trận DFT, trực giao, và Parseval.
