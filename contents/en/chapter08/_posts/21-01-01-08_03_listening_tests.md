---
layout: post
title: "08-03 Listening tests"
chapter: "08"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter08
lesson_type: required
draft: false
---

Objective metrics miss product-critical artifacts: underwater speech, cut consonants, pumping, residual keyboard spikes. **Listening tests** remain the tie-breaker for shipping noise suppression. This lesson shows how to run a *small, honest* AB or MUSHRA-like test with a engineering team — not a full ITU lab — and how to document results for stakeholders.

## 60-minute teaching plan

- 0–10 min: When dogfooding is enough vs when a structured test is required.
- 10–25 min: AB vs MUSHRA-like designs; loudness and order controls.
- 25–40 min: Rater instructions and sample curation.
- 40–50 min: Analysis — win rates, ties, disagreement.
- 50–60 min: Mini-lab: write a 1-page test protocol for a suppression-level change.

## Learning objectives

By the end of this lesson, you can:

- Design a small MUSHRA-like or AB test for a team.
- Control for loudness and order effects.
- Document results for product stakeholders.
- Know when informal dogfooding is enough.

## Choose a protocol

| Protocol | What raters do | Good for |
|----------|----------------|----------|
| Informal dogfood | Use NS in real meetings for a day | Catch UX / crash / CPU issues |
| **AB** | Prefer A or B (or tie) | Two versions / two levels |
| **ABC** | Pick best of three | Baseline vs NS vs NS' |
| MUSHRA-like | Rate multiple systems on a scale with anchors | More systems; needs more care |

ITU-T **P.808** / MUSHRA (ITU-R BS.1534) are formal references — your course team will usually run a **lightweight** variant inspired by them, not a certified lab.

## Loudness and order controls

1. **Loudness:** loudness-normalize clips (e.g. toward a common integrated loudness) so raters do not prefer the louder file.
2. **Order:** randomize A/B assignment per clip; never always put "new" on the right.
3. **Blind labels:** show "System 1 / System 2", not "DF3-80".
4. **Same headphones** when possible; note device if remote.
5. **Short clips:** 5–10 s of critical noise + speech beats 60 s of fatigue.

## Sample curation

Build a **grid**, not a random dump:

| Noise type | SNR-ish difficulty | Device |
|------------|--------------------|--------|
| Café babble | hard | laptop mic |
| Keyboard | medium | laptop |
| Fan / AC | easy | phone |
| Traffic | hard | phone |
| Silent room | control | laptop |

Include **clean** controls — NS should not wreck clean speech.

Typical small test: 8–15 clips × 5–10 raters (teammates). More is better; document N.

## Rater instructions (template)

```text
You will hear two versions of the same take (order random).
Choose which is better for a work meeting, or "tie".
Prefer: clear consonants, natural voice, low distraction from noise.
Penalize: muffled speech, robotic artifacts, cutting out words.
Ignore: tiny loudness differences.
```

Translate instructions to Vietnamese when raters are VI-speaking (same meaning).

## Analysis and reporting

For AB:

- Win rate of New vs Old; ties separately.
- Per-condition breakdown (keyboard vs café).
- Flip rate if you repeat 2 clips for attention checks.

Stakeholder table:

| Condition | New wins | Old wins | Ties |
|-----------|----------|----------|------|
| Keyboard | 7 | 2 | 1 |
| Café | 4 | 5 | 1 |
| **Overall** | … | … | … |

Attach **one** audio example (with permission) in the demo — Chapter 09-05.

## When dogfooding is enough

- Pure reliability change (CDN fallback) with no DSP change.
- Enabling NS behind a flag for internal users only.
- RTF optimization with bit-identical / golden waveform parity.

Require structured listening when:

- Changing suppression defaults.
- New model / WASM build.
- Reports of "voice sounds weird".

## Common pitfalls

1. Testing only on your own voice / headset.
2. Unblinded "of course the new one is better".
3. No clean-speech control clips.
4. Huge clip sets → exhausted raters → noise.

## Exercises

1. Write AB instructions in EN and VI for your team.
2. Curate a 9-clip grid (3 noises × 3 devices) with filenames.
3. Given win table Café loses but Keyboard wins — what do you ship?
4. Design an attention check (duplicate clip) policy.

## Further reading

- ITU-T P.808 (conversational speech quality crowdsourcing) — overview.
- ITU-R BS.1534 (MUSHRA) — overview for multi-system rating.
- DNS Challenge human evaluation notes in challenge summaries.
- Course 08-01/08-02 for objective complements.
