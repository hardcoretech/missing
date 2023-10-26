# Missing

A simple [pre-commit][0] hook to find missing `__init__.py`. Will obey settings in `.gitignore`.

## Example

Default settings

```yaml
- repo: https://github.com/hardcoretech/missing
  rev: v0.3.0
  hooks:
    - id: missing-init-py
```

Exclude some folders

```yaml
- repo: https://github.com/hardcoretech/missing
  rev: v0.3.0
  hooks:
    - id: missing-init-py
      args:
        - --exclude
        - frontend
        - doc
```

[0]: https://pre-commit.com/
