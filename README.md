# Particle Analysis Automation

Batch automation for the Fiji/ImageJ particle-analysis SOP:

1. Open Olympus `.oir` via Bio-Formats.
2. Split channels.
3. Z-project stacks.
4. Convert to 8-bit.
5. Threshold and convert to binary mask.
6. Run Analyze Particles.
7. Save per-image results, outlines, and binary mask.

## Smoke Test

Install locally if you want the `particle-analysis` command:

```bash
python3 -m pip install -e .
```

Install Fiji separately, then expose its launcher as `fiji` on your `PATH`.

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

If you do not want to add Fiji to `PATH`, pass it explicitly:

```bash
python3 scripts/run_particle_analysis.py /path/to/images \
  --fiji /path/to/Fiji.app/ImageJ-linux64
```

```bash
python3 scripts/run_particle_analysis.py mg1_iba1_rat301_0001.oir \
  --channel 1 \
  --threshold-min 30 \
  --threshold-max 255 \
  --size "20-600" \
  --limit 1
```

Outputs land in `outputs/<image-name>/`:

- `results.csv`
- `outlines.tif`
- `binary_mask.tif`

## Batch Run

```bash
python3 scripts/run_particle_analysis.py /path/to/oir-folder --output-dir outputs
```

## Key Parameters

- `--channel 1`: zero-based channel to analyse after Bio-Formats split, matching the GUI's channel 1.
- `--z-project average|max|sum`: projection method for Z-stacks.
- `--threshold-method "Default dark"`: Fiji auto-threshold method.
- `--threshold-min 0 --threshold-max 18`: manual threshold range. Use both or neither.
- `--size "20-600"`: particle size range in microns^2. Script converts to pixel bounds internally.
- `--circularity "0.00-1.00"`: particle circularity filter.
- `--foreground light`: default; selected particles are white on black background.
- `--foreground dark`: optional inverted mask; selected particles are black on white background.
- `--pixel-width-um 0.3107421875 --pixel-height-um 0.3107421875`: calibration override; defaults to 636.40 microns / 2048 px.

For production runs, tune `--threshold-*` and `--size` on a representative subset first, then process the full folder.

For `mg1_iba1_rat301_0001.oir`, the closest tested match to the manual ~70-particle output was:

```bash
python3 scripts/run_particle_analysis.py mg1_iba1_rat301_0001.oir \
  --channel 1 \
  --threshold-min 30 \
  --threshold-max 255 \
  --size "20-600" \
  --output-dir outputs/candidate-70
```

`--threshold-method "Otsu dark"` gave 89 particles on the same image.
