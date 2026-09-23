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

Một hop DeepFilterNet là 480 mẫu. Một quantum AudioWorklet (luồng render của Web Audio) thường là 128. Hai đồng hồ đó gặp nhau trong một **ring buffer**: một mảng cố định cộng chỉ số đọc và chỉ số ghi. Khi bên đọc đuổi kịp bên ghi, bạn có **underrun** (một click hoặc một lỗ). Khi bên ghi vượt bên đọc, bạn có **overrun** (độ trễ lớn dần cho đến khi bạn bỏ mẫu hoặc bypass). Bài này định cỡ ring và hiện thực cả hai chính sách trên đồ chơi 8 mẫu.

![Bộ đệm vòng với chỉ số ghi đi trước chỉ số đọc]({{ site.imgurl }}/generated/ring-buffer.png)

*Figure. Một mảng cố định. Bên ghi tiến `write_pos` khi quantum đến; bên đọc tiến `read_pos` khi đủ một hop. Occupancy là khoảng cách giữa chúng. Vùng xám là state duy nhất phải sống sót sang callback kế. Dung lượng không lớn thêm.*

## Mục tiêu học tập

Bạn tính occupancy và chỗ trống sau khi ghi 6 mẫu và đọc 4 mẫu; hiện thực chính sách overrun bỏ mẫu cũ nhất thay vì cấp phát; và chọn dung lượng lũy thừa của hai cho hop 480 mẫu, quantum 128 mẫu, và một ngân sách jitter nhỏ mà không giấu thêm 100 ms độ trễ trong ring.

## Kế hoạch 60 phút

- **0–10 phút** — Click, dropout, và độ trễ lớn dần nghe như thế nào.
- **10–25 phút** — Chỉ số, mặt nạ, occupancy. Đồ chơi ghi 6 rồi đọc 4.
- **25–40 phút** — Hai ring quanh một hop 10 ms. Số học dung lượng.
- **40–50 phút** — Bỏ mẫu hay bypass khi bên ghi đi trước.
- **50–60 phút** — Mini-lab, bài tập.

## Giải thích cốt lõi

### Cơ học

Cất PCM trong mảng dài $$C$$, nên chọn $$C=2^m$$, để quấn là `index & (C-1)` không có phép chia trên luồng audio. Một producer và một consumer (SPSC) chỉ cần hai chỉ số. Occupancy và chỗ trống:

$$
\mathrm{available}=(\mathrm{write\_pos}-\mathrm{read\_pos})\bmod C,\qquad \mathrm{free}=C-\mathrm{available}.
$$

Nếu giữ một biến đếm như lab, bạn không tính modulo mỗi mẫu; bạn vẫn phải quấn chỉ số khi cất. Producer chỉ được ghi $$n$$ mẫu khi $$\mathrm{free}\ge n$$. Consumer chỉ được đọc $$n$$ khi $$\mathrm{available}\ge n$$. Làm ngược là lỗi: ghi quá chỗ trống phá mẫu consumer chưa phát, đọc quá chỗ có thì phát lại PCM cũ hoặc số không.

Cung xám trong hình là occupancy. Nó là state streaming. Xóa mảng mỗi lần bật tắt thì vứt cung đó và người nghe nghe một khoảng trống (bài 05-04).

### Ring nằm ở đâu

```text
quantum mic (128) → ring A → gom 480 → hop NS → ring B → quantum ra (128)
```

Ring A biến “3,75 quantum mỗi hop” thành một hop nguyên. $$480/128=3{,}75$$, nên sau ba callback ring A giữ 384 mẫu và hop chưa chạy; sau bốn callback nó giữ 512, hop tiêu 480, còn 32. Ring B giữ chùm overlap-add 480 mẫu và nhả 128 mẫu một lần. Một ring không phục vụ cả hai đồng hồ trừ khi bạn cẩn thận ai là producer: micro và mô hình là hai producer nếu bạn ngây thơ dùng chung một buffer. Hãy cho mỗi bên một ring.

### Dung lượng

Gọi độ dài hop là $$H$$ mẫu, quantum $$Q$$, và $$J$$ hop jitter thêm bạn chịu hấp thụ.

$$
C \gtrsim H + J\cdot H + Q.
$$

Với $$H=480$$, $$Q=128$$, $$J=2$$: $$480+960+128=1568$$, lũy thừa của hai kế tiếp là **2048** mẫu, $$2048/48000\approx 42{,}7$$ ms trong tầng đó. $$J=3$$ rơi đúng 2048, nên lũy thừa của hai an toàn kế tiếp là **4096** (85 ms). Hai tầng cộng look-ahead 40 ms của mô hình đã là độ trễ hội thoại dài. Mỗi lần nhân đôi thêm là độ trễ người dùng đổ cho suppressor.

### Underrun, overrun, và hai chính sách

| Sự kiện | Điều kiện | Làm gì | Người dùng nghe nếu bạn đoán |
|---------|-----------|--------|------------------------------|
| Underrun đầu ra | ring B ít hơn $$Q$$ mẫu | Chép quantum khô (bypass) hoặc fade ngắn về 0 | Một click, hoặc một lỗ im |
| Overrun đầu vào | ring A `free < n` | Bỏ các mẫu chưa đọc cũ nhất, rồi ghi | Nhảy tới. Độ trễ bị chặn |
| Mô hình trễ | thời gian tường hop $$> 10$$ ms (RTF p95 $$> 1$$) | Để nguyên đầu ra đã xếp hàng; bypass quantum mới đến khi hop đuổi kịp | Tiếng nứt nếu bạn chặn `process` |

Chặn luồng audio để “cho suy luận xong” biến overrun thành đảo ưu tiên. Quantum 2,67 ms sẽ hết hạn trong lúc bạn giữ khóa. Bypass và bỏ mẫu đều không chặn. Bypass giữ nhịp và để nhiễu lọt. Bỏ mẫu giữ suppressor và vứt audio. Hãy bỏ mẫu trên ring thu (mẫu mic cũ là mẫu bạn sẽ phát muộn) và bypass trên ring phát (loa không thể nhận im lặng mà không fade, nhưng cũng không thể chờ).

### Ghi gì

`underrun_count`, `overrun_count`, occupancy mực cao, occupancy mực thấp. Đối chiếu overrun với RTF p95 của bài 05-01. Ring ngồi ở 95% đầy là độ trễ thừa bạn cắt được. Ring chạm không là một click bạn đã ship.

## Bẫy thường gặp

- Hai producer, một ring, không có câu chuyện đồng bộ thứ hai.
- Stereo xen kẽ ghi vào ring planar, hoặc ngược lại. Bố cục kênh là một phần của phép tính dung lượng (hai ring, hoặc $$2C$$).
- Phóng $$C$$ đến khi cuộc gọi nghe như hop vệ tinh. 4096 mẫu đã là 85 ms.
- Xóa ring khi mute và unmute. Hãy tháo dần, hoặc crossfade (bài 05-04).

## Mini-lab

**Mục tiêu.** Trên ring dung lượng 8, ghi 6 mẫu, đọc 4, in occupancy, rồi ghi thêm 7 mẫu theo chính sách overrun bỏ mẫu cũ nhất và cho thấy cái gì còn.

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

**Expected**. `after_write6 6 2`, rồi `read4 [1.0, 2.0, 3.0, 4.0] occ 2`, rồi `dropped 1 occ 8`, rồi `next4 [6.0, 10.0, 11.0, 12.0]`. Sau lần đọc, ring còn giữ 5 và 6. Bảy mẫu mới cần thêm một ô, nên mẫu cũ nhất còn lại (5) bị bỏ. 6 sống sót, rồi 10, 11 và 12.

**Failure modes**. Tăng dung lượng thay vì bỏ mẫu (độ trễ lớn mà không có dòng log). Chặn khi `free < n`. Dùng chính sách bypass nhưng vẫn báo các số mẫu bị bỏ ở trên — bypass sẽ từ chối lần ghi và để occupancy ở 2. Quên quấn `w` và `r` bằng modulo 8, nên mẫu 16 rơi ra ngoài mảng.

## Bài tập

1. **Đồng nhất.** Sau `write 6` và `read 4` trên ring dung lượng 8 mới, occupancy là bao nhiêu, và mẫu nào còn được cất?
2. **Lũy thừa của hai.** $$H=480$$, $$Q=128$$, $$J=3$$. Tính $$H+JH+Q$$ và lũy thừa của hai kế tiếp. Lũy thừa đó là bao nhiêu mili giây ở 48 kHz?
3. **Chính sách.** Chỗ trống ring thu là 100 mẫu và callback đưa 128. Bạn bỏ 28 mẫu cũ nhất hay bypass mô hình? Mỗi lựa chọn làm gì với độ trễ?
4. **Hai ring.** Vì sao mô hình không được ghi 480 mẫu đầu ra của nó vào ring A?

### Gợi ý đáp án

1. Occupancy 2. Mẫu 5 và 6 còn. 1 đến 4 đã bị tiêu.
2. $$480+3\times 480+128=2048$$ đúng, nên dung lượng 2048 không còn một mẫu dự phòng. Dùng 4096 nếu cần $$\ge$$ nghiêm. $$4096/48000\approx 85{,}3$$ ms mỗi tầng.
3. Bỏ 28 mẫu cũ nhất trên ring thu: độ trễ bị chặn, 28 mẫu ($$28/48000\approx 0{,}58$$ ms) bị nhảy. Bypass: mô hình không chạy quantum này, độ trễ không lớn, nhiễu được cho qua. Chặn không phải lựa chọn thứ ba.
4. Producer của ring A là micro. Người ghi thứ hai chạy đua với callback quantum. Ring B là hàng đợi đầu ra của mô hình.

## Đọc thêm

- Bài 05-01 cho p95 dự báo overrun, và bài 05-02 cho producer 128 mẫu.
- MDN, [AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet), cho luồng không được chặn khi `free` bằng không.
- Ghi chú kích thước buffer của JACK hoặc PipeWire, như từ vựng thứ hai cho “kỳ đối với độ sâu ring”, không phải API bạn phải gọi.
