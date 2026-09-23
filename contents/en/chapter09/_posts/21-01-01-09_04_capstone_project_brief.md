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

Deliver a **written design**, a **measured demo** on a small clip set, and evidence you understand techniques behind Mezon NS — not wrapper trivia. This brief defines milestones, artifacts, and grading emphasis.

## 60-minute teaching plan

- 0–15 min: Read brief + success criteria aloud.
- 15–30 min: Choose track (product harness / UX policy / rust stretch).
- 30–45 min: Milestone calendar (baseline → change → eval → report).
- 45–55 min: Artifact checklist.
- 55–60 min: Q/A on scope cuts.

## Learning objectives

By the end of this lesson, you can:

- Deliver a written design + measured demo on a small clip set.
- Include RTF (or honest systems notes) on at least one target environment.
- Submit a short reading log linking techniques to Mezon code/docs.
- Plan milestones without touching the shared product repo.

## Tracks (pick one primary)

**A. Product eval & policy (recommended)**  
Harness + listening + default level or fallback policy.

**B. Integration engineering**  
CDN readiness UX, telemetry, constraint checklist with measurements.

**C. Rust stretch**  
`df-core` milestone toward real backend + CLI goldens (partial credit for honest stub+tests).

## Milestones

| Week-ish | Output |
|----------|--------|
| M0 | Architecture sketch (09-01) + hypothesis (09-02) |
| M1 | Baseline metrics on frozen clip set |
| M2 | Implement change *outside* product tree (or personal fork) |
| M3 | Full Chapter 08-04 report table |
| M4 | Demo script + checklist (09-05) |

## Required artifacts

1. **Design note** (2–4 pages): problem, approach, risks  
2. **Metrics tables**: synthetic and/or DNSMOS; listening summary  
3. **Systems note**: RTF or CPU/init timing on one device  
4. **Reading log**: ≥5 bullets linking Ch 02–08 ideas to README/API  
5. **Patch or config diff** *or* harness repo link — not "I clicked npm bump" alone  
6. **Limitations** section (honest)

## Grading emphasis

| Weight (guide) | Criterion |
|----------------|-----------|
| High | Technique understanding + honest eval |
| High | Reproducible measurements |
| Medium | Working demo path |
| Low | Polish of slides |
| Zero | Unapproved edits to shared product repo |

## Explicit non-goals

- Training a new SOTA SE model from scratch  
- Guaranteed bit-exact Rust parity in one term  
- Cloud processing of customer audio without a privacy design  

## Exercises

1. Choose track A/B/C and write M0 hypothesis.  
2. Freeze a 10-clip set list today (filenames only).  
3. Draft your reading log with 5 empty links to fill while coding.  
4. Identify the single risk most likely to blow the schedule.

## Further reading

- `COURSE_OUTLINE.md` in this repo  
- mezon-noise-suppression README  
- Chapter 08-04 reporting template
