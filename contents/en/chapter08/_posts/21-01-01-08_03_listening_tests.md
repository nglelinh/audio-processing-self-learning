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

Every audio team eventually learns a humbling lesson: you listen to your brand-new model on your own desk, convinced it sounds "way cleaner" than production—only to run a **blind randomized A/B test** where listeners can’t see which clip is which, and discover your new model actually lost 60–40! Confirmation bias in human hearing is astonishingly powerful; the moment you know which clip is "Model B," your brain hears what it *wants* to hear.

This lecture teaches how to run rigorous, lightweight **subjective listening tests** (blind A/B preference, **CCR**, **ACR / P.835**, and **MUSHRA**) and how to compute exact sample-size confidence intervals so you never mistake 10 noisy votes for a real perceptual win.

---

## Background Knowledge Map: Psychophysics and Statistical Rigor in Listening Tests

Four experimental principles separate trustworthy listening tests from wishful thinking:

1. **Double-Blind Randomization & Loudness Normalization:** Listeners must never see system labels, clip order must be randomized per trial, and all systems must be loudness-matched (e.g., $$-24	ext{ LUFS}$$)—because human ears reflexively rate a 1.5 dB louder clip as "better"!
2. **Choosing the Right Protocol:**
   - **Blind A/B (or ABX):** Fastest for comparing 2 candidate models (e.g., current prod vs. new candidate).
   - **P.835 (SIG/BAK/OVRL):** Separates speech distortion from background suppression on 1–5 scales.
   - **MUSHRA (0–100):** Gold standard for subtle differences among 3–6 systems, calibrated with a hidden reference (100) and a low-quality anchor (e.g., 3.5 kHz low-pass).
3. **Anchor Traps & Listener Screening:** Including hidden reference and degraded anchor clips immediately detects distracted raters clicking randomly.
4. **Binomial Confidence Intervals & Statistical Power:** With only $$N = 10$$ votes, a 7–3 split (70%) is still completely compatible with a 50/50 coin flip; you need enough independent clips and listeners to separate signal from sampling variance.

---

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

---

### Worked Numerical Example: How Many Votes Do You Need for a Confident Blind A/B Win?

Suppose you run a blind A/B preference test comparing New Model B against Prod Model A (excluding ties), and **70%** of ratings prefer Model B ($$\hat{p} = 0.70$$). Compute the 95% Wald confidence interval $$\hat{p} \pm 1.96\sqrt{rac{\hat{p}(1-\hat{p})}{N}}$$ for two test sizes:

| Test Size $$N$$ | Votes for B | Observed $$\hat{p}$$ | Standard Error $$\mathrm{SE}$$ | 95% Confidence Interval | Statistically Significant (excludes 0.50)? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$$N = 10$$** | 7 / 10 | $$0.70$$ | $$\sqrt{rac{0.21}{10}} = 0.145$$ | $$[0.416,\; 0.984]$$ | **NO** (contains 0.50—could be luck!) |
| **$$N = 40$$** | 28 / 40 | $$0.70$$ | $$\sqrt{rac{0.21}{40}} = 0.0725$$ | $$[0.558,\; 0.842]$$ | **YES** (cleanly above 0.50!) |
| **$$N = 100$$** | 70 / 100 | $$0.70$$ | $$\sqrt{rac{0.21}{100}} = 0.0458$$ | $$[0.610,\; 0.790]$$ | **YES** (tight estimate!) |

That simple calculation explains why "I asked 5 teammates to listen to 2 clips" is never enough—even a 70% win rate needs roughly **35–40 independent ratings** (e.g., 8 listeners × 5 diverse clips, or 10 listeners × 4 clips) to clear 95% confidence!

### Deep-Dive Explanation: Four Rules for Running Fast, Honest Listening Tests (Read Slowly)

1. **Loudness-normalize every clip before anyone presses play:** A 2 dB louder output wins blind A/B tests almost automatically—normalize all systems to the same active speech LUFS first.
2. **Stratify your test playlist across failure modes:** Include (a) steady fan/AC noise, (b) babble/café voices, (c) sudden keyboard clicks, (d) double-talk/echo, and (e) **clean quiet speech** to catch clean-speech degradation.
3. **Require headphones and keep sessions under 15 minutes:** Listener fatigue sets in fast; 15–20 short 6-second clips yield far sharper judgments than 60 clips in one sitting.
4. **Always inspect the clips where your new model *lost*:** Aggregate win rate tells you *whether* to ship; the 3 clips where your model lost tell you *what to fix next*.

**Quick check.** Why does a MUSHRA listening test include both a **hidden clean reference** and a **hidden low-quality anchor** alongside the candidate denoisers?

---

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

## Video tham khảo

- [Developing Machine Learning Based Speech Enhancement Models for Teams and Skype | Ross Cutler](https://www.youtube.com/watch?v=Gdvhv8SYcTg) — @Scale, English. **xem trước.** Watch the crowdsourced P.808 section: references, anchors, and screening. That is the listening discipline in the lesson, even when your grid is smaller than a full ITU lab.
