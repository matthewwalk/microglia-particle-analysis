#!/usr/bin/env python3
"""Batch-run Fiji particle analysis for Olympus OIR microscopy images."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCRIPT = REPO_ROOT / "scripts" / "fiji_particle_analysis.py"
DEFAULT_FIJI_CANDIDATES = (
    Path("/Applications/Fiji/Fiji.app/Contents/MacOS/fiji-macos-arm64"),
    Path("/Applications/Fiji/Fiji.app/Contents/MacOS/fiji-macos"),
    Path("/Applications/Fiji.app/Contents/MacOS/fiji-macos-arm64"),
    Path("/Applications/Fiji.app/Contents/MacOS/fiji-macos"),
)


def existing_path(value: str) -> Path:
    """Return a resolved path, raising argparse errors when missing."""
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {path}")
    return path


def positive_int(value: str) -> int:
    """Parse a positive integer argument."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be >= 1")
    return parsed


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run the Fiji/ImageJ particle-analysis SOP over one or more .oir files.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=existing_path,
        help="OIR files or directories containing OIR files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "outputs",
        help="Directory where per-image results are written.",
    )
    parser.add_argument(
        "--fiji",
        type=Path,
        default=None,
        help="Path to Fiji executable. Defaults to /Applications/Fiji/Fiji.app/Contents/MacOS/fiji-macos-arm64.",
    )
    parser.add_argument(
        "--script",
        type=existing_path,
        default=DEFAULT_SCRIPT,
        help="Path to Fiji/ImageJ script.",
    )
    parser.add_argument(
        "--channel",
        type=positive_int,
        default=1,
        help="Split channel number to analyse.",
    )
    parser.add_argument(
        "--z-project",
        choices=("average", "max", "sum"),
        default="average",
        help="Z-projection method for stacks.",
    )
    parser.add_argument(
        "--threshold-method",
        default="Default dark",
        help='ImageJ auto-threshold method, used unless --threshold-min and --threshold-max are set.',
    )
    parser.add_argument(
        "--threshold-min",
        type=float,
        default=None,
        help="Manual threshold minimum.",
    )
    parser.add_argument(
        "--threshold-max",
        type=float,
        default=None,
        help="Manual threshold maximum.",
    )
    parser.add_argument(
        "--size",
        default="20-Infinity",
        help='Particle size range, e.g. "20-120" in calibrated area units.',
    )
    parser.add_argument(
        "--circularity",
        default="0.00-1.00",
        help='Particle circularity range, e.g. "0.00-1.00".',
    )
    parser.add_argument(
        "--pixel-width-um",
        type=float,
        default=None,
        help="Override pixel width in microns when Bio-Formats does not preserve calibration.",
    )
    parser.add_argument(
        "--pixel-height-um",
        type=float,
        default=None,
        help="Override pixel height in microns when Bio-Formats does not preserve calibration.",
    )
    parser.add_argument(
        "--limit",
        type=positive_int,
        default=None,
        help="Only process first N files. Useful for smoke tests.",
    )
    return parser.parse_args(argv)


def discover_fiji(explicit_path: Path | None) -> Path:
    """Find the Fiji launcher."""
    if explicit_path is not None:
        path = explicit_path.expanduser().resolve()
        if path.exists():
            return path
        raise FileNotFoundError(f"Fiji executable does not exist: {path}")

    for candidate in DEFAULT_FIJI_CANDIDATES:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Could not find Fiji. Pass --fiji /path/to/Fiji.app/Contents/MacOS/fiji-macos-arm64."
    )


def discover_inputs(paths: Sequence[Path], limit: int | None) -> list[Path]:
    """Expand file and directory inputs into sorted OIR paths."""
    oir_paths: list[Path] = []
    for path in paths:
        if path.is_dir():
            oir_paths.extend(sorted(path.rglob("*.oir")))
            oir_paths.extend(sorted(path.rglob("*.OIR")))
        else:
            if path.suffix.lower() != ".oir":
                raise ValueError(f"input is not an .oir file: {path}")
            oir_paths.append(path)

    unique_paths = sorted(dict.fromkeys(oir_paths))
    if limit is not None:
        return unique_paths[:limit]
    return unique_paths


def script_args(
    image_path: Path,
    results_path: Path,
    outlines_path: Path,
    binary_path: Path,
    args: argparse.Namespace,
) -> str:
    """Build ImageJ script argument string."""
    values = {
        "input": image_path,
        "results": results_path,
        "outlines": outlines_path,
        "binary": binary_path,
        "channel": args.channel,
        "z_project": args.z_project,
        "threshold_method": args.threshold_method,
        "threshold_min": "" if args.threshold_min is None else args.threshold_min,
        "threshold_max": "" if args.threshold_max is None else args.threshold_max,
        "size": args.size,
        "circularity": args.circularity,
        "pixel_width_um": "" if args.pixel_width_um is None else args.pixel_width_um,
        "pixel_height_um": "" if args.pixel_height_um is None else args.pixel_height_um,
    }

    return ",".join(f'{key}="{value}"' for key, value in values.items())


def run_one(
    fiji_path: Path,
    script_path: Path,
    image_path: Path,
    output_dir: Path,
    args: argparse.Namespace,
) -> Path:
    """Run Fiji particle analysis for one image and return results path."""
    image_output_dir = output_dir / image_path.stem
    image_output_dir.mkdir(parents=True, exist_ok=True)

    results_path = image_output_dir / "results.csv"
    outlines_path = image_output_dir / "outlines.tif"
    binary_path = image_output_dir / "binary_mask.tif"
    command = [
        str(fiji_path),
        "--headless",
        "--run",
        str(script_path),
        script_args(image_path, results_path, outlines_path, binary_path, args),
    ]

    subprocess.run(command, check=True)
    if not results_path.exists() or results_path.stat().st_size == 0:
        raise RuntimeError(f"Fiji completed but did not write results: {results_path}")
    return results_path


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    args = parse_args(argv)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    fiji_path = discover_fiji(args.fiji)
    image_paths = discover_inputs(args.inputs, args.limit)
    if not image_paths:
        raise SystemExit("No .oir files found.")

    print(f"Fiji: {fiji_path}")
    print(f"Script: {args.script}")
    print(f"Images: {len(image_paths)}")

    for index, image_path in enumerate(image_paths, start=1):
        print(f"[{index}/{len(image_paths)}] {image_path.name}")
        results_path = run_one(fiji_path, args.script, image_path, output_dir, args)
        print(f"  results: {results_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
