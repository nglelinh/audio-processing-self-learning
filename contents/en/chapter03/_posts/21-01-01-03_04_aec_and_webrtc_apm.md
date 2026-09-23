---
layout: post
title: "03-04 AEC context and WebRTC APM"
chapter: "03"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter03
lesson_type: required
draft: false
---

Acoustic echo cancellation (AEC) is the sibling problem of noise suppression: the “noise” is a filtered copy of the **far-end reference** playing out of the loudspeaker and coupling back into the microphone. Browser and native VoIP stacks almost always run AEC **before** or **together with** NS inside an audio processing module. This lesson situates AEC in the call graph, sketches adaptive-filter cancellation, and walks the **WebRTC Audio Processing Module (APM)** as the industrial reference you will meet in Mezon / LiveKit / browser integrations (Chapter 07).

## Learning objectives

You will draw the near-end / far-end signal flow with echo path $$\mathbf{h}$$, explain why a reference-driven adaptive filter differs from blind NS, list the major WebRTC APM components (AEC, NS, AGC, HPF, VAD), and state practical constraints (delay, clock drift, nonlinear distortion) that leak residual echo into the NS stage.

## 60-minute teaching plan

- **0–10 min** — Demo narrative: hear echo vs noise; identify the far-end reference.
- **10–25 min** — Echo model $$y = s + \mathbf{h}*\mathbf{x} + n$$; adaptive filter estimate $$\hat{\mathbf{h}}$$.
- **25–40 min** — WebRTC APM pipeline tour (conceptual blocks, not line-by-line source).
- **40–50 min** — Residual echo after AEC → why NS / neural postfilters still matter.
- **50–60 min** — Pitfalls, exercises, checklist for product insertion points.

## Core explanation

### Echo is structured “noise”

Near-end microphone signal:

$$
y[t] = s[t] + \underbrace{(h * x)[t]}_{\text{echo}} + n[t],
$$

where $$x[t]$$ is the **far-end** signal (known to the device that renders it), $$h$$ is the acoustic echo path (room + loudspeaker + mic), $$s$$ is near-end speech, and $$n$$ is ambient noise.

AEC estimates $$\hat{h}$$ (or an equivalent frequency-domain filter) and forms

$$
e[t] = y[t] - (\hat{h} * x)[t].
$$

If $$\hat{h}\approx h$$ and the path is linear and slowly varying, $$e\approx s+n$$—then a **noise suppressor** can focus on $$n$$ without fighting a loud echo replica.

### Adaptive filter intuition (NLMS sketch)

In the time domain, an FIR echo path $$\mathbf{h}$$ of length $$L$$ is updated with a normalized LMS-style rule:

$$
\mathbf{h}_{\ell+1} = \mathbf{h}_\ell + \mu \frac{e_\ell\,\mathbf{x}_\ell}{\|\mathbf{x}_\ell\|^2 + \varepsilon},
$$

where $$\mathbf{x}_\ell$$ is the far-end tap vector. Frequency-domain / partitioned-block adaptive filters (as in many WebRTC-oriented AECs) do the same idea with better complexity and delay control.

**Kalman connection (03-03):** covariance-aware step sizes replace the scalar $$\mu$$; the product idea is identical—track $$\mathbf{h}$$ recursively.

### Why AEC ≠ NS

| | AEC | NS |
|---|-----|----|
| Reference | Far-end $$x$$ required | Usually blind |
| Target impairment | Echo $$h*x$$ | Ambient $$n$$ / interferers |
| Failure mode | Delay misalignment, double-talk, nonlinear spk | Non-stationary noise, musical artifacts |
| Typical place | Early in APM | After AEC / with residual-echo suppression |

Double-talk (near-end and far-end speak together) is the classic AEC stress case: the adaptive filter must freeze or slow updates so near-end speech is not mistaken for echo.

### WebRTC APM — mental model

The WebRTC **Audio Processing Module** is a battle-tested chain used broadly in browsers and native stacks. Mentally order the blocks as:

1. **High-pass filter** — remove DC / rumble.
2. **Echo canceller (AEC / AECM)** — reference-driven cancellation; mobile may use lighter variants.
3. **Noise suppression** — classical spectral / Wiener-style NS (configurable levels).
4. **Automatic gain control (AGC)** — level management (can interact badly with NS if ordered poorly).
5. **Voice detection / other extras** — depending on build flags and API era.

Exact ordering and naming evolve across WebRTC versions; treat the above as an **architecture cartoon** for teaching, and verify against current `AudioProcessing` docs when integrating.

**Product relevance:** Mezon and many LiveKit / WebRTC apps may rely on browser AEC **and** inject a neural NS (DeepFilterNet3 via AudioWorklet). You must know whether AEC already ran, whether you still see residual echo, and whether your NS was trained to treat residual echo as “noise.”

### Residual echo and neural postfilters

Linear AEC leaves leftovers when:

- Loudspeaker distortion is nonlinear,
- Delay estimation is wrong (buffering, Bluetooth),
- Clock drift between render and capture,
- Soft furniture / moving talkers change $$h$$ quickly.

Hybrid research (ULCNet + adaptive filter, etc.) trains a small network on the **AEC residual**. Practically: measure ERLE (echo return loss enhancement) before/after AEC; if residual echo remains audible, either fix delay alignment or add a residual-echo suppressor—not only a generic NS.

## Integration checklist (browser / native)

1. Confirm a **far-end reference** is actually provided to AEC (loopback / `getUserMedia` constraints / native ADM).
2. Measure round-trip buffering; align reference delay.
3. Test **double-talk** clips explicitly.
4. Decide NS insertion: inside APM, after APM PCM, or AudioWorklet neural NS (Ch. 05, 07).
5. Disable duplicate AGC stages that fight each other.
6. Log whether echo or noise dominates customer complaints—triage AEC vs NS.

## Pitfalls

- Running neural NS on a signal that still contains full-volume echo → over-suppression of near-end speech during far-end playback.
- Assuming browser AEC is on without checking platform quirks (especially mobile OS effects).
- Training / evaluating NS only on additive noise datasets (DNS-style) then deploying into echo-heavy laptop speakers.
- Placing AGC before AEC so gains modulate the echo path and confuse adaptation.
- Confusing **acoustic** echo with **line** echo in telephony gateways.

## Exercises

1. **Signal-flow diagram.** Draw capture, render, $$\hat{h}$$, error $$e$$, and NS. Mark where AudioWorklet neural NS would sit in a web app.
2. **Delay lab.** Explain what happens to NLMS if the reference is 40 ms early vs 40 ms late relative to the mic echo.
3. **APM config reading.** Skim current WebRTC APM docs; list the toggle names for NS level and AEC; note defaults.
4. **Triage table.** Write a support playbook: symptom → likely AEC vs NS vs AGC cause → first diagnostic step.

## Further reading

- WebRTC Audio Processing Module documentation and `AudioProcessing` API (project website / source).
- SpeexDSP echo canceller / preprocessor docs (related classical stack).
- Haykin, *Adaptive Filter Theory* — NLMS / frequency-domain adaptive filters.
- Hybrid AENR survey pointers: ULCNet + adaptive filter / Align-ULCNet (name-level; residual echo + noise).
