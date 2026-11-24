---
layout: post
title: "02-01 PCM, sample rates, and channels"
chapter: "02"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

Neural noise suppressors eat clean `float32` tensors; real microphones hand you raw **PCM byte streams**—sometimes signed 16-bit integers, sometimes 44.1 kHz instead of 48 kHz, sometimes interleaved stereo `LRLRLR...` pretending to be mono. A single silent mismatch at this edge layer can either fold 7 kHz into 1 kHz, shift pitch by 8%, or turn anti-correlated stereo into exact silence before your model ever sees sample zero.

Welcome to Chapter 02, where we build the complete **audio processing pipeline**. This first lesson nails down PCM encodings, byte-length arithmetic, channel layouts, downmix policies, and device-clock hygiene.

![Sampling at 8 kHz: a 1 kHz sine is unique, while a 7 kHz sine lands on the same samples and aliases to 1 kHz]({{ site.imgurl }}/generated/sampling-nyquist.png)

*Figure. At $$f_s=8\,\mathrm{kHz}$$ the folding frequency is 4 kHz, so a 7 kHz tone and a 1 kHz tone produce the same sample sequence.*

**Lesson roadmap:** Background Knowledge Map (PCM quantization & dynamic range, planar vs. interleaved memory layout, device clock boundaries) → Encodings, byte arithmetic, and Nyquist rate choices → Downmix policies & WebRTC/Mezon expectations → Worked examples: 3840-byte ambiguity (stereo s16 vs. mono f32), peak clipping, and wrong channel stride → Deep-Dive Explanation (Read Slowly): 3-step edge contract for safe PCM ingestion → Pitfalls, Mini-lab, Exercises & Videos.

---

## Background Knowledge Map: Digital Audio Representation at the System Edge

### 1. Pulse-Code Modulation (PCM) — Amplitude Discretization
A digital audio buffer stores a uniform sequence of quantized pressure readings. Voice pipelines rely on two workhorse formats: **`int16` (`s16`)** (range $$[-32768, 32767]$$, 2 bytes/sample, ~96 dB dynamic range, standard in WAV and WebRTC) and **`float32` (`f32`)** (normalized to $$[-1.0, 1.0]$$ full scale, 4 bytes/sample, standard in Web Audio and neural runtimes).

### 2. Memory Layout — Interleaved vs. Planar
Multi-channel PCM packs samples in two incompatible ways: **interleaved** (`L0, R0, L1, R1, ...`) or **planar** (`[L0, L1, ...], [R0, R1, ...]`). Reading interleaved stereo as a mono stream alternates left and right samples at every step—injecting a massive phantom signal near the Nyquist frequency $$f_s/2$$!

### 3. The Three-Tuple Contract: `(sampleRate, channels, dtype)`
As our worked example proves, `byteLength = 3840` at 20 ms could be *either* 48 kHz stereo `int16` *or* 48 kHz mono `float32`. Every audio boundary must explicitly carry and validate the full tuple `(fs, C, layout, dtype)` before allocating an STFT frame.

---

## Learning objectives

1. Describe PCM encodings common in browsers and native stacks (s16, f32, planar vs interleaved).
2. Convert fluently among samples, seconds, and bytes.
3. Handle mono/stereo layouts before mono NS models.
4. Explain device clock / `AudioContext.sampleRate` mismatches.
5. Tie expected formats to WebRTC / Mezon-style public integration paths.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | Open a raw dump: interpret bytes as s16 LE mono @ 16 kHz |
| 10–25 | Encodings, endianness, float Full Scale, clipping |
| 25–40 | Channels: interleaved/planar; downmix policies |
| 40–52 | Clocks & resampling placement in the graph |
| 52–60 | Exercises |

## Core explanations

### PCM essentials

**Pulse-code modulation** stores uniformly sampled amplitudes. Common voice formats:

| Format | Range | Notes |
|--------|-------|-------|
| `int16` (`s16`) | $$[-32768,32767]$$ | WebRTC, WAV; watch endianness |
| `float32` | typically $$[-1,1]$$ FS | Web Audio `AudioBuffer` |
| `int32` / 24-bit in containers | rare in NS hot path | convert once |

Conversion sketch:

$$
x_{f32} \approx \frac{x_{s16}}{32768}
$$

(Exact libraries may use 32767; be consistent to avoid tiny gain errors.) Pick one scale at the edge of the graph and never mix the two inside the STFT. Samples already clipped in the microphone driver are a hard nonlinearity: the harmonics sit in the same bins as fricatives, so leave a few dB of headroom before the suppressor.

### Time, samples, bytes

$$
N_{\mathrm{samples}} = t\cdot f_s,\qquad
N_{\mathrm{bytes}} = N_{\mathrm{samples}}\cdot C\cdot B
$$

where $$C$$ = channels, $$B$$ = bytes per sample (2 for s16, 4 for f32).

**Example:** 20 ms, 48 kHz, stereo s16 → $$0.02\cdot48000\cdot2\cdot2=3840$$ bytes.

The same 20 ms as mono float32 is also 3840 bytes — same length, different layout. Check $$f_s$$, $$C$$, and dtype together; `byteLength` alone cannot tell them apart. A 128-sample Web Audio quantum is $$2.67\,\mathrm{ms}$$ at 48 kHz and $$8\,\mathrm{ms}$$ at 16 kHz, so it is not a stand-in for “10 ms.”

### Nyquist, and why 16 kHz is not a free downsample

The sampling theorem (Oppenheim & Schafer) says a bandlimited signal whose spectrum is zero at and above $$f_s/2$$ is determined by its samples. The figure is the picture of the failure mode: with $$f_s=8\,\mathrm{kHz}$$,

$$
\sin(2\pi\cdot 7000\cdot n/f_s)=\sin(2\pi\cdot(-1000)\cdot n/f_s)=-\sin(2\pi\cdot 1000\cdot n/f_s).
$$

The 7 kHz waveform and a polarity-flipped 1 kHz waveform hit the same dots. After sampling, no filter — Wiener, spectral subtraction, or DeepFilterNet — can tell them apart.

Practical rates in this course:

| Rate | Nyquist | What you keep |
|------|---------|----------------|
| 8 kHz | 4 kHz | narrowband telephony; most fricative energy is already gone |
| 16 kHz | 8 kHz | wideband voice; common classical NS and DNS Challenge rate |
| 48 kHz | 24 kHz | full-band; DeepFilterNet’s published operating rate, and the rate `deepfilternet3-noise-filter` 1.3.0 expects |

Downsampling 48 kHz to 16 kHz is legal only after a low-pass that stops the band above 8 kHz. Taking every third sample aliases 8–24 kHz into 0–8 kHz, and a later upsample does not restore it. The Mezon full-band path stays at 48 kHz unless you deliberately chose a 16 kHz model and an anti-alias filter.

### Interleaved vs planar

- **Interleaved stereo:** `LRLRLR...`
- **Planar:** all L then all R (or separate pointers)

Feeding interleaved stereo into a mono FFT “as mono” aliases channels into fake high frequencies — the same folding as the figure. Reading `L,R,L,R` as one sequence puts energy near $$f_s/2$$. Deinterleave or downmix explicitly, then window.

### Downmix policies for speech NS

Pick one and document it:

1. **Mean:** $$m=(L+R)/2$$ (watch correlated vs anti-correlated content).
2. **Left-only / right-only:** if product mic is known.
3. **Energy-weighted:** rare in realtime.

Never average after independent NS on L and R without a spatial policy — phasey mess. Anti-correlated stereo $$L=-R$$ (a common test tone, and a real situation with some mid-side mics) averages to exact silence. The suppressor then “succeeds” by outputting zeros. If the product microphone is known to be one capsule of a stereo pair, take that channel and do not average.

### Clocks

`AudioContext.sampleRate` may be 44100, 48000, or others. getUserMedia tracks may be resampled by the browser. **Measure** `sampleRate`; do not hardcode. Place one high-quality resampler at the edge of the NS block to the model’s native rate.

44.1 kHz is the trap on consumer DACs. Samples at 44.1 kHz labeled as 48 kHz shift every frequency by $$44100/48000\approx 0.919$$, so harmonics land in the wrong ERB bands. Read the context rate and resample once.

### Mezon / WebRTC expectations (public)

Browser integrations typically see Float32 from Web Audio, often 48 kHz, mono after downmix. Public DeepFilterNet is full-band 48 kHz ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)). Confirm the current `deepfilternet3-noise-filter` README when shipping.

## Worked examples

### Byte length

1 second mono f32 @ 16 kHz → $$16000\cdot4=64000$$ bytes.

10 ms mono s16 @ 16 kHz → $$0.010\cdot16000\cdot2=320$$ bytes. That is 160 samples, a common classical hop, not a 128-sample Web Audio quantum.

### Peak clipping

s16 near ±32767 clipping creates harmonics that NS may treat as speech or noise — prefer headroom before NS.

### Wrong channel stride

Interleaved stereo length 960 frames misunderstood as 960 mono samples @ 48 kHz → you processed 10 ms of “scrambled” L/R as if 20 ms mono. At 48 kHz, 960 samples is the DeepFilterNet analysis length (20 ms). Halving it by a stride bug feeds the model a 10 ms scrambled frame and shifts every subsequent hop.

---

### Deep-Dive Explanation: The 3-Step Edge Contract for Safe PCM Ingestion (Read Slowly)

#### Step 1: Normalize format once at the graph boundary
Convert `int16` to `float32` via $$x_{f32} = x_{s16} / 32768.0$$ exactly once upon entering your DSP graph, and keep internal signals in $$[-1, 1]$$ with headroom so neither FFT scaling nor neural gains cause hard clipping.

#### Step 2: Resolve channel layout before touching any FFT
Deinterleave stereo explicitly and apply a documented mono policy (left-only for single-capsule headsets, or $$(L+R)/2$$ with a check against anti-correlated cancellation). Never let raw `L,R,L,R` stride into a mono window.

#### Step 3: Lock the sample rate to the model’s native clock
Query `AudioContext.sampleRate` dynamically. If the hardware runs at 44.1 kHz while the suppressor expects 48 kHz, insert **one** polyphase resampler at the input edge (and its inverse at the output edge if required) rather than letting a $$0.919\times$$ pitch shift corrupt every ERB band.

Summary of the PCM ingestion pipeline:

$$
\text{Raw PCM } (f_s, C, \text{s16/f32})
\;\xrightarrow{\text{Scale + Downmix}}\;
\text{Mono f32 } [-1,1]
\;\xrightarrow{\text{Resample if } f_s \neq f_{\mathrm{model}}}\;
\text{Clean STFT input}.
$$

## Common pitfalls

1. Assuming little-endian always when reading files on exotic platforms (usually LE, still assert).
2. Floats outside $$[-1,1]$$ after processing → sink distortion.
3. Hardcoding 48 kHz.
4. Stereo model input silently truncated to first half buffer.
5. Forgetting that WAV headers ≠ raw PCM from callbacks.

## Mini-lab

**Goal.** Show that a 7 kHz tone sampled at 8 kHz matches a polarity-flipped 1 kHz tone, and check two buffer lengths you will meet in the pipeline.

```python
import numpy as np

fs = 8000
n = np.arange(int(0.004 * fs))  # 4 ms, same idea as the figure
s1 = np.sin(2 * np.pi * 1000 * n / fs)
s7 = np.sin(2 * np.pi * 7000 * n / fs)
alias_err = np.max(np.abs(s7 + s1))
print("max |s7 - (-s1)|", alias_err)

def nbytes(seconds, fs, channels, bytes_per_sample):
    return int(round(seconds * fs)) * channels * bytes_per_sample

print("20 ms stereo s16 @ 48 kHz", nbytes(0.020, 48000, 2, 2))
print("10 ms mono s16 @ 16 kHz", nbytes(0.010, 16000, 1, 2))
```

**Expected.** `alias_err` is on the order of $$10^{-14}$$ (numerical zero). The byte counts are `3840` and `320`.

**Failure modes.** Using `np.linspace` in a way that drops or duplicates the last sample makes the alias error jump from roundoff to $$O(1)$$. Forgetting `channels` or using 4 bytes for s16 prints 7680 or 640 and will desynchronize a WAV writer from a worklet. If `alias_err` is ~2, you compared `s7` to `s1` without the minus sign from the folding identity — the samples match in magnitude and opposite sign, which is exactly the alias.

## Mini exercises

1. Bytes for 10 ms mono s16 @ 16 kHz?
2. Write downmix pseudocode interleaved → mono mean.
3. Why is anti-correlated stereo $$(L=-R)$$ dangerous for mean downmix?
4. List three places sampleRate can differ in a WebRTC send path.
5. Convert s16 value −16000 to float FS with /32768.

### Answer hints

1. $$0.010\times16000=160$$ samples, times 2 bytes → 320.
2. Read pairs `(L, R)` and emit `(L+R)/2` in float; do not average bytes.
3. The mean is identically 0, so the model sees silence.
4. Capture device, `AudioContext`, and the model’s native rate (48 kHz vs 16 kHz vs 44.1 kHz).
5. $$-16000/32768\approx -0.488$$.

## Further reading

- Oppenheim & Schafer, *Discrete-Time Signal Processing* — sampling and the Nyquist frequency.
- Web Audio API `AudioBuffer` / `AudioWorkletProcessor` buffer formats.
- WebRTC media track constraints and PCM notes.
- DeepFilterNet full-band framing: [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).

## Video tham khảo

- [Xiph.Org Video Presentations: Digital Show & Tell](https://xiph.org/video/vid2.shtml) — Xiph.Org, English. **xem trước.** Official Xiph.Org presentation of PCM sampling, bit depth, and reconstruction. Watch it before debugging a 16 kHz tensor fed from a 48 kHz callback.
- [Aliasing and the Sampling Theorem Simplified](https://www.youtube.com/watch?v=KuaannH5pnM) — Barry Van Veen, English. The Nyquist wrap is the silent failure when a channel is resampled to the wrong rate.
