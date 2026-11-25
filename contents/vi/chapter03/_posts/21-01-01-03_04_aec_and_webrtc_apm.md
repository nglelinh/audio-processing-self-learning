---
layout: post
title: "03-04 Ngữ cảnh AEC và WebRTC APM"
chapter: "03"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter03
lesson_type: required
draft: false
---

Khử tiếng vọng âm học (Acoustic Echo Cancellation, AEC) là bài toán đi liền với khử nhiễu: ở đây, thành phần gây nhiễu là bản sao đã qua lọc của **tín hiệu đầu xa (far-end)** phát ra từ loa rồi dội ngược vào micro. Các hệ thống VoIP trên trình duyệt và ứng dụng native hầu như luôn chạy AEC **trước** hoặc **song song** với NS bên trong khối xử lý âm thanh. Bài học này đặt AEC vào đúng vị trí trong đồ thị cuộc gọi, phác thảo nguyên lý triệt vọng bằng bộ lọc thích nghi và giới thiệu **WebRTC Audio Processing Module (APM)** như tiêu chuẩn công nghiệp bạn sẽ gặp khi tích hợp Mezon, LiveKit hoặc trình duyệt (Chương 07).

Trong một cuộc gọi video không dùng tai nghe, không có gì gây ức chế bằng việc vừa nói xong nửa câu thì nghe chính giọng mình dội ngược lại sau nửa giây. Nếu khử nhiễu (NS) là bài toán "mù" — bạn không hề có bản ghi riêng của tiếng quạt hay tiếng xe cộ — thì **khử tiếng vọng âm học (AEC)** lại có một lợi thế vàng: thiết bị của bạn *biết chính xác* tín hiệu đầu xa $$x[t]$$ mà nó vừa đẩy ra loa! Nhiệm vụ của AEC vì thế trở thành bài toán nhận dạng hệ thống theo thời gian thực: học bản sao đường truyền phòng $$\hat{\mathbf{h}}$$, tự tổng hợp tiếng vọng dự đoán rồi trừ thẳng trước khi giọng nói đi vào tầng khử nhiễu.

## Kiến thức cần nhớ: Nhận dạng hệ thống thích nghi và kiến trúc đường ống WebRTC APM

### 1. Tích chập đường vọng và bộ lọc thích nghi NLMS
Âm thanh phát từ loa dội qua bàn, tường, trần nhà rồi mới tới micro; chuỗi phản xạ đó được mô tả bằng đáp ứng xung phòng $$\mathbf{h}$$ (tích chập tuyến tính $$d[n] = (\mathbf{h} * \mathbf{x})[n]$$). Bộ lọc thích nghi kinh điển **NLMS (Normalized Least Mean Squares)** cập nhật vector trọng số $$\mathbf{w}[n]$$ bằng cách đi ngược hướng gradient của sai số tức thời $$e[n] = y[n] - \mathbf{w}[n]^T \mathbf{x}[n]$$, có chuẩn hóa theo năng lượng đầu vào $$\|\mathbf{x}[n]\|^2$$ để tốc độ hội tụ không bị bùng nổ khi loa phát to hay ì ạch khi loa phát nhỏ.

### 2. Bài toán nói đè (Double-Talk) và lý do bộ lọc thích nghi dễ "phát điên"
Khi cả hai đầu cùng nói cùng lúc (*double-talk*), tín hiệu micro $$y[n] = s[n] + d[n] + n[n]$$ chứa giọng nói đầu gần $$s[n]$$ rất lớn. Nếu bộ lọc thích nghi không biết mà vẫn cập nhật $$\mathbf{w}[n]$$ theo sai số $$e[n]$$ (vốn đang chứa đầy $$s[n]$$), nó sẽ phá hỏng hoàn toàn ước lượng đường phòng $$\mathbf{w}$$ vừa học được! Do đó mọi bộ AEC thực tế (như WebRTC AEC3) đều cần cơ chế phát hiện nói đè (Double-Talk Detector) hoặc bước học thích nghi theo tỷ lệ năng lượng.

### 3. Vai trò của WebRTC APM và phần vọng dư phi tuyến
Trong các ứng dụng gọi điện hiện đại (trình duyệt, Mezon, LiveKit), **WebRTC APM** xếp các khối theo thứ tự có chủ đích: lọc thông cao (HPF) bỏ rung ù tần số cực thấp → **AEC** dùng tham chiếu loa để triệt vọng tuyến tính → **NS** dọn nhiễu nền và **vọng dư phi tuyến** (do loa laptop nhỏ bị bão hòa/rè, thứ mà bộ lọc tuyến tính $$\mathbf{h} * \mathbf{x}$$ không bao giờ mô hình hóa hết được) → **AGC** cân bằng âm lượng.

### Giải thích: Cầm tay cập nhật 1 bước bộ lọc thích nghi NLMS và tính chỉ số ERLE

Giả sử đường vọng thực của phòng được mô hình gọn bằng 2 tap $$\mathbf{h} = [0{,}5,\; -0{,}2]^T$$. Tại thời điểm $$n$$, loa đang phát vector tham chiếu $$\mathbf{x}[n] = [1{,}0,\; 0{,}5]^T$$ và người dùng đầu gần đang im lặng ($$s[n] = 0$$, bỏ qua nhiễu nhỏ):
- Tiếng vọng thực tế micro thu được:
  $$d[n] = \mathbf{h}^T \mathbf{x}[n] = 0{,}5 \times 1{,}0 + (-0{,}2) \times 0{,}5 = 0{,}50 - 0{,}10 = 0{,}40.$$
- Hiện tại, bộ lọc thích nghi mới ước lượng được $$\mathbf{w}[n] = [0{,}2,\; 0{,}0]^T$$, nên tiếng vọng dự đoán là:
  $$\hat{d}[n] = \mathbf{w}[n]^T \mathbf{x}[n] = 0{,}2 \times 1{,}0 + 0{,}0 \times 0{,}5 = 0{,}20.$$
- Sai số dư (residual echo) còn sót lại:
  $$e[n] = d[n] - \hat{d}[n] = 0{,}40 - 0{,}20 = +0{,}20.$$

**Bước cập nhật NLMS** với tốc độ học $$\mu = 0{,}5$$ (bỏ qua hằng số ổn định $$\epsilon \approx 0$$):
1. Tính năng lượng tín hiệu tham chiếu:
   $$\|\mathbf{x}[n]\|^2 = 1{,}0^2 + 0{,}5^2 = 1{,}00 + 0{,}25 = 1{,}25.$$
2. Tính lượng hiệu chỉnh trọng số:
   $$\Delta \mathbf{w} = \frac{\mu}{\|\mathbf{x}[n]\|^2}\, e[n]\, \mathbf{x}[n] = \frac{0{,}5}{1{,}25} \times 0{,}20 \times \begin{bmatrix} 1{,}0 \\ 0{,}5 \end{bmatrix} = 0{,}08 \times \begin{bmatrix} 1{,}0 \\ 0{,}5 \end{bmatrix} = \begin{bmatrix} 0{,}08 \\ 0{,}04 \end{bmatrix}.$$
3. Trọng số mới:
   $$\mathbf{w}[n+1] = \begin{bmatrix} 0{,}20 \\ 0{,}00 \end{bmatrix} + \begin{bmatrix} 0{,}08 \\ 0{,}04 \end{bmatrix} = \begin{bmatrix} 0{,}28 \\ 0{,}04 \end{bmatrix}.$$
   Kiểm tra nhanh: nếu cùng vector $$\mathbf{x}$$ lặp lại ngay sau đó, tiếng vọng dự đoán tăng lên $$0{,}28(1{,}0) + 0{,}04(0{,}5) = 0{,}30$$, kéo sai số từ $$0{,}20$$ giảm ngay một nửa xuống $$0{,}10$$!

**Đo chất lượng triệt vọng bằng ERLE (Echo Return Loss Enhancement):**
Sau khi hội tụ, giả sử công suất tiếng vọng thu vào là $$P_d = 0{,}16$$ còn công suất vọng dư sau AEC chỉ còn $$P_e = 0{,}0016$$:
$$\mathrm{ERLE} = 10\log_{10}\!\left(\frac{P_d}{P_e}\right) = 10\log_{10}\!\left(\frac{0{,}16}{0{,}0016}\right) = 10\log_{10}(100) = 20\text{ dB}.$$
Trong thực tế, một bộ AEC tuyến tính tốt đạt ERLE khoảng $$15\text{–}25\text{ dB}$$; phần vọng dư phi tuyến còn lại sẽ được tầng hậu lọc NS (hoặc DeepFilterNet) dọn nốt.

## Mục tiêu học tập

Sau bài học này, bạn sẽ vẽ được luồng tín hiệu đầu gần (near-end) và đầu xa (far-end) với đường vọng $$\mathbf{h}$$, giải thích được vì sao bộ lọc thích nghi có tín hiệu tham chiếu khác biệt với khử nhiễu mù, liệt kê các khối chính trong WebRTC APM (AEC, NS, AGC, HPF, VAD), và phân tích các ràng buộc thực tế (độ trễ, lệch đồng hồ, méo phi tuyến) khiến tiếng vọng dư tràn sang tầng NS.

## Kế hoạch 60 phút

- **0–10 phút** — Phân biệt tiếng vọng và nhiễu nền qua nghe trực tiếp; xác định tín hiệu tham chiếu far-end.
- **10–25 phút** — Mô hình $$y=s+\mathbf{h}*\mathbf{x}+n$$ và bài toán ước lượng $$\hat{\mathbf{h}}$$.
- **25–40 phút** — Tổng quan pipeline WebRTC APM (ở mức khối khái niệm).
- **40–50 phút** — Tiếng vọng dư sau AEC và lý do vẫn cần NS hoặc bộ hậu lọc mạng nơ-ron.
- **50–60 phút** — Các bẫy thường gặp, bài tập và danh mục kiểm tra khi tích hợp sản phẩm.

## Giải thích cốt lõi

### Tiếng vọng là "nhiễu có cấu trúc"

$$
y[t]=s[t]+\underbrace{(h*x)[t]}_{\text{echo}}+n[t],
$$

trong đó $$x[t]$$ là tín hiệu đầu xa (thiết bị phát đã biết trước), còn $$h$$ là đường truyền âm học của tiếng vọng (phòng + loa + micro). Khối AEC ước lượng $$\hat{h}$$ và tính tín hiệu sai số (phần dư):

$$
e[t]=y[t]-(\hat{h}*x)[t].
$$

Khi $$\hat{h}\approx h$$ và đường vọng tuyến tính biến đổi chậm, ta thu được $$e\approx s+n$$, cho phép tầng NS phía sau tập trung xử lý nhiễu nền $$n$$.

```text
far-end x ──► loa ──► phòng h ──► mic y
near-end s ─────────────────────► mic y
nhiễu nền n ────────────────────► mic y
AEC:  e = y − ĥ ∗ x
NS:   chạy trên e, không chạy trên y thô
```

Chính phần dư sau phép trừ này mới là đầu vào thực tế của bộ khử nhiễu phía sau. Khi bộ hủy vọng hoạt động đúng, \(e\) có dạng hỗn hợp cộng tính như hình minh họa: tiếng nói đầu gần cộng với phần chưa bị triệt tiêu (nhiễu nền và tiếng vọng dư nhỏ hơn). Lưu ý hình minh họa chỉ biểu diễn hỗn hợp cộng tính đó chứ không vẽ đường truyền âm học trong phòng.

![Tiếng sạch, nhiễu cộng, và tổng của chúng — dạng phần dư sau khi echo đã bị trừ]({{ site.imgurl }}/generated/noise-mixture.png)

*Hình. Sau bước AEC tuyến tính, phần dư có dạng hỗn hợp cộng tính giữa tiếng nói đầu gần và các thành phần chưa hủy hết; sơ đồ này minh họa hỗn hợp cộng tính đó chứ không mô tả đường truyền tiếng vọng.*

### Trực giác về bộ lọc thích nghi (NLMS)

Một bộ lọc FIR độ dài $$L$$ cập nhật trọng số theo quy tắc NLMS:

$$
\mathbf{h}_{\ell+1}=\mathbf{h}_\ell+\mu\frac{e_\ell\,\mathbf{x}_\ell}{\|\mathbf{x}_\ell\|^2+\varepsilon}.
$$

Các bộ lọc thích nghi miền tần số dạng chia khối (partitioned-block, phổ biến trong AEC của WebRTC) vận hành trên cùng ý tưởng nhưng kiểm soát độ phức tạp và độ trễ tốt hơn. **Liên hệ với Kalman (bài 03-03):** thay vì dùng bước học vô hướng $$\mu$$, bộ lọc Kalman điều chỉnh bước cập nhật theo ma trận hiệp phương sai.

### So sánh AEC và NS

| Tiêu chí | AEC | NS |
|----------|-----|----|
| Tín hiệu tham chiếu | Bắt buộc có far-end $$x$$ | Thường là ước lượng mù |
| Thành phần cần loại bỏ | Tiếng vọng $$h*x$$ | Nhiễu nền và tạp âm |
| Nguyên nhân dễ lỗi | Lệch trễ, nói chồng (double-talk), méo phi tuyến của loa | Nhiễu không dừng, méo nhiễu nhạc |
| Vị trí trong chuỗi | Đầu APM | Sau AEC / kết hợp khử vọng dư |

Tình huống nói chồng (**double-talk** — cả hai đầu gần và đầu xa nói cùng lúc) là phép thử khắc nghiệt nhất của AEC: bộ lọc thích nghi bắt buộc phải đóng băng hoặc giảm mạnh tốc độ cập nhật để không phá hỏng ước lượng đường vọng.

### Mô hình khái niệm của WebRTC APM

1. **High-pass (HPF)** — loại bỏ thành phần DC và tiếng ù tần số cực thấp.
2. **Echo canceller (AEC / AECM)** — hủy vọng theo tham chiếu; thiết bị di động có thể dùng biến thể nhẹ hơn.
3. **Noise suppression (NS)** — khử nhiễu phổ / Wiener cổ điển (cho phép chọn mức cường độ).
4. **AGC** — tự động điều chỉnh âm lượng (rất dễ xung đột với NS nếu đặt sai thứ tự).
5. **VAD / các mô-đun mở rộng** — tùy cờ biên dịch.

Thứ tự và tên cụ thể có thể thay đổi giữa các phiên bản WebRTC; hãy xem danh sách trên là **sơ đồ kiến trúc khái niệm** và đối chiếu tài liệu `AudioProcessing` khi tích hợp thực tế.

**Liên hệ với sản phẩm:** Mezon và nhiều ứng dụng LiveKit/WebRTC kết hợp AEC sẵn có của trình duyệt **với** bộ khử nhiễu mạng nơ-ron (như DeepFilterNet3 qua AudioWorklet). Khi tích hợp, cần xác minh AEC đã thực sự hoạt động chưa, tiếng vọng dư còn đáng kể không, và mô hình NS có được huấn luyện để xử lý vọng dư như "nhiễu" hay không.

### Tiếng vọng dư và bộ hậu lọc mạng nơ-ron

AEC tuyến tính vẫn để lại tiếng vọng dư khi loa méo phi tuyến, ước lượng độ trễ bị lệch (ví dụ tai nghe Bluetooth), lệch đồng hồ giữa phát và thu, hoặc đường vọng $$h$$ thay đổi nhanh. Các nghiên cứu kiến trúc lai (như ULCNet + bộ lọc thích nghi) huấn luyện mạng gọn nhẹ trực tiếp trên **phần dư của AEC**. Trong thực hành, hãy đo chỉ số suy hao vọng ERLE trước và sau AEC; nếu vẫn nghe rõ tiếng vọng dư, cần sửa khâu căn chỉnh độ trễ hoặc bổ sung bộ khử vọng dư chuyên dụng thay vì chỉ trông chờ vào NS thông thường.

## Danh mục kiểm tra tích hợp

1. Xác nhận tín hiệu tham chiếu far-end thực sự được cấp vào khối AEC.
2. Đo độ trễ đệm vòng và căn chỉnh thời gian của tín hiệu tham chiếu.
3. Kiểm thử bằng các đoạn mẫu **nói chồng (double-talk)**.
4. Xác định rõ vị trí chèn NS: bên trong APM, ngay sau PCM của APM hay trong AudioWorklet mạng nơ-ron (Chương 05, 07).
5. Tắt các khối AGC trùng lặp để tránh chúng điều chỉnh chồng chéo lẫn nhau.
6. Phân loại phản hồi người dùng theo nhóm tiếng vọng hay nhiễu nền để định tuyến gỡ lỗi đúng giữa AEC và NS.

## Bẫy thường gặp

- Chạy NS mạng nơ-ron trực tiếp trên tín hiệu còn nguyên tiếng vọng lớn → bộ khử sẽ đè mạnh giọng người nói đầu gần mỗi khi đầu xa phát tiếng.
- Mặc định rằng AEC của trình duyệt luôn hoạt động ổn định mà không kiểm thử các đặc thù trên thiết bị di động.
- Huấn luyện và đánh giá NS thuần túy trên nhiễu cộng tính DNS rồi triển khai trên laptop dùng loa ngoài đầy tiếng vọng.
- Đặt AGC trước AEC khiến hệ số khuếch đại làm biến thiên liên tục đường vọng.
- Nhầm lẫn giữa tiếng vọng **âm học (acoustic echo)** với tiếng vọng **đường dây (line echo)** ở cổng điện thoại.

## Mini-lab

**Mục tiêu.** Mô phỏng định lượng sự khác biệt giữa công suất tiếng vọng dư thực sự và công suất lỗi đo được, đặc biệt ở khung có nói chồng (double-talk). Lưu ý đoạn mã này chỉ minh họa khái niệm, không gọi WebRTC hay Audio Processing Module.

```python
import numpy as np

far = np.array([0.0, 0.2, 1.0, 1.0, 0.3, 1.2])
near = np.array([0.0, 0.0, 0.0, 0.8, 0.0, 0.0])  # double-talk chỉ ở frame 3
h, hhat = 0.5, 0.45
residual_echo = (h - hhat) * far
err = near + residual_echo
print("residual echo power", np.round(residual_echo ** 2, 4))
print("measured error power", np.round(err ** 2, 4))
```

**Kết quả kỳ vọng.** Công suất vọng dư giữ ở mức nhỏ: `[0, 0.0001, 0.0025, 0.0025, 0.0002, 0.0036]`. Công suất lỗi đo được trùng khớp ở mọi khung trừ khung 3, nơi giọng nói đầu gần đẩy tổng công suất lên `0.7225` dù vọng dư thực sự vẫn chỉ là `0.0025`. Nếu tiếp tục cập nhật \(\hat{h}\) tại khung này, bộ lọc sẽ nhầm giọng người nói là tiếng vọng.

**Lỗi thường gặp.** Nếu hai mảng công suất trùng nhau ở khung 3 thì `near` vẫn bằng 0 và chưa có tình huống double-talk; nếu công suất vọng dư lớn ở mọi khung có tín hiệu far-end thì ước lượng \(\hat{h}\) đang lệch xa \(h\); dùng trực tiếp công suất lỗi làm nền nhiễu cho độ lợi Wiener sẽ đè mất giọng đầu gần.

## Bài tập

1. Vẽ sơ đồ luồng thu (capture), phát (render), $$\hat{h}$$, $$e$$ và NS, đánh dấu rõ vị trí chèn AudioWorklet mạng nơ-ron.
2. Giải thích điều gì xảy ra với bộ lọc NLMS khi tín hiệu tham chiếu bị sớm hoặc muộn 40 ms so với tiếng vọng thực thu ở micro.
3. Tra cứu tài liệu WebRTC APM và liệt kê tên các tùy chọn bật/tắt AEC và mức cường độ NS.
4. Viết quy trình hỗ trợ chẩn đoán nhanh (playbook): từ triệu chứng người dùng báo → khoanh vùng AEC/NS/AGC → bước kiểm tra đầu tiên.

### Gợi ý đáp án

1. Khối NS mạng nơ-ron đặt trên tín hiệu dư \(e\) ngay sau \(\hat{h}\); trên trình duyệt, vị trí này thường nằm sau AEC của nền tảng và trước bộ mã hóa.
2. Độ lệch 40 ms đẩy tiếng vọng ra ngoài cửa sổ các hệ số tap đang ước lượng \(h\), khiến \(e\) vẫn còn nguyên tiếng vọng và bộ lọc thích nghi hội tụ sai độ trễ.
3. Tra cứu cấu hình mức NS và công tắc AEC trên `AudioProcessing`; vì tên trường có thể đổi giữa các bản phát hành, cần ghi lại mã phiên bản tài liệu đã đối chiếu.
4. Đầu xa nói trong khi đầu gần im là bài kiểm tra AEC; đầu gần nói trong môi trường ồn khi đầu xa im là bài kiểm tra NS; âm lượng nhảy đột ngột khi một phía ngừng nói thường xuất phát từ AGC.

## Đọc thêm

- Tài liệu WebRTC Audio Processing Module và API `AudioProcessing`.
- Bộ khử vọng và tiền xử lý SpeexDSP.
- Haykin, *Adaptive Filter Theory*.
- Các mốc kiến trúc lai AENR: ULCNet + bộ lọc thích nghi và Align-ULCNet.

## Video tham khảo

- [Revamping Audio Quality for RTC Part 1: Beryl Echo Cancellation | Sriram Srinivasan and Hoang Do](https://www.youtube.com/watch?v=lapq9zvUd-k) — @Scale, tiếng Anh. **Xem trước.** Minh họa đường truyền từ loa đến micro và vị trí đặt khối khử vọng trong chuỗi âm thanh thời gian thực — đúng ngữ cảnh WebRTC APM của bài.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Phần bàn về tiếng vọng cho thấy AEC và NS là hai bài toán kế cận nhau, lý giải vì sao không thể gộp chung thành một công tắc duy nhất.
