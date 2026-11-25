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

**DeepFilterNet** (Schröter et al., ICASSP 2022, arXiv:2110.05588) là bộ tăng cường tiếng nói toàn băng tập trung dung lượng tính toán vào đường bao thính giác thô và một bộ lọc phức ngắn, thay vì dùng một mạng dày đặc trên toàn bộ 481 bin. Bài học này trình bày tường minh công thức tổng lọc sâu và chạy thử trên phổ mẫu hai tap, giúp bạn thực hành ngay cả khi không tải được trọng số đã huấn luyện sẵn.

![Sơ đồ hai tầng DeepFilterNet: gain ERB trên đường bao, deep filter trên hài tần số thấp]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. Tầng 1 dự đoán độ lợi thực trên 32 băng ERB (băng thông chữ nhật tương đương) rồi trải lên toàn bộ lưới STFT. Tầng 2 dự đoán bộ lọc phức 5 tap và chỉ áp dụng cho vùng tần số thấp, nơi tập trung phần lớn năng lượng tuần hoàn của tiếng nói; các bin cao hơn giữ nguyên độ lợi ERB.*

Nếu bạn muốn chạy tăng cường tiếng nói toàn băng $$48\text{ kHz}$$ theo thời gian thực ngay trên một nhân CPU laptop hay bên trong trình duyệt, bài toán khó nhất không phải là "làm sao đạt điểm chất lượng cao nhất", mà là **phân bổ ngân sách phép tính vào đúng chỗ tai người cần nhất**. Áp một mạng nơ-ron phức dày đặc lên toàn bộ $$481$$ bin tần số vừa tốn kém vừa lãng phí — bởi trên $$5\text{ kHz}$$, giọng người chủ yếu là nhiễu xát không tuần hoàn (như chữ "s", "f"), nơi tai người chỉ quan tâm đến đường bao năng lượng thô chứ không phân biệt nổi từng họa âm chi tiết. **DeepFilterNet** (Schröter và cộng sự, ICASSP 2022) tỏa sáng chính nhờ một thiết kế hai tầng bám sát sinh lý học thính giác: rẻ và thô cho toàn băng, sâu và phức cho vùng họa âm tần số thấp.

## Kiến thức cần nhớ: Thang thính giác ERB và bộ lọc phức đa khung (Deep Filtering)

### 1. Thang ERB (Equivalent Rectangular Bandwidth) — nén 481 bin về 32 băng thính giác
Ốc tai người không phân chia tần số đều nhau theo tuyến tính (Hz), mà có độ phân giải mịn ở tần số thấp và thô dần theo kiểu logarit ở tần số cao. Thang **ERB** mô hình hóa chính xác độ rộng bộ lọc thính giác đó: thay vì dự đoán $$481$$ độ lợi riêng lẻ, tầng 1 của DeepFilterNet chỉ dự đoán đúng **32 độ lợi thực** trên 32 băng ERB, sau đó nội suy ngược lên toàn bộ 481 bin. Chỉ riêng bước này đã dọn sạch phần lớn nhiễu băng rộng với chi phí tính toán cực nhỏ.

### 2. Deep Filtering — tổng quát hóa CRM từ 1 khung sang $$N$$ khung ($$N = 5$$)
Mặt nạ phức CRM (bài 04-01) chỉ nhân mỗi ô $$Y(t, k)$$ với **1** hệ số phức $$M(t, k)$$. Khi tiếng nói có cấu trúc tuần hoàn mạnh (các họa âm của nguyên âm kéo dài nhiều chục mili-giây), thông tin ở các khung lân cận $$t-2, t-1, t, t+1, t+2$$ chứa manh mối cực mạnh để tái tạo lại cả biên độ lẫn pha bị nhiễu che khuất. **Deep Filtering** (Mack & Habets, 2020) thay phép nhân đơn bằng một bộ lọc FIR phức bậc $$N$$ chạy dọc trục thời gian ngay trên từng bin tần số thấp:
$$\hat{S}(t, k) = \sum_{i=0}^{N-1} C_i(t, k)\, Y(t - i + l,\; k),$$
với $$l$$ là số khung nhìn trước (*look-ahead*, bằng $$2$$ khung trong cấu hình chuẩn).

### 3. Tính nhân quả và nguồn gốc chính xác của độ trễ thuật toán 40 ms
Trong xử lý thời gian thực, độ trễ thuật toán không phải là thời gian chạy CPU (RTF), mà là thời gian chờ tối thiểu do cấu trúc cửa sổ và nhìn trước quy định. Với STFT cửa sổ $$20\text{ ms}$$ ($$960$$ mẫu ở $$48\text{ kHz}$$), bước nhảy hop $$10\text{ ms}$$ ($$480$$ mẫu), và $$2$$ khung nhìn trước ($$2 \times 10\text{ ms} = 20\text{ ms}$$), tổng độ trễ thuật toán tối thiểu đúng bằng $$20 + 20 = 40\text{ ms}$$ — hoàn toàn nằm gọn trong ngân sách $$150\text{ ms}$$ của VoIP.

### Giải thích: Cầm tay đếm số tham số đầu ra và tính thử 1 bước Deep Filter phức 2 tap

**Phần A — Vì sao tách 2 tầng tiết kiệm gấp gần 5 lần đầu ra?**
Với STFT $$48\text{ kHz}$$, $$N_{\text{FFT}} = 960 \implies 481$$ bin tần số (mỗi bin rộng $$50\text{ Hz}$$):
- **Cách làm ngây thơ (5-tap phức trên cả 481 bin):**
  $$481\text{ bin} \times 5\text{ tap} \times 2\text{ (thực/ảo)} = 4\,810\text{ hệ số mỗi khung}.$$
- **Thiết kế 2 tầng của DeepFilterNet (32 ERB + 5-tap phức chỉ cho 96 bin thấp, tức $$0\text{–}4{,}8\text{ kHz}$$):**
  - Tầng 1 (ERB gain): $$32$$ hệ số thực.
  - Tầng 2 (Deep Filter dưới $$4{,}8\text{ kHz}$$): $$96 \times 5 \times 2 = 960$$ hệ số.
  - Tổng đầu ra mỗi khung: $$32 + 960 = 992\text{ hệ số}$$ — gọn hơn **$$4{,}85$$ lần** so với cách làm toàn băng!

**Phần B — Tự tay tính 1 bước Deep Filter phức 2 tap trên một bin tần số thấp $$k$$:**
Giả sử tại bin $$k$$ ta có hai khung đầu vào liên tiếp:
$$Y(t-1, k) = 1 + j, \qquad Y(t, k) = 2 - j,$$
và mạng nơ-ron dự đoán 2 hệ số lọc phức cho khung $$t$$ là:
$$c_{-1} = 0{,}5j, \qquad c_0 = 0{,}5 + 0{,}5j.$$
Áp dụng công thức tổng lọc sâu $$\hat{S}(t, k) = c_{-1} Y(t-1, k) + c_0 Y(t, k)$$:
1. Số hạng khung trước:
   $$c_{-1} Y(t-1, k) = 0{,}5j(1 + j) = 0{,}5j + 0{,}5j^2 = -0{,}5 + 0{,}5j.$$
2. Số hạng khung hiện tại:
   $$c_0 Y(t, k) = (0{,}5 + 0{,}5j)(2 - j) = 1{,}0 - 0{,}5j + 1{,}0j - 0{,}5j^2 = 1{,}5 + 0{,}5j.$$
3. Cộng hai số hạng phức:
   $$\hat{S}(t, k) = (-0{,}5 + 1{,}5) + (0{,}5 + 0{,}5)j = 1{,}0 + 1{,}0j.$$

Chỉ với hai phép nhân phức và một phép cộng, bộ lọc sâu đã vừa tổng hợp năng lượng từ khung trước, vừa xoay góc pha của bin hiện tại về đúng pha sạch mà mặt nạ thực không bao giờ làm được.

## Mục tiêu học tập

Sau bài học này, bạn sẽ tính được trực tiếp một bước áp độ lợi ERB và một tổng lọc sâu đa khung trên bin phức; giải thích được vì sao bộ lọc 5 tap dưới ngưỡng khoảng 5 kHz nhẹ hơn nhiều so với CRM trên toàn bộ các bin ở 48 kHz; nêu đúng cấu hình STFT công bố (cửa sổ 20 ms, hop 10 ms) cùng độ trễ thuật toán 40 ms (gồm 2 khung nhìn trước); và chạy được công cụ CLI `deepFilter` hoặc kịch bản NumPy thay thế.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao cả 481 bin ở 48 kHz không cần chung một ngân sách phép nhân-cộng (MAC).
- **10–25 phút** — Tầng ERB: dự đoán 32 độ lợi thực và phép nhân theo điểm.
- **25–40 phút** — Tổng lọc sâu (deep filter) so với độ lợi Wiener hay CRM một tap.
- **40–50 phút** — Độ nhìn trước (look-ahead), tính nhân quả và kho mã nguồn chính thức.
- **50–60 phút** — Mini-lab (CLI hoặc NumPy) và bài tập.

## Giải thích cốt lõi

### Kiến trúc hai tầng với các thông số công bố

Tai người phân giải tần số tinh hơn ở dải tần thấp, và DeepFilterNet khai thác đặc tính này ở cả hai tầng:

1. **Tầng đường bao.** Dãy lọc ERB dạng chữ nhật nén phổ log-công suất xuống $$N_{\mathrm{ERB}}=32$$ băng. Mạng dự đoán 32 hệ số độ lợi thực, dãy lọc nghịch trải các độ lợi này lên các bin STFT rồi nhân với phổ nhiễu. Đầu vào đặc trưng được chuẩn hóa theo trung bình trượt hàm mũ với hằng số suy giảm 1 giây, nhờ đó sự thay đổi đột ngột độ lợi micro không bị nhận nhầm thành nhiễu mới.
2. **Tầng thành phần tuần hoàn.** Bộ lọc phức 5 tap chỉ hoạt động tới ngưỡng $$f_{\mathrm{DF}}=5$$ kHz (trong bài báo ICASSP và DeepFilterNet2). Bản demo năm 2023 (arXiv:2305.08227) nêu rõ phạm vi là 96 bin thấp nhất: với FFT 960 điểm ở 48 kHz (bước bin 50 Hz), ta có $$96\times 50\,\mathrm{Hz}=4{,}8$$ kHz. Trên ngưỡng này, đầu ra chỉ sử dụng độ lợi ERB.

Các bảng thực nghiệm sử dụng tần số 48 kHz, $$N_{\mathrm{FFT}}=960$$ (20 ms) và chồng lấp 50% (hop 480 mẫu = 10 ms). DeepFilterNet2 và bản demo 2023 dùng 2 khung nhìn trước, đạt **độ trễ thuật toán 40 ms**. Công thức độ trễ trong bài báo ICASSP bằng độ trễ cửa sổ cộng $$\max(l_{\mathrm{DNN}}, l_{\mathrm{DF}})$$, với cấu hình huấn luyện $$l_{\mathrm{DNN}}=2$$ và $$l_{\mathrm{DF}}=1$$. Các khung tương lai này là độ trễ cố hữu cần được cộng đủ trước khi đánh giá khả năng thời gian thực.

Trên bảng kết quả VCTK/DEMAND của bài báo ICASSP, mô hình đầy đủ có 1,778 triệu tham số và 0,348 GMAC/s, đạt WB-PESQ 2,81 và SI-SDR 16,63 dB. Khi bỏ tầng 2, mô hình còn 0,885 triệu tham số và 0,251 GMAC/s, với PESQ giảm xuống 2,57 và SI-SDR xuống 13,81 dB. Tầng 2 chiếm xấp xỉ nửa số tham số nhưng đảm nhiệm phần lớn khả năng khôi phục cấu trúc họa âm.

### Bộ lọc sâu khác với mặt nạ một tap

Mặt nạ một tap (kể cả độ lợi Wiener dưới mô hình Gauss) chỉ là phép nhân trên cùng một khung:

$$
\hat{S}(k,\ell)=M(k,\ell)\,Y(k,\ell).
$$

Ngược lại, kỹ thuật lọc sâu (deep filtering — Mack & Habets, tiếp nối nhánh lọc tuyến tính phức CLC) dự đoán các hệ số tap $$W_i$$ và tổ hợp một đoạn lịch sử ngắn theo thời gian. Với bộ lọc 5 tap và độ nhìn trước tùy chọn $$\ell$$:

$$
\hat{S}(t,f)=\sum_{i=0}^{4} W_i(t,f)\,X(t-i+\ell,f).
$$

Bài báo ICASSP đánh chỉ số bậc $$N=5$$ theo tổng $$\sum_{i=0}^{N}$$, còn bản demo 2023 viết vector $$N=5$$ hệ số $$W_0,\ldots,W_{N-1}$$. Dù theo quy ước chỉ số nào, bản chất vẫn là một bộ lọc FIR theo trục thời gian cho từng bin chứ không phải một phép nhân đơn lẻ. Phần Mini-lab bên dưới sử dụng hai tap để phép tính gọn trong một dòng; ba tap còn lại tuân theo đúng cấu trúc tương tự.

Nhờ các hệ số phức kết hợp với khung quá khứ, bộ lọc sâu có thể xoay và chỉnh pha trên từng bin — điều mặt nạ biên độ không làm được. Vì có nhiều tập hệ số tap khác nhau cùng tạo ra một phổ đầu ra tương đương, bài báo huấn luyện mô hình trực tiếp bằng hàm mất mát phổ nén từ bài 04-01 ($$c=0{,}6$$) thay vì ép khớp một bộ lọc lý tưởng dạng đóng. Mô hình ICASSP cũng học thêm trọng số pha trộn $$\alpha(k)$$ giữa đầu ra deep filter và đầu ra ERB, trong khi bản demo 2023 chuyển sang cơ chế cổng SNR (bài 04-03) — cần phân biệt hai cơ chế này thay vì gộp chung.

### Vì sao chi phí MAC giảm mạnh

Bộ giải mã đường bao chỉ cần xuất 32 độ lợi thay vì 481 (tỷ lệ $$32/481\approx 0{,}067$$). Tầng tinh chỉ tính bộ lọc phức 5 tap trên 96 bin thấp thay vì CRM trên toàn phổ. Ngoài ra, mạng ICASSP chia các lớp tuyến tính và GRU thành $$P=8$$ nhóm với kích thước ẩn $$512/8=64$$. Tên gọi các lớp có thể thay đổi giữa các phiên bản, nhưng nguyên lý phân bổ ngân sách tính toán này vẫn giữ nguyên.

### Tính nhân quả và kho mã nguồn

Các tap lọc chỉ được phép truy cập các khung nằm trong giới hạn nhìn trước đã khai báo. Trạng thái ẩn của GRU, bộ chuẩn hóa trượt 1 giây và bộ đệm các khung phổ quá khứ đều là trạng thái streaming (bài 05-04); việc xóa chúng giữa cuộc gọi sẽ gây tiếng lách tách hoặc lọt một đoạn nhiễu ngắn.

Cấu hình và trọng số chính thức nằm tại [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet). Công cụ dòng lệnh `deepFilter` trong gói `deepfilternet` mặc định sử dụng trọng số DeepFilterNet3, còn bản biên dịch Rust `deep-filter` yêu cầu tệp WAV 48 kHz. Gói npm `deepfilternet3-noise-filter` ([mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression)) chạy đồ thị ONNX/WASM trong AudioWorklet (`DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`) và không cam kết khớp từng bit với CLI.

## Danh mục kiểm tra trước khi gọi một hệ thống là DeepFilterNet

1. STFT toàn băng 48 kHz, không phải mô hình ngoại tuyến 16 kHz.
2. Dự đoán 32 độ lợi ERB cho tầng đường bao.
3. Áp dụng bộ lọc phức nhiều tap chỉ trên dải bin tần số thấp.
4. Tính đủ độ nhìn trước vào độ trễ thuật toán 40 ms, tách biệt khỏi RTF.
5. Bảo toàn trạng thái nhân quả xuyên suốt các hop.
6. Cố định phiên bản trọng số bằng tên tệp hoặc mã commit trước khi xuất đồ thị (Chương 06).

## Bẫy thường gặp

- Gọi chung mọi mạng tạo mặt nạ là "DeepFilterNet".
- Áp bộ lọc 5 tap lên cả 481 bin rồi thắc mắc vì sao chi phí GMAC tăng vọt.
- Đo PESQ ở 16 kHz rồi gán nhầm vào bảng đánh giá 48 kHz.
- Quên độ dài cửa sổ 20 ms khi chỉ nhìn thông số "khung/hop 10 ms".
- Dùng lẫn checkpoint của DF, DF2 và DF3 trên cùng một tệp cấu hình (xem bài tiếp theo).

## Mini-lab

**Mục tiêu.** Chạy tăng cường tiếng nói cho một tệp âm thanh bằng CLI chính thức; trường hợp không tải được trọng số, thực hiện trực tiếp một tổng lọc sâu hai tap bằng NumPy để đối chiếu với mặt nạ một tap.

```bash
pip install deepfilternet
deepFilter --output-dir out/ noisy.wav
```

Các cờ dòng lệnh đã được tài liệu hóa gồm: `--model-base-dir` (trỏ tới trọng số cục bộ), `--pf` (bật post-filter, bài 04-03), `--output-dir` và `--compensate-delay`. Lưu ý bản Rust `deep-filter` yêu cầu đầu vào WAV 48 kHz.

Kịch bản chạy ngoại tuyến (hai tap của tổng lọc sâu):

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

**Kết quả kỳ vọng.** Với CLI: tạo ra tệp WAV đã khử nhiễu trong `out/` kèm dòng log thời gian chạy hoặc RTF. Với kịch bản NumPy: luôn in ra kết quả deep filter `(0.8+0.35j)`, mặt nạ một tap `(0.8+0.4j)`, và biên độ lần lượt khoảng `0.873212` với `0.894427`. Phần ảo thay đổi nhờ hệ số $$H_1$$ khai thác khung quá khứ $$Y_{\mathrm{prev}}$$ — điều mặt nạ đơn điểm không thực hiện được.

**Lỗi thường gặp.** Thiếu kết nối mạng khiến CLI không tải được trọng số (hãy giữ kết quả NumPy và ghi nhận lỗi, không tự tạo tệp WAV giả); đưa tệp không phải 48 kHz vào bản Rust; lấy RTF đo trên laptop làm RTF điện thoại; hoặc quên cờ `--output-dir` rồi tìm nhầm thư mục đầu ra.

## Bài tập

1. **Đối chiếu công thức.** Viết cạnh nhau công thức độ lợi Wiener một tap và tổng lọc sâu 5 tap; chỉ rõ đại lượng nào do mạng học và đại lượng nào do bộ theo dõi nhiễu cổ điển ước lượng.
2. **Tính số bin.** Ở 48 kHz với FFT 960 điểm, ngưỡng 4,8 kHz tương ứng chỉ số bin cuối cùng là bao nhiêu? Với bộ lọc 5 tap, mỗi khung có bao nhiêu hệ số tap phức?
3. **Ước lượng MAC.** Đầu ra tầng đường bao chỉ có 32 giá trị thay vì 481. Hãy tính tỷ số này và giải thích vì sao tỷ số đó chưa phản ánh toàn bộ chi phí GMAC.
4. **Kiểm tra độ trễ.** Với hop 10 ms, nhìn trước 2 khung và cửa sổ 20 ms, độ trễ thuật toán là bao nhiêu? Cờ CLI nào chỉ dịch căn chỉnh tệp đầu ra chứ không loại bỏ độ trễ này?

### Gợi ý đáp án

1. Lọc Wiener dùng $$M=\xi/(\xi+1)$$ (một phép nhân duy nhất, với $$\xi$$ ước lượng từ bộ theo dõi nhiễu); deep filter dùng năm hệ số phức $$W_i$$ do mạng dự đoán để tính tích vô hướng với năm khung $$X$$. Đại lượng học được là $$W_i$$ và độ lợi ERB; hệ cổ điển ước lượng $$\xi$$ hoặc PSD nhiễu.
2. Bước bin là 50 Hz nên bin thứ 96 nằm tại 4,8 kHz (đúng với "96 bin thấp nhất" trong demo 2023), tương ứng $$96\times 5=480$$ hệ số tap phức mỗi khung trước khi áp một độ lợi thực cho các bin cao hơn.
3. Tỷ số là $$32/481\approx 0{,}0665$$, nhưng chưa bao gồm chi phí STFT, bước trải ngược ERB và phép nhân 5 tap trên 96 bin. Bài DeepFilterNet2 còn cho thấy cách nhóm lớp và kích thước kernel làm thay đổi mạnh RTF thực tế ngay cả khi GMAC gần như không đổi.
4. Độ trễ thuật toán là 40 ms. Cờ `--compensate-delay` chỉ căn chỉnh lại thời gian trên tệp để chấm điểm ngoại tuyến chứ không thể xóa bỏ look-ahead trong cuộc gọi thời gian thực.

## Đọc thêm

- Schröter et al., ICASSP 2022, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) — độ lợi ERB, deep filtering và bảng số liệu 1,778 M tham số / 0,348 GMAC.
- Mack & Habets, “Deep Filtering,” *IEEE Signal Processing Letters*, 2020 — nền tảng bộ lọc phức đa khung được DeepFilterNet kế thừa.
- README tại [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) cho hướng dẫn CLI `deepFilter` và model card.
- Bài tiếp theo: những thay đổi cốt lõi của DeepFilterNet2 và trích dẫn năm 2023 gắn với DeepFilterNet3.

## Video tham khảo

- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. **Xem trước.** Trình bày trực tiếp cơ chế tách tầng đường bao ERB và tầng lọc sâu phức trên các bin thấp.
- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, tiếng Anh. Nên nghe ngay sau khi xem sơ đồ để gắn hai tầng xử lý với cảm nhận âm thanh thực tế.
- [RNNoise, Neural Speech Enhancement, and the Browser](https://www.youtube.com/watch?v=nsscrYdrGRE) — W3C, tiếng Anh. Hữu ích để đối chiếu mô hình độ lợi theo băng đơn giản với bộ lọc phức đa khung trong bài.
