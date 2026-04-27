# Microglia Particle Analysis

Batch Fiji/ImageJ particle analysis for Olympus `.oir` microscopy images.

The workflow mirrors the manual SOP:

1. Open `.oir` images with Bio-Formats.
2. Select one split channel.
3. Z-project the stack with average intensity.
4. Convert to 8-bit.
5. Threshold and make a binary image.
6. Run ImageJ particle analysis.
7. Save results, outlines, and binary mask for each image.

## Requirements

- Python 3.10 or newer.
- Fiji installed locally.
- Fiji launcher available as `fiji` on `PATH`, or supplied with `--fiji`.

Fiji provides the ImageJ and Bio-Formats Java classes used by `scripts/fiji_particle_analysis.py`. They are not pip packages.

## Install

Install this project in editable mode:

```bash
python3 -m pip install -e .
```

For development tools:

```bash
python3 -m pip install -e ".[dev]"
```

## Configure Fiji

Expose your Fiji launcher as `fiji`.

Linux example:

```bash
ln -s /path/to/Fiji.app/ImageJ-linux64 ~/.local/bin/fiji
fiji --headless --version
```

macOS example:

```bash
ln -s /Applications/Fiji/Fiji.app/Contents/MacOS/fiji-macos-arm64 /usr/local/bin/fiji
fiji --headless --version
```

If Fiji is not on `PATH`, pass the launcher directly:

```bash
microglia-particle-analysis /path/to/images \
  --fiji /path/to/Fiji.app/ImageJ-linux64
```

Windows explicit launcher example:

```powershell
microglia-particle-analysis C:\path\to\images `
  --fiji C:\path\to\Fiji.app\fiji-win64.exe
```

## Quick Start

Run one image with tuned settings from the initial validation image:

```bash
microglia-particle-analysis mg1_iba1_rat301_0001.oir \
  --channel 1 \
  --threshold-min 30 \
  --threshold-max 255 \
  --size "20-600" \
  --limit 1 \
  --output-dir outputs/candidate-70
```

Outputs are written to `outputs/<image-name>/`:

- `results.csv`: ImageJ particle table.
- `outlines.tif`: particle outline image.
- `binary_mask.tif`: thresholded binary image.

## Batch Run

Process every `.oir` file in a folder:

```bash
microglia-particle-analysis /path/to/oir-folder \
  --channel 1 \
  --threshold-min 30 \
  --threshold-max 255 \
  --size "20-600" \
  --jobs 4 \
  --output-dir outputs
```

`--jobs` controls how many Fiji processes run at once. Start with `--jobs 2` or `--jobs 4`; each worker launches an independent Fiji process and can use significant memory.

For local development without installing the console command:

```bash
python3 scripts/run_particle_analysis.py /path/to/oir-folder \
  --channel 1 \
  --threshold-min 30 \
  --threshold-max 255 \
  --size "20-600" \
  --output-dir outputs
```

## Auto Threshold

Use Fiji auto-thresholding by omitting manual threshold bounds and passing a method:

```bash
microglia-particle-analysis mg1_iba1_rat301_0001.oir \
  --channel 1 \
  --threshold-method "Otsu dark" \
  --size "20-600" \
  --output-dir outputs/otsu
```

On the initial validation image, `Otsu dark` produced 89 particles.

## Parameters

- `--channel 1`: zero-based channel to analyse after Bio-Formats split, matching the GUI's channel 1.
- `--z-project average|max|sum`: projection method for Z-stacks. Default: `average`.
- `--threshold-min 30 --threshold-max 255`: manual threshold range. Use both or neither.
- `--threshold-method "Otsu dark"`: Fiji auto-threshold method used when manual bounds are omitted.
- `--size "20-600"`: particle size range in microns^2. Converted to pixel bounds internally.
- `--circularity "0.00-1.00"`: particle circularity filter.
- `--foreground light`: default; selected particles are white on black background.
- `--foreground dark`: optional inverted mask; selected particles are black on white background.
- `--jobs 1`: number of images to process in parallel. Default: `1`.
- `--pixel-width-um 0.3107421875 --pixel-height-um 0.3107421875`: calibration override; defaults to `636.40 / 2048` microns per pixel.

## Tuning Guidance

Tune `--threshold-*` and `--size` on representative images before running a full batch. Review both `binary_mask.tif` and `outlines.tif`; the mask confirms thresholding, while outlines confirm particle filtering.

Closest tested match to the manual ~70-particle result for `mg1_iba1_rat301_0001.oir`:

```bash
microglia-particle-analysis mg1_iba1_rat301_0001.oir \
  --channel 1 \
  --threshold-min 30 \
  --threshold-max 255 \
  --size "20-600" \
  --output-dir outputs/candidate-70
```

## Contributing

Contributions are welcome. See `CONTRIBUTING.md` for local setup, validation checks, and pull request expectations.

Install pre-commit hooks after installing development dependencies:

```bash
make install-hooks
```

Please do not commit microscopy data or generated outputs. `.oir` files and `outputs/` are ignored by default.

## Licence

This project is licensed under the MIT License. See `LICENSE`.
