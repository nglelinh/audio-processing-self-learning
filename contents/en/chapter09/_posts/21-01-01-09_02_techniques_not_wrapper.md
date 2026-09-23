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

Capstone credit comes from **techniques**: framing, buffering, model choice, quantization mindset, eval discipline — not from renaming a dependency. This lesson helps you pick one improvement grounded in Chapters 02–05 (and 06–08), define metrics, and keep scope shippable.

## 60-minute teaching plan

- 0–10 min: Wrapper trivia vs technique evidence.
- 10–25 min: Idea menu mapped to chapters.
- 25–40 min: Hypothesis → experiment → measure loop.
- 40–50 min: Scope cuts for a course timeline.
- 50–60 min: Pick your capstone hypothesis sentence.

## Learning objectives

By the end of this lesson, you can:

- Propose one improvement grounded in Chapters 02–05 (or 06–08).
- Define success metrics (RTF, SI-SDR/DNSMOS, listening).
- Keep scope shippable in a course capstone.
- Document tradeoffs for maintainers.

## Technique idea menu

| Idea | Chapter fuel | Artifact |
|------|--------------|----------|
| Better readiness / CDN fallback UX | 07-03 | policy + telemetry |
| Suppression level default from listening | 08-03 | AB results + config |
| Eval harness with SI-SDR + DNSMOS | 08 | repo of scripts + tables |
| RTF logging / auto-downgrade | 05, 07 | metrics + policy |
| Disable browser NS when DF on | 03, 07 | constraint checklist |
| Offline CLI parity test vectors | 09-03 | wav goldens |
| Private CDN immutable layout | 07-03 | ops doc |
| Stretch: tract backend in df-core | 06, 09-03 | Rust milestone |

Avoid: drive-by refactors, CSS-only changes, "bump to latest" without measurements.

## Hypothesis → experiment → measure

Template:

```text
Hypothesis: Lowering default suppression 80→60 reduces muffled complaints
            without unacceptable noise leak on keyboard clips.

Experiment: Same 12-clip set; levels 80 vs 60; AB with ≥6 raters;
            DNSMOS mean; optional ΔSI-SDR on synthetic twins.

Success:    Keyboard AB win≥50% for 60 on naturalness OR ties +
            café noise still preferred/tied vs raw; RTF unchanged.

Fail:       Café noise wins for 80 by large margin AND users reject 60.
```

## Metrics you must name

1. **Quality:** SI-SDR and/or DNSMOS + listening  
2. **Systems:** RTF or qualitative CPU; init failure rate  
3. **UX:** time-to-NS-ready; fallback correctness  

## Documentation for maintainers

Deliver a short ADR-style note:

- Context  
- Decision  
- Metrics  
- Alternatives rejected  
- Follow-ups  

## Common pitfalls

1. Multiple unrelated changes in one capstone.
2. No baseline measurement before "improvement".
3. Editing product code when a harness/docs experiment suffices.

## Exercises

1. Write your hypothesis in one sentence; peer-critique specificity.
2. List baseline numbers you will collect *before* changing anything.
3. Cut scope: what is MVP vs stretch for your idea?
4. Draft the ADR outline empty headings.

## Further reading

- DeepFilterNet2/3 papers — experimental protocol inspiration.
- ORT / WASM performance docs (high level) for RTF work.
- Chapter 08 suite template.
