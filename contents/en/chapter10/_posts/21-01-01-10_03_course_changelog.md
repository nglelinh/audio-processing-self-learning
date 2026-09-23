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

## What you should be able to do

You should be able to patch a lesson when `deepfilternet3-noise-filter` or the CDN layout changes, update the Vietnamese twin in the same pull request, add a figure without breaking `baseurl`, and file a maintenance note that lists both language files. You should also build the site locally and name the failure if `bundle exec jekyll build` warns.

## What to watch

| Upstream | What breaks | What you edit |
|----------|-------------|---------------|
| npm `deepfilternet3-noise-filter` above 1.3.0 | Public names or the asset prefix (`v2/` in the README, `v3/` in installed 1.3.0) | Chapters 07 and 09, both languages |
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
