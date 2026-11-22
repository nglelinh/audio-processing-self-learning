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

Tính DFT trực tiếp có độ phức tạp \(O(N^2)\), quá nặng để chạy ở mỗi bước nhảy hop trên CPU điện thoại hay bên trong AudioWorklet cho thoại thời gian thực. Bài học này giải thích cơ chế giúp FFT đạt độ phức tạp \(O(N\log N)\), vai trò của radix-2 và những ràng buộc thực tế khi triển khai trên stack ORT, WASM hoặc native.

![Cùng các tone cơ sở DFT mà FFT vẫn tính; thuật toán chỉ đổi lịch phép tính]({{ site.imgurl }}/generated/dft-basis.png)

*Hình. Thuật toán radix-2 vẫn tính tích trong với chính các thành phần tần số cơ sở này; nó chỉ sắp xếp lại thứ tự phép tính nên kết quả khớp với DFT trực tiếp trong giới hạn sai số làm tròn.*

## Mục tiêu học tập

1. So sánh độ phức tạp \(O(N\log N)\) của FFT với \(O(N^2)\) của DFT trực tiếp.
2. Mô tả ý tưởng chia để trị của thuật toán Cooley–Tukey radix-2 ở mức trực quan.
3. Nêu các ràng buộc thực tế: kích thước lũy thừa của 2, tối ưu real-FFT và tái sử dụng kế hoạch tính (FFT plan).
4. Ước lượng chi phí của FFT so với phần mạng nơ-ron trong ngân sách một hop.
5. Phân biệt việc gọi toán tử FFT bên trong đồ thị ONNX với việc tự cài đặt trên WASM.

## Kế hoạch giảng 60 phút

| Phút | Hoạt động |
|-----:|-----------|
| 0–10 | So sánh số phép tính với \(N=1024\) giữa DFT trực tiếp và FFT |
| 10–28 | Cơ chế cánh bướm (butterfly) radix-2 và nhận diện phép đảo bit (bit-reversal) |
| 28–42 | Real-FFT và xử lý kích thước \(N\) không phải lũy thừa của 2 (mixed-radix / đệm 0) |
| 42–52 | Hệ sinh thái thư viện: native, WASM SIMD và toán tử FFT trong ORT |
| 52–60 | Bài tập nhỏ |

## Giải thích cốt lõi

Trong DFT trực tiếp, mỗi đầu ra trong số \(N\) đầu ra cần \(N\) phép nhân-cộng phức (MAC), dẫn đến độ phức tạp \(\Theta(N^2)\). Với \(N=1024\), mỗi lượt biến đổi tiêu tốn xấp xỉ \(10^6\) phép MAC; khi nhân thêm cả chiều thuận lẫn chiều nghịch theo số hop mỗi giây, chi phí này sẽ nhanh chóng gây quá tải trên thiết bị di động khi chạy kèm mạng nơ-ron.

Thuật toán Cooley–Tukey tách dãy đầu vào thành hai nửa chỉ số chẵn và lẻ:

$$
X[k]=E[k]+e^{-j2\pi k/N}O[k],\qquad
X[k+N/2]=E[k]-e^{-j2\pi k/N}O[k].
$$

Chi phí tính toán thỏa hệ thức truy hồi \(T(N)=2T(N/2)+\Theta(N)\). Khai triển qua \(\log_2 N\) tầng đệ quy, mỗi tầng tiêu tốn \(\Theta(N)\), nên tổng độ phức tạp là \(T(N)=\Theta(N\log N)\). Tại \(N=1024\), ta có \(\log_2 N=10\) và tỷ số hạng bậc cao nhất là \(N^2/(N\log_2 N)=102.4\), tương đương giảm khoảng một trăm lần số phép nhân-cộng trước cả khi tính đến tối ưu real-FFT (bỏ nửa phổ đối xứng thừa). Điều này không có nghĩa thời gian chạy thực tế (wall-clock) lúc nào cũng giảm đúng 102 lần, bởi hằng số ẩn, tập lệnh SIMD và chi phí khung gọi của Python đều làm thay đổi tỷ số đo — phần Mini-lab sẽ minh họa bậc chênh lệch này. Các thừa số xoay (twiddle factor) thực hiện phép quay pha trong cấu trúc cánh bướm (butterfly). Trong sản phẩm thực tế, FFT plan cần được khởi tạo **một lần**, **không cấp phát bộ nhớ** trên audio thread và ưu tiên bật SIMD (Chương 06).

### Video ngắn: vì sao FFT tính nhanh

Đoạn video ngắn của MathDiagram đặt câu hỏi vì sao FFT có thể tính biến đổi Fourier nhanh đến vậy. Nên xem ngay sau phần tách chẵn/lẻ ở trên.

<div class="video-embed" style="text-align:center;margin:1em 0;"><iframe src="https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Freel%2F4039621483008687&show_text=false&width=315&height=560" width="315" height="560" style="border:none;overflow:hidden;max-width:100%;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe></div>

Nếu video không tải được, [xem trên Facebook](https://www.facebook.com/reel/4039621483008687).

Vì tín hiệu PCM tiếng nói là số thực, real-FFT giúp giảm gần một nửa khối lượng tính toán phức nhờ tính đối xứng Hermitian của phổ. Cửa sổ 960 mẫu (20 ms ở tần số 48 kHz toàn băng của `deepfilternet3-noise-filter`) phân tích được thành \(960=2^6\cdot 3\cdot 5\), do đó thuật toán mixed-radix xử lý trực tiếp rất hiệu quả mà không bắt buộc phải chọn lũy thừa của 2. Đệm số 0 lên 1024 vẫn khả thi nhưng sẽ làm dịch tâm các bin tần số — cần **khớp đúng cấu hình huấn luyện**. Việc ép dùng plan dài 256 trên khung 48 kHz chỉ vì nghĩ "FFT phải là lũy thừa của 2" thực chất là thay đổi \(N\), không phải tăng tốc cùng một phép DFT.

Với các bộ khử nhiễu cổ điển gọn nhẹ, FFT có thể chiếm phần lớn thời gian xử lý. Với nhóm mô hình như DeepFilterNet, phép nhân ma trận thường chiếm tỷ trọng chính, nhưng chi phí FFT vẫn đáng kể ở tần số lấy mẫu cao, hop ngắn hoặc trên các bản biên dịch không có SIMD.

## Ví dụ có số

Với hop 10 ms, hệ thống thực hiện 100 cặp FFT + iFFT mỗi giây trên mỗi kênh. Ở \(N=512\), mỗi lượt tốn vài nghìn phép MAC, tương đương xấp xỉ \(10^6\) MAC/giây cho riêng phần FFT — con số này khá nhỏ so với mạng tích chập–hồi tiếp nhiều lớp, nhưng sẽ tăng nhanh nếu giảm hop xuống 2.5 ms và tăng \(N=1024\).

## Bẫy thường gặp

1. Khởi tạo lại FFT plan ở mỗi hop.
2. Gọi API FFT phức trên dữ liệu thực, bỏ qua lợi thế đóng gói của real-FFT.
3. Coi độ phức tạp \(O(N\log N)\) đồng nghĩa với "chi phí không đáng kể".
4. Tự ý tăng \(N\) lên lũy thừa của 2 gần nhất mà không kiểm tra độ tương thích với mô hình.
5. So sánh thời gian chạy giữa bản DEBUG với bản Release hoặc bản thiếu SIMD.

## Mini-lab

**Mục tiêu.** So sánh thời gian tính DFT trực tiếp bằng tích ma trận với `numpy.fft.fft` ở \(N=256\) và \(N=1024\). Đây là phép kiểm tra bậc độ lớn, không phải benchmark chính thức.

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

**Kết quả kỳ vọng.** Sai số `err` nhỏ hơn `1e-8` ở cả hai kích thước (thường khoảng `1e-12` và `1e-11`). Thời gian chạy của `naive_dft` ở \(N=1024\) lớn hơn nhiều lần so với \(N=256\), cùng bậc với hệ số \(4^2=16\) của \(N^2\) (dù chi phí vòng lặp làm tỷ số thực tế nhỏ hơn một chút). Trong khi đó, `np.fft.fft` vẫn hoàn tất dưới 1 ms; tại \(N=1024\), cách tính trực tiếp chậm hơn hàng trăm lần. Giá trị giây tuyệt đối sẽ khác nhau tùy phần cứng.

**Lỗi thường gặp.** Dùng một lần đo đơn lẻ làm chỉ số RTF công bố; quên rằng vòng lặp "naive" ở trên vẫn dùng `np.dot` đã vector hóa cho từng bin thay vì hai vòng lặp Python thuần; hoặc so sánh một lần gọi FFT đã khởi động sẵn với lần chạy trực tiếp đầu tiên rồi coi tỷ số đó là hằng số lý thuyết của Cooley–Tukey.

## Bài tập nhỏ

1. Tính số tầng \(\log_2 1024\) và so sánh sơ bộ \(N\log_2 N\) với \(N^2\).
2. Giải thích vì sao real-FFT giúp giảm khoảng một nửa khối lượng tính toán.
3. Nêu ba lưu ý kỹ thuật quan trọng khi chạy FFT trên AudioWorklet/WASM.
4. Nếu giảm một nửa bước nhảy hop trong khi giữ nguyên \(N\), tải CPU của phần FFT thay đổi như thế nào?
5. Nêu một lý do cần tránh đệm số 0 tùy tiện khi dùng phần tiền xử lý STFT của mô hình đã huấn luyện sẵn.

### Gợi ý đáp án

1. Số tầng là \(\log_2 1024=10\). Ta có \(N\log_2 N=10240\) so với \(N^2=1048576\), chênh lệch khoảng 102 lần ở hạng bậc cao nhất.
2. Phổ của tín hiệu thực có tính đối xứng liên hợp nên thuật toán đóng gói bỏ qua nửa số bin dư thừa; điều này giảm khối lượng tính toán đi gần một nửa chứ không làm thay đổi lớp độ phức tạp tiệm cận.
3. Không cấp phát bộ nhớ trên audio thread, tái sử dụng FFT plan và biên dịch với hỗ trợ SIMD (đồng thời tránh tính lại bảng twiddle ở mỗi hop).
4. Số lượng hop mỗi giây tăng gấp đôi, nên khối lượng tính toán FFT mỗi giây cũng tăng gần gấp đôi khi \(N\) không đổi.
5. Đệm số 0 làm dịch tâm các bin tần số và thay đổi cấu trúc lưới mà trọng số đã học, khiến mô hình đọc sai giá trị Hz ứng với từng chỉ số bin.

## Đọc thêm

- Tổng quan họ thuật toán Cooley–Tukey và mục FFT trong sách Oppenheim & Schafer.
- Julius O. Smith, *Mathematics of the DFT*, https://ccrma.stanford.edu/~jos/mdft/ — khẳng định FFT là thuật toán tính nhanh DFT chứ không phải một phép biến đổi khác.
- Tài liệu toán tử STFT/DFT của ONNX khi triển khai với ONNX Runtime (ORT).

## Video tham khảo

- [The Fast Fourier Transform (FFT)](https://www.youtube.com/watch?v=E8HeD-MUrjY) — Steve Brunton, tiếng Anh. **Xem trước.** Đối chiếu phép nhân ma trận DFT dày đặc với phép phân tích thừa số của FFT, minh họa trực tiếp lập luận \(O(N\log N)\) trong bài.
- [The Fast Fourier Transform Algorithm](https://www.youtube.com/watch?v=toj_IoCQE-4) — Steve Brunton, tiếng Anh. Trình bày chi tiết bước tách radix-2 thành hai biến đổi nửa kích thước kèm thừa số xoay twiddle — nguồn gốc của hệ số logarit.
- [Computing the DFT Matrix](https://www.youtube.com/watch?v=Xw4voABxU5c) — Steve Brunton, tiếng Anh. Dùng làm mốc đối chiếu \(O(N^2)\) mà FFT phải giữ nguyên kết quả số học.
