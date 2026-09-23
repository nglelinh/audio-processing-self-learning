---
layout: post
title: "10-01 Curated reading list"
chapter: "10"
order: 1
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter10
lesson_type: required
draft: false
---

A short **curated** list beats a dump of links. Below are the canonical sources used across this course, split into must-read vs optional survey pointers. **No fabricated citations** — if you add a paper, verify the title/authors/venue first.

## 60-minute teaching plan

- 0–10 min: How to read SE papers for product work (figures → complexity → streaming).
- 10–35 min: Walk must-read list; assign each student one paper summary.
- 35–50 min: Optional successors / ultra-light pointers (named only).
- 50–60 min: Build your personal "five links" card for the capstone.

## Learning objectives

By the end of this lesson, you can:

- Collect the canonical papers/docs used across the course.
- Separate must-read vs optional survey pointers.
- Keep the list free of fabricated citations.
- Point to LiveKit/WebRTC, SI-SDR, DNSMOS, DNS Challenge materials correctly.

## Must-read (core path)

### DeepFilterNet family

1. Schröter et al., **DeepFilterNet** — ICASSP 2022; arXiv:[2110.05588](https://arxiv.org/abs/2110.05588). Low-complexity full-band deep filtering.  
2. Follow-on DeepFilterNet2 / DeepFilterNet3 materials via the [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) repository and associated publications linked there (read the repo README for the current paper list).  
3. Model archive used in product: `DeepFilterNet3_onnx.tar.gz` in that repo's `models/`.

### Classical / teaching bridges

4. **RNNoise** — Jean-Marc Valin; real-time RNN noise suppression (teaching bridge in Ch 04).  
5. **SpeexDSP** / WebRTC **APM** documentation — AEC/NS/AGC baseline behavior.  
6. WebRTC samples & MDN media capture docs — track constraints and insertion points.

### Evaluation

7. **SI-SDR** — scale-invariant SDR usage in BSS / SE evaluation literature (Le Roux et al. discussions on SDR variants).  
8. Microsoft **DNS Challenge** overview papers / challenge pages — protocol + baselines.  
9. **DNSMOS** papers matching the predictor version you run (challenge lineage).  
10. ITU-T **P.808** (overview) and ITU-R **BS.1534** (MUSHRA overview) for listening-test design.

### Product / runtime

11. [LiveKit](https://docs.livekit.io/) client docs — local tracks / processors for your SDK version.  
12. npm [`deepfilternet3-noise-filter`](https://www.npmjs.com/package/deepfilternet3-noise-filter) + [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression).  
13. **ONNX Runtime** performance docs; **tract** docs if on the Rust path.

## Optional survey pointers (named only)

Use as *direction finders*, not required reading:

- Successors: **DPDFNet**, **DeepFilterGAN**, **HDF-Net**  
- Ultra-light / streaming: **FastEnhancer**, **μNet**, **Fast-ULCNet**, **GTCRN**  

Verify each on arXiv or the venue site before citing in reports. Prefer primary papers over blog summaries.

## Reading method for engineers

For each paper, capture on one page:

1. Streaming? Causal? Lookahead?  
2. Sample rate / complexity (MAC, RTF, device).  
3. Metrics reported (SI-SDR, DNSMOS, listening?).  
4. What you would reuse in Mezon-like product.  

## Exercises

1. Produce five-link personal card (DF core, DNS eval, WebRTC/LiveKit, runtime, Mezon README).  
2. Write a 10-line summary of arXiv:2110.05588 focusing on deep filtering idea.  
3. Find the DNS Challenge year page that matches your DNSMOS tooling — note the year.  
4. Add one optional successor paper with verified ID to your notes.

## Further reading

- Course `COURSE_OUTLINE.md` citation policy.  
- `AGENTS.md` — well-known sources only.  
- Upstream DeepFilterNet README "papers" section (living list).
