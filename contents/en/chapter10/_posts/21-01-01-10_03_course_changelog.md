---
layout: post
title: "10-03 Maintaining this course"
chapter: "10"
order: 3
owner: "Nguyen Le Linh"
lang: en
categories:
  - chapter10
lesson_type: required
draft: false
---

This course is a full set of English and Vietnamese articles across Chapters 00–10. APIs still move. The npm package, the CDN `v2/` layout, DeepFilterNet weights, and LiveKit’s TrackProcessor hook will drift, and a lesson that quotes them will drift with them. Maintainers keep the pair of languages in one change, regenerate figures instead of editing PNGs by hand, and treat the shared product repository as upstream reading, not as the homework tree.

![Fourier intuition figure used as the maintainer example]({{ site.imgurl }}/generated/fourier-intuition.png)

*Figure. A sum of tones in time becomes lines in frequency. Maintainers regenerate this PNG, and every other course figure, with `python3 scripts/generate_course_figures.py`. Output lands in `img/generated/`. Lessons embed it as `{{ site.imgurl }}/generated/fourier-intuition.png`.*

Technical courses rot fast. Within eighteen months, an `onnxruntime-web` import path changes, a browser tightens its `AudioWorklet` security policy, a PyTorch ONNX opset deprecates an old flag, or a new open-source denoiser beats the old baseline by 2 dB at half the compute. What separates a living engineering course from an abandoned blog post is **disciplined maintenance**: pinned versions, automated smoke tests, and a transparent changelog!

This closing note documents how to maintain, audit, and evolve `audio-processing-self-learning` cleanly over time—treating course materials with the exact same engineering rigor as production software.

---

## Background Knowledge Map: Four Pillars of Living Technical Course Maintenance

Keeping a systems-and-ML course accurate across years relies on four software-engineering habits:

1. **Pinned Toolchains & Reproducible Environments:** Recording exact tested versions of Python, PyTorch, `onnxruntime-web`, Rust (`rustc`), and browser engines prevents silent drift when upstream APIs change.
2. **Automated Verification Over Manual Hopes:** Code snippets, STFT/SI-SDR unit tests, and MathJax/Markdown link checks should run automatically in CI on every pull request so broken examples never silently reach learners.
3. **Backward-Compatible Changelog Discipline:** When swapping a benchmark model or updating an ONNX opset, log *what* changed, *why* (measured metric/latency delta), and *which* lesson exercises are affected.
4. **Separating Timeless Fundamentals From Fast-Moving Tooling:** Fourier analysis, causal latency math, ring buffers, and SI-SDR projection geometry stay valid for decades; isolate volatile npm/WASM version glue in dedicated integration chapters so updates stay surgical.

---

## What you should be able to do

You should be able to patch a lesson when `deepfilternet3-noise-filter` or the CDN layout changes, update the Vietnamese twin in the same pull request, add a figure without breaking `baseurl`, and file a maintenance note that lists both language files. You should also build the site locally and name the failure if `bundle exec jekyll build` warns.

## What to watch

| Upstream | What breaks | What you edit |
|----------|-------------|---------------|
| npm `deepfilternet3-noise-filter` above 1.3.0 | Public names or the automatic `v2/` prefix | Chapters 07 and 09, both languages |
| CDN layout leaving `v2/` | URLs `{cdnUrl}/v2/pkg/df_bg.wasm` and `{cdnUrl}/v2/models/DeepFilterNet3_onnx.tar.gz` | 07-03 and 09-01 |
| LiveKit `setProcessor` | The publish path in 09-01 | Re-read [docs.livekit.io](https://docs.livekit.io/) and quote the version |
| A new ONNX archive name | Asset sentences in 09 and 10 | The filename only, after you see it |
| DNSMOS checkpoint | Chapter 08 tables | Pin the new name; do not compare old scores as one series |

Public names to preserve until the README itself changes: `DeepFilterNet3Core`, `DeepFilterNoiseFilterProcessor`, `setProcessor`, `setSuppressionLevel(0–100)`, `setEnabled`, `assetConfig.cdnUrl`. Do not document private classes in order to sound precise.

## Changelog discipline

When you change an English lesson, update the Vietnamese twin in the same pull request. Same `chapter`, same `order`, same filename stem, `lang: en` on one side and `lang: vi` on the other. Code blocks, URLs, and the printed lab floats (13.80 and −10.67, the mixer list `[1.237, -0.237, -0.763, 0.263]`) stay identical. Prose is natural Vietnamese. Keep the English terms SI-SDR, DNSMOS, RTF, and TrackProcessor.

When you add a figure, put the PNG in `img/generated/` and reference it with `{{ site.imgurl }}`. Do not paste a one-off screenshot under a new folder. The generator is:

```bash
python3 scripts/generate_course_figures.py
```

That command rewrites the PNGs in `img/generated/`, including `fourier-intuition.png`, `eval-metric-map.png`, `livekit-trackprocessor.png`, `deepfilternet-erb.png`, `onnx-wasm-path.png`, and `rtf-audioworklet.png`. Commit the regenerated PNG with the lesson that embeds it. If you only change a caption, you do not need to regenerate.

A dated line belongs in the PR body, not only in chat:

```text
2026-09-23 — Chapters 08–10 EN and VI: figures, mini-labs, answer hints.
             VI twins updated in the same change. No product-repo edits.
```

## Site build

`_config.yml` sets `baseurl: /audio-processing-self-learning` and `imgurl: /audio-processing-self-learning/img`. Local preview:

```bash
bundle install
bundle exec jekyll serve
# http://127.0.0.1:4000/audio-processing-self-learning/
bundle exec jekyll build
```

The published site is `https://nglelinh.github.io/audio-processing-self-learning/`. A figure that uses a relative path without `site.imgurl` will work on one of those hosts and 404 on the other. After a build, open one Chapter 08 page and one Chapter 10 page and confirm the image request URL contains `/audio-processing-self-learning/img/generated/`.

## Advisor loop and the product boundary

Record syllabus requests in `COURSE_OUTLINE.md`. Citation rules live in `AGENTS.md`: DeepFilterNet and DeepFilterNet2/3, the DNS Challenge, WebRTC APM, SpeexDSP, RNNoise, SI-SDR, DNSMOS, ONNX Runtime, and tract. Survey names stay names. Course tasks read [mezonai/mezon-noise-suppression](https://github.com/mezonai/mezon-noise-suppression). They do not require `/Users/nguyenlelinh/ncc/mezon-noise-suppression`, and they do not take patches there. Students experiment in a personal fork or in `capstone/`.

## Maintenance issue template

```markdown
Title: [course] Update Ch09 CDN paths for package x.y.z
- Upstream version:
- Broken lesson paths:
- EN files:
- VI files:
- Figure touched (img/generated name) or none:
- jekyll build: pass/fail
- Verified image URL contains site imgurl: yes/no
```

File the issue only when both language files are listed. A fix that lands in English alone is incomplete.

## Mini-lab

From the repository root, confirm the generator exists and that every English lesson in Chapters 08–10 still embeds a figure through `site.imgurl`:

```bash
test -f scripts/generate_course_figures.py && echo script_ok
python3 - << 'PY'
from pathlib import Path
bad = []
paths = list(Path("contents/en").glob("chapter0[89]/_posts/*.md"))
paths += list(Path("contents/en").glob("chapter10/_posts/*.md"))
for p in paths:
    if "site.imgurl" not in p.read_text():
        bad.append(p.name)
print("bad", bad or "none")
PY
```

Expected output:

```text
script_ok
bad none
```

Failure modes: editing a PNG in an image editor and skipping the script, so the next regeneration wipes the tweak; changing English lab floats and leaving the Vietnamese twin on the old number; a `baseurl` copied from a different repository name so every image 404s; a pull request that “fixes” a lesson by editing the product repo.

---

### Worked Numerical Example: A Quantitative Maintenance Audit Before Bumping a Course Dependency

Suppose a maintainer wants to upgrade `onnxruntime-web` from `v1.17` to `v1.20` across Chapters 6–9. Run a crisp 4-point quantitative regression audit before merging:

| Audit Check | Before (`v1.17`) | After (`v1.20`) | Pass Rule | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Streaming Parity (`max |Δ|`)** | $$3.2	imes 10^{-6}$$ | $$2.8	imes 10^{-6}$$ | $$< 10^{-5}$$ | **Pass** |
| **WASM SIMD Bundle (Brotli)** | $$1.45	ext{ MB}$$ | $$1.52	ext{ MB}$$ | $$\le +10\%$$ | **Pass (+4.8%)** |
| **$$\mathrm{RTF}_{p99}$$ (48 kHz 10 ms hop)** | $$0.38$$ | $$0.34$$ | $$\le 0.40$$ | **Pass (-10.5% faster!)** |
| **All Lab & Exercise Scripts** | 26 / 26 passing | 26 / 26 passing | 100% pass | **Pass** |

Only when all four objective checks pass does the upgrade land in the changelog with a dated entry—turning course maintenance into a clean, verifiable engineering workflow!

### Deep-Dive Explanation: Four Rules for Maintaining Any Technical Learning Repo (Read Slowly)

1. **Test every code snippet against real synthetic audio:** Even a 0.5-second generated sine wave + white noise fixture in CI catches 95% of broken library imports, shape mismatches, and deprecated kwargs.
2. **Never delete historical context when updating a recommendation:** Keep a short changelog note explaining *why* an older API (like `ScriptProcessorNode`) was replaced by `AudioWorklet`—learners will still encounter legacy code in the wild.
3. **Audit MathJax and formatting automatically:** Unbalanced double-dollar MathJax delimiters or raw `|` pipes inside Markdown tables silently break rendering on static Jekyll/GitHub Pages sites unless caught by an automated linter.
4. **Review external links and reference papers annually:** Prefer archival links (arXiv, DOI, official W3C/MDN specs) over ephemeral blog posts that disappear after two years.

**Quick check.** In the dependency upgrade audit table above, why do we check **both** `max |Δ| < 1e-5` (numerical parity) and `WASM Brotli size` rather than checking only `RTF`?

---

## Exercises

1. Diff the npm README against lesson 09-01 and list one drift risk.
2. Introduce a one-word English typo in a local branch, fix it, and mirror the fix in the Vietnamese file in the same commit. Do not push unless you are the maintainer on duty.
3. Run `bundle exec jekyll build` and copy any warning that mentions chapters 08–10.
4. Fill the issue template for a fictional 1.4.0 that removes the `v2/` prefix. Mark both EN and VI files.
5. Name the generator command and the two path rules for a new figure.

### Answer hints

1. Likely drift: extra public methods, or a CDN prefix change. Quote the README line you saw.
2. One PR, two files. Front matter `lang` stays put.
3. If the build is not installed, say “jekyll not run” rather than inventing a clean log.
4. EN and VI paths both listed. Figure line “none” unless the diagram changes.
5. `python3 scripts/generate_course_figures.py` writes `img/generated/<name>.png`. Lessons use `{{ site.imgurl }}/generated/<name>.png`.

## Video tham khảo

- [Faster and Lighter Model Inference with ONNX Runtime from Cloud to Client](https://www.youtube.com/watch?v=WDww8ce12Mc) — Microsoft Developer, English. **xem trước.** Runtime and packaging details move. Watch the client-inference path this course cites, and treat a version pin in a lesson as something the changelog has to revisit.
- [Group calling architectures in WebRTC: MCU, SFU & P2P](https://www.youtube.com/watch?v=d2N0d6CKrbk) — Tsahi Levent-Levi, English. SFU, MCU, and mesh vocabulary is the WebRTC half of the integration lessons. When a client SDK renames a hook, this architecture is what the prose still has to describe correctly.
- [What is a CDN (Content Delivery Network) and How does a CDN Work?](https://www.youtube.com/watch?v=rIAIzf6utOc) — Cloudflare, English. Cache and origin behavior is the asset half of the changelog: a model URL that used to be fresh can be a stale edge copy.
