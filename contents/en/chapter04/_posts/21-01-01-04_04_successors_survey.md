---
layout: post
title: "04-04 Successors survey: DPDFNet, DeepFilterGAN, HDF-Net"
chapter: "04"
order: 4
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter04
lesson_type: required
draft: false
---

This lesson is a **reading map**, not an implementation marathon. Named successors extend DeepFilterNet-family ideas: **DPDFNet** (dual-path RNN on a DF-style backbone), **DeepFilterGAN** (predictive DF stage + GAN regeneration), and **HDF-Net** (hierarchical deep filtering). Optional nearby ideas include personalization and noise-fingerprint conditioning. Cite only these well-known named works—do not invent papers.

## Learning objectives

You will state one core idea each for DPDFNet, DeepFilterGAN, and HDF-Net; decide which readings are mandatory vs optional for the Mezon capstone; and explain how survey papers should influence product roadmaps without triggering premature rewrites.

## 60-minute teaching plan

- **0–10 min** — Why survey successors if we ship DF3.
- **10–25 min** — DPDFNet: dual-path temporal/frequency modeling + over-attenuation themes.
- **25–40 min** — DeepFilterGAN: two-stage predictive + generative refinement.
- **40–50 min** — HDF-Net pointer; optional personalization / DFingerNet-style conditioning.
- **50–60 min** — Capstone triage exercise; pitfalls.

## Core explanation

### How to use a survey in an engineering course

For each paper, capture exactly four fields:

1. **Problem diagnosed** (e.g. over-attenuation, slow temporal context, missing fine filter structure).
2. **Mechanism** (dual-path blocks, GAN regenerator, hierarchical DF).
3. **Deployability** (params, causal?, ONNX/TFLite mentioned?).
4. **Action for Mezon** (ignore / watch / prototype).

Anything else is journal-club detail.

### DPDFNet — dual-path RNN on DF2-style backbone

**Idea:** insert **dual-path** recurrent blocks (intra/inter-path style familiar from dual-path speech separation) into a DeepFilterNet2-like encoder to strengthen long-context modeling while keeping a real-time mindset. Reports in the paper also discuss **over-attenuation** losses and always-on fine-tuning themes—directly relevant to product complaints (“NS eats my voice”).

**Capstone takeaway:** if DF3 sounds dull on long turns, read DPDFNet’s diagnosis before enlarging the model blindly; consider loss terms that penalize over-suppression.

### DeepFilterGAN — predictive + generative refinement

**Idea:** keep a DeepFilterNet2-style **predictive** enhancer, then add a **lightweight GAN regenerator** to restore speech components that aggressive prediction removed. This is a two-stage quality strategy: stable predictor + generative detail.

**Capstone takeaway:** two ONNX graphs (or a fused graph) may beat a single larger predictor for perceptual quality—but GAN stages complicate streaming determinism and RTF. Prototype only if listening tests show irreversible over-suppression.

### HDF-Net — hierarchical deep filtering

**Idea:** decouple / organize **temporal vs frequency** deep filtering hierarchically rather than a monolithic filter head—still in the “deep filter DNA,” with a small parameter footprint claimed in the paper.

**Capstone takeaway:** architectural alternative if you re-implement deep filters; not required to ship DF3 weights.

### Optional nearby readings (name-level)

- **pDeepFilterNet2** — speaker embeddings for personalized SE.
- **DFingerNet** — noise-fingerprint conditioning for adaptive hearing-aid-style SE.
- Treat both as **optional**; personalization is out of scope unless the capstone explicitly targets it.

### Classical + neural hybrids (pointer back to Ch. 03)

Successors are mostly mono neural. Remember GSC+DeepFilterNet2 and IVA+GTCRN hybrids when spatial hardware exists—the “successor” that matters might be a **front-end**, not a new GAN.

## Capstone triage table (fill in class)

| Work | Idea in 6 words | Ship now? | Watch? |
|------|-----------------|-----------|--------|
| DPDFNet | Dual-path + less over-attenuation | | |
| DeepFilterGAN | GAN restores over-suppressed speech | | |
| HDF-Net | Hierarchical deep filters | | |
| DF3 (baseline) | Product default | Yes | |

## Pitfalls

- Rewriting production models after reading one INTERSPEECH abstract.
- Citing papers you did not open (fabricated takeaways).
- Assuming GAN quality comes for free at AudioWorklet RTF.
- Ignoring ONNX op coverage for dual-path / custom filters.

## Exercises

1. **One-pagers.** For each of the three named papers, write the four-field card (problem, mechanism, deployability, Mezon action).
2. **Over-attenuation.** Script a listening test that detects over-suppression (read aloud soft consonants into NS); propose a metric or checklist item.
3. **Roadmap memo.** 200 words to your tech lead: stay on DF3 vs schedule a DPDFNet spike—defend with RTF and risk.
4. **Citation hygiene.** Provide full bibliographic lines (title, authors, venue/arXiv id) for the three named works from primary sources only.

## Further reading

- DPDFNet paper (arXiv / dual-path DeepFilterNet2 successor).
- DeepFilterGAN (INTERSPEECH / arXiv — DF predictive + GAN regenerator).
- HDF-Net (INTERSPEECH / arXiv — hierarchical deep filtering).
- Optional: pDeepFilterNet2, DFingerNet (personalization / fingerprints).
