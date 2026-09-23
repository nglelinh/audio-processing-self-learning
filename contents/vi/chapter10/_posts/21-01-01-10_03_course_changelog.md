---
layout: post
title: "10-03 Duy trì khóa học này"
chapter: "10"
order: 3
owner: "Nguyen Le Linh"
lang: vi
categories:
  - chapter10
lesson_type: required
draft: false
---

Khóa học “thối” khi API đổi. Bề mặt npm Mezon, layout CDN `v2/`, weights DeepFilterNet, và API processor LiveKit sẽ thay đổi. Bài này là sổ tay maintainer: giữ EN/VI đồng bộ, publish GitHub Pages, và **không** coi bài tập khóa là giấy phép sửa product repo tùy tiện.

## Kế hoạch giảng 60 phút

- 0–15 phút: Cái gì gãy khi dependency đổi.
- 15–30 phút: Quy trình đồng bộ EN/VI.
- 30–45 phút: Checklist Jekyll / GitHub Pages.
- 45–55 phút: Vòng `AGENTS.md` + `COURSE_OUTLINE.md` với advisor.
- 55–60 phút: Mẫu issue bảo trì.

## Mục tiêu học tập

Cuối bài, bạn có thể:

- Cập nhật bài khi API Mezon hoặc weights DF đổi.
- Giữ cặp EN/VI đồng bộ.
- Ghi feedback advisor vào `COURSE_OUTLINE.md`.
- Publish mà không gãy link `baseurl`.

## Theo dõi upstream

| Upstream | Triệu chứng trong khóa | Hành động |
|----------|------------------------|-----------|
| Major `deepfilternet3-noise-filter` | Đổi tên API | Sửa snippet Ch 07 + ghi phiên bản |
| CDN `v2` → `v3` | Sai path 07-03 | Cập nhật bảng; thêm changelog |
| LiveKit SDK | Đổi `setProcessor` | Đối chiếu docs hiện tại |
| Model DeepFilterNet | Đổi tên tar | Sửa link 07/09/10 |
| Phiên bản DNSMOS | Điểm không so được | Pin trong Ch 08 |

## Quy tắc đồng bộ EN/VI

1. Cùng `chapter`, `order`, stem tên file.  
2. Đổi một ngôn ngữ rồi merge cặp trong một PR khi có thể.  
3. Code/URL giống nhau; văn xuôi tiếng Việt thật, không dump máy chưa biên tập.  
4. Công thức KaTeX giống nhau giữa hai ngôn ngữ.

## Checklist Jekyll / Pages

```text
bundle install
bundle exec jekyll build
# baseurl: /audio-noise-suppression-self-learning
# soi chương 07–10 local
# commit; chỉ push khi chủ đích (task này: commit local OK)
```

Site: `https://nglelinh.github.io/audio-noise-suppression-self-learning/`

## Ranh giới product repo

Bài tập khóa: **đọc** README/API Mezon; thử trên fork cá nhân / rust sibling / harness.  
**Không** sửa `/Users/nguyenlelinh/ncc/mezon-noise-suppression` như một phần homework trừ khi được chỉ thị ngoài khóa này.

## Mẫu issue bảo trì

```markdown
Title: [course] Cập nhật path CDN Ch07 cho gói x.y.z
- Phiên bản upstream:
- Bài bị gãy:
- File EN / VI:
- Đã verify local: yes/no
```

## Kỷ luật changelog

Khi mở rộng stub hoặc sửa API, thêm bullet có ngày, ví dụ:

- `2026-09-22` — Mở rộng đầy đủ chương 07–10 EN/VI.

## Bài tập

1. Diff README npm vs Ch 07-04; liệt kê rủi ro lệch.  
2. Sửa một typo EN và phản chiếu VI.  
3. Chạy `jekyll build` và ghi warning.  
4. Mở issue bảo trì theo mẫu (dù draft).

## Đọc thêm

- `AGENTS.md`, `README.md`, `CONTRIBUTING.md`  
- Template: `course-self-learning-template`  
- `DEPLOYMENT.md` / `GITHUB_SETUP.md`
