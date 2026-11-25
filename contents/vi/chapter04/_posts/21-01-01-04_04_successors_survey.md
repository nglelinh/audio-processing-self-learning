---
layout: post
title: "04-04 Khảo sát kế tục: DPDFNet, DeepFilterGAN, HDF-Net"
chapter: "04"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter04
lesson_type: required
draft: false
---

DPDFNet, DeepFilterGAN và HDF-Net trong khóa học này chỉ đóng vai trò **các điểm neo khảo sát (survey pointers)**. Bài học này cố ý không gán tiêu đề bài báo, năm xuất bản, hội nghị hay liên kết URL cho ba tên gọi đó: khi chưa trực tiếp mở đọc tệp PDF gốc, ta chưa có thông tin thư mục hợp lệ và không được suy đoán. Trọng tâm của buổi học là đặt các hướng phát triển kế tục bên cạnh khung kiến trúc ERB + deep filter để đánh giá xem một bản triển khai DeepFilterNet3 có thực sự cần thay đổi hay không.

![Bộ xương ERB cộng deep filter mà mọi tên kế tục vẫn phải thắng trên RTF và lượt nghe]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Hình. DPDFNet, DeepFilterGAN và HDF-Net chỉ là các tên gọi khảo sát trong danh sách đọc, không phải checkpoint tải trực tiếp từ bài học này. Mọi phương án thay thế đều phải duy trì bước nhảy hop STFT nhân quả, kích thước trạng thái bị chặn và hệ số RTF dưới 1 trên CPU đích.*

Trong nghiên cứu học sâu cho âm thanh, hầu như mỗi tháng đều xuất hiện một cái tên kiến trúc mới hứa hẹn nhích thêm $$0{,}05$$ điểm PESQ hay $$0{,}2\text{ dB}$$ SI-SDR trên bảng xếp hạng. Nhưng dưới góc nhìn của một kỹ sư hệ thống đang vận hành sản phẩm thời gian thực (như bộ lọc nhiễu trên trình duyệt hay ứng dụng gọi thoại), **một cái tên mới trên bảng benchmark chưa bao giờ tự động trở thành lý do để thay mô hình đang chạy ổn định**. Bài khảo sát này giúp bạn xây dựng "bộ lọc tư duy kỹ thuật" khi đứng trước các hướng kế tục xoay quanh họ DeepFilterNet — như kiến trúc hai đường (dual-path), huấn luyện đối nghịch (GAN) hay lọc phân cấp (hierarchical) — dựa trên ba thước đo không biết nói dối: ngân sách RTF, độ trễ thuật toán và tính tương thích thực thi ONNX/AudioWorklet.

## Kiến thức cần nhớ: Ba hướng mở rộng kiến trúc và chi phí kỹ thuật đi kèm

### 1. Hai đường thời gian–tần số (Dual-Path: Thời gian + Tần số)
Các mạng RNN/GRU chuẩn trong DeepFilterNet quét mạnh theo trục thời gian, còn trục tần số chủ yếu xử lý bằng tích chập cục bộ. Tư duy **Dual-Path** (như trong các biến thể kiểu DPDFNet) luân phiên quét dọc theo *trục tần số* (để nắm bắt quan hệ họa âm cách xa nhau trên cùng một khung) rồi quét dọc theo *trục thời gian* (để bám quỹ đạo giọng nói). Lợi ích là nắm bắt cấu trúc họa âm toàn cục tốt hơn, nhưng cái giá phải trả là thêm nhiều lớp tuần tự/chú ý trên mỗi khung, dễ đội RTF và làm tăng số toán tử khó tối ưu trên WebAssembly/ONNX Runtime.

### 2. Huấn luyện đối nghịch (GAN) — chi phí 0 lúc suy luận nhưng rủi ro "ảo giác"
Ý tưởng của các nhánh kiểu **DeepFilterGAN** là giữ một bộ sinh (Generator) gọn nhẹ để chạy lúc suy luận, còn bộ phân biệt (Discriminator — ví dụ phân biệt phổ đa thang đo) chỉ tồn tại *lúc huấn luyện* nhằm ép âm thanh đầu ra nghe sắc nét, giống tiếng người thật thay vì bị mờ đục do hàm mất mát MSE. Điểm cộng tuyệt vời là **không tăng thêm RTF lúc triển khai** nếu giữ nguyên bộ sinh; điểm trừ là mô hình GAN có thể sinh ra các thành phần tần số cao giả hoặc méo nhẹ ở tình huống ngoài phân bố (OOD), đòi hỏi kiểm thử nghe mù kỹ lưỡng.

### 3. Lọc phân cấp (Hierarchical) và nguyên tắc kỷ luật thư mục khoa học
Các hướng lọc phân cấp (kiểu HDF-Net) chia bài toán khử nhiễu theo nhiều mức độ phân giải hoặc nhiều chặng tinh chỉnh liên tiếp. Tuy nhiên, mỗi tầng tinh chỉnh bổ sung đều có nguy cơ cộng thêm khung nhìn trước (*look-ahead*) hoặc tăng dung lượng trạng thái cần giữ trong bộ nhớ cache. Quan trọng không kém về mặt học thuật: bài học này rèn thói quen **kỷ luật trích dẫn** — chỉ ghi nhận con số, năm xuất bản và cấu trúc khi đã tự tay mở đọc bài báo gốc, tuyệt đối không suy đoán từ tên gọi.

### Giải thích: Cầm tay tính ngân sách độ phức tạp và quyết định "Đổi hay Giữ" trong AudioWorklet

Giả sử bạn đang vận hành một luồng âm thanh $$48\text{ kHz}$$ với hop $$H = 10\text{ ms}$$ trong trình duyệt (AudioWorklet + WASM/ONNX). Để đảm bảo không bao giờ giật tiếng (buffer underrun) trên laptop tầm trung khi còn chạy kèm WebRTC AEC và video, đội kỹ thuật đặt trần an toàn:
- Thời gian suy luận tối đa mỗi khung: $$T_{\max} = 2{,}5\text{ ms}$$ (tương ứng $$\mathrm{RTF} \le 0{,}25$$).
- Tổng độ trễ thuật toán tối đa: $$L_{\max} = 40\text{ ms}$$.

Ta đặt lên bàn cân một phép tính nhanh cho 3 kịch bản nâng cấp giả định so với nền **DeepFilterNet3** (đang chạy $$T_{\text{base}} = 0{,}8\text{ ms/khung}$$, $$\mathrm{RTF} = 0{,}08$$, độ trễ $$40\text{ ms}$$):

| Kịch bản nâng cấp | Phép tính chi phí cốt lõi | Thời gian / khung ước tính | Độ trễ thuật toán | Quyết định kỹ thuật |
| :--- | :--- | :---: | :---: | :--- |
| **1. Thêm Self-Attention toàn cục dọc $$F = 96$$ bin (Dual-Path ngây thơ)** | Số cặp tương tác mỗi khung tăng từ $$O(F) = 96$$ lên $$O(F^2) = 96^2 = 9\,216$$ (gấp $$96\times$$ tương tác) | Giả sử đội $$3\times \to 2{,}4\text{ ms}$$ ($$\mathrm{RTF}=0{,}24$$) | $$40\text{ ms}$$ | **Rủi ro cao** — sát trần $$2{,}5\text{ ms}$$, dễ rớt khung khi CPU bận |
| **2. Huấn luyện lại Generator cũ bằng Discriminator (hướng GAN)** | Discriminator bỏ hoàn toàn khi xuất ONNX $$\implies +0\text{ ms}$$ suy luận | $$0{,}8\text{ ms}$$ ($$\mathrm{RTF}=0{,}08$$) | $$40\text{ ms}$$ | **Đáng thử** — miễn là vượt qua bài nghe mù không sinh lỗi giả |
| **3. Thêm 1 tầng tinh chỉnh phân cấp cần thêm $$1$$ khung nhìn trước** | Độ trễ cộng thêm $$+1 \times H = +10\text{ ms}$$ | Giả sử $$1{,}3\text{ ms}$$ ($$\mathrm{RTF}=0{,}13$$) | $$40 + 10 = 50\text{ ms}$$ | **Vượt trần độ trễ** $$L_{\max} = 40\text{ ms}$$ — cần cân nhắc kỹ với VoIP |

Bảng tính gọn này minh họa một nguyên tắc vàng của kỹ thuật âm thanh thực chiến: **chỉ chuyển đổi mô hình khi bạn chứng minh được bằng con số rằng nó sửa được một lỗi nghe tái hiện được mà không phá vỡ trần RTF và độ trễ của sản phẩm**.

## Mục tiêu học tập

Sau bài học này, bạn sẽ tóm tắt được trọng tâm nghiên cứu gắn với từng cái tên DPDFNet, DeepFilterGAN và HDF-Net; tuân thủ nguyên tắc không trích dẫn tiêu đề hay năm xuất bản nếu chưa đọc trực tiếp PDF; và ra quyết định triển khai, theo dõi hay bỏ qua dựa trên RTF, khả năng hỗ trợ toán tử ONNX và một lỗi nghe tái hiện được.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao một tên mô hình mới chưa phải là kế hoạch chuyển đổi (migration).
- **10–25 phút** — Mẫu thẻ đọc bốn ô: chỉ ghi nhận những gì kiểm chứng được từ tài liệu gốc.
- **25–40 phút** — Chi phí thực tế của "dual-path", "tầng GAN" và "bộ lọc phân cấp" bên trong AudioWorklet.
- **40–50 phút** — Hiện tượng suy hao quá mức (over-attenuation) như một lỗi sản phẩm độc lập.
- **50–60 phút** — Mini-lab và quy tắc chuẩn hóa trích dẫn.

## Giải thích cốt lõi

### Phạm vi khẳng định hợp lệ của một bài khảo sát

Bài 04-02 và 04-03 trích dẫn bảng số liệu vì các bảng đó xuất hiện trực tiếp trong arXiv:2110.05588, arXiv:2205.05474 và arXiv:2305.08227. Bài này không đặt thêm trích dẫn mới mà chỉ định vị ba cái tên trên bản đồ đọc:

- **DPDFNet** — cái tên thường được tra cứu khi cần giải quyết bài toán ngữ cảnh dài và hiện tượng khử quá mức (over-attenuation) trên khung kiểu DeepFilterNet2.
- **DeepFilterGAN** — cái tên thường được tra cứu khi nối thêm một tầng sinh (generative) phía sau tầng dự đoán kiểu DeepFilterNet nhằm khôi phục phần chi tiết giọng nói đã bị xóa.
- **HDF-Net** — cái tên thường được tra cứu khi cơ chế deep filtering được phân tách phân cấp theo thời gian và tần số thay vì dùng một đầu lọc đơn lẻ.

Ba mô tả trên chỉ mang tính định hướng tra cứu chứ không phải tóm tắt bài báo, do đó không đi kèm số tham số, độ chênh PESQ, biểu đồ hay đường dẫn. Một số cái tên lân cận (cũng chỉ nêu ở mức định hướng, không trích dẫn) gồm pDeepFilterNet2 (cá nhân hóa theo người nói) và DFingerNet (điều kiện theo dấu vân nhiễu) — hướng cá nhân hóa nằm ngoài phạm vi trừ khi đề tài tổng kết yêu cầu riêng.

### Mẫu thẻ đọc bốn ô

Với mỗi tệp PDF thực sự mở đọc, hãy ghi nhận đúng bốn mục sau:

1. **Bài toán** tác giả đo lường (suy hao quá mức, mất họa âm, giới hạn độ trễ).
2. **Cơ chế** theo đúng tên khối được in trong bài báo gốc.
3. **Khả năng triển khai:** số lượng tham số (nếu công bố), đồ thị có nhân quả hay không, có thông tin xuất ONNX hoặc đo RTF hay không.
4. **Hành động:** bỏ qua, tiếp tục theo dõi hoặc làm thử nghiệm (prototype) — bản thử nghiệm phải xác định rõ hop, thiết bị đích và đoạn mẫu nghe thử.

Nếu mục 3 bị bỏ trống vì bài báo không đề cập đến streaming, hành động chắc chắn không phải là "triển khai". Các mô hình đứng đầu bảng xếp hạng dùng lớp hồi tiếp hai chiều sẽ không thể chạy trong hàm `process()`.

### Phân tích chi phí giả định (ở thể điều kiện)

Phần này dịch ý nghĩa kỹ thuật của **tên kiến trúc** để ước lượng ngân sách cho một đợt thử nghiệm khảo sát (spike), không phải tóm tắt kết quả từ bài báo gốc.

Cấu trúc **dual-path** (gắn với tên DPDFNet) xử lý song song hoặc luân phiên một nhánh theo thời gian và một nhánh theo tần số. Với hop 10 ms, nhánh thời gian bắt buộc phải duy trì trạng thái GRU cố định hoặc chờ thêm các hop tương lai. Chờ thêm 4 hop tương lai đồng nghĩa cộng thêm 40 ms lên trên độ trễ 40 ms đã công bố của DeepFilterNet2, đẩy tổng độ trễ thuật toán lên 80 ms (con số này tách biệt với RTF), đồng thời hai khối GRU có thể làm tăng gấp đôi phân vị p95. Lưu ý rằng hiện tượng suy hao quá mức (như mất các phụ âm xát nhẹ) hoàn toàn có thể kiểm chứng thực tế trên sản phẩm mà không cần chờ bài báo mới.

**Tầng tái tạo GAN** (gắn với tên DeepFilterGAN) đặt thêm một mạng thứ hai sau tầng dự đoán. Dù chạy hai phiên ONNX hay gộp thành một đồ thị, hệ thống đều gánh thêm chi phí MAC và khó bảo đảm tính tất định trong `process()`. Trên bề mặt gói npm hiện có, cường độ khử đã có thể điều chỉnh qua `setSuppressionLevel(0–100)` — hãy thử hạ mức khử trước khi tính đến việc bổ sung mạng GAN.

**Deep filter phân cấp** (gắn với tên HDF-Net) vẫn dựa trên phép lọc phức dạng:

$$
\hat{S}(t,f)=\sum_{i} W_i(t,f)\,X(t-i+\ell,f),
$$

nhưng tách thành nhiều đầu lọc. Riêng 5 tap trên 96 bin đã tiêu tốn 480 phép nhân phức mỗi khung (bài 04-02); một đầu lọc bổ sung theo trục tần số có thể kết hợp thêm các bin lân cận, còn tính nhân quả cụ thể phải kiểm tra trực tiếp trên sơ đồ của bài báo gốc.

### Phân loại sản phẩm dựa trên mốc DF3 đã kiểm chứng

Bảng số liệu duy nhất của DeepFilterNet3 được trích dẫn trong khóa là kết quả Voicebank+Demand từ arXiv:2305.08227: PESQ 3,17, CSIG 4,34, CBAK 3,61, COVL 3,77 và STOI 0,944 (so với PESQ 3,08 của DF2), cùng các số đo RTF đã công bố là 0,04 (DF2 trên laptop Core i5) và 0,19 (bản `tract` năm 2023 trên i5-8250U). Một kiến trúc kế tục chỉ đáng đầu tư thử nghiệm khi tệp âm thanh sản phẩm bộc lộ lỗi mà các checkpoint trên không xử lý được, đồng thời đồ thị nhân quả vẫn đáp ứng kịp hop 10 ms (nhớ rằng quantum 2,67 ms là đơn vị callback, không phải ngân sách hop).

| Tên | Ý tưởng định hướng | Triển khai từ bài này? | Lý do |
|-----|--------------------|------------------------|-------|
| DPDFNet | Ngữ cảnh dual-path; thường tra cứu cho lỗi suy hao quá mức | Không | Chưa có tiêu đề, năm xuất bản hay URL kiểm chứng trong bài |
| DeepFilterGAN | Tầng dự đoán nối tiếp tầng sinh | Không | Phát sinh mạng thứ hai; chưa rõ RTF và tính tất định khi chưa đọc gốc |
| HDF-Net | Deep filter phân cấp | Không | Tương tự trên |
| Mốc DeepFilterNet3 | 32 băng ERB + bộ lọc 5 tap (trích dẫn 2023 trong README) | Có (làm mốc chuẩn khóa học) | Số liệu kiểm chứng đầy đủ ở bài 04-03 |

Các tầng tiền xử lý không gian ở Chương 03 (GSC hoặc IVA nối vào bộ tăng cường đơn kênh) thuộc một hướng mở rộng khác vì chúng thay đổi số lượng micro; chúng ở mức kiến trúc lai tham khảo, không phải lý do để loại bỏ DF3.

## Bẫy thường gặp

- Viết lại toàn bộ đồ thị ONNX chỉ sau khi đọc lướt phần tóm tắt (abstract).
- Tự điền tiêu đề, năm xuất bản hoặc mã arXiv theo trí nhớ cho DPDFNet, DeepFilterGAN hay HDF-Net.
- Cho rằng bổ sung tầng GAN vẫn giữ nguyên được phân vị p95 của tầng dự đoán ban đầu.
- Đưa vào một toán tử lọc tùy biến mà `tract` hoặc ONNX Runtime WASM không hỗ trợ rồi mới phát hiện lỗi trên luồng âm thanh.

## Mini-lab

**Mục tiêu.** Khởi tạo mẫu thẻ bốn ô với mọi trường chưa kiểm chứng để giá trị trống (`None`) nhằm ngăn việc điền thông tin trích dẫn suy đoán.

```bash
python3 - << 'PY'
names = ["DPDFNet", "DeepFilterGAN", "HDF-Net"]
# Fill only from a PDF you opened. Leave unknown fields as None.
cards = {
    name: {"problem": None, "mechanism": None, "params": None,
           "causal": None, "url": None, "year": None, "title": None}
    for name in names
}
for name, card in cards.items():
    missing = [k for k, v in card.items() if v is None]
    print(f"{name}: missing={missing}")
print("survey_pointers_only=True")
PY
```

**Kết quả kỳ vọng.** Mỗi cái tên đều in `missing=['problem', 'mechanism', 'params', 'causal', 'url', 'year', 'title']` cho đến khi bạn tự điền từ tệp PDF đã mở, và dòng cuối in `survey_pointers_only=True`.

**Lỗi thường gặp.** Chép tiêu đề hoặc năm từ đoạn trích tìm kiếm mà chưa mở bài gốc; điền `params` bằng con số không có trong PDF; coi trường `causal` bỏ trống là "đủ nhân quả"; hoặc gắn các đường dẫn chưa được kiểm chứng.

## Bài tập

1. **Điền thẻ bốn ô.** Sau khi tự tìm và mở đọc từng tệp PDF gốc, hãy điền đầy đủ bốn ô; nếu không tiếp cận được tệp gốc thì để trống và ghi rõ lý do.
2. **Kiểm chứng suy hao quá mức không cần bài báo.** Ghi âm 10 giây chứa các phụ âm xát nhẹ (như "see", "fish") ở hai mức âm lượng vừa và nhỏ, cho chạy qua đường DF3 tại mức `setSuppressionLevel` 30 và 90, rồi mô tả sự khác biệt nghe thấy trong hai câu.
3. **Ngân sách độ trễ.** Nếu một khối dual-path cần chờ thêm 4 hop dài 10 ms chồng lên độ trễ 40 ms đã công bố của DeepFilterNet2, tổng độ trễ thuật toán là bao nhiêu và tổng đó có phải là RTF không?
4. **Bản ghi nhớ kỹ thuật.** Trong tối đa 150 từ, đề xuất với trưởng nhóm kỹ thuật nên giữ nguyên mốc DF3 hay mở một đợt thử nghiệm đọc tài liệu; chỉ được phép trích dẫn arXiv:2110.05588, arXiv:2205.05474 và arXiv:2305.08227.

### Gợi ý đáp án

1. Một thẻ để trống trung thực có giá trị hơn một tiêu đề suy đoán; phần cơ chế phải dùng đúng thuật ngữ xuất hiện trong PDF gốc.
2. Bạn sẽ nghe thấy sự khác biệt rõ ở việc phụ âm nhẹ bị cắt mất hoặc phần đuôi âm bị khô/bơm chứ không phải một con số MOS; tham số `setSuppressionLevel` nằm trên thang 0–100, không phải giá trị dB trong bài báo.
3. Tổng độ trễ thuật toán là $$40+4\times 10=80$$ ms nếu khối đó bổ sung thêm look-ahead; RTF là tỷ số thời gian xử lý thực tế trên thời lượng âm thanh nên có thể bằng 0,2 hoặc 1,4 hoàn toàn độc lập với mốc 80 ms.
4. Mốc chuẩn có cơ sở bảo vệ là kết quả DF3 từ trích dẫn năm 2023 cùng các thông số 40 ms và RTF đã công bố; đợt thử nghiệm nên giới hạn ở việc đọc tài liệu gốc và chạy kiểm thử khói (smoke test) đồ thị ONNX nhân quả, không viết lại hệ thống ngay.

## Đọc thêm

- Bài 04-02 và 04-03 cùng ba nguồn đã kiểm chứng: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [arXiv:2205.05474](https://arxiv.org/abs/2205.05474) và [arXiv:2305.08227](https://arxiv.org/abs/2305.08227).
- Các tệp PDF gốc bạn tự tra cứu cho DPDFNet, DeepFilterGAN và HDF-Net (bài học này cố ý không gắn đường dẫn cho chúng).
- Chương 05 cho các ràng buộc RTF và AudioWorklet mà mọi kiến trúc kế tục đều phải đáp ứng.

## Video tham khảo

- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. **Xem trước.** Trình bày khung ERB + deep filter dùng làm mốc so sánh với các mô hình kế tục trong bài.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, tiếng Anh. Phần dữ liệu, nghe thử và độ phức tạp cung cấp khung phương pháp so sánh khách quan trước khi quyết định nâng cấp mô hình.
