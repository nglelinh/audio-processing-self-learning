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

DPDFNet, DeepFilterGAN, and HDF-Net are **survey pointers only**. This lesson gives them no paper title, year, venue, or URL. If you have not opened the PDF, you do not have a bibliographic line. The hour is how to set a successor next to the ERB-plus-deep-filter skeleton, then decide whether a DF3 deployment should change.

![ERB-plus-deep-filter skeleton that successor names still have to beat on RTF and listening]({{ site.imgurl }}/generated/deepfilternet-erb.png)

*Figure. DPDFNet, DeepFilterGAN, and HDF-Net are survey pointers only: names on a reading list, not checkpoints you can load from this page. Any of them still has to preserve a causal STFT hop, a bounded state, and an RTF under 1 on the target CPU. This lesson states no paper title, year, or URL for those three names.*

## Learning objectives

You will attach one sentence each to DPDFNet, DeepFilterGAN, and HDF-Net; refuse a title or year you did not copy from a PDF; and decide ship, watch, or ignore from RTF, ONNX coverage, and a listening failure you can reproduce.

## 60-minute teaching plan

- **0–10 min** — Why a name is not a migration plan.
- **10–25 min** — The four-field card, filled only with what you can point at.
- **25–40 min** — What “dual-path,” “GAN stage,” and “hierarchical filter” would cost in an AudioWorklet.
- **40–50 min** — Over-attenuation as a product bug, independent of any one paper.
- **50–60 min** — Mini-lab and citation hygiene.

## Core explanation

### What a survey lesson is allowed to claim

Lessons 04-02 and 04-03 quoted tables because those tables are in arXiv:2110.05588, arXiv:2205.05474, and arXiv:2305.08227. This lesson does not have that license. The course reading map uses three names:

- **DPDFNet** — a successor people look up when long-context modeling and over-attenuation, on a DeepFilterNet2-style backbone, are the complaint.
- **DeepFilterGAN** — a successor people look up when a predictive DeepFilterNet-style stage is followed by a generative stage that tries to put back speech the predictor removed.
- **HDF-Net** — a successor people look up when deep filtering is split hierarchically across time and frequency instead of one filter head.

Those sentences are the map, not abstracts. They do not authorize a parameter count, a PESQ delta, a figure, or a link. Optional nearby names, also without citations here, are pDeepFilterNet2 (speaker conditioning) and DFingerNet (noise-fingerprint conditioning). Personalization is out of scope unless the capstone says otherwise.

### The four-field card

For each PDF you actually open, write four fields and nothing else:

1. **Problem** the authors measured (over-attenuation, a missing harmonic, a latency number).
2. **Mechanism** with the block names printed in that PDF, not synonyms you prefer.
3. **Deployability:** parameter count if the PDF prints one, whether the graph is causal, whether ONNX or a real-time factor appears.
4. **Action:** ignore, watch, or prototype. A prototype needs a hop size, a device, and a listening clip.

If field 3 is empty because the PDF never mentions streaming, the action is not “ship.” A leaderboard model with a bidirectional layer will not run inside `process()`.

### What each idea would cost, without pretending you read the PDF

Keep this section in the conditional. It is an engineering translation of the **names**, so you can budget a spike. It is not a summary of results.

A **dual-path** block, the pattern the DPDFNet name points at, runs one sequence in time and one in frequency. On a 10 ms hop the time path is either a fixed GRU state or a wait for future hops. Four future hops are another 40 ms on top of DeepFilterNet2’s published 40 ms, so 80 ms of delay. That sum is not an RTF. Two GRUs can also double p95. Over-attenuation itself needs no paper: soft fricatives disappear. A loss that floors the gain is a hypothesis, not a quoted result.

A **GAN regenerator**, the pattern the DeepFilterGAN name points at, is a second network on top of a predictive stage. Two ONNX sessions, or one fused graph, add MACs and a stage that is awkward to keep deterministic in `process()`. Suppression on the npm surface is already an integer 0–100 via `setSuppressionLevel`. Turn it down before you add a GAN.

A **hierarchical deep filter**, the pattern the HDF-Net name points at, still computes

$$
\hat{S}(t,f)=\sum_{i} W_i(t,f)\,X(t-i+\ell,f),
$$

with more than one head. Five taps on 96 bins are already 480 complex multiplies per frame (04-02). A frequency-axis head can see neighboring bins; whether a given PDF’s head is causal is a question for that figure, not for this page.

### Product triage against the DF3 row you can actually cite

The only DeepFilterNet3 metric row you may quote is Voicebank+Demand in arXiv:2305.08227: PESQ 3.17, CSIG 4.34, CBAK 3.61, COVL 3.77, STOI 0.944, next to DF2 at PESQ 3.08. RTFs you may quote are 0.04 (DF2, notebook i5) and 0.19 (the 2023 tract loop on an i5-8250U). A successor earns a spike only if your clips show a failure those checkpoints miss, and a causal graph can live in a 10 ms hop (a single 2.67 ms quantum is the wrong budget).

| Name | Idea you may repeat | Ship from this lesson? | Why |
|------|---------------------|------------------------|-----|
| DPDFNet | Dual-path context; over-attenuation is the theme to look up | No | No title, year, or URL here |
| DeepFilterGAN | Predictive stage plus a generative stage | No | Second network, RTF and determinism unknown until you read |
| HDF-Net | Hierarchical deep filter | No | Same |
| DeepFilterNet3 baseline | 32 ERB + 5-tap filter, README-associated 2023 citation | Yes, as the course baseline | Numbers live in 04-03 |

Spatial front-ends from Chapter 03 (GSC into a mono enhancer, IVA into a mono enhancer) are a different kind of “successor”: they change the microphone count. They are still survey-level hybrids, not a reason to drop DF3.

## Pitfalls

- Rewriting the ONNX graph after an abstract.
- Typing a title, year, or arXiv id from memory for DPDFNet, DeepFilterGAN, or HDF-Net.
- Assuming a GAN stage fits the same p95 as the predictor.
- Importing a custom filter op that tract or ONNX Runtime WASM does not implement, then discovering it on the audio thread.

## Mini-lab

**Goal.** Build the four-field card with the fields you are **not** allowed to invent left blank, and check that a string scan of your notes does not contain a made-up citation.

```bash
python3 - << 'PY'
names = ["DPDFNet", "DeepFilterGAN", "HDF-Net"]
# Fill only from a PDF you opened. Leave unknown fields as None.
cards = {
    name: {"problem": None, "mechanism": None, "params": None,
           "causal": None, "url": None, "year": None, "title": None}
    for name in names
}
for name, card in cards.items():
    missing = [k for k, v in card.items() if v is None]
    print(f"{name}: missing={missing}")
print("survey_pointers_only=True")
PY
```

**Expected**. Each name prints `missing=['problem', 'mechanism', 'params', 'causal', 'url', 'year', 'title']` until you replace `None` from a PDF. The last line is `survey_pointers_only=True`.

**Failure modes**. Pasting a title or year from a search snippet you did not open. Filling `params` with a number that is not in the PDF. Treating a blank `causal` field as “causal enough.” Linking a URL this lesson does not provide.

## Exercises

1. **Cards.** After you open each PDF yourself, fill the four fields. If you cannot open it, leave the card blank and say so.
2. **Over-attenuation, no paper required.** Record ten seconds with soft fricatives (“see”, “fish”) at a comfortable level and at a low level, through a DF3 path at suppression 30 and at suppression 90. Write the listening difference in two sentences.
3. **Delay budget.** A dual-path chunk waits 4 hops of 10 ms, and DeepFilterNet2’s published delay is already 40 ms. What is the sum, and is that sum an RTF?
4. **Memo.** In 150 words, tell a tech lead to stay on the DF3 baseline or to schedule a reading spike. You may cite only arXiv:2110.05588, arXiv:2205.05474, and arXiv:2305.08227.

### Answer hints

1. A blank card scores higher than a fabricated title. Mechanism text must use the PDF’s nouns.
2. You are listening for deleted consonants and a “dry” or pumping tail, not for a MOS number. Suppression is 0–100 via `setSuppressionLevel`, not a dB from the paper.
3. $$40+4\times 10=80$$ ms algorithmic delay if the chunk is extra look-ahead. RTF is wall time over audio time and can be 0.2 or 1.4 independently of those 80 ms.
4. The defendable baseline is the 2023 citation’s DF3 row and the published 40 ms / RTF figures. A spike is a reading assignment plus one causal ONNX smoke test, not a rewrite.

## Further reading

- Lessons 04-02 and 04-03, which cite [arXiv:2110.05588](https://arxiv.org/abs/2110.05588), [arXiv:2205.05474](https://arxiv.org/abs/2205.05474), and [arXiv:2305.08227](https://arxiv.org/abs/2305.08227).
- The PDFs you obtain yourself for DPDFNet, DeepFilterGAN, and HDF-Net. This page intentionally has no link for them.
- Chapter 05 for the RTF and AudioWorklet constraints any successor still has to meet.
