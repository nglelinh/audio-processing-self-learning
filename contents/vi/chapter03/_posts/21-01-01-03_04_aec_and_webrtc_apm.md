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

Khử echo âm học (AEC) là bài toán anh em của khử nhiễu: “nhiễu” là bản sao đã lọc của **tín hiệu far-end** phát ra loa rồi ghép vào micro. Stack VoIP trình duyệt và native hầu như luôn chạy AEC **trước** hoặc **cùng** NS trong audio processing module. Bài này đặt AEC trong đồ thị cuộc gọi, phác thảo hủy bằng adaptive filter, và xem **WebRTC Audio Processing Module (APM)** như chuẩn công nghiệp bạn sẽ gặp khi tích hợp Mezon / LiveKit / trình duyệt (Chương 07).

## Mục tiêu học tập

Bạn vẽ được luồng near-end / far-end với đường echo $$\mathbf{h}$$, giải thích vì sao adaptive filter có tham chiếu khác NS mù, liệt kê khối chính của WebRTC APM (AEC, NS, AGC, HPF, VAD), và nêu ràng buộc thực tế (trễ, lệch clock, méo phi tuyến) khiến echo dư chảy sang tầng NS.

## Kế hoạch 60 phút

- **0–10 phút** — Nghe phân biệt echo vs nhiễu; nhận diện tham chiếu far-end.
- **10–25 phút** — Mô hình $$y=s+\mathbf{h}*\mathbf{x}+n$$; ước lượng $$\hat{\mathbf{h}}$$.
- **25–40 phút** — Tour pipeline WebRTC APM (khối khái niệm).
- **40–50 phút** — Echo dư sau AEC → vì sao NS / postfilter neural vẫn cần.
- **50–60 phút** — Bẫy, bài tập, checklist chèn sản phẩm.

## Giải thích cốt lõi

### Echo là “nhiễu có cấu trúc”

$$
y[t]=s[t]+\underbrace{(h*x)[t]}_{\text{echo}}+n[t],
$$

$$x[t]$$ là far-end (thiết bị render biết), $$h$$ là đường echo (phòng + loa + mic). AEC ước lượng $$\hat{h}$$ và tạo

$$
e[t]=y[t]-(\hat{h}*x)[t].
$$

Khi $$\hat{h}\approx h$$ và đường tuyến tính biến chậm, $$e\approx s+n$$—NS có thể tập trung vào $$n$$.

```text
far-end x ──► loa ──► phòng h ──► mic y
near-end s ─────────────────────► mic y
nhiễu nền n ────────────────────► mic y
AEC:  e = y − ĥ ∗ x
NS:   chạy trên e, không chạy trên y thô
```

Phần dư sau phép trừ đó mới là thứ suppressor phía sau thực sự nghe. Khi bộ hủy làm đúng việc, \(e\) trông như hỗn hợp cộng trên hình: tiếng near-end cộng với thứ chưa hủy (nhiễu nền, và echo sót nhỏ hơn). Hình không vẽ đường phòng.

![Tiếng sạch, nhiễu cộng, và tổng của chúng — dạng phần dư sau khi echo đã bị trừ]({{ site.imgurl }}/generated/noise-mixture.png)

*Hình. Sau AEC tuyến tính, phần dư là hỗn hợp cộng của tiếng near-end và thứ bộ hủy chưa bỏ; hoạt hình này là hỗn hợp đó, không phải đường echo.*

### Trực giác adaptive filter (NLMS)

FIR độ dài $$L$$ cập nhật kiểu NLMS:

$$
\mathbf{h}_{\ell+1}=\mathbf{h}_\ell+\mu\frac{e_\ell\,\mathbf{x}_\ell}{\|\mathbf{x}_\ell\|^2+\varepsilon}.
$$

Bộ lọc thích nghi miền tần số / partition-block (nhiều AEC hướng WebRTC) cùng ý tưởng với kiểm soát độ phức tạp và trễ tốt hơn. **Nối Kalman (03-03):** bước theo hiệp phương sai thay $$\mu$$ vô hướng.

### AEC ≠ NS

| | AEC | NS |
|---|-----|----|
| Tham chiếu | Cần far-end $$x$$ | Thường mù |
| Tổn thất | Echo $$h*x$$ | Nhiễu / nhiễu giao thoa |
| Thất bại | Lệch trễ, double-talk, loa phi tuyến | Nhiễu không dừng, musical artifact |
| Vị trí | Đầu APM | Sau AEC / kèm residual-echo suppression |

Double-talk (near-end và far-end nói cùng lúc) là stress test kinh điển: phải đóng băng/chậm cập nhật adaptive filter.

### Mô hình tinh thần WebRTC APM

1. **High-pass** — bỏ DC / rumble.
2. **Echo canceller (AEC / AECM)** — hủy theo tham chiếu; mobile có thể dùng biến thể nhẹ.
3. **Noise suppression** — NS phổ / Wiener cổ điển (mức cấu hình được).
4. **AGC** — chỉnh mức (dễ xung đột với NS nếu xếp sai thứ tự).
5. **VAD / mở rộng** — tùy flag build.

Thứ tự và tên biến thiên theo phiên bản WebRTC; coi trên là **cartoon kiến trúc**, đối chiếu docs `AudioProcessing` khi tích hợp thật.

**Liên quan sản phẩm:** Mezon và nhiều app LiveKit / WebRTC có thể dựa vào AEC trình duyệt **và** chèn NS neural (DeepFilterNet3 qua AudioWorklet). Phải biết AEC đã chạy chưa, còn echo dư không, và NS có bị train xem echo dư như “nhiễu” không.

### Echo dư và postfilter neural

AEC tuyến tính để lại phần dư khi loa méo phi tuyến, ước lượng trễ sai (Bluetooth), lệch clock render/capture, hoặc $$h$$ đổi nhanh. Research hybrid (ULCNet + adaptive filter) train mạng nhỏ trên **residual AEC**. Thực tế: đo ERLE trước/sau AEC; nếu echo dư còn nghe thấy, sửa căn chỉnh trễ hoặc thêm residual-echo suppressor—không chỉ NS chung chung.

## Checklist tích hợp

1. Xác nhận far-end reference thật sự tới AEC.
2. Đo buffering vòng; căn chỉnh trễ tham chiếu.
3. Kiểm thử clip **double-talk**.
4. Quyết định điểm chèn NS: trong APM, sau PCM APM, hay AudioWorklet neural (Ch. 05, 07).
5. Tắt AGC trùng lặp “đá” nhau.
6. Log khiếu nại nghiêng echo hay nhiễu—chia triage AEC vs NS.

## Bẫy thường gặp

- NS neural trên tín hiệu còn echo full volume → over-suppress near-end lúc far-end phát.
- Coi AEC trình duyệt luôn bật mà không kiểm tra quirk di động.
- Train/đánh giá NS chỉ trên nhiễu cộng DNS rồi deploy loa laptop đầy echo.
- AGC trước AEC khiến gain điều chế đường echo.
- Nhầm echo **âm học** với echo **đường dây** gateway điện thoại.

## Mini-lab

**Mục tiêu.** Hoạt hình số: công suất echo dư so với lỗi bạn thực sự đo, và một frame double-talk (hai phía cùng nói) làm gì. Đây không phải bản dựng WebRTC và không gọi Audio Processing Module.

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

**Kỳ vọng.** Công suất echo dư vẫn nhỏ: `[0, 0.0001, 0.0025, 0.0025, 0.0002, 0.0036]`. Công suất lỗi đo được khớp nó mọi frame trừ frame 3, nơi tiếng near-end đẩy lên khoảng `0.7225` trong khi echo sót thật vẫn là `0.0025`. Thích nghi \(\hat{h}\) trên frame đó sẽ coi người nói là echo.

**Khi hỏng.** Nếu hai công suất ở frame 3 khớp nhau, `near` còn bằng 0 và bạn không ở double-talk. Nếu công suất echo dư lớn trên mọi frame far-end có tiếng, \(\hat{h}\) còn xa \(h\) (thử hoán 0.5 và 0.45). Coi công suất lỗi là sàn nhiễu rồi đưa vào gain Wiener sẽ đè người nói near-end. Không có gì ở đây khởi tạo AEC của WebRTC.

## Bài tập

1. Vẽ capture, render, $$\hat{h}$$, $$e$$, NS; đánh dấu chỗ AudioWorklet neural.
2. Giải thích NLMS khi reference sớm/muộn 40 ms so với echo trong mic.
3. Lướt docs WebRTC APM; liệt kê tên toggle NS level và AEC.
4. Playbook hỗ trợ: triệu chứng → nghi AEC/NS/AGC → bước chẩn đoán đầu.

### Gợi ý đáp án

1. NS neural ngồi trên \(e\), sau \(\hat{h}\). Trên đồ thị trình duyệt, chỗ đó thường là sau AEC của nền tảng và trước encoder.
2. Tham chiếu sớm hoặc muộn 40 ms sẽ trượt các tap đang giữ \(h\), nên \(e\) vẫn còn echo và bộ lọc thích nghi sai lag.
3. Tìm mức NS và công tắc AEC trên `AudioProcessing`; tên đổi giữa các bản, nên ghi revision bạn đã đọc.
4. Far-end phát mà không có người near-end là bài test AEC. Người near-end trong nhiễu, far-end im, là bài test NS. Mức nhảy khi một phía ngừng nói thường là AGC.

## Đọc thêm

- Tài liệu WebRTC Audio Processing Module / API `AudioProcessing`.
- SpeexDSP echo canceller / preprocessor.
- Haykin, *Adaptive Filter Theory*.
- Con trỏ hybrid AENR: ULCNet + adaptive filter / Align-ULCNet.
