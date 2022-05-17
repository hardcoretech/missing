# Missing #

A simple [pre-commit][0] hook to find missing `__init__.py` that is required for unit test cases to be discovered.

## Example ##

Default setting, everything except `.git` will be scanned

```yaml
- repo: https://github.com/hardcoretech/missing
  rev: v0.2.5
  hooks:
    - id: missing-init-py
```

Exclude according to .gitignore

```yaml
- repo: https://github.com/hardcoretech/missing
  rev: v0.2.5
  hooks:
    - id: missing-init-py
      args:
        - --mode
        - obey_gitignore
```

Only include git staged files

```yaml
- repo: https://github.com/hardcoretech/missing
  rev: v0.2.5
  hooks:
    - id: missing-init-py
      args:
        - --mode
        - staged_only
```

Exclude frontend and doc folder

```yaml
- repo: https://github.com/hardcoretech/missing
  rev: v0.2.5
  hooks:
    - id: missing-init-py
      args:
        - --exclude
        - frontend
        - doc
```

[0]: https://pre-commit.com/
