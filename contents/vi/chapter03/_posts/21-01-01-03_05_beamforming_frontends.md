---
layout: post
title: "03-05 Beamforming / GSC / IVA như front-end"
chapter: "03"
order: 5
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter03
lesson_type: required
draft: false
---

Khi thiết bị có **từ hai micro trở lên**, hình học mảng thu mang lại một lợi thế mà khử nhiễu đơn kênh không có: khả năng chọn lọc theo hướng không gian. Beamforming, bộ triệt búp phụ tổng quát (Generalized Sidelobe Canceller, GSC) và phân tích vector độc lập (Independent Vector Analysis, IVA) là các tầng tiền xử lý đa kênh cổ điển có thể cung cấp đầu vào sạch hơn cho bộ khử nhiễu mạng nơ-ron đơn kênh. Bài học này trình bày trực giác kỹ thuật về delay-and-sum, MVDR giản lược, ma trận chặn của GSC, IVA theo hướng tách nguồn mù, cùng các mô hình lai như GSC+DeepFilterNet2 hay IVA+GTCRN trong bối cảnh SNR thấp, drone hoặc thiết bị hai micro (ở mức định hướng khảo sát).

Tại sao con người lại có **hai** cái tai thay vì một? Không phải để nghe to gấp đôi, mà để biến *hình học không gian* thành một bộ lọc vật lý: một âm thanh phát ra từ bên phải sẽ chạm vào tai phải sớm hơn tai trái khoảng vài trăm micro-giây. Khi một chiếc laptop, điện thoại hay loa thông minh sở hữu từ hai micro trở lên, ta có thể làm điều tương tự bằng toán học: tạo ra một "đèn pin âm học" chiếu thẳng vào miệng người nói và đẩy tiếng quạt hay tiếng người nói chuyện bên cạnh vào vùng tối — kỹ thuật gọi là **tạo búp sóng (beamforming)**.

## Kiến thức cần nhớ: Mảng micro, hình học sóng phẳng và lọc không gian

### 1. Độ trễ thời gian đến (TDOA) và Vector lái hướng (Steering Vector)
Với hai micro đặt cách nhau khoảng cách $$d$$ trong không khí (tốc độ âm thanh $$c \approx 343\text{ m/s}$$), một sóng phẳng đến từ góc lệch $$\theta$$ so với phương trực diện phải đi thêm quãng đường $$\Delta r = d \sin\theta$$ để tới micro thứ hai, tạo ra độ trễ $$\Delta\tau = \frac{d \sin\theta}{c}$$. Trên miền tần số $$f$$, độ trễ thời gian biến thành phép xoay pha $$e^{-j 2\pi f \Delta\tau}$$. Xếp pha của tất cả $$M$$ micro thành một cột ta thu được **vector lái hướng** $$\mathbf{a}(\theta, f)$$.

### 2. Từ Delay-and-Sum đến MVDR và cấu trúc GSC
- **Delay-and-Sum (DSB):** đơn giản bù lại đúng độ trễ của hướng mục tiêu $$\theta_s$$ rồi cộng trung bình các micro. Tín hiệu mục tiêu cộng đồng pha nên giữ nguyên biên độ, còn nhiễu từ hướng khác lệch pha nên tự triệt tiêu một phần.
- **MVDR (Minimum Variance Distortionless Response):** tối ưu vector trọng số phức $$\mathbf{w}(f)$$ để cực tiểu hóa tổng công suất nhiễu đầu ra $$\mathbf{w}^H \mathbf{R}_{vv} \mathbf{w}$$ với ràng buộc giữ nguyên hướng mục tiêu $$\mathbf{w}^H \mathbf{a}(\theta_s, f) = 1$$.
- **GSC (Generalized Sidelobe Canceller):** viết lại bài toán tối ưu có ràng buộc MVDR thành hai nhánh song song dễ chạy thời gian thực: nhánh trên cố định hướng vào người nói, nhánh dưới dùng *ma trận chặn (blocking matrix)* xóa người nói để chỉ lấy nhiễu tham chiếu rồi trừ dần khỏi nhánh trên.

### 3. Tách nguồn mù đa kênh (IVA) và giới hạn vật lý của mảng nhỏ
Khi không biết trước hướng người nói, **IVA (Independent Vector Analysis)** khai thác giả định các nguồn âm độc lập thống kê nhau và liên kết các tần số của cùng một nguồn để tránh hoán vị tần số (*permutation problem*). Tuy nhiên, vật lý sóng đặt ra một giới hạn cứng: khi bước sóng âm thanh $$\lambda = c/f$$ lớn hơn nhiều so với khoảng cách micro $$d$$ (ở tần số trầm), lệch pha giữa hai micro quá bé nên beamforming đơn thuần suy giảm mạnh — đó là lý do các hệ thống hiện đại ghép tiền xử lý không gian với hậu lọc mạng nơ-ron đơn kênh.

### Giải thích: Cầm tay tính độ trễ TDOA và kiểm tra "điểm mù tần số trầm" của mảng 2 micro laptop

Xét một chiếc laptop có 2 micro đặt cách nhau $$d = 4\text{ cm} = 0{,}04\text{ m}$$, tốc độ âm thanh $$c = 343\text{ m/s}$$, tần số lấy mẫu $$f_s = 48\,000\text{ Hz}$$.
- Người nói ngồi chính diện trước màn hình: $$\theta_s = 0^\circ \implies \Delta\tau_s = 0$$.
- Một nguồn nhiễu (quạt hoặc người nói chuyện) nằm lệch góc $$\theta_n = 30^\circ$$:
  - Quãng đường chênh lệch: $$\Delta r = d \sin 30^\circ = 0{,}04 \times 0{,}5 = 0{,}02\text{ m}$$.
  - Độ trễ thời gian đến (TDOA): $$\Delta\tau_n = \frac{0{,}02}{343} \approx 58{,}3\,\mu\text{s}$$ (tương đương $$58{,}3 \times 10^{-6} \times 48\,000 \approx 2{,}8$$ mẫu!).

Ta dùng bộ Delay-and-Sum hướng thẳng $$0^\circ$$: $$y(t) = \frac{1}{2}[x_1(t) + x_2(t)]$$. Biên độ đáp ứng theo tần số cho nguồn có độ trễ $$\Delta\tau$$ là:
$$\vert H(f) \vert = \left\vert \frac{1 + e^{-j 2\pi f \Delta\tau}}{2} \right\vert = \vert \cos(\pi f \Delta\tau) \vert.$$

Hãy thay số trực tiếp ở 2 tần số để thấy sức mạnh và điểm yếu của mảng 2 micro:
1. **Tại tần số cao $$f = 8\,575\text{ Hz}$$:**
   $$\pi f \Delta\tau_n = \pi \times 8\,575 \times \frac{0{,}02}{343} = \frac{\pi}{2}\text{ rad} \implies \vert H(8\,575\text{ Hz}) \vert = \left\vert \cos\!\left(\frac{\pi}{2}\right) \right\vert = 0.$$
   Sóng nhiễu đến hai micro ngược pha nhau hoàn toàn ($$180^\circ$$) và **tự triệt tiêu $$100\%$$** trong khi tiếng nói chính diện ($$\Delta\tau_s = 0$$) vẫn giữ nguyên độ lợi $$1{,}0$$!
2. **Tại tần số trầm $$f = 500\text{ Hz}$$ (vùng năng lượng chính của giọng nói và tiếng ù):**
   $$\pi f \Delta\tau_n \approx \pi \times 500 \times 58{,}3 \times 10^{-6} \approx 0{,}0916\text{ rad} \implies \vert H(500\text{ Hz}) \vert = \cos(0{,}0916) \approx 0{,}996 \quad (-0{,}04\text{ dB}).$$
   Nhiễu $$500\text{ Hz}$$ gần như đi qua nguyên vẹn vì bước sóng $$\lambda = 343/500 = 68{,}6\text{ cm}$$ quá dài so với khoảng cách micro $$4\text{ cm}$$. Con số $$0{,}996$$ này giải thích trọn vẹn vì sao mảng 2 micro trên laptop không bao giờ thay thế được tầng khử nhiễu đơn kênh (như DeepFilterNet) ở dải tần thấp!

## Mục tiêu học tập

Sau bài học này, bạn sẽ giải thích được mục tiêu của delay-and-sum và MVDR bằng ngôn ngữ trực quan, phác thảo cấu trúc GSC (beamformer cố định + ma trận chặn + bộ hủy nhiễu thích nghi), tóm tắt vai trò tách nguồn mù đa kênh của IVA, và xác định khi nào kết hợp tầng tiền xử lý không gian với DeepFilterNet đơn kênh hiệu quả hơn chạy NS đơn kênh thuần túy.

## Kế hoạch 60 phút

- **0–10 phút** — Tình huống mở đầu với laptop 2 micro: tách người nói mục tiêu khỏi nguồn nhiễu ở hướng khác.
- **10–25 phút** — Vector lái hướng (steering vector), delay-and-sum và bài toán tối ưu MVDR.
- **25–40 phút** — Cấu trúc GSC và vai trò triệt nhiễu của nhánh thích nghi.
- **40–50 phút** — Định hướng IVA / tách nguồn mù (BSS) và kiến trúc lai tiền xử lý không gian + tinh chỉnh mạng nơ-ron.
- **50–60 phút** — Các bẫy thường gặp, bài tập và thực tế sản phẩm (Mezon chủ yếu vẫn xử lý mono).

## Giải thích cốt lõi

### Mô hình không gian (xấp xỉ trường xa)

Với mảng gồm $$m=1\ldots M$$ micro, một sóng phẳng đến từ hướng $$\theta$$ tại tần số $$f$$ được đặc trưng bởi **vector lái hướng (steering vector)** $$\mathbf{a}(\theta,f)$$. Vector phổ xếp chồng từ các micro có dạng:

$$
\mathbf{y}(f,\ell)=\mathbf{a}(\theta,f)\,S(f,\ell)+\mathbf{v}(f,\ell).
$$

Đầu ra của beamformer tuyến tính là tổ hợp phức $$Z=\mathbf{w}^H\mathbf{y}$$.

### Delay-and-sum

Phương pháp này bù độ trễ (dịch pha) giữa các micro sao cho tín hiệu từ hướng mục tiêu cộng đồng pha rồi lấy trung bình. Kỹ thuật này cải thiện tốt với nhiễu **không tương quan (incoherent)**, còn nhiễu giao thoa **tương quan (coherent)** đến từ hướng khác chỉ giảm một phần. Đây là mốc đối chiếu nền tảng rất hữu ích khi giảng dạy và kiểm thử.

### Mô hình giản lược MVDR

$$
\min_{\mathbf{w}}\mathbf{w}^H\mathbf{R}_{yy}\mathbf{w}\quad\text{s.t.}\quad\mathbf{w}^H\mathbf{a}=1.
$$

Nghiệm chuẩn hóa $$\mathbf{w}\propto\mathbf{R}_{yy}^{-1}\mathbf{a}$$ giữ nguyên độ lợi ở hướng mục tiêu đồng thời hướng vùng triệt tiêu (null) về phía nguồn nhiễu giao thoa. Thách thức lớn nhất trong thực tế là ước lượng ổn định ma trận hiệp phương sai $$\mathbf{R}$$: chỉ cần lệch hướng lái (steering mismatch) sẽ dẫn tới **tự triệt tiêu chính tín hiệu mục tiêu**.

### Cấu trúc GSC

1. **Fixed beamformer (FBF)** — hướng búp chính về phía người nói mục tiêu.
2. **Blocking matrix (BM)** — chiếu vuông góc để loại bỏ tín hiệu mục tiêu, tạo ra tín hiệu tham chiếu "chỉ gồm nhiễu".
3. **Adaptive noise canceler** — dùng bộ lọc thích nghi NLMS/RLS để trừ phần nhiễu ước lượng từ nhánh BM khỏi đầu ra của FBF.

**Ưu điểm của GSC:** Nhánh thích nghi hoạt động không ràng buộc trên tín hiệu tham chiếu nhiễu và rất dễ kết hợp với VAD để đóng băng cập nhật mỗi khi người nói mục tiêu lên tiếng.

### IVA (định hướng khảo sát)

**IVA** và các kỹ thuật tách nguồn mù (BSS) liên quan tách các nguồn âm từ hỗn hợp đa micro dựa trên tính độc lập thống kê mà không cần biết trước vector lái hướng tường minh. Ở phạm vi khóa học này, hãy nắm hai ý chính:

- Xem IVA như một **tầng tiền xử lý không gian mù** tạo ra ước lượng sơ bộ cho tín hiệu mục tiêu và nguồn nhiễu giao thoa.
- Dùng một mạng gọn nhẹ (nhóm GTCRN) phía sau để tinh chỉnh đầu ra của IVA — đây là mẫu thiết kế phổ biến trong các bài báo xử lý hai kênh ở SNR thấp.

### Kiến trúc lai kết hợp mạng nơ-ron đơn kênh

- **GSC → DeepFilterNet2**: hủy nhiễu có hướng (như tiếng cánh quạt drone) ở tầng không gian, sau đó DeepFilterNet2 dọn phần nhiễu khuếch tán còn sót.
- **IVA → GTCRN**: tách nguồn mù đa kênh rồi tinh chỉnh bằng mạng CRN gọn nhẹ.
- **Chỉ dùng DF3 đơn kênh**: lựa chọn mặc định hợp lý khi $$M=1$$ (phần lớn các tab trình duyệt).

**Ghi chú về Mezon:** Đường tích hợp npm/WASM mặc định là **đơn kênh (mono)**. Xử lý đa micro thuộc phần mở rộng — học các tầng tiền xử lý không gian giúp bạn thiết kế pipeline ứng dụng native về sau mà không phải viết lại lõi mạng nơ-ron. Trong kiến trúc đó, beamformer đóng vai trò bộ lọc không gian đặt trước bộ xử lý đơn kênh: nhận nhiều micro, xuất ra một kênh duy nhất rồi mới đi vào bộ khử nhiễu theo bin. Hình dưới minh họa luồng xuất bản đơn kênh của sản phẩm (không chứa beamformer); nếu bổ sung, beamformer sẽ nằm ngay phía trước `DeepFilterNoiseFilterProcessor`.

![Đường publish LiveKit qua DeepFilterNoiseFilterProcessor một kênh, chặng mà beamformer sẽ phải nuôi]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Hình. Sơ đồ luồng xuất bản đơn kênh; beamformer không nằm trong sơ đồ này mà sẽ đứng ngay trước `DeepFilterNoiseFilterProcessor` để bộ xử lý vẫn chỉ nhận đúng một kênh đầu vào.*

## Danh mục quyết định nhanh

- $$M=1$$ → dùng NS đơn kênh (cổ điển hoặc mạng nơ-ron), bỏ qua beamforming.
- $$M\ge 2$$, biết rõ hướng mục tiêu và có nhiễu định hướng mạnh → chọn GSC hoặc MVDR.
- $$M\ge 2$$, không rõ hình học mảng hoặc người nói di chuyển → cân nhắc IVA hoặc beamforming thích nghi bền vững kết hợp mạng nơ-ron.
- Ngân sách CPU rất hẹp → kết hợp delay-and-sum đơn giản với NS siêu nhẹ thay vì chạy IVA đầy đủ.
- Lưu ý `getUserMedia` đôi khi đã bị hệ điều hành gộp sẵn thành mono — luôn kiểm tra số kênh thực tế nhận được.

## Bẫy thường gặp

- Lệch vector lái hướng → **tự triệt tiêu tiếng nói mục tiêu** (nghe giống như NS cắt mất giọng).
- Để GSC thích nghi ngay lúc mục tiêu đang nói mà thiếu VAD → tiếng nói rò vào ma trận chặn BM và bị xóa ngược lại.
- Mặc định cặp micro stereo trên laptop đã được hiệu chuẩn chính xác về mặt hình học.
- Tính STFT đa kênh trên các micro bị lệch đồng hồ hoặc lệch trễ kênh (như thiết bị USB riêng lẻ).
- Kỳ vọng beamforming tự xử lý được **tiếng vọng** mà không cần tham chiếu far-end — hệ thống vẫn bắt buộc phải có AEC.

## Mini-lab

**Mục tiêu.** Tính độ trễ truyền âm trường xa giữa hai micro đặt cách nhau 2 cm tại góc thẳng đứng (broadside, 0°) và góc nghiêng 45°.

```python
import numpy as np

d, c, fs = 0.02, 343.0, 48000  # mét, m/s, Hz
for deg in (0, 45):
    tau = d * np.sin(np.deg2rad(deg)) / c
    print(deg, "deg", round(tau * 1e6, 1), "us", round(tau * fs, 2), "samples")
```

**Kết quả kỳ vọng.** Tại góc broadside (0°): `0.0 µs`, tương đương `0.0` mẫu. Tại góc 45°: khoảng `41.2 µs`, tương đương khoảng `1.98` mẫu ở 48 kHz. Có thể thấy delay-and-sum ở 48 kHz đòi hỏi phép dịch phân số mẫu (fractional delay) chứ không phải bộ lọc nhiều tap cỡ cả căn phòng.

**Lỗi thường gặp.** Truyền trực tiếp đơn vị độ vào `np.sin` mà quên đổi sang radian sẽ cho kết quả vô nghĩa (góc 45° không còn gần 2 mẫu); quên nhân \(\sin\theta\) và lấy \(d/c\) cho mọi góc sẽ làm góc broadside cho kết quả giống góc dọc trục (endfire); nếu đổi sang 16 kHz thì góc 45° chỉ tương ứng khoảng 0.66 mẫu, nên giả định 48 kHz phải được thể hiện rõ trong mã nguồn.

## Bài tập

1. Với mảng 2 micro cách nhau $$d=2\,\mathrm{cm}$$, tần số $$f=2\,\mathrm{kHz}$$ và tốc độ âm thanh $$c=343\,\mathrm{m/s}$$, hãy tính độ trễ giữa hai micro ở góc broadside và góc 45°.
2. Vẽ sơ đồ khối GSC và đánh dấu rõ vị trí gắn bộ hậu lọc mạng nơ-ron.
3. Viết bản tóm tắt thiết kế dài một trang cho chế độ hai micro trên ứng dụng native: tái sử dụng mô hình DF3 ONNX đơn kênh và chỉ bổ sung thêm delay-and-sum ở phía trước.
4. Đọc tóm tắt (abstract) của một bài báo kiến trúc lai (GSC+DF2 hoặc IVA+GTCRN) và tóm lược trong 3 gạch đầu dòng phần đóng góp của tầng cổ điển so với tầng mạng nơ-ron.

### Gợi ý đáp án

1. Độ trễ ở góc broadside bằng 0; ở góc 45°, \(\tau=d\sin\theta/c\approx 41.2\,\mu\mathrm{s}\), tương đương gần 2 mẫu ở 48 kHz.
2. Bộ hậu lọc mạng nơ-ron được gắn ngay sau đầu ra đơn kênh của GSC (sau phép trừ của nhánh thích nghi).
3. Delay-and-sum gộp hai tín hiệu micro thành một dạng sóng đơn kênh duy nhất, nên đồ thị ONNX mono hiện có không cần thêm đầu vào thứ hai.
4. Tầng cổ điển khai thác thông tin không gian từ nhiều micro (tạo hướng triệt tiêu hoặc dùng tính độc lập thống kê), còn tầng mạng nơ-ron vẫn đóng vai trò bộ tăng cường đơn kênh xử lý phần nhiễu dư lọt qua tầng không gian.

## Đọc thêm

- Van Trees, *Optimum Array Processing*.
- Griffiths & Jim — bài báo kinh điển về cấu trúc GSC.
- Tài liệu kỹ thuật xử lý đa micro của WebRTC và thiết bị di động.
- Các mốc tham khảo kiến trúc lai: GSC–DeepFilterNet2 và IVA+GTCRN (ở mức khái niệm).
- DeepFilterNet2 — ví dụ điển hình cho tầng mạng nơ-ron đơn kênh đặt *sau* khâu lọc không gian.

## Video tham khảo

- [What is Beamforming? ("the best explanation I’ve ever heard")](https://www.youtube.com/watch?v=A1n5Hhwtz78) — Iain Explains Signals, Systems, and Digital Comms, tiếng Anh. **Xem trước.** Minh họa cách căn chỉnh độ trễ theo một hướng trước khi cộng tín hiệu — đúng trực giác hình học của delay-and-sum làm nền cho GSC và IVA.
