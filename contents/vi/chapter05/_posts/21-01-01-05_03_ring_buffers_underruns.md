---
layout: post
title: "05-03 Ring buffer và underrun"
chapter: "05"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter05
lesson_type: required
draft: false
---

Một hop của DeepFilterNet dài 480 mẫu, trong khi một render quantum của AudioWorklet (luồng render của Web Audio) thường chỉ dài 128 mẫu. Hai nhịp đồng hồ khác nhau này được nối với nhau bằng một **bộ đệm vòng (ring buffer)**: một mảng có kích thước cố định đi kèm chỉ số đọc và chỉ số ghi. Khi bên đọc tiêu thụ nhanh hơn khiến bộ đệm cạn dữ liệu, ta gặp lỗi **underrun** (gây tiếng tách hoặc khoảng mất tiếng). Ngược lại, khi bên ghi đẩy dữ liệu vào nhanh hơn và vượt quá chỗ trống, ta gặp lỗi **overrun** (khiến độ trễ phình dần cho đến khi buộc phải bỏ bớt mẫu hoặc chuyển sang bypass). Bài học này hướng dẫn cách tính dung lượng ring buffer và cài đặt cả hai chính sách xử lý trên mô hình minh họa 8 mẫu.

![Bộ đệm vòng với chỉ số ghi đi trước chỉ số đọc]({{ site.imgurl }}/generated/ring-buffer.png)

*Hình. Một mảng bộ nhớ có kích thước cố định. Bên ghi tăng `write_pos` mỗi khi một quantum mới đến; bên đọc tăng `read_pos` mỗi khi đủ một hop để xử lý. Mức chiếm chỗ (occupancy) là khoảng cách giữa hai chỉ số này. Vùng tô xám chính là trạng thái duy nhất phải được giữ nguyên sang callback kế tiếp, và dung lượng mảng không bao giờ tự mở rộng.*

## Mục tiêu học tập

Sau bài học này, bạn sẽ tính được mức chiếm chỗ (occupancy) và số chỗ trống sau khi ghi 6 mẫu rồi đọc 4 mẫu; cài đặt được chính sách xử lý overrun bằng cách bỏ mẫu cũ nhất thay vì cấp phát thêm bộ nhớ; và chọn được dung lượng lũy thừa của hai phù hợp cho hop 480 mẫu, quantum 128 mẫu cùng một khoảng dự phòng jitter nhỏ mà không vô tình cộng thêm 100 ms độ trễ vào bộ đệm.

## Kế hoạch 60 phút

- **0–10 phút** — Tiếng tách, mất tiếng (dropout) và độ trễ phình dần nghe như thế nào trong thực tế.
- **10–25 phút** — Chỉ số đọc/ghi, mặt nạ bit, mức chiếm chỗ và ví dụ minh họa ghi 6 rồi đọc 4.
- **25–40 phút** — Hai ring buffer bao quanh một hop 10 ms và phép tính dung lượng.
- **40–50 phút** — Chọn bỏ mẫu hay chuyển sang bypass khi bên ghi chạy trước.
- **50–60 phút** — Thực hành mini-lab và làm bài tập.

## Giải thích cốt lõi

### Cơ chế hoạt động

Dữ liệu PCM được lưu trong một mảng có độ dài $$C$$, trong đó nên chọn $$C=2^m$$ để thao tác quay vòng chỉ số chỉ cần phép toán bit `index & (C-1)` mà không phải dùng phép chia trên luồng âm thanh. Với mô hình một bên ghi và một bên đọc (SPSC — single-producer single-consumer), ta chỉ cần duy trì hai chỉ số. Số mẫu sẵn có (occupancy) và số chỗ trống được xác định như sau:

$$
\mathrm{available}=(\mathrm{write\_pos}-\mathrm{read\_pos})\bmod C,\qquad \mathrm{free}=C-\mathrm{available}.
$$

Nếu duy trì thêm một biến đếm số phần tử như trong bài lab, bạn không cần tính phép chia dư cho mọi phép kiểm tra, nhưng vẫn phải quay vòng chỉ số khi ghi hoặc đọc. Bên ghi chỉ được phép ghi $$n$$ mẫu khi $$\mathrm{free}\ge n$$, và bên đọc chỉ được phép đọc $$n$$ mẫu khi $$\mathrm{available}\ge n$$. Vi phạm điều kiện này sẽ gây lỗi ngay lập tức: ghi vượt quá chỗ trống sẽ ghi đè lên các mẫu chưa kịp phát, còn đọc vượt quá số mẫu hiện có sẽ phát lặp lại dữ liệu PCM cũ hoặc toàn số 0.

Phần cung tô xám trong hình minh họa chính là mức chiếm chỗ — một dạng trạng thái streaming. Nếu xóa trắng mảng mỗi lần bật hoặc tắt bộ khử nhiễu, phần dữ liệu này bị vứt bỏ và người nghe sẽ nghe thấy một khoảng khựng (xem bài 05-04).

### Vị trí của các ring buffer trong chuỗi xử lý

```text
quantum mic (128) → ring A → gom 480 → hop NS → ring B → quantum ra (128)
```

Ring A có nhiệm vụ quy đổi nhịp “3,75 quantum cho mỗi hop” thành từng hop nguyên vẹn. Vì $$480/128=3{,}75$$, sau 3 callback đầu tiên ring A chứa 384 mẫu nên hop chưa thể chạy; đến callback thứ 4, ring A đạt 512 mẫu, hop lấy đi 480 mẫu và để lại 32 mẫu. Ở đầu ra, ring B nhận khối 480 mẫu sau bước overlap-add rồi nhả dần ra từng quantum 128 mẫu. Không nên dùng chung một ring buffer duy nhất cho cả hai nhịp đồng hồ nếu không kiểm soát chặt quyền ghi, bởi micro và mô hình xử lý sẽ trở thành hai bên ghi cùng tranh chấp một bộ đệm. Cách thiết kế an toàn là cấp riêng một ring buffer cho mỗi chiều.

### Tính toán dung lượng

Gọi độ dài hop là $$H$$ mẫu, độ dài quantum là $$Q$$ mẫu, và $$J$$ là số hop dự phòng cho dao động thời gian (jitter) mà hệ thống cần hấp thụ:

$$
C \gtrsim H + J\cdot H + Q.
$$

Với $$H=480$$, $$Q=128$$ và $$J=2$$, ta có $$480+960+128=1568$$ mẫu; lũy thừa của hai lớn hơn kế tiếp là **2048** mẫu, tương ứng $$2048/48000\approx 42{,}7$$ ms ở riêng tầng đệm này. Nếu tăng $$J=3$$, tổng rơi đúng vào 2048 mẫu nên lũy thừa của hai kế tiếp có khoảng dư an toàn là **4096** mẫu (khoảng 85 ms). Khi cộng dồn hai tầng ring buffer cùng 40 ms look-ahead của mô hình, độ trễ hội thoại đã trở nên rất đáng kể. Mỗi lần nhân đôi dung lượng bộ đệm không cần thiết đều tạo thêm độ trễ mà người dùng sẽ quy lỗi cho bộ khử nhiễu.

### Underrun, overrun và hai chính sách xử lý

| Sự kiện | Điều kiện xảy ra | Cách xử lý chuẩn | Hệ quả nếu xử lý tùy tiện |
|---------|-----------|--------|------------------------------|
| Underrun đầu ra | Ring B có ít hơn $$Q$$ mẫu | Sao chép quantum tín hiệu gốc (bypass) hoặc fade ngắn về 0 | Gây tiếng tách hoặc một khoảng lặng đột ngột |
| Overrun đầu vào | Ring A có `free < n` | Bỏ các mẫu chưa đọc cũ nhất rồi ghi mẫu mới | Âm thanh nhảy cóc nhẹ, nhưng độ trễ được giữ trong giới hạn |
| Mô hình trễ hạn | Thời gian xử lý hop $$> 10$$ ms (RTF p95 $$> 1$$) | Giữ nguyên các mẫu đầu ra đã xếp hàng; bypass quantum mới đến khi hop đuổi kịp | Gây tiếng nứt liên tục nếu chặn luồng `process` |

Việc chặn luồng âm thanh để “chờ suy luận chạy xong” sẽ biến lỗi overrun thành hiện tượng đảo ưu tiên (priority inversion): quantum 2,67 ms chắc chắn sẽ trễ hạn trong lúc bạn giữ khóa. Cả hai chiến lược bypass và bỏ mẫu đều không chặn luồng. Bypass giữ đúng nhịp thời gian nhưng để lọt nhiễu nền; bỏ mẫu duy trì hoạt động của bộ khử nhiễu nhưng đánh đổi bằng việc mất một đoạn ngắn âm thanh. Nguyên tắc thực tế là bỏ mẫu cũ trên ring thu (vì mẫu micro cũ đằng nào cũng sẽ bị phát muộn) và dùng bypass trên ring phát (loa không thể đột ngột nhận toàn số 0 mà không fade, nhưng cũng không thể dừng lại chờ).

### Các chỉ số cần ghi log

Cần theo dõi `underrun_count`, `overrun_count`, mức chiếm chỗ cực đại (high-water mark) và mức chiếm chỗ cực tiểu (low-water mark), đồng thời đối chiếu số lần overrun với chỉ số RTF p95 ở bài 05-01. Nếu một ring buffer thường xuyên đầy tới 95%, đó là phần độ trễ thừa hoàn toàn có thể cắt giảm; ngược lại, mỗi lần ring buffer chạm mức 0 tương ứng với một tiếng tách đã phát tới tai người dùng.

## Bẫy thường gặp

- Để hai bên ghi cùng truy cập một ring buffer mà không có cơ chế đồng bộ tách biệt.
- Ghi dữ liệu stereo xen kẽ (interleaved) vào ring buffer dạng tách kênh (planar) hoặc ngược lại; bố cục kênh là một phần bắt buộc của phép tính dung lượng (dùng hai ring riêng hoặc mảng có kích thước $$2C$$).
- Tăng dung lượng $$C$$ quá lớn cho đến khi cuộc gọi có độ trễ như liên lạc qua vệ tinh (chỉ riêng 4096 mẫu đã chiếm 85 ms).
- Xóa trắng ring buffer mỗi khi người dùng tắt hoặc bật micro (mute/unmute); thay vào đó hãy tháo dần bộ đệm hoặc dùng crossfade (bài 05-04).

## Mini-lab

**Mục tiêu.** Trên một ring buffer dung lượng 8 mẫu, thực hiện ghi 6 mẫu, đọc 4 mẫu, in mức chiếm chỗ hiện tại, sau đó ghi thêm 7 mẫu theo chính sách xử lý overrun bỏ mẫu cũ nhất và quan sát các mẫu còn lại trong bộ đệm.

```bash
python3 - << 'PY'
import numpy as np

class Ring:
    def __init__(self, cap):
        self.buf = np.zeros(cap, dtype=np.float64)
        self.cap = cap
        self.w = 0
        self.r = 0
        self.n = 0
    def free(self):
        return self.cap - self.n
    def write(self, samples):
        if len(samples) > self.free():
            raise RuntimeError("overrun")
        for v in samples:
            self.buf[self.w] = v
            self.w = (self.w + 1) % self.cap
            self.n += 1
    def read(self, k):
        if k > self.n:
            raise RuntimeError("underrun")
        out = np.empty(k, dtype=np.float64)
        for i in range(k):
            out[i] = self.buf[self.r]
            self.r = (self.r + 1) % self.cap
            self.n -= 1
        return out
    def write_drop_oldest(self, samples):
        dropped = 0
        for v in samples:
            if self.free() == 0:
                self.r = (self.r + 1) % self.cap
                self.n -= 1
                dropped += 1
            self.buf[self.w] = v
            self.w = (self.w + 1) % self.cap
            self.n += 1
        return dropped

rb = Ring(8)
rb.write([1, 2, 3, 4, 5, 6])
print("after_write6", rb.n, rb.free())
got = rb.read(4)
print("read4", got.tolist(), "occ", rb.n)
dropped = rb.write_drop_oldest([10, 11, 12, 13, 14, 15, 16])
print("dropped", dropped, "occ", rb.n)
print("next4", rb.read(4).tolist())
PY
```

**Kết quả kỳ vọng.** `after_write6 6 2`, tiếp theo là `read4 [1.0, 2.0, 3.0, 4.0] occ 2`, sau đó `dropped 1 occ 8`, và cuối cùng `next4 [6.0, 10.0, 11.0, 12.0]`. Sau bước đọc 4 mẫu, ring buffer còn lại hai mẫu 5 và 6 (tức còn 6 chỗ trống). Khi ghi 7 mẫu mới, bộ đệm thiếu đúng 1 ô nên mẫu chưa đọc cũ nhất (5) bị loại bỏ; mẫu 6 được giữ lại, nối tiếp bởi 10, 11 và 12.

**Lỗi thường gặp.** Tự động nới rộng dung lượng mảng thay vì bỏ mẫu cũ (làm độ trễ tăng ngầm mà không để lại dấu vết trong log); chặn luồng khi `free < n`; áp dụng chính sách bypass nhưng vẫn kỳ vọng số mẫu bị bỏ như trên (chính sách bypass sẽ từ chối lần ghi đó và giữ nguyên mức chiếm chỗ bằng 2); hoặc quên quay vòng `w` và `r` theo phép chia dư cho 8 khiến mẫu 16 vượt ra ngoài biên mảng.

## Bài tập

1. **Theo dõi trạng thái.** Sau khi ghi 6 mẫu và đọc 4 mẫu trên một ring buffer dung lượng 8 mới khởi tạo, mức chiếm chỗ bằng bao nhiêu và những mẫu nào còn nằm trong bộ đệm?
2. **Chọn lũy thừa của hai.** Với $$H=480$$, $$Q=128$$ và $$J=3$$, hãy tính $$H+JH+Q$$ và lũy thừa của hai kế tiếp. Dung lượng đó tương ứng bao nhiêu mili giây ở tần số 48 kHz?
3. **Lựa chọn chính sách.** Ring buffer đầu vào chỉ còn 100 chỗ trống trong khi callback đưa tới 128 mẫu. Bạn chọn bỏ 28 mẫu cũ nhất hay bypass mô hình? Mỗi phương án tác động thế nào đến độ trễ?
4. **Tách riêng hai ring buffer.** Vì sao mô hình không được ghi 480 mẫu đầu ra ngược trở lại vào ring A?

### Gợi ý đáp án

1. Mức chiếm chỗ bằng 2; hai mẫu còn lại là 5 và 6 (các mẫu từ 1 đến 4 đã được đọc ra).
2. $$480+3\times 480+128=2048$$ vừa khít, nên chọn dung lượng 2048 sẽ không còn mẫu dự phòng nào. Cần chọn 4096 nếu muốn có bất đẳng thức nghiêm ngặt; mức này tương ứng $$4096/48000\approx 85{,}3$$ ms cho riêng một tầng đệm.
3. Nếu bỏ 28 mẫu cũ nhất trên ring thu: độ trễ được giới hạn cố định và âm thanh bị nhảy qua 28 mẫu ($$28/48000\approx 0{,}58$$ ms). Nếu chọn bypass: mô hình không xử lý quantum này, độ trễ không tăng nhưng nhiễu nền đi thẳng qua đầu ra. Chặn luồng chờ không phải là lựa chọn hợp lệ.
4. Bên ghi của ring A là micro; nếu mô hình cũng ghi vào ring A thì sẽ xảy ra tranh chấp dữ liệu với callback quantum. Ring B tồn tại riêng để làm hàng đợi đầu ra cho mô hình.

## Đọc thêm

- Bài 05-01 về phân vị p95 giúp dự báo nguy cơ overrun, và bài 05-02 về nguồn cung cấp quantum 128 mẫu.
- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet), tài liệu về luồng render không được phép chặn khi `free` bằng 0.
- Ghi chú về kích thước bộ đệm của JACK hoặc PipeWire — tham khảo thêm một hệ thuật ngữ khác cho mối quan hệ giữa chu kỳ (period) và độ sâu bộ đệm vòng, không phải API bắt buộc phải gọi.

## Video tham khảo

- [Sonic Boom! Audio Programming on Android and Chrome (Google I/O'19)](https://www.youtube.com/watch?v=EeQr0zfvF04) — Google for Developers, tiếng Anh. **Xem trước.** Video phân tích sự chênh lệch giữa kích thước callback phần cứng và khối xử lý lớn hơn của thuật toán; ring buffer trong bài chính là cầu nối giữa hai nhịp đồng hồ đó.
- [AudioWorklet :: What, Why, and How - Hongchan Choi](https://www.youtube.com/watch?v=g1L4O1smMC0) — WebAudio PDX, tiếng Anh. Callback `process` đóng vai trò bên đọc không được phép chặn, và một lần đọc trên bộ đệm rỗng chính là hiện tượng underrun được trình bày trong bài.
