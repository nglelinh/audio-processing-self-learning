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

After the capstone, pick a **path** instead of randomly bookmarking papers. Three productive directions: classical DSP depth, neural SE research, or productization (WebRTC/LiveKit/on-device). This lesson also suggests a 30-day practice schedule and portfolio artifacts.

## 60-minute teaching plan

- 0–10 min: Reflect on which chapters felt strongest.  
- 10–30 min: Path A/B/C deep-dive options.  
- 30–45 min: Adjacent topics (AEC, multi-mic, personalized SE).  
- 45–55 min: Draft a 30-day plan.  
- 55–60 min: Portfolio checklist.

## Learning objectives

By the end of this lesson, you can:

- Pick a path: classical depth, neural SE research, or productization.  
- Suggest adjacent topics worth a mini-project.  
- Plan a 30-day practice schedule.  
- Turn capstone artifacts into portfolio pieces.

## Path A — Classical DSP depth

- Re-derive STFT perfect reconstruction; implement OLA carefully.  
- SpeexDSP / WebRTC APM reading; measure AEC on your hardware.  
- Beamforming / GSC intuition on a stereo recording.

**Exit ticket:** a blog-quality note: "When classical NS beats a small neural model."

## Path B — Neural SE research

- Reading group: one paper/week from the curated optional list.  
- Reproduce a baseline RTF on ONNX Runtime CPU.  
- Compare DF3 vs one ultra-light model on *your* clip set.

**Exit ticket:** public eval table + caveats (no leaderboard cosplay).

## Path C — Productization

- LiveKit production patterns; failure telemetry.  
- CDN/perf budgets for SEA mobile networks.  
- Rust `df-core` milestones or mobile embedding study.

**Exit ticket:** design doc + measured init/RTF on two devices.

## Adjacent topics

| Topic | Why |
|-------|-----|
| AEC deep dive | Echo dominates meeting quality |
| Multi-mic / spatial | Laptops increasingly multi-mic |
| Personalized SE | Target speaker in babble |
| Codec interaction | Opus × NS artifacts |
| Accessibility captions | WER after NS |

## 30-day practice schedule (template)

| Days | Focus |
|------|-------|
| 1–3 | Re-read Ch 02 + implement SI-SDR notebook |
| 4–7 | Freeze personal 20-clip eval set |
| 8–14 | Path project MVP |
| 15–21 | Metrics + listening with one peer |
| 22–26 | Write-up + polish demo |
| 27–30 | Open-source docs/eval contribution *or* ADR at work |

## Open-source contribution ideas

- Improve eval harness docs (your own repo).  
- Reproduce RTF numbers; file careful issues upstream with versions.  
- Translation / examples for LiveKit processor usage (no drive-by refactors).

## Portfolio artifacts from the capstone

1. Architecture sketch diagram  
2. Metrics tables (CSV + markdown)  
3. AB listening protocol (EN/VI)  
4. Short demo video (≤3 min)  
5. Reading log  

## Exercises

1. Choose Path A/B/C; write a 30-day calendar in your notes.  
2. Name one adjacent topic and a weekend experiment.  
3. Identify one upstream doc gap you could fix.  
4. Draft portfolio README section linking artifacts.

## Further reading

- DNS Challenge future editions / related workshops (INTERSpeech, ICASSP SE sessions).  
- LiveKit & WebRTC community docs.  
- DeepFilterNet GitHub discussions/issues for real deployment pain.
