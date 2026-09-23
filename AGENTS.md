# AGENTS.md

## Project

Jekyll 4.3 bilingual (EN/VI) teaching course: **Real-Time Audio Noise Suppression: From DSP to DeepFilterNet**.

This course is aligned with Mezon noise-suppression product work (`mezonai/mezon-noise-suppression`, npm `deepfilternet3-noise-filter`). Teach **techniques** (DSP, classical NS, DeepFilterNet family, realtime/on-device, eval). Do **not** treat the npm wrapper as the syllabus, and do **not** modify the product repository from course tasks.

## Commands

```bash
bundle install
bundle exec jekyll serve    # http://127.0.0.1:4000/audio-processing-self-learning/
bundle exec jekyll build
```

Docker: `docker-compose up`

## Layout

Same as `course-self-learning-template` / `rust-self-learning`:

- `contents/{en,vi}/chapterXX/_posts/` — lessons
- `home/_posts/` — introduction, contents, makers
- `_config.yml` — titles, `baseurl: /audio-processing-self-learning`, author
- `COURSE_OUTLINE.md` — advisor-facing module map

## Front matter (match template / rust-self-learning)

```yaml
---
layout: post
title: "…"
chapter: "XX"
order: N
owner: "Nguyen Le Linh"
lang: en   # or vi
categories:
  - chapterXX
lesson_type: required
draft: false
---
```

## Citations

Only well-known sources: DeepFilterNet / DeepFilterNet2/3, DNS Challenge, WebRTC APM, SpeexDSP, RNNoise, SI-SDR, DNSMOS, ONNX Runtime / tract. Survey pointers only for named successors (DPDFNet, DeepFilterGAN, HDF-Net) and ultra-light models (FastEnhancer, μNet, Fast-ULCNet, GTCRN). Do not invent papers.

## Capstone

Optional Rust native (`df-core`) path is stretch. Local product path for the instructor: `/Users/nguyenlelinh/ncc/mezon-noise-suppression`.

## Chapter emphasis (00–10)

- **01 Fourier (deep)** and **02 audio pipeline** are first-class modules (5–7 lessons each), not a brief DSP aside.
- Capstone (**09**) aligns with Mezon NS; do not edit the product repo from course work.
- Prefer fleshing out 01 → 02 → 04 → 05–07 → 09.
