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

Research and product teams both need a **suite**, not a single number. The Microsoft **DNS Challenge** tradition is the template most DeepFilterNet-related papers and industrial evals echo: synthetic mixtures with intrusive metrics, real recordings with non-intrusive predictors, plus human listening. This lesson turns that tradition into a reproducible harness outline and a capstone reporting template.

## 60-minute teaching plan

- 0–10 min: Why suites beat single metrics.
- 10–25 min: Typical DNS-style tracks (synthetic / real / listening).
- 25–40 min: Minimal reproducible harness architecture.
- 40–50 min: Optional ASR WER downstream metric.
- 50–60 min: Fill the capstone reporting template.

## Learning objectives

By the end of this lesson, you can:

- List typical tracks/metrics used in DNS-style evals.
- Build a minimal reproducible eval harness outline.
- Avoid overfitting to a single synthetic set.
- Produce a product-facing eval report section.

## Typical tracks in a DNS-style suite

| Track | Material | Metrics |
|-------|----------|---------|
| Synthetic blind | noisy/clean pairs | SI-SDR, (PESQ/STOI if you choose), Δ vs baseline |
| Real recordings | no clean ref | DNSMOS (version pinned), optional other predictors |
| Listening | curated subset | AB / MUSHRA-like |
| Stress / systems | long streams, device matrix | RTF p95, glitches, init failure rate |
| Optional downstream | enhanced speech → ASR | WER / CER delta |

Challenge editions vary — **pin** the challenge year or paper when you claim "DNS metrics".

## Synthetic vs real

**Synthetic pros:** controllable SNR, reproducible, intrusive metrics.  
**Synthetic cons:** ISM reverberation and noise banks can mismatch real rooms (see also training-data discussions in DeepFilterNet follow-ons).

**Real pros:** product truth.  
**Real cons:** no SI-SDR; harder to automate.

**Rule:** never tune only on synthetic SI-SDR; always keep a frozen real set + listening subsample.

## Minimal harness outline

```text
eval/
  datasets/
    synthetic/  # clean/, noisy/, meta.csv
    real/       # wavs + notes
  baselines/
    raw/        # copy of noisy or bypass
    apm/        # optional browser APM capture
  systems/
    df3_level80/
    df3_level60/
  scripts/
    run_enhance.py
    compute_si_sdr.py
    compute_dnsmos.py
    make_tables.py
  reports/
    YYYY-MM-DD_capstone.md
```

Reproducibility checklist:

- Package version + git commit of enhancer
- Model archive hash
- DNSMOS model version
- Machine / OS for RTF
- Random seeds if any stochastic stage exists

## Optional ASR WER

Enhancement that pleases MOS but hurts ASR (or vice versa) happens. If your product feeds captions/bots:

1. Pick a fixed ASR engine/version.
2. Transcribe clean (if any), noisy, enhanced.
3. Report WER delta on the same utterances.

Do not treat WER as a MOS substitute.

## What to report in a product eval (template)

```markdown
## NS eval — <date>
- System: deepfilternet3-noise-filter <ver> / level <n>
- Devices: <list>; RTF p50/p95: <…>

### Synthetic
| Condition | ΔSI-SDR | notes |
| Real (DNSMOS <ver>)
| Condition | mean | n |
### Listening (AB, N raters)
| Condition | new win% |
### Decision
Ship / no-ship / ship behind flag — rationale
### Limits
…
```

## Overfitting defenses

1. Hold out a **final** listening set untouched during tuning.
2. Separate noise types; ban cherry-picking one café clip.
3. Track regressions on clean speech.
4. Re-run after WASM/SIMD upgrades (bit-exactness rarely holds — watch metrics).

## Common pitfalls

1. "We beat DNS Challenge winner" without same test set / protocol.
2. Mixing DNSMOS versions in one chart.
3. No systems metrics in a realtime product report.
4. Harness that only the author can run.

## Exercises

1. Fill the template using hypothetical but consistent numbers for level 60 vs 80.
2. Write `meta.csv` column schema for synthetic clips.
3. Propose ε thresholds for CI fail on DNSMOS and ΔSI-SDR.
4. List two ways your suite could overfit Mezon meeting audio — and mitigations.

## Further reading

- Microsoft DNS Challenge overview papers and baseline reports (by year).
- SI-SDR + DNSMOS combination practices in DeepFilterNet2/3 papers.
- Course 08-01…08-03; Capstone 09-04/09-05.
- LiveKit/WebRTC integration lessons for systems metrics context (Chapter 07).
