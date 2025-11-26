Here are some of the life saving commands I frequently use in dire cases.
Kindly ignore.

## For when I need to push the changes to an older commit

```bash
git status --porcelain
git add -u; git commit --amend --no-edit; git push --force-with-lease origin main

```

## For when I have commits and corrections after release but they were supposed to be part of the release
```bash
git log --oneline --decorate -n 5
git tag -l -n1 v1.0.0; git rev-parse v1.0.0
git tag -d v1.0.0; git tag v1.0.0; git push origin v1.0.0 --force
```