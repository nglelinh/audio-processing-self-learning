---
layout: post
title: "09-05 Capstone checklist & demo day"
chapter: "09"
order: 5
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter09
lesson_type: required
draft: false
---

Demo day is a five-minute proof that the publish path, the metrics, and the limits all exist. A polished title slide with no RTF number and no backup recording is a miss. This checklist is the day-before runbook: commands, files, and the failures you will inject on purpose.

![RTF against the AudioWorklet render quantum]({{ site.imgurl }}/generated/rtf-audioworklet.png)

*Figure. RTF is wall time of a quantum divided by the quantum’s duration. A mean below 1 can still overrun if p95 or p99 spills the callback. Log p95, and keep cold-start asset download out of that number.*

## What you should be able to do

You should be able to walk the audio path, the asset path, and the metric files, rehearse a five-minute script, and inject a CDN failure without ending the call. You should also show one listening example with the condition name visible.

## Technical checklist

Copy this into `capstone/notes/demo_checklist.md` and tick it. A blank box is a fail until you write `n/a` and why.

Audio path:

- Microphone permission works on the machine you will demo.
- `setEnabled(true)` and `setEnabled(false)` both leave a published track. If your UI must rejoin, write that limitation down.
- Browser `noiseSuppression` is recorded as on or off so you do not credit `DeepFilterNoiseFilterProcessor` for the browser’s own suppressor.
- Leaving the room does not leak an extra audio context you can hear on the next join.

Model load:

- Cold start fetches `{cdnUrl}/v2/pkg/df_bg.wasm` and `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` for package ≥ 1.2.0, including 1.3.0. Confirm in the network panel that you did **not** also put `v2/` inside `assetConfig.cdnUrl`.
- A second join uses cache or you document that it does not.
- With the CDN blocked, the call still publishes unprocessed audio and the UI shows an error. Screenshot or a one-line log goes in `capstone/notes/`.

Metrics, from `capstone/metrics/suite.md`:

- Six columns: clip id, condition, SI-SDR or `n/a`, DNSMOS or `n/a`, listening note, RTF p95.
- At least one real row with SI-SDR `n/a`.
- RTF p95 names the device. If you only dogfooded, the cell is `n/a`, not a guessed 0.2.
- Versions: `deepfilternet3-noise-filter` version, model archive name, DNSMOS build or `not run`.

Demo hygiene:

- A backup recording plays if the live mic fails.
- Headphones are on the table.
- One café or babble clip, one keyboard clip, one quiet clip.

Rust, if you touched it: the first spoken sentence matches `df_core_status.md`. Passthrough means you say “noise suppression is not running.”

## Five-minute script

| Time | Say this | File you can open |
|------|----------|-------------------|
| 0:00–0:40 | Uplink noise, on-device, LiveKit publish | `design/sketch.md` |
| 0:40–1:20 | Eight public steps, no private classes | `publish-path.md` |
| 1:20–2:30 | Play raw versus processed, name the condition | backup wav |
| 2:30–3:30 | One row of the suite that improved, one that did not | `metrics/suite.md` |
| 3:30–4:20 | Hypothesis result, including a fail if that is the truth | `design/hypothesis.md` |
| 4:20–5:00 | Limits: language, device, DNSMOS version, Rust status | `notes/limits.md` |

If the rehearsal exceeds five minutes, cut the architecture slide before you cut the counterexample row. The row that did not improve is the evidence you understand the map.

## Failure injection

Block the CDN host (DevTools offline, or a bad `cdnUrl`) and join. Expected: the room still has audio; the processor does not pretend the model ran; your notes say whether `setEnabled` was reachable. Restore the network and reload. Expected: WASM and the tar.gz load from the `v2/` paths. If either injection does something else, that behavior is a limit, not a surprise you hide.

RTF injection, if you have a log: scroll to the worst quantum, not the mean. The figure’s overrun bar is the failure mode. A p95 you never computed stays `n/a`.

## Mini-lab

Run the checklist file through a checker after you have copied the headings.

```python
from pathlib import Path
text = Path("capstone/notes/demo_checklist.md").read_text().lower()
need = [
    "setenabled",
    "noisesuppression",
    "df_bg.wasm",
    "deepfilternet3_onnx.tar.gz",
    "si-sdr",
    "dnsmos",
    "rtf p95",
    "backup",
    "passthrough",
]
missing = [n for n in need if n not in text]
print("missing", missing or "none")
```

Expected output:

```text
missing none
```

Use the token `passthrough` even if your line is “Rust: not attempted, so not a passthrough claim.” The checker only requires the word so the demo script cannot forget the stretch rule. Failure modes: ticking RTF with no device; a backup recording that is a different sentence than the live clip; `v2/` typed into `cdnUrl` and also added by the package, so the request 404s; calling a passthrough Rust build “NS works.”

## Exercises

1. Time a rehearsal. Write the wall time in `capstone/notes/rehearsal.txt`. Cut until you are at or under 5:00.
2. Perform the CDN block. Paste the observed publish behavior under the checklist.
3. Exchange limitation sections with a peer. Each of you must find one overclaim.
4. List the files from 09-04 that you will zip or push from your fork. Exclude the product repo.
5. Point at the overrun bar in the RTF figure and say what you will report if your log only has a mean.

### Answer hints

1. Cut architecture before the bad metric row.
2. Expected honest line: “audio published, model not loaded, UI showed an error” or whatever you truly saw.
3. Typical overclaim: SI-SDR language on a real clip, or DNSMOS without a version.
4. `capstone/design`, `audio`, `metrics`, `notes`. No path under the shared Mezon tree.
5. Report the mean and set RTF p95 to `n/a`. Do not invent a percentile.
