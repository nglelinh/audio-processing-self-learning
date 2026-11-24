---
layout: post
title: "04-05 Ultra-light streaming models"
chapter: "04"
order: 5
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

Some products cannot spend DeepFilterNet2’s notebook budget. The names **GTCRN**, **FastEnhancer**, **μNet**, and **Fast-ULCNet** are a shortlist vocabulary for ultra-light streaming enhancers. This lesson does **not** attach paper titles, years, or URLs to them. It teaches the measurement that decides the shortlist: MAC tables and wall-clock RTF come apart, and a GRU state that runs for an hour is a different bug from a slow hop.

![Real-time factor against an AudioWorklet quantum: wall time per audio block, not a MAC table]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Figure. RTF is wall time divided by audio time. A 128-sample AudioWorklet quantum at 48 kHz lasts about 2.67 ms. An ultra-light model is one whose p95 wall time fits the hop you actually run, on the CPU you actually ship. GTCRN, FastEnhancer, μNet, and Fast-ULCNet are names only on this figure — no paper, year, or URL.*

A noise-suppression model that scores a dazzling 21 dB SI-SDR on an offline benchmark can be completely unusable on a live Zoom or Mezon call. Why? Because offline models peek 500 milliseconds into the future and burn 40 GFLOPs per second on a desktop GPU—whereas a live call inside a laptop browser tab gives you roughly **20–40 milliseconds of total algorithmic latency** and a tiny slice of a single CPU core!

This lecture introduces the engineering art of **ultra-light streaming speech enhancement models**: how strict causality, compact STFT front-ends, depthwise-separable convolutions, and small recurrent bottlenecks squeeze high-quality denoising into a few hundred thousand parameters running smoothly in real time.

---

## Background Knowledge Map: Four Pillars of Ultra-Light Streaming Audio Models

Designing a neural audio model that runs live on CPU/WASM rests on four interlocking constraints:

1. **Strict Causality & Algorithmic Latency:** A streaming model cannot see future audio beyond a tiny budgeted lookahead $$L$$. Total algorithmic latency equals the STFT synthesis window (or frame + overlap-add delay) plus any neural lookahead—typically capped below 30–40 ms so human conversation stays natural.
2. **Compute Complexity (MACs/sec) vs. Parameter Count:** Parameter count governs *download size* and *RAM*, while **multiply-accumulate operations per second (MACs/s)** govern CPU time. A small 1D convolution run 100 times per second can cost fewer MACs than a tiny dense layer applied to every frequency bin.
3. **Hybrid DSP + Neural Decomposition:** Instead of forcing a neural network to learn Fourier physics from raw waveforms, ultra-light architectures operate on STFT magnitudes or perceptually spaced filterbanks (ERB/Bark), letting the network predict smooth gain masks or small complex residuals.
4. **Depthwise-Separable & Grouped Recurrence:** Replacing full 2D convolutions with depthwise + pointwise layers and using grouped GRUs cuts MACs by 5–10× with minimal loss in speech intelligibility.

---

## Learning objectives

You will explain, with the DeepFilterNet2 table as the worked example, why GMAC and RTF can move in opposite directions; place the four ultra-light names on a selection checklist without inventing their results; and design a long-stream state check that does not depend on any of those papers.

## 60-minute teaching plan

- **0–10 min** — Hearable DSP versus a laptop tab: two budgets.
- **10–25 min** — The DF2 numbers as a MAC-versus-RTF proof.
- **25–40 min** — The four names, one line each, and what you still must measure.
- **40–50 min** — State drift over tens of minutes.
- **50–60 min** — Mini-lab, checklist, exercises.

## Core explanation

### Two budgets that are not the DF2 table

DeepFilterNet2 (arXiv:2205.05474) reports RTF **0.04** at **0.356 GMAC** on a notebook Core i5-8250U, against the ICASSP row at 0.348 GMAC and RTF **0.11**. The 2023 tract loop reports RTF **0.19** on an i5-8250U. RNNoise, on that DF2 table, is about 0.06 M parameters, RTF 0.027, PESQ 2.33, against DF2’s PESQ 3.08. Those are the only compute numbers treated as printed here. A hearable or a phone is a different machine: laptop RTF is not phone RTF. Ultra-light graphs aim at much smaller memory and one short hop, and they usually land nearer PESQ 2.33 than 3.17. That is acceptable when the alternative is an underrun.

### Why a MAC table lies

A multiply-accumulate count assumes every MAC has the same wall time. It does not.

- Grouped or sub-band gathers jump around memory. The ALU waits on the cache. FastEnhancer is the name people cite when they make this argument; this page does not quote that paper.
- A slightly larger dense GEMM, fused by the runtime, can finish sooner than a clever grouped conv the ONNX Runtime kernel does not vectorize.
- Temporal kernels store a ring of past activations. DF2 cut kernels from $$2\times 3$$ to $$1\times 3$$ (input layer excepted) and the RTF fell from 0.11 to 0.04 with GMAC flat. That is the mechanism to copy into your own reading of any ultra-light graph: count bytes moved per hop, not only MACs.

**Measurement rule (Chapter 05).** Single thread, warm-up discarded, p50 and p95 of per-hop wall time, divided by the hop duration. Run it on the target device under the audio callback’s pacing. A paper MAC column is a hypothesis.

### The four names, and only the names

| Name | Role on this course’s shortlist | What this lesson will not say |
|------|---------------------------------|--------------------------------|
| **GTCRN** | A widely mentioned ultra-light grouped convolutional recurrent net | No title, year, URL, MAC, or MOS |
| **FastEnhancer** | A name attached to “speed on device,” including ONNX Runtime timing | No result numbers |
| **μNet** | A name attached to extreme low memory (DSP, hearable) | No result numbers |
| **Fast-ULCNet** | A name attached to the ULCNet line and to long-stream RNN state | No result numbers |

Related strings you will see in the same cluster — ULCNet, UL-UNAS, AdaptCRN, CoFi-Lite, FSPEN — are optional vocabulary. They are not exam content and they are not given citations here.

### State that runs longer than the demo clip

A 3-second clip hides GRU drift. At a 10 ms hop, 45 minutes is $$45\times 60\times 100=270\,000$$ updates. Quantization, an unstable gate, or unseen silence walks the state off the training region. You hear a slow rise in musical noise or a slow ducking, not a click at $$t=0$$. Fast-ULCNet is only the shortlist name associated with that discussion; this page states no cure from a paper. Tests you can run without a citation:

- During detected silence, blend the GRU state toward zero over a few hundred milliseconds, not in one hop. A hard zero is the click or noise burst of lesson 05-04.
- Bound the state norm if the architecture allows a scale that does not change the gain.
- Log gain histograms at minute 1 and minute 40. A shift at the same input level is drift.

### When the DF3 path still wins

Prefer the DeepFilterNet3-associated model on a laptop browser when WASM SIMD holds the hop and a few megabytes of weights are acceptable. Prefer an ultra-light name on a DSP or a tiny CPU, where residual noise is allowed. A split is coherent: classical AEC plus a tiny residual suppressor on the device, DF3 in the browser. A 16 kHz weight file in a 48 kHz graph is not a light DF3; resample on purpose.

## Shortlist checklist

1. Causal, and how many look-ahead frames?
2. 16 kHz or 48 kHz, and where is the resampler?
3. p95 RTF on **your** device, one thread, warm cache, callback pacing.
4. Weight bytes and cold-start time, separate from RTF.
5. A run of at least 30 minutes with a silence stretch.
6. License of the weights.
7. Every operator present in your ONNX Runtime or tract build.

## Pitfalls

- Picking the winner from a MAC column.
- Porting grouped convolutions the WASM runtime executes as scalar loops.
- Skipping the 30-minute run.
- Feeding 48 kHz PCM to a model whose STFT was trained at 16 kHz.

## Mini-lab

**Goal.** Reproduce the DF2 “GMAC flat, RTF not flat” comparison from published numbers, then apply the same ratio test to a fake ultra-light pair so you see what a decision looks like before any unnamed paper is involved.

```bash
python3 - << 'PY'
# Numbers from the DeepFilterNet2 paper's Voicebank table (notebook i5).
rows = [
    ("DF ICASSP row", 0.348, 0.11),
    ("DF2 simplified", 0.356, 0.04),
]
for name, gmac, rtf in rows:
    print(f"{name}: gmac={gmac:.3f} rtf={rtf:.2f} rtf_per_gmac={rtf/gmac:.3f}")
# Hypothetical shortlist. These MACs are lab fiction, not paper results.
fake = [("modelA", 0.05, 0.30), ("modelB", 0.08, 0.12)]
best = min(fake, key=lambda r: r[2])
print("lower_p95_rtf", best[0])
PY
```

**Expected**. `DF ICASSP row: gmac=0.348 rtf=0.11 rtf_per_gmac=0.316` and `DF2 simplified: gmac=0.356 rtf=0.04 rtf_per_gmac=0.112`. Then `lower_p95_rtf modelB`. Model B has more MACs and a lower RTF, which is the selection rule.

**Failure modes**. Treating the fake pair as GTCRN or FastEnhancer results. Quoting 0.04 as a phone RTF. Ranking on `rtf_per_gmac` alone when one model’s p95, not its mean, misses the hop.

---

### Worked Numerical Example: Budgeting Latency and MACs/sec for a 48 kHz Streaming Denoiser

Suppose we design a causal STFT denoiser at sample rate $$f_s = 48{,}000	ext{ Hz}$$ with window length $$N = 960$$ samples, hop size $$H = 480$$ samples (50% overlap), and $$L = 1$$ frame of lookahead in the neural network:

1. **Frame duration & frame rate:**
   $$T_{	ext{win}} = rac{960}{48{,}000} = 20	ext{ ms}, \qquad T_{	ext{hop}} = rac{480}{48{,}000} = 10	ext{ ms} \implies 100	ext{ frames/s}.$$
2. **Total algorithmic latency:**
   $$T_{	ext{alg}} = T_{	ext{win}} + L \cdot T_{	ext{hop}} = 20	ext{ ms} + 1 	imes 10	ext{ ms} = 30	ext{ ms}$$
   *(still well below the ~150 ms ITU-T G.114 one-way conversational comfort threshold, leaving room for network + jitter buffer!)*.
3. **Compute rate:** Suppose each forward pass on one STFT frame costs $$1.5	ext{ MMACs}$$ (1.5 million multiply-adds). At 100 frames/s:
   $$	ext{Compute rate} = 100 	imes 1.5	ext{ MMAC} = 150	ext{ MMAC/s} pprox 300	ext{ MFLOP/s}.$$
   On a single browser WASM core sustaining ~3 GFLOP/s, the model consumes roughly $$300 / 3000 = 10\%$$ of the frame budget ($$\mathrm{RTF} pprox 0.10$$)!

### Deep-Dive Explanation: Four Rules for Designing Real-Time Streaming Models (Read Slowly)

1. **Always separate *algorithmic* latency from *compute* latency:** Even on an infinitely fast CPU, a 20 ms STFT window plus 2 frames of lookahead (20 ms) still introduces 40 ms of unavoidable delay.
2. **Halving the hop size doubles your CPU bill:** Dropping $$H$$ from 10 ms to 5 ms cuts latency by 5 ms, but doubles the neural network frame rate from 100 to 200 calls per second!
3. **Inspect activation memory, not just weight size:** A model with only 200 KB of weights can still stall CPU caches if intermediate feature maps explode across frequency bins.
4. **Profile end-to-end (STFT + neural net + iSTFT):** On ultra-light models, FFTs, windowing, and data marshaling can easily account for 20–30% of total wall-clock time.

**Quick check.** If we double the neural lookahead from $$L = 1$$ frame to $$L = 3$$ frames (keeping $$T_{	ext{win}} = 20	ext{ ms}$$ and $$T_{	ext{hop}} = 10	ext{ ms}$$), what is the new algorithmic latency—and does the MACs/sec compute cost change?

---

## Exercises

1. **Scenario.** For an on-ear DSP, a mid-range laptop in Chrome, and a Raspberry Pi class speakerphone, choose DF3 or “an ultra-light name” and give the budget reason in one sentence each.
2. **Harness sketch.** Warm-up count, hop duration, and the percentile you will gate on. Why is the mean not the gate?
3. **Drift.** 10 ms hop, 40 minutes. How many GRU updates is that? What do you compare at the start and at the end?
4. **Names.** Write one sentence each for GTCRN, FastEnhancer, μNet, and Fast-ULCNet that contains no digit and no year.

### Answer hints

1. DSP: ultra-light, because the DF2 0.04 RTF was measured on a Core i5. Laptop Chrome: DF3, if WASM SIMD holds p95 inside the hop and the download size is acceptable. Pi-class board: the DF2 paper claims real-time on a Pi 4 for **that** model; an ultra-light name is the fallback if your build’s p95 does not.
2. Drop the first 50 hops, hop = 10 ms = 0.01 s, gate on p95 (and watch p99). The mean hides the late frame that underruns. Chapter 05 computes this exactly.
3. $$40\times 60\times 100=240\,000$$ updates. Compare band-gain histograms or the state norm on a repeated calibration clip, not the raw waveform of the whole call.
4. Use only the one-line roles in the table above. A digit means you invented a result.

## Further reading

- Schröter et al., DeepFilterNet2, [arXiv:2205.05474](https://arxiv.org/abs/2205.05474), for the 0.11 versus 0.04 RTF rows. That is the MAC-versus-RTF example.
- Schröter et al., Interspeech 2023, [arXiv:2305.08227](https://arxiv.org/abs/2305.08227), for the RTF 0.19 tract-loop figure.
- Valin, [arXiv:1709.08243](https://arxiv.org/abs/1709.08243), as the tiny hybrid baseline (lesson 04-06).
- Primary sources you open yourself for GTCRN, FastEnhancer, μNet, and Fast-ULCNet. None are linked here.

## Video tham khảo

- [RNNoise, Neural Speech Enhancement, and the Browser](https://www.youtube.com/watch?v=nsscrYdrGRE) — W3C, English. **xem trước.** Watch a suppressor small enough for a browser and a Raspberry Pi. That budget is the ultra-light streaming problem, without attaching papers to the shortlist names.
- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, English. The complexity-versus-quality plot is what an ultra-light model has to survive before the name on the shortlist matters.
- [Zoom on Web: getting connected with advanced web technology](https://www.youtube.com/watch?v=nhTxJBgTywc) — Chrome for Developers, English. The SIMD section shows why a tiny model still needs a vectorized runtime if the hop is a few milliseconds.
