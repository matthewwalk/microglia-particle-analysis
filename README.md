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

```bash
python3 scripts/run_particle_analysis.py mg1_iba1_rat301_0001.oir --limit 1 --size 20-Infinity
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

- `--channel 1`: channel to analyse after Bio-Formats split.
- `--z-project average|max|sum`: projection method for Z-stacks.
- `--threshold-method "Default dark"`: Fiji auto-threshold method.
- `--threshold-min 0 --threshold-max 18`: manual threshold range. Use both or neither.
- `--size "20-120"`: particle size range in calibrated area units.
- `--circularity "0.00-1.00"`: particle circularity filter.
- `--pixel-width-um 0.3107421875 --pixel-height-um 0.3107421875`: optional calibration override.

For production runs, tune `--threshold-*` and `--size` on a representative subset first, then process the full folder.
