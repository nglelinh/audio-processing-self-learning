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

SI-SDR can stay high while the voice turns metallic, and DNSMOS can miss a domain your users actually occupy. A listening test is the column that catches both, if you control loudness, order, and the clip grid. You do not need an ITU-certified lab to learn the discipline. You do need a written protocol, blinded labels, and a table that can lose. This lesson is a small AB (or MUSHRA-like) design for an engineering team deciding whether to change `setSuppressionLevel` on `DeepFilterNoiseFilterProcessor`.

![Evaluation map: intrusive SI-SDR, non-intrusive DNSMOS, and listening tests]({{ site.imgurl }}/generated/eval-metric-map.png)

*Figure. Listening tests are the slow, high-value column. They arbitrate when SI-SDR and DNSMOS disagree, which is a normal outcome on real microphones.*

## What you should be able to do

You should be able to pick AB versus a light MUSHRA-like scale, loudness-normalize the stimuli, randomize order, write rater instructions in English and Vietnamese, and report wins, losses, and ties per condition. You should also know when a day of dogfooding is enough and when it is not.

## Pick a protocol that matches the decision

Informal dogfooding — using noise suppression in a real meeting — catches crashes, CPU spikes, and “I hate this” moments. It does not estimate a preference rate. AB asks each rater to prefer A, prefer B, or tie, on one pair. That is the right tool for level 80 versus level 60, or for the processor enabled versus bypassed with `setEnabled(false)`. An ABC task adds a raw microphone anchor. A MUSHRA-like scale, inspired by ITU-R BS.1534, rates several systems against an anchor and needs more rater training. ITU-T P.808 describes crowdsourced conversational-speech tests; read it as a standard to respect, then run a lightweight variant and say so in the report. Do not label a five-person hallway test as P.808.

## Controls that keep the result about noise suppression

Loudness is the classic confound. If the suppressed file is quieter, raters who were told to judge “comfort” will pick it even when fricatives died. Normalize integrated loudness toward a common target and say which tool you used. Randomize which system is A on each clip. Never park the new level on the right. Show “System 1” and “System 2,” not “DF3-80.” Use the same headphones when you can, and record the device when you cannot. Prefer 5–10 seconds that contain the hard noise and a consonant, not a full minute that exhausts the rater. Keep the playback path identical: same browser, same sample rate, no extra limiter on one side.

Include a clean-speech control. A suppressor that only helps on café babble and wounds a quiet sentence is not a default you can ship. Include at least one impulsive noise (keyboard) and one babble noise. A single favorite café clip is how suites overfit.

## A grid, not a dump

| Noise | Difficulty | Device | Why it is here |
|-------|------------|--------|----------------|
| Café babble | Hard | Laptop mic | Overlapping speech-like noise |
| Keyboard | Medium | Laptop | Impulsive; easy to over-cut |
| Fan or AC | Easier | Phone | Stationary; bandwidth differs |
| Traffic | Hard | Phone | Low-frequency rumble |
| Quiet room | Control | Laptop | Over-suppression detector |

Eight to fifteen clips and five to ten raters is a small team test. Write $$N$$ in the table. Repeat two clips with the labels flipped as an attention check. If a rater contradicts themselves on both, set their sheet aside and say so. Translate the instruction sheet into Vietnamese when the raters work in Vietnamese. The decision criterion must stay the same language-to-language: clear consonants, a natural voice, low distraction, and a penalty for muffling, robotic timbre, or chopped words. Tell raters to ignore leftover loudness differences.

## What you report

For AB, report wins for the candidate, wins for the baseline, and ties, overall and per condition. A keyboard win plus a café loss is a split decision: you might ship the lower suppression level as default and document the residual café noise, or you might refuse to change the default. You do not average those rows into a single triumphant percentage. Attach one example you have rights to play on demo day (lesson 09-05), with the condition named.

Stakeholder table shape:

| Condition | New wins | Old wins | Ties | N |
|-----------|----------|----------|------|---|
| Keyboard | 7 | 2 | 1 | 10 |
| Café | 4 | 5 | 1 | 10 |
| Quiet | 3 | 2 | 5 | 10 |

The quiet row full of ties is a success if the candidate was not supposed to touch clean speech. A quiet row where “old” wins means the new level is eating the voice.

## When dogfooding is the whole test

Use dogfooding alone for a change that must be bit-identical in the waveform: a CDN fallback, a logging line, a cache header. Use it for an internal flag that does not change the default listeners hear. Require the structured test when you change the default suppression level, ship a new WASM or model archive, or respond to “the voice sounds weird.” RTF work can skip listening only when the output samples match a golden wav within a tolerance you wrote down. A faster build that is not sample-close is a new system.

## Mini-lab

Write `ab_protocol.md` for a suppression-level change (for example 80 versus 60 on `setSuppressionLevel`). Then run the checker. The lab passes when the protocol names loudness, blinding, a clean control, and both languages.

```python
from pathlib import Path
text = Path("ab_protocol.md").read_text().lower()
need = ["loudness", "blind", "tie", "quiet", "keyboard", "cafe", "vietnamese", "setsuppressionlevel"]
missing = [n for n in need if n not in text]
print("missing", missing or "none")
print("chars", len(text))
```

Expected output:

```text
missing none
chars <some integer above 400>
```

The character count will be your own. The checker’s `missing none` line is the pass signal. Failure modes: unblinded filenames in the rater UI; no tie option, which forces a preference when the clips match; no quiet control; instructions only in English for a Vietnamese-speaking panel; judging a level change on one talker’s voice.

A minimal protocol body that satisfies the checker will state the task in both languages, name `setSuppressionLevel`, and list the three conditions. Expand it with the rater paragraph from this lesson rather than keyword-stuffing.

## Exercises

1. Write the rater paragraph in English and a natural Vietnamese equivalent. Keep the same penalties.
2. List nine filenames for a 3×3 grid (babble, keyboard, quiet × laptop, phone, headset).
3. Keyboard: new wins 7–2–1. Café: new wins 4–5–1. Quiet: 3–2–5. What do you ship as the default level, and what do you retest?
4. Define an attention-check rule for one duplicated clip.
5. Name two product changes that do not need this protocol, and one that does.

### Answer hints

1. Penalize muffling, robotic timbre, and chopped words. Ignore small loudness gaps. Vietnamese should sound like an instruction to a colleague, not a word-for-word gloss.
2. Encode condition and device in the stem, for example `babble__laptop__01.wav`.
3. Do not ship on the keyboard row alone. The café loss and the quiet ties mean you either keep the old default or retest a middle level. Say which.
4. Flip A/B on the duplicate. A rater who flips their own preference fails the check.
5. CDN fallback with unchanged samples can be dogfood. A new default for `setSuppressionLevel` cannot.
