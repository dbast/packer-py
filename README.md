[![build status](https://github.com/dbast/packer-py/actions/workflows/main.yml/badge.svg)](https://github.com/dbast/packer-py/actions/workflows/main.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/dbast/packer-py/main.svg)](https://results.pre-commit.ci/latest/github/dbast/packer-py/main)

# packer-py

A [pre-commit] [packer] hook. This provides a convenient way to download the pre-built
packer binary for your particular platform and use it via pre-commit hook.

### As a pre-commit hook

See [pre-commit] for instructions

Sample `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/dbast/packer-py
    rev: 1.11.2.1
    hooks:
    -   id: packer-fmt
```

[packer]: https://developer.hashicorp.com/packer
[pre-commit]: https://pre-commit.com
