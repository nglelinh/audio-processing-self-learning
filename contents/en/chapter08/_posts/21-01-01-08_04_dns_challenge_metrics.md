---
layout: post
title: "08-04 DNS Challenge-style metric suites"
chapter: "08"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter08
lesson_type: required
draft: false
---

A single SI-SDR mean is how enhancement papers get quoted and how products get surprised. The Microsoft DNS Challenge ([microsoft/DNS-Challenge](https://github.com/microsoft/DNS-Challenge)) is the public pattern this course copies in miniature: synthetic pairs where intrusive metrics are legal, real recordings where they are not, a listening slice, and a systems column so realtime software cannot hide behind a quality table. Challenge editions change their metric menus. Pin the year or the paper you follow. Do not claim you “beat the DNS Challenge” unless you ran that year’s blind set with that year’s protocol.

![Evaluation map: intrusive SI-SDR, non-intrusive DNSMOS, and listening tests]({{ site.imgurl }}/generated/eval-metric-map.png)

*Figure. A suite is the whole map, not one box. SI-SDR, DNSMOS, listening, and RTF answer different questions. Empty cells are written `n/a`, not imputed.*

## What you should be able to do

You should be able to lay out a six-column score sheet with one row per clip, run a checker that rejects a missing column, and explain which cells must be `n/a`. You should also separate a lab regression epsilon from any number that appears in a paper.

## Tracks worth keeping

| Track | Material | Legal metrics |
|-------|----------|----------------|
| Synthetic | Noisy/clean pairs you generated | SI-SDR, optional PESQ/STOI, delta versus bypass |
| Real | Meeting-like recordings, no clean file | DNSMOS if the checkpoint is pinned, else `n/a` |
| Listening | The same conditions, short clips | AB note: win, loss, or tie |
| Systems | The machine that will demo | RTF p95, plus init or fallback if you measured it |
| Optional downstream | Fixed ASR build | WER or CER delta, never as a MOS substitute |

Synthetic data gives you SNR knobs and a reference. It also lies when the noise bank is cleaner than a real room. Real data is the product and refuses SI-SDR. The rule is to tune on neither column alone. Freeze a final listening subset that you do not open while you are still changing levels.

## Harness layout

Keep the harness in your own directory or fork. Do not put it inside the shared product tree `mezonai/mezon-noise-suppression`, and do not require the instructor checkout at `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.

```text
eval/
  datasets/synthetic/   # clean/, noisy/, meta.csv
  datasets/real/
  systems/bypass/
  systems/level60/
  systems/level80/
  scripts/compute_si_sdr.py
  reports/YYYY-MM-DD.md
```

`meta.csv` needs at least `clip_id,condition,snr_db,clean_path,noisy_path`. Real rows leave `clean_path` empty. Reproducibility is a header on the report: package version (npm `deepfilternet3-noise-filter` 1.3.0 if that is what you ran), model archive name `DeepFilterNet3_onnx.tar.gz`, DNSMOS checkpoint name or `not run`, OS, and the device you used for RTF. If enhancement is deterministic, say so. If it is not, record the seed.

There is no official SI-SDR or DNSMOS cutoff to copy into CI. You may choose a lab epsilon after you have a baseline on this exact set, and you must label it as local. A paper’s table is not that epsilon.

Optional ASR: pick one engine version, transcribe noisy and enhanced with the same settings, and report the delta. Enhancement that helps DNSMOS and hurts WER is a product fact, not a contradiction to hide.

## Report skeleton

```markdown
## NS eval — <date>
- System: deepfilternet3-noise-filter <version>, setSuppressionLevel <n>
- RTF p95: <number and device> or n/a

### Per clip
(the six-column table from the mini-lab)

### Decision
Ship, no-ship, or ship behind a flag — and which column forced it.

### Limits
Languages, devices, and metrics you did not run.
```

Overfitting shows up as a suite that only contains your own voice, one café, and a mean with no per-condition rows. Re-run after a WASM or SIMD change. Sample equality rarely survives a runtime swap, so the metrics must move with the binary.

## Mini-lab

Create `suite.md` with a markdown table of **six data rows**. The header must contain these columns: clip id, condition, SI-SDR or `n/a`, DNSMOS or `n/a`, listening note, RTF p95. Use `n/a` when the metric is illegal or not run. At least one row must be a real clip (`n/a` SI-SDR) and at least one row must be synthetic. Listening notes are short (`new`, `old`, `tie`, or `not listened`). RTF p95 is a number you measured or `n/a` if you did not.

Checker `check_suite.py`:

```python
from pathlib import Path
lines = Path("suite.md").read_text().splitlines()
tables = [ln for ln in lines if ln.strip().startswith("|")]
header = tables[0].lower()
need = ["clip id", "condition", "si-sdr", "dnsmos", "listening note", "rtf p95"]
missing = [n for n in need if n not in header]
data = [ln for ln in tables[2:] if ln.strip().strip("|").strip()]
print("missing", missing or "none")
print("data_rows", len(data))
```

Expected output:

```text
missing none
data_rows 6
```

Shape example (your six rows must be your own clips; this single row only shows the cells):

```markdown
| clip id | condition | SI-SDR or n/a | DNSMOS or n/a | listening note | RTF p95 |
| --- | --- | --- | --- | --- | --- |
| syn_fan_01 | synthetic fan, 10 dB | 13.80 | n/a | tie | 0.35 |
```

The 13.80 here is the lesson 08-01 lab float, pasted so the column type is obvious. It is not a measurement of DeepFilterNet. Failure modes: a header that says “quality” instead of the six names; five rows; a real recording with a made-up SI-SDR; one RTF number copied onto every row without saying it is a session-level figure; an official-looking threshold such as “DNSMOS must exceed 3.5.”

## Exercises

1. Fill all six rows for a mix of synthetic and real conditions. Run the checker until it prints `data_rows 6`.
2. Write the `meta.csv` header and one synthetic row and one real row.
3. Propose a CI fail rule that does not pretend to be an official DNSMOS threshold.
4. Name two ways a suite overfits Mezon meeting audio, and the holdout that blocks each.
5. Add an ASR column as optional. State why it must not replace the listening note.

### Answer hints

1. Real rows: SI-SDR is `n/a`. Rows without a DNSMOS run: DNSMOS is `n/a`.
2. Real row: empty clean path. Do not invent a reference file.
3. Example policy: “on this 12-clip golden set, fail if the per-condition DNSMOS mean drops by more than the epsilon written in the report.” The epsilon is yours.
4. Only the author’s voice; only café. Hold out other talkers and a keyboard or fan condition you do not tune on.
5. WER can rise when the suppressor damages consonants the metric likes. Keep the listening note.
