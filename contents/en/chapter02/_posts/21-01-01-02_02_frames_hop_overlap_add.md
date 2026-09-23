---
layout: post
title: "02-02 Frames, hop size, and overlap-add"
chapter: "02"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter02
lesson_type: required
draft: false
---

STFT pipelines carve audio into overlapping frames, process each, and glue them with overlap-add (OLA). Getting hop and OLA wrong produces musical warble that no neural weight update will fix.

## Learning objectives

1. Define frame length \(L\), hop \(R\), and overlap ratio.
2. Explain overlap-add reconstruction and the COLA condition.
3. Compute algorithmic delay implications of \(L\) and \(R\).
4. Choose hops for speech NS with latency/quality intuition.
5. Implement a mental model of streaming OLA buffers.

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–12 | Frame/hop diagrams on the whiteboard |
| 12–28 | OLA math; COLA with Hann examples |
| 28–42 | Streaming buffer mechanics; edge effects |
| 42–52 | Numerics at 16/48 kHz for speech |
| 52–60 | Exercises |

## Core explanations

### Framing

Window length \(L\) samples; hop \(R\) samples (\(1\le R\le L\)). Overlap ratio:

$$
\rho = 1-\frac{R}{L}
$$

50% overlap means \(R=L/2\); 75% means \(R=L/4\).

### Overlap-add

Given modified frames \(y_m[n]=w_{\mathrm{syn}}[n]\cdot \mathrm{iFFT}(\hat{X}_m)\), output:

$$
\hat{x}[n]=\sum_m y_m[n-mR]
$$

If \(\hat{X}_m\) equals analysis STFT of \(x\) and windows satisfy **COLA**, \(\hat{x}\) reconstructs \(x\) (up to delay/gain).

### COLA (constant overlap-add)

For hop \(R\), analysis/synthesis windows must make the sum of shifted window products constant:

$$
\sum_m w_{\mathrm{ana}}[n-mR]\,w_{\mathrm{syn}}[n-mR] = C
$$

(Exact statement depends on whether windows are applied once or twice; be consistent with your STFT definition.) Hann with 50% overlap is a classic COLA choice when used carefully.

### Latency

Larger \(L\) → more frequency detail, more buffering delay. Smaller \(R\) → denser updates, higher CPU (more hops/s), often smoother masks. Product NS usually lives in the 5–20 ms hop ballpark for speech, but **match the model**.

### Streaming OLA buffer

Keep an output accumulator of length \(\ge L\). Each hop: add the new windowed frame at the write cursor; emit \(R\) samples that are “finished”; shift/carry the overlap tail. On start/stop, flush tails to avoid clicks.

## Worked examples

### Numbers

\(f_s=48\,\mathrm{kHz}\), \(L=960\) (20 ms), \(R=480\) (10 ms): \(\rho=0.5\), hops/s=100.

\(f_s=16\,\mathrm{kHz}\), \(L=512\), \(R=256\): 16 ms window, 8 ms hop, hops/s=62.5.

### Broken COLA symptom

Amplitude tremolo at \(f_s/R\) Hz (e.g. 100 Hz for 10 ms hop). Listeners say “robotic” or “phasey.”

### Warm-up

First \(L-R\) samples of output may be incomplete depending on implementation — discard or fade in for metrics.

## Common pitfalls

1. Analysis Hann + synthesis rectangular without checking COLA.
2. Changing hop but reusing windows from another hop.
3. Emitting full \(L\) samples every hop (massive overlap redundancy / desync).
4. Clearing OLA memory each callback.
5. Offline STFT (center-padded) vs streaming STFT mismatch in eval.

## Mini exercises

1. Overlap ratio for \(L=1024\), \(R=256\)?
2. Hop ms at 16 kHz with \(R=160\)?
3. Why does smaller hop increase CPU?
4. Sketch OLA buffer after 3 hops of length \(L=8\), \(R=4\) (toy).
5. Name one test signal to verify COLA (hint: impulse or linear chirp).

## Further reading

- Oppenheim & Schafer — STFT / filterbank / OLA sections.
- Classic COLA window references in DSP notes.
- DeepFilterNet framing descriptions in papers.
