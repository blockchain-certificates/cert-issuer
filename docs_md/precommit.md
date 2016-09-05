
Pre-commit hooks
================
Install the pre-commit hook as follows:

```shell
cp pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This does the following:

- runs unit tests
- copies docker instructions to docs/ folder (to avoid maintaining these separately)