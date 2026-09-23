---
layout: post
title: "09-01 Mezon NS architecture tour"
chapter: "09"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter09
lesson_type: required
draft: false
---

Mezon noise suppression is a product case study, not a second syllabus. The public path is a browser microphone, a LiveKit local track, and `DeepFilterNoiseFilterProcessor` from the npm package `deepfilternet3-noise-filter` (version 1.3.0 in this course). Inference stays on device. The package loads a WASM build and the DeepFilterNet3 ONNX archive from a CDN base you pass as `assetConfig.cdnUrl`. Package ≥ 1.2.0, including 1.3.0, adds `v2/` itself, so the files fetched are `{cdnUrl}/v2/pkg/df_bg.wasm` and `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`. The example base is `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`. You study that path. The weights are the Rikorose DeepFilterNet3 archive. You do not edit the shared repository [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression) as the assignment. A personal fork or an external harness is the workspace. The instructor tree at `/Users/nguyenlelinh/ncc/mezon-noise-suppression` is optional and not required to finish the lab.

![LiveKit publish path with DeepFilterNoiseFilterProcessor]({{ site.imgurl }}/generated/livekit-trackprocessor.png)

*Figure. Public publish path only: mic, `setProcessor`, `DeepFilterNoiseFilterProcessor`, encoded audio, LiveKit. CDN assets feed the processor. `setSuppressionLevel` and `setEnabled` are runtime controls. On asset failure, publish unprocessed audio.*

## What you should be able to do

You should be able to trace eight public steps from the microphone to a published track, name only the API this course treats as public, and map each box to an earlier chapter. You should also write an architecture sketch an advisor can grade without opening private source.

## Public names you may use

Stay on this surface:

| Name | Role |
|------|------|
| `DeepFilterNoiseFilterProcessor` | LiveKit processor that owns the on-device graph |
| `DeepFilterNet3Core` | Lower-level core for a WebAudio graph that is not LiveKit |
| `setProcessor` | Attaches the processor to the local track before publish |
| `setSuppressionLevel(0–100)` | Runtime aggressiveness |
| `setEnabled` | Bypass without pretending the model ran |
| `assetConfig.cdnUrl` | CDN **base**. Do not append `v2/` yourself |

LiveKit’s own docs are the signaling reference: [docs.livekit.io](https://docs.livekit.io/). The processor does not own tokens, the room, or the SFU. `DeepFilterNet3Core` is the escape hatch when you are not inside a LiveKit `TrackProcessor`. It is still the same product package, not a private class you invent.

## Eight-step publish path

Read this once, then close it and rewrite it in the mini-lab.

1. The page requests the microphone and receives a `MediaStream`.
2. You wrap that stream in a LiveKit local audio track. The track is the object that can accept a processor.
3. You construct `DeepFilterNoiseFilterProcessor` (or `DeepFilterNoiseFilter(options)`, which returns that processor) and pass `assetConfig.cdnUrl` as the CDN base, with no `v2/` suffix.
4. Package ≥ 1.2.0, including 1.3.0, requests `{cdnUrl}/v2/pkg/df_bg.wasm` and `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz`.
5. You call `setProcessor` with that processor so samples are enhanced before encode.
6. You publish the track to the room. The SFU receives encoded audio, not your CDN credentials.
7. Later, `setSuppressionLevel` between 0 and 100 changes aggressiveness without a new publish.
8. `setEnabled(false)` bypasses the model. If WASM or the archive fails to load, you still publish the unprocessed microphone and you surface the error. A dead join button is not a noise-suppression feature.

That is the whole public story. Rust `df-core` is not on this diagram. It is an optional stretch in lesson 09-03, not a second product you must draw to pass.

## What each layer is for

The application layer is the LiveKit room: join, mute, leave. Chapter 07 owns that boundary. The processor layer is `DeepFilterNoiseFilterProcessor` together with the audio callback that must finish inside the render quantum (Chapter 05). The asset layer is the WASM module and the ONNX tar on the CDN (Chapters 06 and 07). The model those assets run is the DeepFilterNet3 line from [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet): an ERB gain stage plus a deep filter on the STFT, which is why Chapters 02 and 04 are prerequisites. Controls are `setEnabled` and `setSuppressionLevel`. Evaluation is Chapter 08: SI-SDR when you have a clean reference, DNSMOS when you do not, a listening note, and RTF p95.

Browser noise suppression and echo control still exist beside this processor. If both run, you will not know which one ate the consonants. Document the `noiseSuppression` constraint you set. That interaction is a checklist item, not a private class.

## Advisor sketch

```markdown
## Mezon NS — architecture sketch
- Goal: on-device uplink noise suppression for a LiveKit meeting
- Data path: mic → setProcessor(DeepFilterNoiseFilterProcessor) → publish
- Assets for ≥ 1.2.0 including 1.3.0: {cdnUrl}/v2/pkg/df_bg.wasm and {cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz
- Controls: setEnabled, setSuppressionLevel(0–100)
- Eval: SI-SDR on synthetic pairs, DNSMOS or n/a on real clips, AB note, RTF p95
- Non-goals: uploading raw audio for cloud inference; editing the shared product repo
- Stretch (optional): a personal Rust df-core harness, labeled passthrough until a real backend exists
```

| Chapter | Question the sketch must answer |
|---------|----------------------------------|
| 02 | Sample rate and frame/hop, without inventing a hidden buffer API |
| 03 | Whether browser AEC/NS is on at the same time |
| 04 | Why this model is DeepFilterNet3 and what the level knob trades |
| 05 | What happens when the callback misses its quantum |
| 06 | WASM and the ONNX archive; the package adds `v2/` for ≥ 1.2.0 |
| 07 | `setProcessor` and `assetConfig.cdnUrl` |
| 08 | Which metric is `n/a` on a real recording |

## Mini-lab

Write `publish-path.md` with exactly eight numbered steps from the microphone to publish. Use only public names. Then run:

```python
import re
from pathlib import Path
text = Path("publish-path.md").read_text()
steps = re.findall(r"(?m)^\s*(\d+)\.\s+\S", text)
need = [
    "DeepFilterNoiseFilterProcessor",
    "setProcessor",
    "setSuppressionLevel",
    "setEnabled",
    "cdnUrl",
    "df_bg.wasm",
    "DeepFilterNet3_onnx.tar.gz",
]
missing = [n for n in need if n not in text]
print("steps", len(steps))
print("missing", missing or "none")
```

Expected output:

```text
steps 8
missing none
```

Failure modes: a ninth step that names a private class; putting `v2/` inside `cdnUrl` itself; stopping the call when assets fail; describing Rust `df-core` as required; pointing the lab at `/Users/nguyenlelinh/ncc/mezon-noise-suppression` as if that tree were part of the assignment.

## Exercises

1. Fill the advisor sketch in your own words, one page, with the asset URLs written out.
2. Draw the failure branch for a blocked CDN. The success branch still publishes audio. Say which audio.
3. List three telemetry events that do not upload PCM (for example asset HTTP status, init milliseconds, `setEnabled` flips).
4. State where `DeepFilterNet3Core` is allowed in your design, and where `DeepFilterNoiseFilterProcessor` is required.
5. Explain why a personal fork is the workspace and the shared GitHub repo is not.

### Answer hints

1. Include both `v2/` files and say the prefix is the package’s, not yours.
2. On failure, publish the unprocessed mic and show an error. Do not block the room.
3. Counters and timings only. No samples, no transcripts of the room.
4. LiveKit publish path uses the processor and `setProcessor`. A custom WebAudio page may use the core. Do not invent further methods.
5. Course tasks read the public README and API. Experiments go in your fork or harness.
