---
layout: post
title: introduction
order: 3
chapter: home
owner: Nguyen Le Linh
---

# Welcome — Real-Time Audio Noise Suppression

This bilingual course takes you from first-principles DSP to shipping neural noise suppression in real-time call stacks. The intended audience is Vietnamese software engineers who already write code and want a rigorous, product-aware path into speech enhancement.

## What you will learn

- Frame-based audio processing, STFT/ISTFT, and latency budgets.
- Classical NS ideas still used as front-ends or fallbacks.
- DeepFilterNet-style deep filtering and how it differs from magnitude masks.
- Real-time and on-device constraints (RTF, AudioWorklet, ORT/WASM).
- Integration patterns with WebRTC and LiveKit.
- Honest evaluation (SI-SDR, DNSMOS, listening).

## Capstone context

Work is aligned with **Mezon** noise suppression: GitHub `mezonai/mezon-noise-suppression`, npm `deepfilternet3-noise-filter`. You will learn the techniques behind the product — not only how to call the package.

## Prerequisites

- Comfortable with TypeScript/JavaScript or similar; willingness to read short Python/Rust snippets.
- No prior DSP course required.
- Headphones recommended for listening comparisons.

## How to navigate

1. Start at Chapter 00 for framing and the Mezon map.
2. Follow 01 → 03 for foundations and models.
3. Use 04 → 06 when you care about shipping.
4. Chapter 07 before claiming quality wins; Chapter 08 for the capstone; Chapter 09 for reading paths.

## Feedback

Open issues on [GitHub](https://github.com/nglelinh/audio-noise-suppression-self-learning) or contact Nguyen Le Linh (`nglelinh@gmail.com`).
