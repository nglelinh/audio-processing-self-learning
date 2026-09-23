---
layout: post
title: "09-04 Capstone project brief"
chapter: "09"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter09
lesson_type: required
draft: false
---

The capstone is a written design, a measured demo on a small clip set, and a public-API story you can defend. It is not a patch to the shared product repository [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression). Work in a personal fork or in the `capstone/` tree this lab creates. The instructor path `/Users/nguyenlelinh/ncc/mezon-noise-suppression` is optional local context, not a required checkout and not a place to invent files.

![Evaluation map for the capstone report]({{ site.imgurl }}/generated/eval-metric-map.png)

*Figure. The report uses the evaluation map: SI-SDR only with a clean reference, DNSMOS or `n/a`, a listening note, and a systems line for RTF. The ship box is a decision, not a slogan.*

## What you should be able to do

You should be able to create the capstone directories, mix a four-sample signal at a known SNR, pick one primary track, and list the artifacts a grader will open. You should also state the failure mode of each milestone so a slip does not become a silent skip.

## Tracks

**A. Eval and policy (recommended).** Freeze clips, fill the six-column sheet from lesson 08-04, and justify one `setSuppressionLevel` choice with an AB note.

**B. Integration.** Exercise `assetConfig.cdnUrl` (Mezon example `https://cdn.mezon.ai/AI/models/datas/noise_suppression/deepfilternet3`), the automatic `v2/` prefix on package ≥ 1.2.0 including 1.3.0, `setEnabled`, and a blocked-CDN drill that still publishes audio.

**C. Rust stretch.** Optional `df-core` from lesson 09-03. A passthrough backend must be labeled passthrough. Partial credit is real if the label is honest. No credit for “NS works” on a copy loop.

Pick one primary track. The others may appear only as a named non-goal.

## Milestones and how they fail

| ID | Output | Failure mode |
|----|--------|----------------|
| M0 | Architecture sketch (09-01) and hypothesis (09-02) | Private class names, or no fail rule |
| M1 | Baseline on a frozen clip list | Tuning the list after you see the score |
| M2 | Change lives in your fork or `capstone/`, not the shared tree | A commit on the product repo “just to try” |
| M3 | Six-column table, `n/a` where required | Invented SI-SDR on a real mic file |
| M4 | Demo checklist (09-05) | Live CDN as the only path, no backup recording |

There is no week count hiding in the IDs. Finish M0 before you collect M3, or you will fit the hypothesis to the number.

## Artifacts the grader opens

1. `capstone/design/sketch.md` — goal, public data path, asset URLs, non-goals.
2. `capstone/design/hypothesis.md` — hypothesis, experiment, success, fail.
3. `capstone/audio/` — small wavs or the `.npy` from the mixer, plus a README of filenames.
4. `capstone/metrics/suite.md` — clip id, condition, SI-SDR or `n/a`, DNSMOS or `n/a`, listening note, RTF p95.
5. `capstone/notes/reading.md` — at least five bullets that tie Chapters 02–08 to a public API or a paper URL from lesson 10-01.
6. `capstone/notes/limits.md` — languages, devices, and the Rust status (`not attempted` or `passthrough` or a real backend).

A slide deck is optional. An unreproducible screenshot of a score is not a metric.

## Grading emphasis

High weight: the technique is real and the table is honest, including `n/a`. High weight: someone else can re-run the mixer or the checker. Medium weight: a demo path that survives headphones and a blocked CDN. Low weight: visual polish. Zero: unapproved edits to the shared product repo, and any report that calls passthrough “noise suppression.”

Non-goals, stated so they do not creep: training a new state-of-the-art model, bit-exact Rust parity as a graduation requirement, and uploading customer audio to a cloud model without a privacy design you do not have.

## Mini-lab

From an empty working directory that is **not** the product repo:

```bash
mkdir -p capstone/{design,audio,metrics,notes}
find capstone -type d | sort
python3 -c 'import numpy as np; s=np.array([1.,0,-1,.5]); n=np.array([.2,-.2,.2,-.2]); g=np.linalg.norm(s)/(10**(10/20)*np.linalg.norm(n)); y=s+g*n; np.save("capstone/audio/mix.npy", y); print(np.round(y,3).tolist())'
```

Expected output:

```text
capstone
capstone/audio
capstone/design
capstone/metrics
capstone/notes
[1.237, -0.237, -0.763, 0.263]
```

The mixer builds a 10 dB mixture of the lesson 08-01 reference `s` with a four-point noise vector. `g` scales the noise so that $$10\log_{10}(\|s\|^2/\|gn\|^2) = 10$$. The printed samples are $$s + gn$$ rounded to three decimals. Confirm with `find capstone -type f | sort` that `capstone/audio/mix.npy` exists.

Failure modes: running `mkdir` inside the shared product clone; a different SNR because the formula used amplitude ratios twice; forgetting `np.save` and then claiming the directory listing is the whole lab; treating `[1.237, -0.237, -0.763, 0.263]` as a DeepFilterNet output. It is the noisy mixture.

After the commands, add a milestone checklist to `capstone/design/sketch.md` with M0–M4 marked `todo` or `done`. A grader should see the directories even if every milestone is still `todo`.

## Exercises

1. Choose track A, B, or C and write the M0 hypothesis under `capstone/design/`.
2. Freeze ten clip filenames in `capstone/audio/CLIPS.txt` before you score anything.
3. Start `capstone/notes/reading.md` with five bullets and real URLs you will actually open.
4. Name the single failure mode most likely to hit you, from the table above, and the file that will show it.
5. Re-run the one-line mixer at 0 dB (replace `10/20` with `0/20`) and explain why the samples change.

### Answer hints

1. Track C still needs the passthrough label if you have no model.
2. Filenames only. No scores yet, so you cannot steer the set.
3. Use the URLs in lesson 10-01. Do not invent a successor paper.
4. The common miss is M2 on the shared repo, or M3 with a fake SI-SDR.
5. At 0 dB, $$\|gn\| = \|s\|$$, so `g` is larger and the noise is more visible in the printout.
