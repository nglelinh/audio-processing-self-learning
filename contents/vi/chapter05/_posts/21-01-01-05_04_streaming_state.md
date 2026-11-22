---
layout: post
title: "05-04 Trạng thái mô hình streaming"
chapter: "05"
order: 4
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter05
lesson_type: required
draft: false
---

Một bộ tăng cường giọng nói chạy theo luồng (streaming) là hàm của cả hop hiện tại lẫn toàn bộ trạng thái (state) được giữ lại từ hop trước đó: đuôi chồng lấp của STFT (short-time Fourier transform, biến đổi Fourier thời gian ngắn), véctơ trạng thái của GRU (gated recurrent unit, đơn vị hồi tiếp có cổng), lịch sử khung của bộ lọc sâu (deep filter) và các mẫu chưa đọc trong ring buffer. Nếu xóa trắng cụm trạng thái này giữa cuộc gọi, hop kế tiếp sẽ không còn khớp với phần đuôi trước đó, khiến người nghe nghe thấy tiếng tách (click) hoặc một chùm nhiễu kéo dài bằng một hop.

![Ring buffer mà các mẫu chưa đọc là state phải sống qua hop kế]({{ site.imgurl }}/generated/ring-buffer.png)

*Hình. Cung chứa các mẫu chưa đọc trong ring buffer là một phần của trạng thái: nó phải nằm trên cùng vùng nhớ đó ở callback kế tiếp. Quy tắc tương tự áp dụng cho véctơ ẩn của GRU và cho 4 khung STFT quá khứ mà bộ lọc sâu 5 tap vẫn cần dùng. Xóa bất kỳ thành phần nào trong số này tại biên hop đều tạo ra một bước nhảy đột ngột, nghe thành tiếng tách hoặc một chùm nhiễu ngắn.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ liệt kê được đầy đủ các trạng thái mà một hop kiểu DeepFilterNet phải truyền ngược lại cho bước tiếp theo, tính được độ dài đuôi chồng lấp ở cấu hình cửa sổ 20 ms / hop 10 ms đã công bố, và áp dụng kỹ thuật chuyển mờ chéo (crossfade) khi tắt/bật tiếng (mute) thay vì xóa trắng phần đuôi đó.

## Kế hoạch 60 phút

- **0–10 phút** — Phân tích một tiếng tách lúc bật khử nhiễu và truy vết về lỗi xóa đuôi chồng lấp.
- **10–25 phút** — Kiểm kê trạng thái: ring buffer, đuôi STFT, GRU, lịch sử 5 tap và cổng SNR.
- **25–40 phút** — Tắt tiếng (mute), đổi thiết bị và underrun: ba tình huống reset khác nhau.
- **40–50 phút** — Cuộc gọi kéo dài và hiện tượng trôi trạng thái (drift).
- **50–60 phút** — Thực hành mini-lab và làm bài tập.

## Giải thích cốt lõi

### Những thành phần trạng thái phải được duy trì sang hop kế tiếp

| Trạng thái | Kích thước ở 48 kHz | Hệ quả nếu xóa giữa cuộc gọi |
|-------|-------------|------------------------|
| Ring buffer đầu vào | 0–479 mẫu đang chờ đủ hop 480 mẫu | Tạo khoảng trống âm thanh hoặc lặp lại một quantum |
| Đuôi cộng chồng (OLA) | **480 mẫu = 10 ms** | Tạo bước nhảy biên độ kéo dài 10 ms, nghe thành tiếng tách |
| Trạng thái ẩn GRU | 256 phần tử trong cấu hình DeepFilterNet2 | Hệ số khuếch đại nhảy đột ngột về trạng thái khởi tạo, thường gây chùm nhiễu |
| Lịch sử bộ lọc sâu | 4 khung quá khứ trên 96 bin tần số thấp (demo 2023) | Các thành phần hài bị sụt giảm trong tối đa 4 hop (40 ms) |
| Bộ chuẩn hóa mức tín hiệu | Trung bình trượt mũ, hằng số suy giảm 1 s (đặc trưng ICASSP) | Mức âm lượng bị nhảy bậc trong khoảng một giây |
| Cổng SNR | Giá trị $$\xi$$ đang cập nhật liên tục (bài 04-03) | Gây im lặng đột ngột nếu ép $$\xi<-10$$ dB |
| Hệ số khuếch đại làm trơn | Một giá trị cho mỗi băng tần ($$\lambda=0{,}6$$ trong RNNoise) | Tạo gai khuếch đại kéo dài một khung |

ONNX Runtime chỉ duy trì cụm trạng thái này nếu đồ thị mô hình khai báo rõ các tensor trạng thái ở đầu vào/đầu ra và bạn sao chép đầu ra của hop này đưa ngược lại làm đầu vào cho hop kế tiếp. Một lời gọi không trạng thái (stateless) vẫn trả về tensor hợp lệ về mặt cú pháp, nhưng đó không phải là bộ khử nhiễu streaming đúng nghĩa. Việc khởi tạo lại session ở mỗi hop cũng phá vỡ hoàn toàn ngân sách RTF (real-time factor, hệ số thời gian thực; xem bài 05-01). Nguyên tắc bất di bất dịch là mỗi cuộc gọi sở hữu một véctơ trạng thái riêng: nếu hai tab dùng chung một vùng trạng thái, chúng sẽ ghi đè cập nhật của nhau và cả hai đều phát ra tiếng tách.

### Hiện tượng nghe được khi reset trạng thái

Với cửa sổ 960 mẫu và hop 480 mẫu, mỗi khung sau khi biến đổi ngược sẽ giữ lại **480 mẫu (10 ms)** đuôi để cộng chồng vào khung kế tiếp. Nếu hop $$n$$ kết thúc ở biên độ khoảng 0,3 mà bạn xóa trắng phần đuôi này, tín hiệu đầu ra sẽ nhảy bậc một lượng xấp xỉ 0,3. Bước nhảy gián đoạn đó chính là tiếng tách, vì phần chồng lấp cần thiết để tái tạo liên tục cửa sổ đã bị loại bỏ.

Trong khi đó, xóa trạng thái GRU thường gây ra một chùm nhiễu ngắn. Khi bị ép về 0, các ước lượng SNR và hệ số khuếch đại ở một hoặc hai hop 10 ms đầu tiên sẽ phản ánh giá trị kích hoạt khởi tạo — thường là “không có giọng nói” hoặc “giữ nguyên biên độ (gain đầy)”. Giữ gain đầy trên các bin chứa nhiễu sẽ tạo thành một chùm nhiễu, còn cổng SNR ép $$\xi<-10$$ dB (bài 04-03) sẽ tạo thành một khoảng lặng hụt hơi. Cả hai hiện tượng đều xảy ra ngay thời điểm người dùng vừa bấm nút.

Do đó, xóa cứng bộ đệm là cách xử lý mute sai. Cách đúng là thực hiện chuyển mờ chéo (crossfade) từ tín hiệu đã xử lý (wet) sang tín hiệu gốc (dry) trong khoảng một hop (480 mẫu, tương ứng khoảng 3,75 quantum 128 mẫu). Nếu GRU vẫn được giữ ấm trong lúc bypass, chỉ cần áp dụng fade trên các mẫu trong ring buffer chứ không can thiệp vào trạng thái ẩn của mạng.

### Chính sách xử lý theo từng sự kiện

1. **Khởi động lạnh (cold start).** Khởi tạo toàn bộ trạng thái bằng 0 trước hop âm thanh nghe được đầu tiên, đồng thời chạy trước vài hop im lặng trước khi cuộc gọi bắt đầu để bộ chuẩn hóa 1 giây ổn định dần khỏi điểm 0 tuyệt đối.
2. **Bật bộ khử nhiễu.** Không xóa đuôi chồng lấp đang chứa tín hiệu gốc; thực hiện crossfade từ tín hiệu gốc sang tín hiệu đã xử lý trong 10–20 ms, đồng thời giữ GRU ở trạng thái ấm trong suốt thời gian bypass.
3. **Tắt bộ khử nhiễu.** Thực hiện crossfade từ tín hiệu đã xử lý sang tín hiệu gốc và đóng băng trạng thái GRU; nếu xóa trắng GRU, lần bật lại kế tiếp sẽ phát sinh một chùm nhiễu.
4. **Đổi thiết bị hoặc tần số lấy mẫu.** Thực hiện reset toàn bộ trạng thái và cập nhật lại độ dài hop. Một chuỗi quantum 44,1 kHz đưa vào bộ STFT thiết kế cho 48 kHz sẽ không thể khắc phục bằng crossfade.
5. **Underrun.** Chuyển sang bypass (bài 05-03) cho tới khi ring buffer đầu ra tích lũy đủ một hop rồi mới fade quay lại. Xóa đuôi chồng lấp mà không fade sẽ tạo ra thêm một tiếng tách ngay tại thời điểm bạn đang cố che giấu một tiếng tách khác.

### Cuộc gọi kéo dài

Một cuộc gọi dài 45 phút với hop 10 ms trải qua $$45\times 60\times 100=270\,000$$ bước cập nhật GRU liên tiếp. Hiện tượng trôi trạng thái (drift) là sự dịch chuyển chậm của véctơ ẩn theo thời gian — khiến âm thanh bị đục dần hoặc có cảm giác bơm tiếng — khác hẳn với tiếng tách đột ngột dài một hop. Lưu ý rằng bài 04-05 chỉ liệt kê Fast-ULCNet trong danh sách tham khảo cho chủ đề luồng dài, chứ không trích dẫn bài báo nào tại đây. Một biện pháp thực tế là kéo dần trạng thái về 0 trong vài trăm mili giây khi phát hiện khoảng lặng (kéo tức thì sẽ tương đương một lần reset), đồng thời so sánh bản ghi của cùng một đoạn âm thanh hiệu chuẩn ở phút thứ 1 và phút thứ 40 để kiểm tra độ ổn định.

### Vòng lặp phản hồi trạng thái

```text
state = initial   # zeros only before audio starts
for hop in stream:
    y, state = model(hop, state)
    emit y
```

Cần kiểm tra kích thước (shape) của từng tensor ngay lúc khởi tạo: đầu vào/đầu ra GRU (256 trong cấu hình DF2), 4 khung phức quá khứ dưới ngưỡng tần số của bộ lọc sâu, và đuôi chồng lấp 480 số thực. Nếu gán lệch thứ tự binding, mô hình sẽ đọc nhầm sang tensor kế tiếp và phát ra âm thanh méo như thể trọng số bị hỏng.

## Bẫy thường gặp

- Tạo session suy luận mới ở mỗi hop, vừa làm mất toàn bộ trạng thái vừa phá hỏng RTF.
- Dùng chung một đối tượng trạng thái cho hai tab trình duyệt khác nhau.
- Tua (seek) trong tệp âm thanh offline mà không reset trạng thái, khiến tệp thứ hai thừa kế trạng thái GRU từ tệp thứ nhất.
- Mặc định rằng khi tải lại AudioWorklet thì trạng thái bên trong WASM vẫn còn; thực tế mỗi module nạp mới đều là một lần khởi động lạnh.

## Mini-lab

**Mục tiêu.** Định lượng tác động của việc xóa trạng thái bằng một con số cụ thể. Xây dựng phép cộng chồng lấp (overlap-add) cho hai hop với đuôi chồng lấp dài 4 mẫu (mô hình thu gọn thay cho 480 mẫu), xuất kết quả bình thường, sau đó xóa trắng phần đuôi về 0 và so sánh sự chênh lệch.

```bash
python3 - << 'PY'
import numpy as np

def ola(prev_tail, frame):
    # frame layout: [overlap_with_previous | new_tail]
    mixed = prev_tail + frame[: len(prev_tail)]
    new_tail = frame[len(prev_tail) :].copy()
    return mixed, new_tail

frame0 = np.array([0.2, 0.2, 0.4, 0.4])  # tail that hop 1 will need
frame1 = np.array([0.4, 0.4, 0.1, 0.1])
mixed, tail = ola(frame0[2:], frame1)
print("continuous", mixed.tolist(), "tail", tail.tolist())
mixed_reset, tail_reset = ola(np.zeros(2), frame1)
print("after_zero_tail", mixed_reset.tolist())
print("step", float(mixed[0] - mixed_reset[0]))
PY
```

**Kết quả kỳ vọng.** `continuous [0.8, 0.8] tail [0.1, 0.1]`, `after_zero_tail [0.4, 0.4]`, và `step 0.4`. Ở đường xử lý liên tục, đuôi của khung trước (`[0.4, 0.4]`) được cộng vào phần chồng lấp của khung kế tiếp. Khi xóa đuôi về 0, phần đóng góp đó biến mất và đầu ra bị hụt một bậc bằng 0,4. Khi phóng đại lên hop thực tế 480 mẫu, bước nhảy gián đoạn đó sẽ nghe rõ thành một tiếng tách. Reset trạng thái GRU cũng có bản chất tương tự với một véctơ phức tạp hơn: hop đầu tiên sau khi xóa về 0 rơi vào trạng thái quá độ chưa từng gặp lúc huấn luyện, phát ra tiếng tách hoặc một chùm nhiễu.

**Lỗi thường gặp.** Xóa `tail` “cho chắc ăn” ở mỗi hop rồi tạo ra tiếng tách đều đặn sau từng hop; reset trạng thái khi mute mà không crossfade; dùng chung một biến `tail` cho hai luồng âm thanh khiến chúng cộng chồng lấp sang nhau; hoặc chẩn đoán nhầm bước nhảy 0,4 là lỗi RTF trong khi CPU vẫn xử lý đúng hạn còn nguyên nhân nằm ở quản lý trạng thái.

## Bài tập

1. **Kiểm kê trạng thái.** Với một hop kiểu DF3, hãy liệt kê 5 thành phần trạng thái quan trọng cùng đối tượng nắm giữ chúng (thuộc tính worklet, đầu vào ONNX hay ring buffer).
2. **Độ dài vùng bị ảnh hưởng.** Với cửa sổ 960 mẫu, hop 480 mẫu ở tần số 48 kHz, một lần reset cứng sẽ xóa mất bao nhiêu mili giây của phần đuôi chồng lấp?
3. **Chính sách vận hành.** Hãy viết ngắn gọn (mỗi tình huống một câu) cách xử lý khi mute, unmute và đổi micro. Trường hợp nào trong ba trường hợp này được phép xóa trạng thái GRU?
4. **Phân biệt trôi trạng thái và reset.** Một người dùng phản ánh nghe tiếng tách đúng lúc bật khử nhiễu, trong khi người khác báo âm thanh bị đục dần sau 40 phút gọi. Lỗi nào do reset trạng thái, lỗi nào do trôi trạng thái?

### Gợi ý đáp án

1. Năm thành phần gồm: các mẫu đang nằm trong ring buffer đầu vào, đuôi OLA 480 số thực, trạng thái ẩn GRU (256 phần tử trong cấu hình DF2; cần xác nhận lại trên I/O của file ONNX thực tế), 4 khung lịch sử của bộ lọc sâu, và trung bình trượt của đặc trưng ERB. Worklet quản lý các ring buffer; giao diện I/O của đồ thị quản lý trạng thái GRU nếu nó được tách thành tensor đầu vào.
2. $$480/48000=10$$ ms âm thanh. Đây là thời lượng của đoạn gián đoạn gây tiếng tách, không liên quan đến RTF.
3. Khi mute và unmute: áp dụng crossfade trong 10–20 ms và giữ/đóng băng trạng thái GRU. Khi đổi micro hoặc tần số lấy mẫu: reset sạch trạng thái khi chưa phát âm thanh, làm nóng mô hình trên vài hop im lặng rồi mới mở luồng. Chỉ trường hợp thứ ba mới được phép xóa GRU.
4. Tiếng tách xuất hiện đúng lúc bật tính năng là lỗi reset trạng thái. Âm thanh bị đục dần sau 40 phút (tương đương $$240\,000$$ hop) là hiện tượng trôi trạng thái hoặc suy giảm RTF do quá nhiệt; việc xóa trạng thái giữa câu nói không giải quyết được lỗi trôi.

## Đọc thêm

- Bài 04-02 và 04-03 về lịch sử 5 tap, GRU độ rộng 256 trong DeepFilterNet2 và cổng SNR trong [arXiv:2305.08227](https://arxiv.org/abs/2305.08227).
- Bài 05-03 về ring buffer giữ phần đuôi giữa các quantum 128 mẫu.
- Tài liệu I/O binding của ONNX Runtime về cách truyền ngược tensor trạng thái mà không cần khởi tạo lại session.
- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet), về vòng đời processor: nạp mới worklet đồng nghĩa tạo trạng thái mới và hop đầu tiên là khởi động lạnh.

## Video tham khảo

- [Gated Recurrent Unit | GRU | Explained in detail](https://www.youtube.com/watch?v=IBs8D8PWMc8) — Learn With Jay, tiếng Anh. **Xem trước.** Video giải thích cách cổng cập nhật duy trì trạng thái qua từng bước thời gian — đúng với vai trò véctơ GRU giữa các hop trong bộ khử nhiễu streaming.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, tiếng Anh. Bộ mã hóa GRU chính là trạng thái hồi tiếp không được phép xóa giữa cuộc gọi.
- [RNNoise, Neural Speech Enhancement, and the Browser](https://www.youtube.com/watch?v=nsscrYdrGRE) — W3C, tiếng Anh. Mô hình GRU gọn nhẹ xuất hệ số khuếch đại theo từng khung là ví dụ trực quan ở quy mô giảng dạy cho khái niệm trạng thái streaming.
