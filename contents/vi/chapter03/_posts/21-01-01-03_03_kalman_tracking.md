---
layout: post
title: "03-03 Theo dõi kiểu Kalman (trực giác)"
chapter: "03"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter03
lesson_type: required
draft: false
---

Bộ lọc Kalman không phải là "một dạng mặt nạ phổ khác" mà là một **bộ theo dõi Bayes đệ quy**: ở mỗi bước, nó dự đoán trạng thái tiếng nói tiếp theo rồi hiệu chỉnh lại dựa trên phép đo có nhiễu mới nhận được. Trong tăng cường tiếng nói (SE) và khử vọng (AEC), tư duy Kalman xuất hiện ở các bộ lọc thích nghi, bộ theo dõi tiếng vọng dư và các kiến trúc lai AEC+NS (ví dụ AEC Kalman cổ điển nối tiếp bộ hậu lọc mạng nơ-ron gọn nhẹ). Bài học này dừng ở mức **trực giác và sơ đồ khối** — đủ để đọc bài báo và gỡ lỗi hệ thống lai — mà không đi sâu vào lý thuyết điều khiển tổng quát.

Hãy tưởng tượng bạn đang theo dõi vị trí một con tàu giữa biển sương mù bằng chiếc radar bị nhiễu nặng. Nếu chỉ tin hoàn toàn vào chấm sáng nhảy nhót trên màn hình radar ở giây hiện tại, con tàu trông như đang dịch chuyển tức thời; nhưng nếu bạn nhớ vận tốc con tàu ở giây trước để *dự đoán* nó sẽ ở đâu, rồi chỉ *kéo nhẹ* dự đoán đó về phía chấm radar mới theo mức độ tin cậy của radar, quỹ đạo ước lượng sẽ mượt mà đến kinh ngạc. Đó chính là linh hồn của **bộ lọc Kalman** — không phải một chiếc mặt nạ cắt phổ độc lập từng khung, mà là một cỗ máy suy luận Bayes đệ quy biết cân đo đong đếm giữa *niềm tin vào mô hình quá khứ* và *bằng chứng từ phép đo nhiễu hiện tại*.

## Bản đồ kiến thức nền: Không gian trạng thái và suy luận Bayes đệ quy

### 1. Mô hình không gian trạng thái (State-Space Model)
Thay vì coi mỗi khung âm thanh là một ốc đảo tách biệt, bộ lọc Kalman mô tả tín hiệu ẩn $$x_k$$ (có thể là mẫu tiếng nói theo mô hình tự hồi quy AR, hoặc vector đáp ứng xung đường vọng $$\mathbf{h}_k$$) tiến hóa theo thời gian qua hai phương trình:
- **Phương trình trạng thái (động học):** $$x_k = A x_{k-1} + w_k$$, với nhiễu quá trình $$w_k \sim \mathcal{N}(0, Q)$$ đo mức độ "thay đổi bất ngờ" của trạng thái.
- **Phương trình quan sát (phép đo):** $$y_k = H x_k + v_k$$, với nhiễu đo $$v_k \sim \mathcal{N}(0, R)$$ đo độ ồn của micro.

### 2. Độ lợi Kalman (Kalman Gain) — chiếc cân tự động giữa mô hình và dữ liệu
Ở mỗi bước, thuật toán chạy đúng hai pha: **Dự đoán (Predict)** đẩy ước lượng cũ và độ bất định $$P$$ về phía trước; sau đó **Cập nhật (Update)** tính sai lệch bất ngờ (*innovation*) $$e_k = y_k - H \hat{x}_{k\vert k-1}$$ và nhân với **độ lợi Kalman** $$K_k$$. Khi phép đo rất ồn ($$R \gg P$$), $$K_k \to 0$$ (tin vào dự đoán hơn); ngược lại khi trạng thái biến đổi mạnh còn phép đo sạch ($$P \gg R$$), $$K_k \to 1$$ (bám sát phép đo mới).

### 3. Vì sao Kalman sống khỏe trong các hệ thống AEC+NS lai hiện đại?
Khử vọng tuyến tính (AEC) có cấu trúc vật lý rõ ràng: đáp ứng xung phòng thay đổi chậm theo thời gian (trừ khi có người di chuyển hoặc đổi vị trí loa), cực kỳ hợp với bộ lọc Kalman miền tần số (như trong kiến trúc của Enzner & Vary). Một tầng Kalman gọn nhẹ có thể triệt sạch phần vọng tuyến tính ổn định mà không cần học lại từ đầu, để phần việc khó còn lại (vọng phi tuyến do loa rè, nhiễu nền không dừng) cho một mạng nơ-ron nhỏ gọn phía sau xử lý.

### Khung giải thích: Cầm tay chạy 1 chu kỳ Dự đoán – Cập nhật của bộ lọc Kalman vô hướng (nên đọc chậm)

Xét một bài toán 1 chiều theo dõi biên độ trạng thái tiếng nói $$x_k$$ với mô hình tự hồi quy bậc 1:
- Động học: $$x_k = 0{,}9\,x_{k-1} + w_k$$, phương sai nhiễu quá trình $$Q = 0{,}09$$.
- Phép đo có nhiễu: $$y_k = x_k + v_k$$ ($$H = 1$$), phương sai nhiễu đo $$R = 0{,}50$$.

Giả sử ở bước trước ($$k-1$$), ta đã có ước lượng hậu nghiệm $$\hat{x}_{k-1\vert k-1} = 2{,}00$$ với phương sai sai số $$P_{k-1\vert k-1} = 0{,}20$$. Nay micro thu được mẫu nhiễu mới $$y_k = 2{,}60$$. Hãy tính tay từng bước:

1. **Bước 1 — Dự đoán (Predict):**
   - Trạng thái dự đoán: $$\hat{x}_{k\vert k-1} = 0{,}9 \times 2{,}00 = 1{,}80$$.
   - Phương sai bất định dự đoán: $$P_{k\vert k-1} = 0{,}9^2 \times 0{,}20 + Q = 0{,}81 \times 0{,}20 + 0{,}09 = 0{,}162 + 0{,}09 = 0{,}252$$.
   *(Lưu ý: sau bước dự đoán, độ bất định tăng từ $$0{,}20$$ lên $$0{,}252$$ vì ta chưa nhìn thấy phép đo mới.)*

2. **Bước 2 — Tính độ lợi Kalman (Kalman Gain):**
   $$K_k = \frac{P_{k\vert k-1}}{P_{k\vert k-1} + R} = \frac{0{,}252}{0{,}252 + 0{,}50} = \frac{0{,}252}{0{,}752} \approx 0{,}335.$$
   Vì nhiễu đo $$R = 0{,}50$$ lớn gần gấp đôi bất định dự đoán $$P^- = 0{,}252$$, bộ lọc chỉ đặt niềm tin khoảng $$33{,}5\%$$ vào phép đo mới.

3. **Bước 3 — Cập nhật trạng thái và thu hẹp độ bất định (Update):**
   - Phần bất ngờ (innovation): $$y_k - \hat{x}_{k\vert k-1} = 2{,}60 - 1{,}80 = +0{,}80$$.
   - Ước lượng hậu nghiệm mới: $$\hat{x}_{k\vert k} = 1{,}80 + 0{,}335 \times 0{,}80 = 1{,}80 + 0{,}268 = 2{,}068$$.
   - Phương sai hậu nghiệm mới: $$P_{k\vert k} = (1 - K_k)\,P_{k\vert k-1} = 0{,}665 \times 0{,}252 \approx 0{,}168$$.

Kiểm chứng trực giác: kết quả $$2{,}068$$ nằm gọn giữa dự đoán $$1{,}80$$ và phép đo ồn $$2{,}60$$ (nghiêng về phía dự đoán vì radar đang ồn), đồng thời độ bất định giảm từ $$0{,}252$$ xuống $$0{,}168$$ — mỗi phép đo mới, dù ồn, vẫn cung cấp thêm thông tin để làm sắc nét ước lượng!

## Mục tiêu học tập

Sau bài học này, bạn sẽ giải thích được vòng lặp dự đoán–cập nhật (predict–update) cùng vai trò của hiệp phương sai nhiễu quá trình và nhiễu đo, ánh xạ bài toán SE sang mô hình không gian trạng thái, so sánh Kalman với độ lợi Wiener theo từng khung, và nhận diện mô hình triển khai thực tế: dùng Kalman/LMS/RLS làm tầng tiền xử lý cho bộ khử phần dư bằng mạng nơ-ron.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao theo dõi đệ quy hiệu quả hơn việc ước lượng lại từ đầu ở mỗi khung.
- **10–25 phút** — Mô hình không gian trạng thái, bước dự đoán và trực giác về độ lợi Kalman (Kalman gain).
- **25–40 phút** — Ứng dụng trong tiếng nói và AEC: theo dõi hệ số AR hoặc đáp ứng xung đường vọng.
- **40–50 phút** — Kiến trúc lai: AEC Kalman kết hợp hậu lọc mạng nơ-ron (các mốc tham khảo).
- **50–60 phút** — Các bẫy thường gặp, bài tập và cầu nối sang WebRTC APM (bài 03-04).

## Giải thích cốt lõi

### Nguyên lý Kalman tóm gọn

Hệ thống duy trì một ước lượng kèm độ bất định về trạng thái ẩn $$x_\ell$$ (có thể là mẫu tiếng nói sạch, hệ số LPC hoặc đáp ứng xung đường vọng). Tại mỗi khung:

1. **Dự đoán (Predict)** theo mô hình động học: $$x_{\ell|\ell-1}=A x_{\ell-1|\ell-1}$$.
2. **Cập nhật (Update)** với phép đo $$y_\ell=H x_\ell+v_\ell$$: kéo giá trị dự đoán về phía quan sát theo tỷ lệ tương ứng với độ tin cậy của phép đo.

**Độ lợi Kalman** $$K_\ell$$ lớn khi phép đo đáng tin cậy (ưu tiên tín hiệu từ micro) và nhỏ khi phép đo nhiều nhiễu (ưu tiên dự đoán từ mô hình).

### Mô hình vô hướng giản lược

$$
x_\ell = x_{\ell-1}+w_\ell,\quad y_\ell=x_\ell+v_\ell,
$$

$$
K=\frac{p^{-}}{p^{-}+r},\quad \hat{x}=\hat{x}^{-}+K(y-\hat{x}^{-}).
$$

So với bộ lọc Wiener, $$K$$ có dạng tương đồng với $$\xi/(\xi+1)$$ nếu coi $$p^{-}/r$$ như một dạng SNR tiên nghiệm. Nói ngắn gọn, Kalman giống như bộ lọc Wiener **có thêm bộ nhớ** thông qua trạng thái và phương sai dự đoán. Trên hình minh họa, đường cam đại diện cho mức nền mà một bộ theo dõi đệ quy duy trì, còn đường cong bên phải là độ lợi được tính từ nền đó. Bước cập nhật Kalman cung cấp một cơ chế thống kê tường minh để cập nhật nền ổn định; bản thân hình vẽ vẫn minh họa khử nhiễu cổ điển chứ không phải sơ đồ khối chi tiết của bộ lọc Kalman.

![Sàn nhiễu được theo dõi, cạnh gain theo SNR mà sàn đó dùng để tính]({{ site.imgurl }}/generated/spectral-subtraction-wiener.png)

*Hình. Đường cam biểu diễn bộ theo dõi sàn nhiễu; đường bên phải là độ lợi suy ra từ sàn đó — phần mà bước cập nhật đệ quy kiểu Kalman giúp giữ ổn định theo thời gian.*

### Vì sao kỹ sư âm thanh quan tâm

| Ứng dụng | Trạng thái ẩn $$x$$ | Phép đo $$y$$ |
|----------|---------------------|---------------|
| Theo dõi tiếng nói sạch | Mẫu tín hiệu / biên độ phổ | Tín hiệu micro có nhiễu |
| Mô hình LPC / formant | Các hệ số tự hồi quy (AR) | Phần dư / phổ tín hiệu |
| Ước lượng đường vọng AEC | Đáp ứng xung $$\mathbf{h}$$ | Tín hiệu micro hồi quy theo tín hiệu far-end |
| Mật độ phổ công suất vọng dư | Công suất vọng dư | Tín hiệu lỗi sau bộ lọc thích nghi |

Các **bộ lọc thích nghi** (NLMS, RLS) trong AEC là họ hàng gần của Kalman vì cùng ước lượng đệ quy đường vọng. Kalman cung cấp lịch cập nhật độ lợi dựa trên mô hình hiệp phương sai, còn NLMS dùng bước cập nhật chuẩn hóa với chi phí thấp hơn. WebRTC APM và SpeexDSP ưu tiên các bộ lọc thích nghi thực dụng, trong khi nhiều bài báo kiến trúc lai gọi là "Kalman AEC" theo nghĩa bộ theo dõi có cập nhật hiệp phương sai.

### Kiến trúc lai: cổ điển kết hợp mạng nơ-ron

1. Bộ lọc thích nghi hoặc Kalman triệt tiêu phần tiếng vọng **tuyến tính** dựa trên tín hiệu tham chiếu far-end.
2. Một mạng nơ-ron **nhỏ** (kiểu ULCNet, GTCRN hoặc bộ hậu lọc DeepFilterNet) dọn sạch tiếng vọng dư phi tuyến và nhiễu nền mà mô hình tuyến tính không xử lý hết.

Các mốc tham khảo tiêu biểu trong nghiên cứu gồm Align-ULCNet, kiến trúc lai ULCNet + bộ lọc thích nghi, và GSC + DeepFilterNet2 cho bài toán nhiễu có hướng (ego-noise).

**Bài học kỹ thuật:** Đừng ép mạng nơ-ron phải tự học hủy tiếng vọng tuyến tính thuần túy khi đã có sẵn tín hiệu tham chiếu — hãy để bộ lọc thích nghi xử lý phần tuyến tính rồi đưa tín hiệu dư sạch hơn vào mạng.

## Danh mục kiểm tra: khi nào nên dùng tư duy Kalman

- Khi bài toán có **mô hình động học** rõ ràng (đường vọng thay đổi chậm, đường bao AR).
- Khi có **tín hiệu tham chiếu** (far-end cho AEC).
- Khi phần dư sau bộ hủy tuyến tính vẫn cần khử phi tuyến.
- Khi ngân sách CPU chặt — kết hợp bộ lọc thích nghi cổ điển với mạng NS gọn nhẹ hiệu quả hơn một mạng đầu–cuối khổng lồ.

## Bẫy thường gặp

- Coi Kalman là "bộ khử nhiễu vạn năng" mà không định nghĩa rõ vector trạng thái và mô hình đo.
- Thiết lập sai ma trận $$A$$ hoặc $$H$$ dẫn tới sai lệch hệ thống.
- Mất ổn định số ở ma trận hiệp phương sai (cần duy trì tính đối xứng xác định dương SPD).
- Áp dụng Kalman toàn ma trận lên vector STFT chiều lớn trong khi xấp xỉ đường chéo hoặc NLMS mới khả thi ở thời gian thực.
- Quên rằng tầng mạng nơ-ron hậu lọc vẫn cộng thêm độ trễ và trạng thái streaming (Chương 05–06).

## Mini-lab

**Mục tiêu.** Thực hiện một bước dự đoán–cập nhật vô hướng và in độ lợi Kalman trong hai trường hợp: phép đo đáng tin cậy và phép đo nhiễu mạnh.

```python
def kalman_gain(p, q, r):
    p_pred = p + q
    return p_pred / (p_pred + r)

for r in (0.1, 10.0):
    K = kalman_gain(p=1.0, q=0.1, r=r)
    print("r", r, "K", round(K, 3))
```

**Kết quả kỳ vọng.** Phương sai tiên nghiệm sau bước dự đoán bằng \(1.1\). Với \(r=0.1\), ta có \(K\approx 0.917\) (tin tưởng phép đo); với \(r=10\), ta có \(K\approx 0.099\) (bám sát dự đoán). Công thức có cùng dạng với độ lợi Wiener: giá trị tăng khi tỷ số \(p^{-}/r\) lớn.

**Lỗi thường gặp.** Cập nhật \(p\) bằng phép đo trước khi tính \(K\) sẽ làm sai cả hai kết quả; hoán đổi nhầm \(q\) và \(r\) sẽ khiến cảm biến nhiễu trông đáng tin hơn cảm biến sạch. Lưu ý đây chỉ là mô phỏng vô hướng minh họa cơ chế độ lợi, không phải bộ lọc Kalman đầy đủ cho tiếng nói hay bộ theo dõi PSD nhiễu.

## Bài tập

1. Cài đặt vòng lặp dự đoán–cập nhật vô hướng với trạng thái $$x$$ là một sóng sin biến thiên chậm và quan sát sự thay đổi của $$K$$ khi điều chỉnh $$r$$.
2. Vẽ sơ đồ một trang cho hệ thống AEC có trạng thái $$=\mathbf{h}$$, đánh dấu rõ vị trí gắn bộ hậu lọc mạng nơ-ron.
3. Nêu ba điểm giống và khác nhau giữa bộ lọc Wiener decision-directed và bộ lọc Kalman cho mật độ phổ công suất tiếng nói.
4. Viết bản phác thảo thiết kế cho tình huống gọi trên trình duyệt có tiếng vọng loa theo chuỗi: WebRTC AEC → bộ khử nhiễu dư mạng nơ-ron, nêu rõ trách nhiệm của từng khối.

### Gợi ý đáp án

1. Giá trị \(K\) phải giảm khi \(r\) tăng, đồng thời ước lượng sẽ đáp ứng chậm hơn trước biến động nhanh của \(y\) khi \(r\) lớn.
2. Các mẫu trễ của far-end đóng vai trò vector hồi quy, tín hiệu micro là \(y\), và khối mạng nơ-ron nhận đầu vào là tín hiệu dư \(e=y-\hat{h}*x\) thay vì tín hiệu micro thô.
3. Cả hai đều có tính đệ quy và đều hạ độ lợi khi nhiễu lấn át; điểm khác là Wiener decision-directed theo dõi một tỷ số công suất, còn Kalman theo dõi tường minh cả trạng thái lẫn phương sai dựa trên mô hình động học quá trình.
4. AEC chịu trách nhiệm triệt tiêu tiếng vọng tuyến tính dựa trên tham chiếu far-end; tầng mạng nơ-ron xử lý phần còn lại gồm vọng dư phi tuyến và nhiễu nền mà không phải học lại \(\mathbf{h}\).

## Đọc thêm

- R. E. Kalman, bài báo nền tảng năm 1960.
- Haykin, *Adaptive Filter Theory* (NLMS và RLS).
- Tổng quan WebRTC Audio Processing Module.
- Các mốc kiến trúc lai Kalman/ULCNet cho AENR (Align-ULCNet, ở mức khái niệm).

## Video tham khảo

- [Why Use Kalman Filters? | Understanding Kalman Filters, Part 1](https://www.youtube.com/watch?v=mwn8xhgNpFY) — MATLAB, tiếng Anh. **Xem trước.** Trình bày trực quan chu trình dự đoán rồi hiệu chỉnh — cùng tư duy hai bước với bộ theo dõi nền nhiễu nhưng tổng quát hơn.
- [Kalman Filter - VISUALLY EXPLAINED!](https://www.youtube.com/watch?v=-DiZGpAh7T4) — Kapil Sachdeva, tiếng Anh. Minh họa cách độ bất định thu hẹp lại sau mỗi bước cập nhật phép đo, tạo trực giác rõ ràng cho các bộ theo dõi tiếng nói đệ quy.
