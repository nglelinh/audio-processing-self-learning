---
layout: post
title: "00-01 Why real-time noise suppression matters"
chapter: "00"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter00
lesson_type: required
draft: false
---

Picture yourself joining a high-stakes design review from a bustling café—espresso grinders roaring behind you, a mechanical keyboard clacking beside the laptop mic, and two colleagues debating at the next table. The person on the other end does not care how impressive your neural network’s offline benchmark looks on a research leaderboard; they care about one thing: *can they understand you effortlessly, without robotic warble and without an awkward half-second delay?*

That lived product constraint is **real-time noise suppression (NS)**. This opening lesson frames the *problem* before a single filter or neural layer is chosen: what “good” actually means to human ears versus speech recognizers, why streaming causality changes everything, and how this course connects to Mezon’s public noise-suppression stack.

![Offline file enhancement beside a causal call path that cannot see the future]({{ site.imgurl }}/generated/realtime-vs-offline.png)

*Figure. A real-time suppressor may use audio only up to “now,” plus a small look-ahead budget; an offline enhancer may see the whole file.*

**Lesson roadmap:** Background Knowledge Map (additive mixture model, causal vs. offline systems, three competing enhancement goals) → Core product constraints & Mezon public surface → Worked example: a complete 48 kHz latency & RTF budget checked by hand → Deep-Dive Explanation (Read Slowly): 3 steps from raw microphone PCM to a shippable real-time budget → Pitfalls, Mini-lab, Exercises & Videos.

---

## Background Knowledge Map: What Does Real-Time Speech Enhancement Actually Study?

### 1. The Observation Model — Separating Signal from Interference
At the microphone, clean speech $$x(t)$$ and unwanted background noise $$n(t)$$ add together into a single waveform $$y(t) = x(t) + n(t)$$ (or in a reverberant room, $$y(t) = (x * h)(t) + n(t)$$). Single-channel noise suppression is an **ill-posed inverse problem**: you receive one sum and must recover one of its two unknown summands in real time, usually after transforming short overlapping frames into the time–frequency (STFT) domain $$Y(\ell, k) = X(\ell, k) + N(\ell, k)$$.

### 2. Three Competing Objectives — Intelligibility, Quality, and ASR
A quieter spectrogram is not automatically a better call. Speech enhancement balances three distinct targets: **intelligibility** (preserving consonants like /s/, /f/, /t/ so words stay clear), **perceptual quality** (natural timbre without watery “musical noise”), and **ASR accuracy** (avoiding spectral distortions that confuse downstream speech-to-text models). Optimizing one can degrade another.

### 3. Causality, Latency, and Real-Time Factor (RTF)
In interactive voice calls, a suppressor cannot peek 500 ms into the future. It must run **causally** inside a strict **latency budget** (typically $$\le 20\text{–}40\,\mathrm{ms}$$ algorithmic buffering) and finish each audio hop faster than the hop arrives—measured by the **Real-Time Factor** $$\mathrm{RTF} = T_{\mathrm{proc}} / T_{\mathrm{audio}} \ll 1$$ on the *actual target CPU*, including worst-case spikes.

---

## Learning objectives

By the end of this lesson (~60 minutes) you should be able to:

1. Explain why single-channel NS is a first-class requirement in VoIP, conferencing, and embedded voice UIs.
2. Separate three enhancement goals: **intelligibility**, **perceptual quality**, and **ASR-friendly** input.
3. Distinguish real-time / causal enhancement from offline batch enhancement in product terms (latency, RTF).
4. Locate this course relative to the public Mezon stack (`mezonai/mezon-noise-suppression`, npm `deepfilternet3-noise-filter`) without inventing unpublished internals.
5. State what this course will *not* treat as primary (full AEC/AGC product stacks).

## 60-minute teaching plan

| Minutes | Activity |
|--------:|----------|
| 0–8 | Warm-up: listen mentally to three scenes (office HVAC, street, keyboard) and list what breaks in a call |
| 8–20 | Product goals: intelligibility vs quality vs ASR; map each to a failure mode |
| 20–35 | Real-time constraints: frame delay, RTF, why offline SOTA often cannot ship |
| 35–48 | Mezon / DeepFilterNet product context (public surface only) and course scope |
| 48–60 | Mini exercises + discussion of pitfalls |

## Core explanations

### Noise as a product constraint

In consumer and enterprise voice products, noise is not an academic additive disturbance $$n(t)$$. It is a **user-visible SLA**:

- **Office / HVAC**: quasi-stationary low-frequency rumble; easy for classical estimators, annoying if left alone.
- **Street / café**: non-stationary bursts; classical noise-floor trackers lag; neural models earn their keep.
- **Keyboard / mouse**: impulsive, broadband clicks that punch through speech formants.
- **Babble**: competing speech; the hardest single-channel case because the “noise” lives in the same time–frequency patterns as the target.

A usable NS block must reduce these without turning speech into watery artifacts, without adding tens of milliseconds of delay that destroy conversational turn-taking, and without burning so much CPU that an AudioWorklet callback underruns.

### Three enhancement goals (do not collapse them)

Engineers often say “make it cleaner.” That hides three different objectives:

1. **Intelligibility** — can a listener (or ASR) recover words? Spectral distortion that removes consonants can *look* quieter on a spectrogram and still destroy intelligibility.
2. **Perceptual quality** — MOS / DNSMOS-style pleasantness: less hiss, less musical noise, natural timbre.
3. **ASR upstream** — some pipelines optimize word-error rate; aggressive NS that helps humans can *hurt* ASR if it removes cues the recognizer relies on.

Classical metrics (SI-SDR) and listening metrics (DNSMOS) disagree often enough that product teams must pick a primary goal. This course emphasizes **real-time conversational quality** aligned with Mezon-style browser / WebRTC paths, while teaching evaluation tools in Chapter 08.

### Real-time vs offline (preview; deep dive in 00-03)

Offline enhancement may use the whole utterance, bidirectional context, and large networks. Real-time enhancement is **causal**: at time $$t$$ you may only use audio up to $$t$$ (plus a small intentional look-ahead budget).

Two numbers dominate design reviews:

- **Algorithmic / buffering latency** (ms): how long until the cleaned sample leaves the pipeline.
- **Real-time factor (RTF)**: wall-clock processing time divided by audio duration. For streaming, you need worst-case RTF $$\ll 1$$ on the *target* device, not the mean on a laptop CPU.

If a published model needs 200 ms look-ahead and RTF 0.8 on a phone CPU, it is research-interesting and product-dead for interactive calls.

### Mixture model (one equation to keep)

Single-channel observation in the time domain:

$$
y(t) = x(t) + n(t)
$$

or, after an STFT,

$$
Y(\ell,k) = X(\ell,k) + N(\ell,k)
$$

where $$\ell$$ is the frame index and $$k$$ the frequency bin. Almost every classical and neural NS method is a strategy for estimating $$X$$ (or a mask / filter that recovers $$X$$) from $$Y$$ under real-time constraints. Convolutional distortion (reverb) is a *related but separate* problem:

$$
y(t) = (x * h)(t) + n(t)
$$

Do not claim a single-channel NS model “solves reverb” unless evaluation explicitly includes it.

### Mezon product context (public facts only)

This course is aligned with Mezon noise-suppression product work:

- GitHub organization/repo: **`mezonai/mezon-noise-suppression`**
- npm package surface commonly referenced in the outline: **`deepfilternet3-noise-filter`**
- Instructor local checkout (do not require students to have this path): `/Users/nguyenlelinh/ncc/mezon-noise-suppression`

**Teach techniques** (DSP → classical NS → DeepFilterNet family → realtime/on-device → eval → integration), not “how to call one npm wrapper.” Anything not documented in public READMEs, papers, or npm docs is out of scope for claims.

### Scope boundaries

| In scope | Out of scope as primary syllabus |
|----------|-----------------------------------|
| Framing, STFT, classical NS, DeepFilterNet ideas, RTF, ORT/WASM, WebRTC/LiveKit integration patterns, metrics | Full acoustic echo cancellation (AEC) product design, multi-mic beamforming hardware, unpublished Mezon internals |
| AEC / AGC / WebRTC APM as *context* (Ch. 03) | Claiming the course replaces WebRTC APM |

## Worked example — latency budget sketch

A conferencing product targets $$\le 40\,\mathrm{ms}$$ algorithmic buffering from mic callback to cleaned PCM handed to the encoder.

Assume $$f_s = 48\,\mathrm{kHz}$$, frame length $$L = 480$$ samples (10 ms), hop $$R = 240$$ samples (5 ms), and a model that needs one frame of look-ahead.

- Buffering to assemble one analysis window of 10 ms already costs 10 ms if you wait for a full window (implementations can overlap; still, *some* buffering exists).
- Hop 5 ms means you emit a new STFT column every 5 ms — good for continuity, but CPU must finish each hop’s work within that budget on average.
- One-frame look-ahead adds another $$\sim 5$$–$$10\,\mathrm{ms}$$ depending on definition.

**Numerical intuition.** At 48 kHz, 1 ms is 48 samples, so the 40 ms budget is $$40\times 48=1920$$ samples. Waiting for the 480-sample window spends 10 ms; one hop of look-ahead spends another 5 ms; 25 ms remain for everything else in that sketch. A forward pass that takes 8 ms on a separate 20 ms hop has RTF $$8/20=0.40$$. The same pass at 22 ms has RTF $$1.1$$ and will underrun unless you lengthen the hop or shrink the model. The mini-lab prints the first set of figures.

---

### Deep-Dive Explanation: How a Product Latency Budget Constrains Your Algorithm (Read Slowly)

Why do so many impressive academic speech-enhancement papers fail the moment you drop them into a browser call? Trace the 3-step constraint chain:

#### Step 1: Convert milliseconds into exact sample counts at the device clock
At $$f_s = 48{,}000\,\mathrm{Hz}$$, every millisecond equals exactly $$48$$ samples. A $$40\,\mathrm{ms}$$ total algorithmic budget gives you only $$1{,}920$$ samples of leeway from the moment air hits the microphone until clean PCM reaches the network encoder.

#### Step 2: Subtract unavoidable framing and look-ahead delay before running a single layer
Assembling a $$480$$-sample analysis window spends $$10\,\mathrm{ms}$$; granting the neural network just one hop ($$240$$ samples) of future look-ahead spends another $$5\,\mathrm{ms}$$. Before you write a single line of model code, $$15\,\mathrm{ms}$$ is already spoken for—leaving $$25\,\mathrm{ms}$$ for overlap-add reconstruction, WebAudio callback buffering, and jitter margin.

#### Step 3: Gate the compute path by worst-case RTF, not mean RTF
Every $$5\,\mathrm{ms}$$ hop triggers a new forward pass. Even if average compute is $$2\,\mathrm{ms}$$ ($$\mathrm{RTF} = 0.40$$), a single $$7\,\mathrm{ms}$$ thermal or garbage-collection spike pushes that hop to $$\mathrm{RTF} = 1.40$$, causing an audible dropout. Real-time engineering therefore designs for **causal look-ahead + p99 RTF $$\ll 1$$** from Day 1.

Summary of the real-time NS design gate:

$$
y(t) = x(t) + n(t)
\;\xrightarrow{\text{STFT } (L, R)}\;
\text{Latency} \le 40\,\mathrm{ms}
\quad \& \quad
\mathrm{RTF}_{p99} = \frac{T_{\mathrm{proc}, p99}}{T_{\mathrm{hop}}} \ll 1.
$$

## Common pitfalls

1. **Optimizing SI-SDR offline** and shipping the same checkpoint for streaming without measuring causal latency and device RTF.
2. **Treating “noise reduction %”** as a metric — undefined for product QA.
3. **Assuming mono NS** works unchanged on stereo without a documented downmix policy.
4. **Blaming the neural model** when the bug is sample-rate mismatch, wrong hop, or OLA window mismatch (Ch. 01–02 checklists).
5. **Claiming Mezon-specific secrets** from reading this course — stick to public surfaces and general DeepFilterNet literature.

## Mini-lab

**Goal.** Recompute the 48 kHz sketch so a hop change cannot hide inside a spreadsheet.

```python
fs, hop, window, budget_ms = 48_000, 240, 480, 40.0
hop_ms = 1_000 * hop / fs
window_ms = 1_000 * window / fs
print(f"hop_ms={hop_ms:.1f} window_ms={window_ms:.1f}")
print(f"samples_per_ms={fs/1000:.0f} budget_samples={budget_ms*fs/1000:.0f}")
print(f"remaining_ms={budget_ms - window_ms - hop_ms:.1f} rtf={8/20:.2f}")
```

**Expected.** `hop_ms=5.0 window_ms=10.0`, then `samples_per_ms=48 budget_samples=1920`, then `remaining_ms=25.0 rtf=0.40`.

**Failure modes.** Swapping hop and window, counting 16 kHz samples inside a 48 kHz budget, or defining RTF as audio duration over processing time.

## Mini exercises

1. Pick a 10-second mental scene (café). List three noise events and mark each as stationary / non-stationary / speech-like.
2. Write one sentence each for intelligibility, quality, and ASR goals for a customer-support softphone.
3. Given $$f_s=16\,\mathrm{kHz}$$ and hop $$R=160$$ samples, compute hop duration in ms and the maximum average processing time for RTF $$= 0.5$$.
4. Browse the public `mezonai/mezon-noise-suppression` README (when online) and list three *documented* capabilities — do not invent others.

### Answer hints

1. HVAC changes slowly; a door slam does not; a nearby talker is speech-like babble.
2. Intelligibility is words recovered, quality is pleasantness, ASR is word error — the third can move against the first two.
3. Hop duration is $$160/16000=10\,\mathrm{ms}$$. RTF $$0.5$$ allows $$5\,\mathrm{ms}$$ of average processing on that hop.
4. Quote README bullets only (package, runtime, sample rate). Do not infer an unpublished graph.

## Further reading

- WebRTC Audio Processing Module (APM) documentation — noise suppression overview.
- Schröter et al., DeepFilterNet (arXiv:2110.05588), DeepFilterNet2 (arXiv:2205.05474), DeepFilterNet3 (arXiv:2305.08227) — introductions for why causal enhancement is the product problem. Repo: https://github.com/Rikorose/DeepFilterNet.
- DNS Challenge overview pages (dataset and track motivation).

## Video tham khảo

- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, English. **xem trước.** Watch how a calling product treats background noise as a user complaint before any filter is chosen; that is the problem this lesson frames.
- [DeepFilterNet: A Low Complexity Speech Enhancement Framework for Full-Band Audio (ICASSP 2022)](https://www.youtube.com/watch?v=it90gBqkY6k) — Hendrik Schröter, English. The author states a full-band causal enhancer with a few milliseconds of latency, which is the real-time constraint the lesson contrasts with offline enhancement.
- [DeepFilterNet Noise Suppression Demo](https://www.youtube.com/watch?v=EO7n96YwnyE) — Hendrik Schröter, English. Listen to the before-and-after the lesson is motivating: office and non-stationary noise on a live suppressor, not a metric table.
