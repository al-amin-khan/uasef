# Publish UASEF to your GitHub account

This project is distributed as a Git-ready source tree, not automatically connected to a GitHub repository. Create an **empty** repository (for example `uasef`) under the intended GitHub account. Do not initialize it with another README or license.

From the extracted `uasef` directory:

```bash
git init
git add .
git commit -m "feat: release UASEF v0.2 agent execution and orchestration"
git branch -M main
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

Replace OWNER/REPOSITORY with your actual destination. Never push to an unrelated existing repository without checking its contents. Use the Git credential manager or GitHub CLI for authentication; **do not paste personal access tokens into chat or source files**.

To contribute future versions, create a feature branch and open a pull request with GitHub Actions tests enabled. Protect `main` and enable branch review/rulesets for important projects.
