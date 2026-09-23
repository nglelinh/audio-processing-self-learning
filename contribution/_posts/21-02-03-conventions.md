---
layout: post
title: "Conventions"
chapter: home
order: 2
owner: "Your Name"
---

## 1. Directory Convention

- Main content lives under `contents/{lang}/chapterXX/` (e.g. `contents/en/chapter01/`). Images go in `img/chapter_img/`.
- A typical chapter directory looks like this:

```
contents/
├── en/
│   └── chapter01/
│       ├── _posts/
│       │   ├── 21-01-07-01_00_Introduction.md
│       │   ├── 21-01-07-01_01_optimization_problems.md
│       │   └── ...
│       └── index.html
└── vi/
    └── chapter01/
        ├── _posts/
        └── index.html
```

- Jekyll treats Markdown or HTML files inside `_posts` as blog posts. To add a new post, create a file in the chapter's `_posts/` directory.
- Post filenames must follow this naming convention:
    - `YYYY-MM-DD-post_name.md`
- Files outside `contents/` and `img/` are site configuration. For stability, open an issue instead of editing config directly (config changes can make PR merges difficult).

## 2. Posting Convention

### 2.1. Header Fields

- Every post must include front matter like this:

```
---
layout: post
title: Quasi-Newton Methods
chapter: "18"
order: 1
owner: "Your Name"
lang: en
categories:
- chapter18
lesson_type: required
---
```

- **layout** must be `post`.
- **title** can be any descriptive string.
- **chapter** is the two-digit chapter number as a string (e.g. `"01"` for chapter 1).
- **order** controls sort order within the chapter and prev/next navigation.
- **owner** is the post maintainer.
- **lang** is `en` or `vi`.
- **categories** must match the chapter directory name (e.g. `chapter18`).
- **lesson_type** is `required` or `optional`.

### 2.2. LaTeX

- Write formulas using LaTeX syntax.
- Use double dollar signs (`$$`) to mark math.

```
$$\theta x_1 + (1-\theta)x_2 \in C$$
```

renders as:

$$\theta x_1 + (1-\theta)x_2 \in C$$

### 2.3. Image Convention

- When inserting images in a post, use this format:

```
<figure class="image" style="align: center;">
<p align="center">
  <img src="{image_path}" alt="{description of image}" width="{scale_ratio}%" height="{scale_ratio}%">
  <figcaption style="text-align: center;">{figcaption}</figcaption>
</p>
</figure>
```

- The figure class must be `image`.
- Replace `{}` placeholders with appropriate values.

Alternatively, use markdown with the site image URL:

```markdown
![Alt text]({{ site.imgurl }}/chapter_img/your-image.png)
```

### 2.4 Hyperlink Convention

- For links to other posts in this site, use the `multilang_post_url` tag. Example:

```
[Your Post Title]({% multilang_post_url contents/chapter01/21-01-07-01_01_your_post %})
```

- For external URLs:

```
[External Link](<https://example.com>)
```

## 3. GitHub Convention

If you have questions or find something to fix, use one of these:

- Leave a comment on the post
- Open an issue in the repository

To add or edit content, create a new branch, make your changes, then open a `Pull Request`. Anyone can contribute new or updated content.

### 3.1. Repository Policy

Merging into `main` requires approval from at least one reviewer. If CODEOWNERS is configured, chapter reviewers are assigned automatically.

### 3.2. Branch Naming Convention

Name branches using this pattern:

```
[feature|bugfix]/[chapter**|settings]-change-description
```

Use two prefixes:

- **feature**
  - Migration work
  - Changes to text, formulas, or images
  - New content
- **bugfix**
  - Typo fixes
  - Broken LaTeX rendering

Examples:

- `feature/chapter01-migration`: chapter01 migration
- `feature/chapter01-fix-formula`: update formula in chapter01
- `feature/settings-update-branch-convention`: update conventions
- `bugfix/chapter01-fix-typo`: fix typo in chapter01