---
layout: post
title: "06-02 Quantization for speech models"
chapter: "06"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter06
lesson_type: required
draft: false
---

**Quantization** shrinks weights and often speeds speech-enhancement inference. That matters for WASM download size and for CPU real-time factor. It can also damage speech or destabilize recurrent state. The dangerous errors are not the large weights. They are the gains near zero, because those gains are applied directly to frequency bins. This lesson covers INT8 at an engineering level, calibration on speech rather than on images, and a numeric lab you can self-check.

![Quantized weights packed into the model archive before the browser loads WASM]({{ site.imgurl }}/generated/onnx-wasm-path.png)

*Figure. Quantization happens before the WASM the browser loads.*

A full-precision `FP32` speech denoiser takes 4 bytes for every single weight. Shrink those weights down to 8-bit integers (`INT8`), and two magical things happen simultaneously: your model download shrinks by **4×** (so it loads in a blink over mobile networks and fits inside CPU L2 cache), and modern SIMD instructions (`VNNI`, `NEON dotprod`, `WASM SIMD`) can crunch **2–4× more multiply-adds per clock cycle**!

Yet naive quantization can wreck a speech model—turning soft background silence into audible buzzing or crushing quiet consonants because audio features span a huge dynamic range in decibels. This lecture walks through the exact math of **symmetric & affine INT8 quantization**, compares **PTQ (Post-Training Quantization)** vs. **QAT (Quantization-Aware Training)**, and shows which sensitive layers (like final gain heads) are best left in `FP32`.

---

## Key ideas: Fixed-Point Arithmetic and Quantization Noise in Audio

Four mathematical concepts explain when quantization shines and when it breaks speech quality:

1. **Affine & Symmetric Mapping:** Quantization maps a real value $$x \in [x_{\min}, x_{\max}]$$ to an integer $$q \in [-127, 127]$$ via $$q = \operatorname{round}(x / s) + z$$ and reconstructs $$\hat{x} = s(q - z)$$. **Symmetric quantization** sets zero-point $$z = 0$$ (ideal for zero-centered weights, eliminating cross-terms in integer matrix multiplication).
2. **Quantization Noise & SQNR:** Rounding introduces uniform error $$e = \hat{x} - x \in [-s/2, +s/2]$$ with variance $$s^2/12$$. For 8-bit uniform quantization, peak Signal-to-Quantization-Noise Ratio (SQNR) is roughly $$6.02 	imes 8 pprox 48	ext{ dB}$$—plenty for intermediate weights, but tight if an extreme outlier stretches $$s$$!
3. **Per-Channel vs. Per-Tensor Scaling:** Giving each output channel its own scale $$s_c$$ prevents one large-magnitude channel from blowing up the quantization step size for 63 quiet channels.
4. **PTQ vs. QAT & Mixed Precision:** Dynamic/static **PTQ** requires no retraining; **QAT** inserts fake-quantization nodes during fine-tuning so weights adapt to rounding noise. Keeping input/output gain heads in `FP32` while quantizing heavy `Conv`/`GRU` bodies often yields 95% of the speedup with zero audible degradation.

---

## Learning objectives

You will distinguish dynamic and static INT8 quantization, compute a symmetric scale and the maximum absolute error on a gain vector, explain why bins whose gain is near zero dominate audible damage, and design an A/B listening plus SI-SDR gate before shipping quantized weights.

## 60-minute teaching plan

- **0–10 min** — Size and real-time factor for a DeepFilter-class WASM download.
- **10–25 min** — Symmetric INT8, per-tensor versus per-channel scales.
- **25–40 min** — Calibration audio, and why ImageNet statistics do not transfer.
- **40–50 min** — Gains near zero, residual noise, state drift.
- **50–60 min** — Mini-lab, pitfalls, exercises.

## Core explanation

### The scale you will actually code

A float value \(g\) maps to an integer code \(q\) with scale \(s\) and optional zero-point \(z\):

$$
g \approx s\,(q - z).
$$

For a symmetric gain vector with no zero-point, take

$$
s = \frac{\max_i |g_i|}{127}, \qquad q_i = \mathrm{clip}\big(\mathrm{round}(g_i / s), -128, 127\big), \qquad \hat g_i = s\, q_i.
$$

The reconstruction error on each element is at most about half a step, \(s/2\), when rounding behaves. GEMM kernels multiply the integers and rescale. **Per-channel** scales on convolutions usually beat one coarse per-tensor scale, because a single outlier channel would otherwise inflate \(s\) for every channel.

### Where the error becomes audible

Suppose the peak gain is \(1\). Then \(s = 1/127 \approx 0.00787\), and the absolute error is only a few thousandths. Relative to a full-scale bin that is nothing. Relative to a bin whose true gain is \(0.004\), one code is the entire signal. The mini-lab’s vector \([1.0,\ 0.5,\ 0.02,\ 0.004,\ 0.0]\) quantizes to codes \([127,\ 64,\ 3,\ 1,\ 0]\). The \(0.004\) bin moves to \(1/127 \approx 0.00787\). That is almost a doubling of a weak bin, and the maximum absolute error on the vector is about \(0.00394\), coming from the half-step on \(0.5\), not from the speech-like full-scale bin.

In noise suppression those small gains are the noise-dominated bins and the weak harmonics. Collapse a harmonic to code \(0\) and the vowel thins. Round a near-silent bin up to one quantum and you leak a steady tonal floor, the usual source of musical noise. Weight error inside a convolution is filtered by later layers. Gain error is multiplied onto the STFT bin and summed by overlap-add. Calibrate and listen to the gain head even when you leave it in float32.

### Approaches

| Mode | Idea | Pros | Cons |
|------|------|------|------|
| Dynamic quant | Activations quantized at runtime | Easy to try | Overhead; variable latency |
| Static PTQ | Calibrate ranges offline | Fast inference | Needs representative audio |
| QAT | Train with quant noise | Best quality when it converges | Costly |
| Weight-only | INT8 or INT4 weights, float activations | Simple size win | Smaller speed win |

For streaming enhancement, static post-training quantization in the ONNX Runtime toolchain is the usual first experiment. Move to quantization-aware training when SI-SDR or listening regresses. Quantization is a **packaging** step: it runs before you compress the archive and before the browser compiles WASM (lesson 06-04, lesson 07-03). Do not quantize a graph whose STFT still disagrees with production.

### Calibration is speech, not ImageNet

A calibration set that is only white noise produces scales that misfit café babble and near-end speech. Include silence, noise-only, loud near-end speech, low-SNR mixes, and residual-echo-like clips if echo is in scope. A minute of diverse DNS-style mixes is a teaching minimum. Products use a broader set and freeze it. Otherwise you get pumping or a harsh residual that objective scores on clean speech will miss.

### What often stays float32

Sensitive elementwise gates, the final gain head, and very small layers where INT8 overhead exceeds the benefit often stay in float. First and last layers are a common heuristic, not a theorem. Verify. Recurrent state is a special case: an overflow that would be a one-bin click in a feed-forward net can ring for the rest of the call. Watch state ranges on a 30-minute stream (lesson 05-04).

### Validation gate

1. SI-SDR and DNSMOS delta against the float model on a frozen set (Chapter 08).
2. Ten or more paired clips, forced choice, including gains that were near zero.
3. A long stream for state drift.
4. Real-time factor on the target device, not a smaller file size alone.

Survey notes on FastEnhancer and faster-enhancer.c show that fused INT8 kernels can move real-time factor a lot. ORT post-training quantization often moves it less. Measure. The package README’s 20–30% SIMD claim (lesson 06-03) is a separate speedup and is not a quantization result.

## Mini-lab

Run `python3 quant_gain.py` with this script. It uses Python’s `round` (half to even), which matches the codes below.

```python
g = [1.0, 0.5, 0.02, 0.004, 0.0]
scale = max(abs(x) for x in g) / 127.0
q = [max(-128, min(127, int(round(x / scale)))) for x in g]
hat = [scale * qi for qi in q]
err = max(abs(a - b) for a, b in zip(g, hat))
print(f"scale={scale:.8f}")
print(f"q={q}")
print(f"max_abs_error={err:.8f}")
```

**Expected**

```text
scale=0.00787402
q=[127, 64, 3, 1, 0]
max_abs_error=0.00393701
```

**Failure modes**

- Using \(128\) as the divisor. Signed INT8’s positive end is \(127\), so the full-scale code is \(127\), not \(128\).
- Reporting relative error only on the \(1.0\) bin and declaring the quantizer harmless. The \(0.004\) bin is the speech-NS case.
- Quantizing before STFT parity. A one-bin frequency shift then gets baked into the scales.
- Assuming this toy uses the same zero-point as a production ORT static quantizer. Production tools may use an affine zero-point; the lab is symmetric on purpose.

## Pitfalls

- Calibrating on white noise only.
- Shipping INT8 with no written quality delta for support.
- Ignoring overflow in state tensors.
- Treating a smaller `.tar.gz` as proof the AudioWorklet meets its budget.

---

### Worked Numerical Example: Hand-Quantizing a 4-Weight Vector to Symmetric INT8

Take a tiny weight vector from a speech denoiser layer:

$$\mathbf{w} = [-0.80,\; -0.15,\; 0.42,\; 0.95].$$

1. **Compute the symmetric INT8 scale factor $$s$$** (mapping $$\max\lvert w_i
vert = 0.95$$ to $$127$$):
   $$s = rac{0.95}{127} pprox 0.0074803.$$
2. **Quantize each weight** $$q_i = \operatorname{round}(w_i / s)$$ and **dequantize** $$\hat{w}_i = s \cdot q_i$$:

| Original $$w_i$$ | $$w_i / s$$ | Quantized $$q_i$$ (`i8`) | Dequantized $$\hat{w}_i = s q_i$$ | Error $$e_i = \hat{w}_i - w_i$$ |
| :--- | :--- | :--- | :--- | :--- |
| $$-0.80$$ | $$-106.95$$ | $$-107$$ | $$-0.8004$$ | $$-0.0004$$ |
| $$-0.15$$ | $$-20.05$$ | $$-20$$ | $$-0.1496$$ | $$+0.0004$$ |
| $$+0.42$$ | $$+56.15$$ | $$+56$$ | $$+0.4189$$ | $$-0.0011$$ |
| $$+0.95$$ | $$+127.00$$ | $$+127$$ | $$+0.9500$$ | $$0.0000$$ |

3. **Compute the exact SQNR in decibels:**
   - Signal energy: $$\sum w_i^2 = 0.64 + 0.0225 + 0.1764 + 0.9025 = 1.7414$$.
   - Quantization error energy: $$\sum e_i^2 pprox 1.6	imes 10^{-7} + 1.6	imes 10^{-7} + 1.21	imes 10^{-6} + 0 = 1.53	imes 10^{-6}$$.
   - $$\mathrm{SQNR} = 10\log_{10}\!\left(rac{1.7414}{1.53	imes 10^{-6}}
ight) pprox \mathbf{60.6	ext{ dB}}$$ — virtually indistinguishable from `FP32`, while cutting storage by **4×** (from 16 bytes to 4 bytes + 1 scale float)!

### Explanation: Four Rules for Quantizing Speech Models Safely

1. **Always use *per-channel* quantization for Conv/Linear weights:** A single outlier filter in a convolutional layer can degrade SQNR by 15+ dB under per-tensor scaling.
2. **Calibrate activations on realistic noisy + quiet audio:** If you calibrate static PTQ only on loud clean speech, quiet silence frames and sudden loud transient claps will clip or buzz in production.
3. **Protect the final sigmoid/mask head in `FP32`:** The final output layer costs less than 2% of total MACs, yet small rounding errors in gains near $$0.01$$ ($$-40	ext{ dB}$$) create audible "musical noise" during speech pauses.
4. **Verify quantization with both SI-SDR/DNSMOS *and* real headphone listening:** Numbers can stay flat while subtle high-frequency hiss creeps into silence—always listen to quiet-tail segments!

**Quick check.** In our 4-weight vector above, suppose one extra outlier weight $$w_5 = 9.50$$ (10× larger!) were added to the same tensor under *per-tensor* symmetric INT8 quantization. How would the scale factor $$s$$ change, and what would happen to the precision of the small weight $$-0.15$$?

---

## Exercises

1. Recompute the symmetric scale for weights confined to \([-0.8,\ 0.8]\). What is \(s\), and what code does \(0.8\) receive?
2. List eight clip types for a Mezon-style post-training calibration set.
3. Design a blind sheet for float versus INT8 that includes at least two near-zero-gain conditions (soft speech, noise floor).
4. Name the ONNX Runtime quantization entry points you would call, from the official docs, without running them yet.
5. Explain, with the lab’s \(0.004\) bin, why a gain head is a poor candidate for aggressive INT8 even when the convolutions are not.

### Answer hints

1. \(s = 0.8 / 127\). The value \(0.8\) maps to code \(127\) if it is the max-abs. Do not use \(255\) unless you switched to an unsigned affine scheme and said so.
2. Include silence, noise-only, loud speech, whisper, low-SNR babble, non-stationary keyboard, a tone, and a residual-echo-like clip.
3. Forced choice, same gain, hidden labels, plus a “musical noise / thin voice” checkbox.
4. Start from the ONNX Runtime quantization documentation: static post-training quantization with a calibration reader. Exact class names change by API version; cite the page you opened.
5. \(0.004\) moved to about \(0.00787\). That relative jump is applied straight to a bin. Later layers do not smooth a mask the way they smooth a weight error.

## Further reading

- [ONNX Runtime documentation](https://onnxruntime.ai/docs/) quantization guides.
- Jacob et al., quantization for integer-arithmetic-only inference, the standard mobile reference.
- FastEnhancer / faster-enhancer.c notes on INT8 enhancement runtimes (survey pointers only).
- DeepFilterNet model-size and real-time discussion in the upstream repository.

## Video tham khảo

- [Quantization explained with PyTorch - Post-Training Quantization, Quantization-Aware Training](https://www.youtube.com/watch?v=0VdNflU08yA) — Umar Jamil, English. **xem trước.** Watch post-training quantization and quantization-aware training, including why a min-max range punishes every small gain when one outlier is huge.
- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, English. The INT8 section is quantization landing in ONNX Runtime, which is the path a speech model takes after the PyTorch explanation.
- [Enable Model Quantization for ONNX and TensorRT!](https://www.youtube.com/watch?v=phmFvMOHt4I) — Nicolai Nielsen Tech, English. Watch a quantized ONNX graph actually load. Treat TensorRT as optional; the lesson's risk is the speech model, not the GPU vendor.
