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

Courses rot when APIs move. Mezon's npm surface, CDN `v2/` layout, DeepFilterNet weights, and LiveKit processor APIs will change. This lesson is the maintainer playbook: keep EN/VI in sync, publish on GitHub Pages, and **never** treat course work as a license to edit the product repo casually.

## 60-minute teaching plan

- 0–15 min: What breaks when dependencies move (checklist).  
- 15–30 min: EN/VI sync workflow.  
- 30–45 min: Jekyll / GitHub Pages publish checklist.  
- 45–55 min: AGENTS.md + COURSE_OUTLINE.md advisor loop.  
- 55–60 min: File a maintenance issue template.

## Learning objectives

By the end of this lesson, you can:

- Update lessons when Mezon APIs or DF weights change.  
- Keep EN/VI pairs in sync.  
- Record advisor feedback in `COURSE_OUTLINE.md`.  
- Publish without breaking `baseurl` links.

## What to watch upstream

| Upstream | Symptom in course | Action |
|----------|-------------------|--------|
| `deepfilternet3-noise-filter` major | API rename | Update Ch 07 snippets + version notes |
| CDN layout `v2` → `v3` | 07-03 paths wrong | Update tables; add changelog entry |
| LiveKit SDK | `setProcessor` changes | Re-verify against current docs |
| DeepFilterNet models | new tar name | Update 07/09/10 links |
| DNSMOS version | scores incomparable | Pin version in Ch 08 |

## EN/VI sync rules

1. Same `chapter`, `order`, filename stem.  
2. Change EN first (or VI first) — but merge the pair in one PR when possible.  
3. Code blocks and URLs stay identical; prose is real Vietnamese, not machine-dump unedited.  
4. KaTeX formulas identical across languages.

## Jekyll / GitHub Pages checklist

```text
bundle install
bundle exec jekyll build
# verify baseurl: /audio-noise-suppression-self-learning
# spot-check chapter 07–10 pages locally
# commit; push only when intentional (this task: local commit OK)
```

Site: `https://nglelinh.github.io/audio-noise-suppression-self-learning/`

## Advisor feedback loop

- Capture requests in `COURSE_OUTLINE.md` advisor notes.  
- Prefer fleshing priority: 01 → 02 → 04 → 05–07 → 09 (already in outline).  
- Citation policy: well-known sources only (`AGENTS.md`).

## Product repo boundary

- Course tasks: **read** Mezon README/API; experiment in personal forks / rust sibling / eval harness.  
- Do **not** modify `/Users/nguyenlelinh/ncc/mezon-noise-suppression` as part of homework unless explicitly directed outside this course.

## Maintenance issue template

```markdown
Title: [course] Update Ch07 CDN paths for package x.y.z
- Upstream version:
- Broken lesson paths:
- EN files:
- VI files:
- Verified locally: yes/no
```

## Changelog discipline

When you expand stubs or fix APIs, add a dated bullet under a "Course changelog" section in README or here in future edits:

- `2026-09-22` — Expanded chapters 07–10 EN/VI full lessons.

## Exercises

1. Diff npm README vs Ch 07-04; list drift risks.  
2. Make an EN typo fix and mirror in VI.  
3. Run `jekyll build` and note any warnings.  
4. Open a maintenance issue using the template (even if draft).

## Further reading

- This repo `AGENTS.md`, `README.md`, `CONTRIBUTING.md`  
- Template upstream: `course-self-learning-template`  
- `DEPLOYMENT.md` / `GITHUB_SETUP.md` for Pages
