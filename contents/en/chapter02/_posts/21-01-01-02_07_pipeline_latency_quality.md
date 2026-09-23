---
layout: post
title: "02-07 Pipeline latency–quality tradeoffs"
chapter: "02"
order: 7
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

Every STFT and model choice trades latency, CPU, and quality. The distinction that prevents bad ship decisions: **algorithmic latency is how late the audio is, and real-time factor is whether the CPU keeps up.** A fast model can still be too late.

## Learning objectives

1. Enumerate pipeline stages that add latency and CPU.
2. Trade window/hop/FFT size against quality and delay with numbers.
3. Explain quality failure modes when over-optimizing latency.
4. Build a go/no-go scorecard for shipping configurations.
5. Connect tradeoffs to DeepFilterNet-class real-time design goals.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–10 | End-to-end pipeline diagram (mic → NS → encoder) |
| 10–28 | Parameter sweep thought experiments with numerics |
| 28–42 | Quality vs latency failure modes |
| 42–52 | Scorecard for Mezon-like shipping |
| 52–60 | Exercises |

![AudioWorklet quanta on a timeline, with process() sometimes overrunning a quantum: RTF is wall time over audio duration, and a good average can still miss a deadline]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Figure. Each tick is a render quantum; RTF compares process() wall time to that audio duration, which is a different number from the STFT window’s algorithmic delay.*

## Core explanations

### Two clocks

Algorithmic latency is a property of the signal graph. For the causal STFT in lesson 02-02,

$$
D_{\mathrm{alg}}\approx T_L=\frac{L}{f_s},
$$

plus look-ahead, resampling delay, and packet buffer. At 48 kHz, \(L=960\) contributes about **20 ms** whether the FFT takes 0.2 ms or 2 ms of wall time. The samples are late because you waited to fill the window.

Real-time factor is a property of the implementation:

$$
\mathrm{RTF}=\frac{T_{\mathrm{wall}}(D)}{D}.
$$

\(D\) is the audio duration you just processed (one hop, or one quantum). \(\mathrm{RTF}<1\) means you finished before the next block was due. It does not say how much look-ahead you already inserted. The figure’s other warning: a mean RTF of 0.4 still clicks if p99 exceeds the hop. Log p95/p99.

A 128-sample quantum at 48 kHz lasts \(128/48000\approx 2.67\,\mathrm{ms}\). That is the grid in the figure, not the model hop. A 10 ms hop spans about four quanta; the red `process()` bar is the quantum where the FFT and the network overrun. Cold start (WASM/ONNX compile) is main-thread work, not steady-state RTF.

### Pipeline stages (typical)

1. Capture / AudioWorklet quantum buffering
2. Resample to model rate
3. Mono downmix
4. STFT framing (window/hop)
5. Feature transform (e.g. ERB)
6. Neural / classical enhance
7. Inverse features / ISTFT / OLA
8. Resample to sink rate
9. Hand off to WebRTC encoder

For each stage, log waveform delay and RTF separately. A resampler can be cheap in RTF and still add group delay; an ONNX session can be expensive in RTF and add no look-ahead beyond the STFT.

### Knobs and effects

| Knob ↑ | Latency | CPU | Quality tendency |
|--------|---------|-----|------------------|
| Window \(L\) | ↑ | ↑ (larger FFT) | better freq detail; blurrier time |
| Hop \(R\) | hop itself is not \(D_{\mathrm{alg}}\); smaller \(R\) raises hops/s | ↑ as \(R\)↓ | smoother masks often |
| Model size | ≈ (if lookahead fixed) | ↑ | often ↑ until RTF fails |
| Look-ahead | ↑ | ↑ | often ↑ quality |
| Sample rate | ↑ | ↑ | ↑ bandwidth if model trained for it |

**Measure.** Cutting \(R\) from 480 to 240 at 48 kHz doubles hops/s (100 → 200) and STFT CPU; \(D_{\mathrm{alg}}\) stays near \(L/f_s\) unless the window shrinks too. Shortening the window widens bins (lesson 02-03). It is a quality change, not a free RTF win.

### Numerics to keep

At 48 kHz:

- 128-sample quantum ≈ 2.67 ms
- 480-sample hop = 10 ms → 100 decisions/s
- 960-sample window = 20 ms buffering scale

At 16 kHz, the same *milliseconds* use fewer samples (cheaper FFTs) but less bandwidth. The same *sample counts* are different milliseconds: \(L=512\) at 16 kHz is 32 ms, not 20 ms. A wall time of 3 ms on a 10 ms hop is \(\mathrm{RTF}=0.3\), comfortable. A wall time of 12 ms on that same hop is \(\mathrm{RTF}=1.2\), an overrun, even though 12 ms is less than a 20 ms window. The mini-lab prints both pairs so the two clocks stay in different variables.

### Failure modes

**Too little latency budget:** tiny windows leave harmonics unresolved and masks harsh.

**Too much latency:** the call feels late, and a look-ahead parked before AEC looks like a moving echo path.

**Too little CPU headroom:** a single p99 overrun (the red bar) crackles even when mean RTF looks fine.

### Shipping scorecard (example)

| Criterion | Target (illustrative) | Pass? |
|-----------|----------------------|-------|
| Algorithmic look-ahead | ≤ product budget (e.g. 20–40 ms class) | |
| p95 RTF on device | ≤ 0.5 | |
| COLA round-trip | error below threshold | |
| DNSMOS / listening | vs baseline WebRTC NS | |
| No hop warble | listening + spectrogram | |

Replace illustrative numbers with your product’s SLA. Do not mark “RTF ≤ 0.5” as a pass on algorithmic latency, or the reverse.

### DeepFilterNet-class moral

The published full-band setup is 48 kHz, a 960-point STFT (20 ms), and 50% overlap (10 ms hop), plus a small frame look-ahead ([arXiv:2110.05588](https://arxiv.org/abs/2110.05588)). Treat those as hard requirements. Tradeoffs belong in graph placement, resampling, and device budget. `deepfilternet3-noise-filter` 1.3.0 is a 48 kHz processor on that contract; if p95 RTF fails, do not quietly change the hop.

## Worked examples

### Sweep

Config A: 16 kHz, L=20 ms, R=10 ms, small model, RTF 0.2, MOS OK.
Config B: 48 kHz, L=40 ms, R=5 ms, large model, RTF 0.9, MOS higher offline, glitches on phone → **do not ship B**.

B’s window is already 40 ms, and mean RTF 0.9 leaves no room for a red-bar quantum.

### Budget split

A 40 ms algorithmic budget that already spends 20 ms on the window cannot also absorb several 10 ms look-ahead frames. Do not “save” the 20 ms by reporting only the 3 ms of wall time.

## Common pitfalls

1. Optimizing mean RTF only.
2. Changing L/R without regenerating eval sets.
3. Comparing quality at different latencies unfairly.
4. Ignoring resample cost in RTF.
5. Shipping debug builds’ timings as production truth.

## Mini-lab

**Goal.** Print algorithmic frame delay and RTF as different numbers for one 48 kHz hop, including an overrun case. No audio device required.

```python
fs, L, R = 48000, 960, 480
frame_ms = 1000 * L / fs
hop_ms = 1000 * R / fs
quantum_ms = 1000 * 128 / fs
print("algorithmic frame ms", frame_ms)
print("hop ms", hop_ms, "quantum ms", round(quantum_ms, 2))

def rtf(wall_ms, audio_ms):
    return wall_ms / audio_ms

print("RTF if process() takes 3 ms", rtf(3.0, hop_ms))
print("RTF if process() takes 12 ms", rtf(12.0, hop_ms))
```

**Expected.** Frame delay `20.0` ms, hop `10.0` ms, quantum about `2.67` ms. RTF prints `0.3` and `1.2`. The second case misses the hop even though 12 ms is less than the 20 ms window.

**Failure modes.** Dividing wall time by the window instead of the hop reports RTF 12/20 = 0.6 and hides the overrun. Dividing the window by hops/s, or treating RTF 0.3 as “3 ms of latency,” mixes the two clocks and will pass a scorecard that users still hear as delay or as crackle. A p99 of 12 ms with a mean of 3 ms is the figure’s warning: log both.

## Mini exercises

1. Draw the 9-stage pipeline and mark where you would log timestamps.
2. If hop goes 10→5 ms, what happens to hops/s and CPU roughly?
3. Propose three scorecard metrics for a customer-support softphone.
4. Why might 48 kHz hurt a 16 kHz-trained model even if CPU allows?
5. Name one quality artifact from too-short windows.

### Answer hints

1. Stamp capture, after resample, STFT in, STFT out, and encoder handoff; subtract to separate delay from wall time.
2. hops/s doubles (100 → 200 at 48 kHz if the hop was 480 samples); STFT CPU roughly doubles. \(D_{\mathrm{alg}}\) does not halve unless \(L\) changes.
3. For example p95 RTF, algorithmic delay against the call budget, and a listening/DNSMOS check on names and digits.
4. The network’s bins and ERB edges are laid out for 16 kHz; 48 kHz audio labeled as 16 kHz is the wrong spectrum, and extra bandwidth may alias in if you forgot the low-pass.
5. Unresolved harmonics and harsh, flickery masks; plosives smeared is the opposite fault, from a window that is too long.

## Further reading

- DeepFilterNet real-time framing, [arXiv:2110.05588](https://arxiv.org/abs/2110.05588) and [github.com/Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).
- WebRTC APM overview: [modules/audio_processing](https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/).
- MDN AudioWorklet performance guidance — quanta versus your hop.
