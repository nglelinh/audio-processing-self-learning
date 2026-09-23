---
layout: post
title: "10-02 Further learning paths"
chapter: "10"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter10
lesson_type: required
draft: false
---

After the capstone, pick one path and a thirty-day practice that produces files, not a reading list you will not open. The three paths below reuse the evaluation map: intrusive SI-SDR where a clean reference exists, DNSMOS or `n/a` on real audio, a listening note, and RTF when the work is realtime. Adjacent topics are named so you can choose a weekend experiment. They are not a second course you must finish.

![Evaluation map used to choose a follow-on project]({{ site.imgurl }}/generated/eval-metric-map.png)

*Figure. Whatever path you pick, the map still applies. A classical filter, a paper reproduction, and a LiveKit policy are all graded by which column they actually move.*

## What you should be able to do

You should be able to choose classical DSP, neural speech enhancement, or productization, write a thirty-day calendar with a file you will commit each week, and name one adjacent topic with a concrete weekend command or measurement. You should also turn the capstone `capstone/` tree into a portfolio piece that does not depend on the shared product repo.

## Path A — classical depth

Re-implement overlap-add until a sine reconstructs within a tolerance you print. Read SpeexDSP (<https://github.com/xiph/speexdsp>) or WebRTC APM (<https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/>) far enough to say what the noise suppressor block is responsible for, as distinct from AEC. On a stereo file you recorded, describe one beamforming failure (a talker off to the side, a noisy reference mic) without claiming a new algorithm.

Exit ticket: a note, `path-a/when-classical.md`, that shows one clip where a simple spectral gate or Wiener-style gain beats a heavy model on RTF and does not embarrass the listening note. Include SI-SDR only if you still have the clean reference.

## Path B — neural speech enhancement

Read one primary paper a week from lesson 10-01, starting with arXiv:2110.05588, arXiv:2205.05474, and arXiv:2305.08227. Reproduce one ONNX Runtime or tract timing on a laptop CPU and write RTF as wall time over audio duration, plus the CPU name. If you compare DeepFilterNet3 to an ultra-light name (FastEnhancer, μNet, Fast-ULCNet, GTCRN), keep the comparison on **your** clips and do not invent a paper URL. Successors DPDFNet, DeepFilterGAN, and HDF-Net are the same kind of pointer: names until you have a real citation in front of you.

Exit ticket: `path-b/table.md` with the six columns from lesson 08-04 and a limits paragraph. No leaderboard language.

## Path C — productization

Stay on the public LiveKit path: mic, `DeepFilterNoiseFilterProcessor`, `setProcessor`, publish. Measure cold-start time of `{cdnUrl}/v2/pkg/df_bg.wasm` and `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` (the prefix 1.3.0 adds for ≥ 1.2.0) on a network you actually have, and repeat with the CDN blocked. Optional Rust `df-core` remains a stretch alternative to the WASM box. If the backend is passthrough, the portfolio README says so.

Exit ticket: `path-c/design.md` with init time, RTF p95 or `n/a`, and the failure log from the blocked CDN.

## Adjacent weekends

| Topic | Weekend artifact |
|-------|------------------|
| AEC | A recording where echo dominates noise, plus a note that NS will not remove it |
| Multi-mic | One stereo file and a paragraph on which channel you would trust |
| Target speaker | A babble clip where DNSMOS and your ear disagree |
| Codec | The same utterance through a low-rate Opus encode before and after NS |
| Captions | WER or a manual error count on ten sentences, not a MOS claim |

## Thirty-day calendar

| Days | File you add | Done when |
|------|----------------|-----------|
| 1–3 | `notes/si_sdr.py` re-run of the 13.80 / −10.67 lab | Both floats match lesson 08-01 |
| 4–7 | `audio/CLIPS.txt` with 20 filenames | No scores in the file yet |
| 8–14 | Path MVP (`path-a`, `path-b`, or `path-c`) | A command in the README |
| 15–21 | `metrics/suite.md` and one peer listening note | Checker from 08-04 prints 6 data rows, or you document fewer and why |
| 22–26 | `DEMO.md` under five minutes | Backup audio named |
| 27–30 | A doc patch in **your** fork, or an ADR at work | No commit to the shared Mezon product repo unless that is your job outside this course |

## Portfolio contents

Ship the architecture sketch, the metrics table, the AB protocol in English and Vietnamese, a demo recording at or under three minutes, and the reading cards from 10-01. Strip local absolute paths. The optional instructor checkout is not part of the public portfolio.

## Mini-lab

Create `path_plan.md`:

```text
path: A
week1_file: notes/si_sdr.py
weekend: aec
command: python3 notes/si_sdr.py
```

Use `A`, `B`, or `C`. `weekend` must be one of `aec`, `multimic`, `target`, `codec`, `captions`.

```python
from pathlib import Path
text = Path("path_plan.md").read_text().lower()
path_ok = any(f"path: {p}" in text for p in "abc")
weekend_ok = any(w in text for w in ("aec", "multimic", "target", "codec", "captions"))
print("path", "ok" if path_ok else "fix")
print("weekend", "ok" if weekend_ok else "fix")
print("command", "ok" if "command:" in text else "fix")
```

Expected output:

```text
path ok
weekend ok
command ok
```

Failure modes: three paths in one month; a weekend topic with no artifact; an RTF goal with no device; a plan that starts by forking nothing and editing the shared product tree.

## Exercises

1. Fill `path_plan.md` for the path you will actually do. Run the checker.
2. Write the week-by-week filenames into the same file under the four-line header.
3. Name one upstream doc gap (LiveKit processor page, npm README, or DeepFilterNet README) you could fix with a paragraph, and the paragraph’s claim.
4. Draft the portfolio README section that links the five artifacts. Include the passthrough rule if Rust appears.
5. State which evaluation-map column your path will leave as `n/a` and why.

### Answer hints

1. One letter. Switching paths on day 20 is a new plan, not a bonus.
2. Filenames must be creatable on your machine. Do not point at the instructor’s home directory.
3. A real gap: the `v2/` prefix, or the difference between `setEnabled(false)` and a failed asset load.
4. Link files, not private repos you cannot share.
5. Real audio leaves SI-SDR as `n/a`. A pure DSP reconstruction lab can leave DNSMOS as `n/a`.
