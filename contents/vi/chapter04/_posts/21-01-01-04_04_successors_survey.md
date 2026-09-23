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

Bài này là **bản đồ đọc**, không phải marathon cài đặt. Các kế tục được đặt tên mở rộng ý tưởng họ DeepFilterNet: **DPDFNet** (RNN dual-path trên backbone kiểu DF), **DeepFilterGAN** (tầng dự đoán DF + tái sinh GAN), và **HDF-Net** (deep filtering phân cấp). Ý tùy chọn gần đó: cá nhân hóa và điều kiện hóa “vân nhiễu”. Chỉ trích dẫn các công trình đã đặt tên—không bịa paper.

## Mục tiêu học tập

Bạn nêu được một ý cốt lõi cho từng DPDFNet, DeepFilterGAN, HDF-Net; quyết định đọc nào bắt buộc vs tùy chọn cho capstone Mezon; và giải thích survey ảnh hưởng roadmap sản phẩm thế nào mà không kích hoạt viết lại sớm.

## Kế hoạch 60 phút

- **0–10 phút** — Vì sao khảo sát kế tục nếu đang ship DF3.
- **10–25 phút** — DPDFNet: dual-path + chủ đề over-attenuation.
- **25–40 phút** — DeepFilterGAN: hai tầng dự đoán + generative.
- **40–50 phút** — Con trỏ HDF-Net; tùy chọn personalization / DFingerNet.
- **50–60 phút** — Bài triage capstone; bẫy.

## Giải thích cốt lõi

### Cách dùng survey trong khóa kỹ sư

Mỗi paper lấy đúng bốn trường:

1. **Vấn đề chẩn đoán** (over-attenuation, ngữ cảnh thời gian chậm, thiếu cấu trúc lọc tinh…).
2. **Cơ chế** (khối dual-path, regenerator GAN, DF phân cấp).
3. **Khả năng triển khai** (params, nhân quả?, có nhắc ONNX/TFLite?).
4. **Hành động Mezon** (bỏ qua / theo dõi / prototype).

### DPDFNet

**Ý:** chèn khối recurrent **dual-path** vào encoder kiểu DeepFilterNet2 để mạnh ngữ cảnh dài, vẫn giữ tư duy realtime. Paper cũng bàn loss **over-attenuation** và fine-tune always-on—liên quan trực tiếp khiếu nại sản phẩm (“NS ăn tiếng tôi”).

**Takeaway capstone:** nếu DF3 nghe đục trên lượt nói dài, đọc chẩn đoán DPDFNet trước khi phóng to mô hình mù quáng.

### DeepFilterGAN

**Ý:** giữ enhancer **dự đoán** kiểu DF2, thêm **GAN regenerator nhẹ** phục hồi thành phần tiếng bị dự đoán mạnh nuốt. Chiến lược hai tầng: predictor ổn định + chi tiết generative.

**Takeaway:** hai đồ thị ONNX (hoặc fuse) có thể thắng một predictor lớn hơn về cảm nhận—nhưng GAN làm phức tạp tính xác định streaming và RTF. Chỉ prototype nếu listening cho thấy over-suppression không đảo ngược được.

### HDF-Net

**Ý:** tổ chức deep filtering **thời gian vs tần số** phân cấp thay vì đầu lọc nguyên khối—vẫn DNA “deep filter”, footprint tham số nhỏ theo paper.

**Takeaway:** phương án kiến trúc nếu tự cài deep filter; không bắt buộc để ship weight DF3.

### Đọc tùy chọn (mức tên)

- **pDeepFilterNet2** — embedding người nói cho SE cá nhân hóa.
- **DFingerNet** — điều kiện hóa vân nhiễu kiểu hearing aid.
- Coi là **tùy chọn** trừ khi capstone nhắm cá nhân hóa.

### Hybrid cổ điển + neural (nhắc Ch. 03)

Kế tục chủ yếu neural mono. Nhớ GSC+DeepFilterNet2 và IVA+GTCRN khi có phần cứng không gian—“kế tục” quan trọng có thể là **front-end**, không phải GAN mới.

## Bảng triage capstone (điền trên lớp)

| Công trình | Ý 6 từ | Ship ngay? | Theo dõi? |
|------------|--------|------------|-----------|
| DPDFNet | Dual-path + bớt over-attenuation | | |
| DeepFilterGAN | GAN phục hồi tiếng bị nuốt | | |
| HDF-Net | Deep filter phân cấp | | |
| DF3 (baseline) | Mặc định sản phẩm | Có | |

## Bẫy thường gặp

- Viết lại mô hình production sau một abstract INTERSPEECH.
- Trích paper chưa mở (takeaway bịa).
- Coi chất lượng GAN “miễn phí” ở RTF AudioWorklet.
- Bỏ qua độ phủ op ONNX cho dual-path / lớp tùy biến.

## Bài tập

1. Thẻ bốn trường cho từng trong ba paper đã tên.
2. Listening phát hiện over-suppression (phụ âm nhẹ); đề xuất metric/checklist.
3. Memo 200 từ cho tech lead: ở DF3 vs spike DPDFNet—bảo vệ bằng RTF và rủi ro.
4. Vệ sinh trích dẫn: dòng thư mục đầy đủ từ nguồn sơ cấp cho ba công trình.

## Đọc thêm

- DPDFNet (arXiv / dual-path kế DeepFilterNet2).
- DeepFilterGAN (INTERSPEECH / arXiv).
- HDF-Net (INTERSPEECH / arXiv).
- Tùy chọn: pDeepFilterNet2, DFingerNet.
