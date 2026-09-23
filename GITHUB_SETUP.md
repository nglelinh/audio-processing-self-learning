# GitHub setup (local scaffold complete; remote not pushed)

`gh` on this box has **no valid auth** (`gh auth status` → not logged in). Local git history is ready on `main`.

## Create + push (run on Mac as Linh)

```bash
# 1) Place the course tree at:
#    /Users/nguyenlelinh/teaching/audio-processing-self-learning
#    (copy from box tarball /workspace/audio-processing-self-learning.tar.gz if needed)

cd /Users/nguyenlelinh/teaching/audio-processing-self-learning

gh auth login   # if needed
gh repo create nglelinh/audio-processing-self-learning --public --source=. --remote=origin --push
```

If the empty repo already exists on GitHub:

```bash
git remote add origin git@github.com:nglelinh/audio-processing-self-learning.git
# or: https://github.com/nglelinh/audio-processing-self-learning.git
git push -u origin main
```

Enable **Settings → Pages → GitHub Actions** (workflow already under `.github/workflows/jekyll.yml`).

Do not treat the remote as published until `git push` succeeds.
