# AGENTS.md

## Project

Jekyll 4.3 multilingual course template (English/Vietnamese). Built on the Lanyon theme, deployed to GitHub Pages via GitHub Actions. Uses custom Jekyll plugins for language switching and URL redirects.

## Commands

```bash
bundle install                              # Install Ruby dependencies (Jekyll ~> 4.3.0)
bundle exec jekyll serve                    # Local dev at http://127.0.0.1:4000/{baseurl}/
bundle exec jekyll build                    # Production build
```

Docker alternative:

```bash
docker-compose up                           # Jekyll 4.2 on port 4000
```

After changing `_config.yml`, restart Jekyll.

## Repository Layout

```
.
├── _config.yml                 # Site config, translations, author
├── _includes/                  # head.html, sidebar.html
├── _layouts/                   # default.html, page.html, post.html
├── _plugins/                   # Custom Jekyll plugins (see below)
├── contents/
│   ├── en/chapterXX/
│   │   ├── index.html          # Chapter landing page
│   │   └── _posts/             # Lecture markdown files
│   └── vi/chapterXX/           # Mirror structure for Vietnamese
├── home/_posts/                # Home page sections
├── contribution/_posts/        # Contributor docs
├── reference/_posts/           # Reference materials
├── public/                     # CSS, JS, logos (served at /public/)
├── img/chapter_img/            # Lecture images (create as needed)
├── index.html                  # Home page (renders home/_posts by order)
├── Gemfile                     # jekyll, jekyll-feed, jekyll-paginate, webrick
└── .github/workflows/jekyll.yml
```

## Configuration

Edit `_config.yml` before first use:

- `title`, `description`, `url`, `baseurl`, `imgurl` — site identity and asset paths
- `languages` / `default_lang` — `["en", "vi"]`, default `"en"`
- `t.en.*` / `t.vi.*` — UI translation strings (`home`, `chapters`, `required`, `optional`, `switch_language`, etc.)
- `author.name` / `author.email` — instructor contact

Also update:

- `_layouts/default.html` line 24 — GitHub repo link (`your-username/your-repo-name`)
- `AUTHORS.md` — instructor bio

## Content Structure

### Lecture posts

Path: `contents/{lang}/chapterXX/_posts/YYYY-MM-DD-title.md`

Required front matter:

```yaml
---
layout: post
title: "Lesson Title"
chapter: 'XX'           # Two-digit chapter number as string
order: N                # Integer ordering within chapter (drives prev/next nav)
owner: Author Name
lang: en                # 'en' or 'vi'
categories:
- chapterXX             # Must match chapter directory name
lesson_type: required   # 'required' or 'optional' (shows badge in sidebar)
---
```

Language switching matches posts by `chapter` + `order` across `en`/`vi`. Keep these aligned when adding bilingual content.

### Chapter landing pages

Each chapter needs `contents/{lang}/chapterXX/index.html`:

```yaml
---
layout: page
lang: en
title: "Chapter Title"
chapter: "XX"
owner: "Author Name"
---
```

Sidebar lists pages with `layout: page` and a `chapter` field, sorted by `chapter`.

### Home page

`index.html` renders posts from `home/_posts/` where `categories` includes `home`, sorted by `order`:

| File | Purpose |
|------|---------|
| `21-01-20-introduction.md` | Course intro |
| `21-01-20-contents.md` | Course outline |
| `21-02-03-makers.md` | Instructor info |
| `21-05-20-author-details.md` | Author details |
| `21-01-27-link_to_how_to_contribute.md` | Contribution link |

Home posts use `chapter: home` and an `order` field.

### Adding a new chapter

1. Create `contents/en/chapterXX/` and `contents/vi/chapterXX/` with `_posts/` subdirs
2. Add `index.html` in each language directory
3. Add lecture posts with matching `chapter`, `order`, and `categories`
4. Posts auto-appear in sidebar via chapter index and in prev/next navigation via `order`

## Math and LaTeX

MathJax 3 is loaded in `_includes/head.html`. Use `$$...$$` for both inline and display math (not single `$`):

```markdown
Inline: $$f(x) = x^2$$

Display block:
$$
\nabla f(x) = 0
$$
```

## Custom Plugins

Located in `_plugins/`:

| Plugin | Tags / behavior |
|--------|-----------------|
| `multilang.rb` | `{% t key %}` — translate UI string; `{% language_switch %}` — lang toggle link; `{% lang en %}` — active class |
| `multilang_post_url.rb` | `{% multilang_post_url contents/chapterXX/post-name %}` — resolve post URL in current language |
| `redirect_generator.rb` | Generates redirect pages from legacy `/contents/chapterXX/` URLs to `/contents/en/chapterXX/` |

## URL Structure

- English chapters: `/contents/en/chapter00/`
- Vietnamese chapters: `/contents/vi/chapter00/`
- All URLs are prefixed with `baseurl` on GitHub Pages

## Images

Place images in `img/chapter_img/` and reference in markdown:

```markdown
![Alt text]({{ site.imgurl }}/chapter_img/image.png)
```

## Styling and Assets

- CSS: `public/css/` (`lanyon.css`, `poole.css`, `syntax.css`, `github-markdown.css`, `multilang.css`, `content-boxes.css`)
- JS: `public/js/script.js`, `public/js/multilang.js`
- Logos: `public/logo.png`, `public/convex-logo-144x144.png`

## Deployment

Push to `main`. GitHub Actions (`.github/workflows/jekyll.yml`) builds with Ruby 3.1 and deploys via `actions/deploy-pages`.

Repository settings: **Settings > Pages > Source: GitHub Actions**.

See `DEPLOYMENT.md` for details. Custom plugins require Actions-based deploy (not default GitHub Pages Jekyll build).

## Lecture Writing Guidelines

See `.cursor/rules/` when authoring course content:

- `lecture-notes-rule.mdc` — Lecture structure, prose style, 1500–3000 words per lecture, objectives/prerequisites/examples/exercises format
- `math-formula-rule.mdc` — LaTeX conventions; always use `$$` delimiters

## Related Docs

- `SETUP.md` — First-time setup checklist
- `CONTRIBUTING.md` — Contribution workflow and content format
- `README.md` — Feature overview (some sections reference plugins not present in repo, e.g. `search_generator.rb`)