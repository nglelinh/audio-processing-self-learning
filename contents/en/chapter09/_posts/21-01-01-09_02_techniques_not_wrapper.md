---
layout: post
title: "09-02 Techniques beyond the npm wrapper"
chapter: "09"
order: 2
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter09
lesson_type: required
draft: false
---

Capstone credit is for a technique you can measure: framing and overlap, a suppression-level policy, an eval harness, a CDN failure path, or an RTF budget. It is not for renaming `deepfilternet3-noise-filter` or for a drive-by refactor inside the shared product repo. The wrapper is the vehicle. DeepFilterNet’s ERB stage and deep filter are the reason the vehicle exists. This lesson forces one hypothesis, one baseline, and one table a maintainer can re-run.

![DeepFilterNet block: ERB path plus multi-frame deep filter]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. The technique under the wrapper: 48 kHz PCM, STFT, an ERB gain path, a deep filter on the complex spectrum, then ISTFT and overlap-add. Your capstone should name which of these you are studying.*

## What you should be able to do

You should be able to propose one change grounded in Chapters 02–08, write the success and fail rules before you collect the second number, and keep the work in a personal fork or an external harness. You should also say which public control you will touch (`setSuppressionLevel`, `setEnabled`, or `assetConfig.cdnUrl`) and which metrics will stay `n/a`.

## A menu that maps to chapters

| Idea | Fuel | Artifact you can grade |
|------|------|------------------------|
| Eval harness with the six-column sheet from 08-04 | Ch. 08 | `suite.md` plus the checker |
| Default level chosen by an AB test | 08-03 | Protocol, N, per-condition wins |
| RTF p95 log and a written downgrade rule | 05, 07 | Device, p95, what you disable |
| Document browser NS versus this processor | 03, 07 | Constraint checklist |
| CDN base and the `v2/` prefix, with a failure drill | 07 | Log of blocked versus cached load |
| Offline synthetic mixer and SI-SDR | 02, 08-01 | The 13.80 / −10.67 lab, then your own wavs |
| Rust `df-core` | 09-03 | Optional stretch, passthrough labeled as such |

Reject CSS-only edits, dependency bumps without a table, and two unrelated hypotheses in one report. If you cannot name the baseline number you will collect first, you do not have an experiment.

## Hypothesis, experiment, measure

Write this before you change a knob:

```text
Hypothesis: Moving setSuppressionLevel from 80 to 60 reduces muffled
            consonants on keyboard clips without a café collapse.

Experiment: The same 12 clips. Levels 80 and 60. AB with at least 6 raters.
            SI-SDR only on synthetic twins. DNSMOS only if one checkpoint
            is pinned; otherwise n/a. RTF p95 on one named laptop.

Success:    Keyboard listening does not prefer 80 for naturalness, café is
            tie or better than bypass, quiet-speech control is mostly ties,
            RTF p95 stays inside the budget you wrote down.

Fail:       Café listeners clearly prefer 80, or quiet speech loses, or
            p95 misses the AudioWorklet quantum. Then you do not change
            the default.
```

The numbers in that box are a template, not a result. Your report replaces them with measurements. There is still no official DNSMOS threshold to hide behind.

## Metrics you must name

Quality is SI-SDR on aligned synthetic pairs, DNSMOS or `n/a` on real files, and a listening note. Systems is RTF p95 or an honest statement that you only have a mean, plus whether init failed when the CDN was blocked. UX is whether `setEnabled(false)` returns the raw mic and whether a missing asset still lets the call publish. If you skip a column, write `n/a` and the reason. Do not copy 13.80 from the SI-SDR lab into a product table and call it DeepFilterNet.

## A note maintainers can keep

Use a short decision record:

- Context: which public API and which chapter.
- Decision: the level, the flag, or the harness layout.
- Metrics: the six-column sheet or a pointer to it.
- Alternatives you rejected, including “edit the shared repo.”
- Follow-ups: what you did not measure (languages, phones, ASR).

The DeepFilterNet figure is the technical content of that note. If your change is only a CDN policy, say that you did not retune the ERB gains or the deep-filter taps. If your change is a level knob, say that the knob is `setSuppressionLevel(0–100)` and that you did not retrain the network.

## Scope cuts

An MVP for this course is a frozen clip list, a baseline column, one change, and a report. A stretch is a second device, a DNSMOS checkpoint you actually run, or the Rust path in 09-03. Training a new enhancement network is out of scope. So is cloud inference of customer audio. So is any patch that lands only on the shared product repository.

## Mini-lab

Write `hypothesis.md` with the four labels `Hypothesis:`, `Experiment:`, `Success:`, and `Fail:`. Name one public API and one metric that will be `n/a`. Run:

```python
from pathlib import Path
text = Path("hypothesis.md").read_text()
need = ["Hypothesis:", "Experiment:", "Success:", "Fail:", "n/a", "setSuppressionLevel"]
# Allow either suppression level or another public control if you edit the checker.
missing = [n for n in need if n not in text]
print("missing", missing or "none")
print("lines", len(text.splitlines()))
```

If your hypothesis uses `setEnabled` or `cdnUrl` instead of `setSuppressionLevel`, change the last required token to that name and say so in the file. Expected output for the level study:

```text
missing none
lines <your count, at least 8>
```

Failure modes: a hypothesis with no fail rule; success defined only as “SI-SDR goes up”; editing files under the shared product repo as the implementation step; claiming the ERB diagram means you must retrain the filter.

## Exercises

1. Write the one-sentence hypothesis you will actually grade. Ask whether a stranger could falsify it.
2. List the baseline numbers you will collect before the change, including at least one `n/a`.
3. Split the idea into MVP and stretch in five lines.
4. Draft the decision-record headings empty, then fill Context and Alternatives.
5. Point at one block in the ERB figure and say whether your capstone touches it.

### Answer hints

1. Include the knob, the condition (keyboard, café, quiet), and the metric. “Make it better” is not falsifiable.
2. Baseline is level 80 or bypass on the same files. Real clips have SI-SDR `n/a` until a clean reference exists.
3. MVP is the table and the AB. Stretch is a second device or Rust. Training is neither.
4. Alternatives should include “do nothing” and “patch the shared repo” (rejected).
5. A level policy does not retune ERB gains. An eval harness does not either. Say that plainly.
