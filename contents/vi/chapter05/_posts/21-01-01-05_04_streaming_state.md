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

Một enhancer streaming là hàm của hop hiện tại và của state sống sót từ hop trước: đuôi chồng STFT (short-time Fourier transform, biến đổi Fourier thời gian ngắn), véctơ GRU (gated recurrent unit, đơn vị hồi tiếp có cổng), lịch sử deep filter, và các mẫu chưa đọc trong ring. Reset bó đó giữa cuộc gọi thì hop kế không khớp đuôi. Bạn nghe một click hoặc một chùm nhiễu dài một hop.

![Ring buffer mà các mẫu chưa đọc là state phải sống qua hop kế]({{ site.imgurl }}/generated/ring-buffer.png)

*Figure. Cung chưa đọc của ring là state: nó phải là cùng một vùng nhớ ở callback kế. Cùng luật áp cho véctơ GRU và cho bốn khung STFT quá khứ mà filter sâu 5 tap vẫn cần. Xóa cái nào ở biên hop cũng là một xung. Người nghe nghe thành click hoặc một chùm nhiễu ngắn.*

## Mục tiêu học tập

Bạn liệt kê state mà một hop kiểu DeepFilterNet đưa ngược lại, tính đuôi chồng ở khung 20 ms / 10 ms đã công bố, và crossfade khi mute thay vì xóa đuôi đó.

## Kế hoạch 60 phút

- **0–10 phút** — Một click lúc bật, truy ra đuôi chồng bị xóa.
- **10–25 phút** — Kiểm kê: ring, STFT, GRU, 5 tap, cổng SNR.
- **25–40 phút** — Mute, đổi thiết bị, underrun: ba lần reset khác nhau.
- **40–50 phút** — Cuộc gọi dài và trôi, không bịa paper.
- **50–60 phút** — Mini-lab, bài tập.

## Giải thích cốt lõi

### Cái gì phải là cùng một đối tượng ở hop kế

| State | Cỡ ở 48 kHz | Nếu xóa giữa cuộc gọi |
|-------|-------------|------------------------|
| Ring đầu vào | 0–479 mẫu đang chờ hop 480 mẫu | Một lỗ, hoặc một quantum lặp |
| Đuôi OLA | **480 mẫu = 10 ms** | Một bước 10 ms. Đó là click |
| GRU | 256 trong setup DeepFilterNet2 | Gain nhảy từ state khởi tạo: thường là một chùm nhiễu |
| Lịch sử deep filter | 4 khung quá khứ, 96 bin thấp trong demo 2023 | Hài rơi tối đa 4 hop (40 ms) |
| Bộ chuẩn hóa mức | Trung bình mũ, suy giảm 1 s (đặc trưng ICASSP) | Nhảy mức khoảng một giây |
| Cổng SNR | $$\xi$$ đang chạy (04-03) | Im lặng nếu bạn ép $$\xi<-10$$ dB |
| Gain đã làm trơn | Một giá trị mỗi băng ($$\lambda=0{,}6$$ trong RNNoise) | Một spike gain dài một khung |

ONNX Runtime chỉ giữ bó này nếu đồ thị phơi nó ra và bạn chép đầu ra về đầu vào lần kế. Một lời gọi không state vẫn trả một tensor; đó là enhancer sai. Session mới mỗi hop cũng phá RTF (real-time factor, hệ số thời gian thực; bài 05-01). Một véctơ state, một cuộc gọi. Hai tab dùng chung sẽ ăn cập nhật của nhau và cả hai đều click.

### Reset nghe như thế nào

Cửa sổ 960 điểm và hop 480 điểm cất **480 mẫu (10 ms)** mà khung kế phải cộng vào. Nếu hop $$n$$ kết thúc gần biên độ 0,3 và bạn xóa đuôi đó, đầu ra bước khoảng 0,3. Bước đó là một click: bạn đã bỏ phần chồng mà cửa sổ cần.

Reset GRU thường là một chùm. Từ số không, các ước lượng SNR và gain đầu tiên là thứ activation khởi tạo phát ra, thường là “không có tiếng” hoặc “gain đầy”, trong một hoặc hai hop 10 ms. Gain đầy trên bin nhiễu là một chùm nhiễu; cổng ép $$\xi<-10$$ dB (04-03) là một lỗ. Cả hai thẳng hàng với nút người dùng vừa bấm.

Xóa cứng là mute sai. Crossfade từ ướt sang khô trong một hop (480 mẫu, khoảng 3,75 quantum 128 mẫu). Fade các mẫu trong ring, không fade đơn vị ẩn, nếu GRU đã ấm trong lúc bypass.

### Chính sách

1. **Cold start.** Số không là đúng trước hop nghe được đầu tiên. Chạy vài hop im trước cuộc gọi để bộ chuẩn hóa 1 s rời đúng số không.
2. **Bật.** Đừng xóa đuôi đang giữ audio khô. Crossfade khô sang ướt trong 10–20 ms. Giữ GRU đã ấm trong lúc bypass.
3. **Tắt.** Crossfade ướt sang khô và đóng băng GRU. Xóa nó khiến lần bật sau thành một chùm.
4. **Thiết bị hoặc sample rate mới.** Reset đầy đủ và độ dài hop mới. Quantum 44,1 kHz vào STFT 48 kHz sẽ không fade thành đúng.
5. **Underrun.** Bypass (05-03) đến khi ring đầu ra giữ một hop, rồi fade. Xóa đuôi mà không fade thì click đúng lúc bạn đang giấu một click.

### Cuộc gọi dài

Cuộc gọi 45 phút ở hop 10 ms là $$45\times 60\times 100=270\,000$$ lần cập nhật GRU. Trôi là một bước đi chậm của véctơ đó (âm đục hoặc bơm), khác một click dài một hop. Bài 04-05 chỉ nêu Fast-ULCNet như mục shortlist cho thảo luận stream dài; không paper nào được trích ở đây. Hãy hòa state về không trong vài trăm mili giây im lặng. Hòa tức thì là một reset. So một clip hiệu chuẩn ở phút 1 và phút 40.

### Vòng phản hồi

```text
state = initial   # zeros only before audio starts
for hop in stream:
    y, state = model(hop, state)
    emit y
```

Kiểm shape một lần: GRU vào và ra (256 trong setup DF2), bốn khung phức quá khứ dưới ngưỡng deep filter, một đuôi 480 số thực. Binding lệch sẽ đọc tensor kế tiếp và nghe như mô hình hỏng.

## Bẫy thường gặp

- Session suy luận mới mỗi hop (mất state, mất RTF).
- Một đối tượng state dùng chung hai tab.
- Seek file offline mà không reset, nên file hai thừa kế GRU của file một.
- Cho rằng worklet nạp lại vẫn giữ state WASM. Module mới là cold start.

## Mini-lab

**Mục tiêu.** Nghe reset bằng một con số. Dựng đuôi chồng hai hop dài 4 mẫu (đồ chơi thay đuôi 480 mẫu), phát tổng, rồi xóa đuôi và phát lại.

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

**Expected**. `continuous [0.8, 0.8] tail [0.1, 0.1]`, `after_zero_tail [0.4, 0.4]`, `step 0.4`. Đường liên tục cộng đuôi trước (0,4, 0,4) vào phần chồng của khung kế. Xóa đuôi làm rơi phần đóng góp đó và đầu ra bước 0,4 trên các mẫu ấy. Phóng 0,4 lên hop thật 480 mẫu thì bước đó là một click. Reset GRU là cùng thí nghiệm với một véctơ khó vẽ hơn: hop đầu sau số không là một quá độ chưa được train, nghe thành click hoặc chùm nhiễu.

**Failure modes**. Xóa `tail` “cho an toàn” mỗi hop rồi ship một click mỗi hop. Reset khi mute mà không crossfade. Dùng chung `tail` cho hai stream nên mỗi hop cộng chồng của stream kia. Coi bước 0,4 là vấn đề RTF — CPU đúng giờ; state thì sai.

## Bài tập

1. **Kiểm kê.** Với một hop kiểu DF3, liệt kê năm đối tượng state và chủ sở hữu (trường worklet, đầu vào ONNX, ring).
2. **Độ dài click.** Cửa sổ 960, hop 480, sample rate 48 kHz. Một reset cứng đã xóa bao nhiêu mili giây đuôi?
3. **Chính sách.** Viết hành động mute, unmute và đổi mic, mỗi cái một câu. Cái nào được phép xóa GRU?
4. **Trôi và reset.** Một người báo click đúng lúc bật NS, người khác báo âm đục sau 40 phút. Lỗi nào là reset state, lỗi nào là trôi?

### Gợi ý đáp án

1. Occupancy ring đầu vào, đuôi OLA 480 số thực, GRU (256 trong setup DF2; xác nhận trên I/O ONNX), bốn khung lịch sử deep filter, và trung bình chạy của đặc trưng ERB. Worklet sở hữu các ring; I/O đồ thị sở hữu GRU nếu nó là một đầu vào.
2. $$480/48000=10$$ ms audio. Đó là độ dài của click, không phải RTF.
3. Mute và unmute: crossfade 10–20 ms và đóng băng GRU. Đổi mic hoặc sample rate: xóa khi chưa phát, warm-up trên im lặng, rồi mở mic. Chỉ trường hợp thứ ba được xóa GRU.
4. Click lúc bật là một reset. Âm đục sau 40 phút là trôi ($$240\,000$$ hop) hoặc RTF nhiệt. Xóa giữa câu không chữa trôi.

## Đọc thêm

- Bài 04-02 và 04-03 cho lịch sử 5 tap, GRU rộng 256 trong DeepFilterNet2, và cổng SNR trong [arXiv:2305.08227](https://arxiv.org/abs/2305.08227).
- Bài 05-03 cho ring giữ đuôi giữa các quantum 128 mẫu.
- Tài liệu I/O binding của ONNX Runtime, để đưa tensor state trở lại mà không dựng lại session.
- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet), cho đời processor: worklet mới là state mới, và hop đầu là cold start.
