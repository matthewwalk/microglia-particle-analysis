# Contributing

Thanks for helping improve `microglia-particle-analysis`.

## Development Setup

Install Fiji first and make sure `fiji --headless --version` works. Then install the Python package with development tools:

```bash
python3 -m pip install -e ".[dev]"
```

Install the git hooks:

```bash
make install-hooks
```

## Before Opening a Pull Request

Run the pre-commit checks:

```bash
make pre-commit
```

If your change affects Fiji processing, run a small `.oir` smoke test and inspect:

- `<image-stem>_results.csv`
- `<image-stem>_binary_mask.tif`
- `<image-stem>_outlines.tif`

Do not commit microscopy data, generated outputs, local environments, or cache files.

## Pull Request Guidelines

- Keep changes focused and reviewable.
- Describe the microscopy workflow impact, if any.
- Include the exact command used for smoke testing.
- Mention any Fiji/ImageJ version assumptions.

## Reporting Issues

When reporting a bug, include:

- Operating system.
- Python version.
- Fiji version from `fiji --headless --version`.
- Exact command run.
- Error output or unexpected result.
- Whether `*_binary_mask.tif` or `*_outlines.tif` looked incorrect.
