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

Demo day rewards **clarity**: a working path, numbers you can defend, and known limits. Use this checklist the day before and a 5-minute script on stage.

## 60-minute teaching plan

- 0–15 min: Run the technical checklist in pairs.
- 15–30 min: Build metrics + listening slide.
- 30–45 min: Rehearse 5-minute demo script.
- 45–55 min: Failure injection (CDN off / NS toggle).
- 55–60 min: Submit artifact inventory.

## Learning objectives

By the end of this lesson, you can:

- Run a final checklist covering correctness, latency, and UX flags.
- Prepare a 5-minute demo script.
- List known limitations honestly.
- Show one listening example with context.

## Technical checklist

### Audio path

- [ ] Mic permission + correct device  
- [ ] NS enable/disable toggles without restarting the whole app (or document if it must)  
- [ ] Browser NS interaction documented (`noiseSuppression` on/off)  
- [ ] Leave/dispose without zombie AudioContexts  

### Model load

- [ ] Cold start: assets download OR clear error  
- [ ] Offline after cache: documented behavior  
- [ ] Fallback: call still works if CDN fails  

### Metrics

- [ ] Table for SI-SDR and/or DNSMOS  
- [ ] Listening AB summary with N  
- [ ] RTF or systems timing on named device  
- [ ] Package/commit/model versions pinned  

### Demo hygiene

- [ ] Backup recording if live mic fails  
- [ ] Headphones available  
- [ ] One café + one keyboard + one clean clip  

## 5-minute demo script

| Time | Content |
|------|---------|
| 0:00–0:40 | Problem: uplink noise in meetings; on-device DF3 |
| 0:40–1:30 | Architecture one-slide (Ch 09-01 sketch) |
| 1:30–2:30 | Live or recorded AB (raw vs NS) |
| 2:30–3:30 | Metrics table — what improved / what did not |
| 3:30–4:20 | Your technique contribution (hypothesis result) |
| 4:20–5:00 | Limits + next steps |

## Limitations slide (required)

Examples of honest limits:

- Domain: only tested on English/Vietnamese laptop mics  
- SIMD required for ≥1.2.0 path  
- No formal ITU listening lab  
- Rust backend still stub (if applicable)  

## Common pitfalls

1. Demo depends on a single café Wi-Fi CDN path with no fallback story.  
2. Metrics without versions.  
3. Overclaiming MOS from SI-SDR.  

## Exercises

1. Time a rehearsal; cut content until ≤5:00.  
2. Run failure injection: block CDN; film the fallback.  
3. Peer-review each other's limitations slide for honesty.  
4. Final artifact zip/list per 09-04.

## Further reading

- Chapter 07 (integration) and 08 (eval)  
- LiveKit / WebRTC docs for track processing  
- Package README troubleshooting mindset (assets, browsers)
