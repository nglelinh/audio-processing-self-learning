---
layout: post
title: "How to Contribute"
chapter: home
order: 3
owner: kyeongminwoo
---

---

## 1. Editing Content Directly

### (1) Open your local repository directory. If you do not have a local copy yet, see [Initial Settings]({{ site.baseurl }}/contribution/2021/01/27/initial_settings/).

### (2) Sync with the remote repository.

```bash
$ git checkout main
$ git pull --all
```

### (3) Create a new branch for your changes. Use `[prefix]/[chapter]/[reason]` (see [Branch Naming Convention]({{ site.baseurl }}/contribution/2021/02/03/conventions/)). Example:

```bash
$ git checkout -b bugfix/chapter01-fix-typo
```

### (4) Edit files. Follow the [Conventions]({{ site.baseurl }}/contribution/2021/02/03/conventions/) when creating or updating content.

### (5) Push to the remote. Example:

```bash
$ git push origin bugfix/chapter01-fix-typo
```

### (6) Open a Pull Request to `main` on GitHub. See GitHub Docs for details:

- [Creating a pull request](<https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request>)

---

## 2. Requesting Content Changes

- You can open an [Issue](https://github.com/your-username/your-repo-name/issues) on the GitHub repository.

---