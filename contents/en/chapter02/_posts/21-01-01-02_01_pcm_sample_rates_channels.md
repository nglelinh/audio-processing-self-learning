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

Neural noise suppressors eat tensors; microphones produce PCM. This lesson makes buffer formats, rates, and channel layouts explicit — the #1 source of “integration” bugs before any model runs.

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
| `int16` (`s16`) | \([-32768,32767]\) | WebRTC, WAV; watch endianness |
| `float32` | typically \([-1,1]\) FS | Web Audio `AudioBuffer` |
| `int32` / 24-bit in containers | rare in NS hot path | convert once |

Conversion sketch:

$$
x_{f32} \approx \frac{x_{s16}}{32768}
$$

(Exact libraries may use 32767; be consistent to avoid tiny gain errors.)

### Time, samples, bytes

$$
N_{\mathrm{samples}} = t\cdot f_s,\qquad
N_{\mathrm{bytes}} = N_{\mathrm{samples}}\cdot C\cdot B
$$

where \(C\) = channels, \(B\) = bytes per sample (2 for s16, 4 for f32).

**Example:** 20 ms, 48 kHz, stereo s16 → \(0.02\cdot48000\cdot2\cdot2=3840\) bytes.

### Interleaved vs planar

- **Interleaved stereo:** `LRLRLR...`
- **Planar:** all L then all R (or separate pointers)

Feeding interleaved stereo into a mono FFT “as mono” aliases channels into fake high frequencies — catastrophic. Always deinterleave / downmix explicitly.

### Downmix policies for speech NS

Pick one and document it:

1. **Mean:** \(m=(L+R)/2\) (watch correlated vs anti-correlated content).
2. **Left-only / right-only:** if product mic is known.
3. **Energy-weighted:** rare in realtime.

Never average after independent NS on L and R without a spatial policy — phasey mess.

### Clocks

`AudioContext.sampleRate` may be 44100, 48000, or others. getUserMedia tracks may be resampled by the browser. **Measure** `sampleRate`; do not hardcode. Place one high-quality resampler at the edge of the NS block to the model’s native rate.

### Mezon / WebRTC expectations (public)

Browser integrations typically deal with Float32 PCM from Web Audio / worklets, often 48 kHz device rate, mono after downmix for single-channel models. Confirm against the current `deepfilternet3-noise-filter` / repo README rather than this lesson’s assumptions when shipping.

## Worked examples

### Byte length

1 second mono f32 @ 16 kHz → \(16000\cdot4=64000\) bytes.

### Peak clipping

s16 near ±32767 clipping creates harmonics (distortion) that NS may treat as speech/noise unpredictably — prefer headroom before NS.

### Wrong channel stride

Interleaved stereo length 960 frames misunderstood as 960 mono samples @ 48 kHz → you processed 10 ms of “scrambled” L/R as if 20 ms mono.

## Common pitfalls

1. Assuming little-endian always when reading files on exotic platforms (usually LE, still assert).
2. Floats outside \([-1,1]\) after processing → sink distortion.
3. Hardcoding 48 kHz.
4. Stereo model input silently truncated to first half buffer.
5. Forgetting that WAV headers ≠ raw PCM from callbacks.

## Mini exercises

1. Bytes for 10 ms mono s16 @ 16 kHz?
2. Write downmix pseudocode interleaved → mono mean.
3. Why is anti-correlated stereo \((L=-R)\) dangerous for mean downmix?
4. List three places sampleRate can differ in a WebRTC send path.
5. Convert s16 value −16000 to float FS with /32768.

## Further reading

- Web Audio API `AudioBuffer` / `AudioWorkletProcessor` buffer formats.
- WebRTC media track constraints and PCM notes.
- WAV / RFC PCM format references as needed for offline eval tools.
