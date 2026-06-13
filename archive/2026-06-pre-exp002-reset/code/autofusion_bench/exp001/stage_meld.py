"""Stage official MELD assets for exp-001.

This script downloads annotations and, optionally, the official feature/raw
tarballs. It avoids project-local outputs and stores data under /usr1 by default
on ntu-gpu43.
"""

from __future__ import annotations

import argparse
import ssl
import tarfile
import urllib.request
from pathlib import Path

from .meld_schema import ANNOTATION_URLS, FEATURES_URL, RAW_URL


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = Path(args.root)
    annotations_dir = root / "annotations"
    official_dir = root / "official"
    annotations_dir.mkdir(parents=True, exist_ok=True)
    official_dir.mkdir(parents=True, exist_ok=True)

    context = None
    if args.no_check_certificate:
        context = ssl._create_unverified_context()

    for split, url in ANNOTATION_URLS.items():
        output = annotations_dir / Path(url).name
        _download(url, output, context=context)

    if args.features:
        archive = official_dir / "MELD.Features.Models.tar.gz"
        _download(FEATURES_URL, archive, context=context)
        if args.extract:
            _extract(archive, official_dir / "features")

    if args.raw:
        archive = official_dir / "MELD.Raw.tar.gz"
        _download(RAW_URL, archive, context=context)
        if args.extract:
            raw_output = official_dir / "raw"
            _extract(archive, raw_output)
            if args.extract_nested_raw:
                _extract_nested_raw(raw_output)

    print(f"staged MELD root: {root}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage official MELD assets.")
    parser.add_argument(
        "--root",
        default="/usr1/home/s125mdg43_10/datasets/MELD",
        help="MELD staging root",
    )
    parser.add_argument("--features", action="store_true", help="Download official features/models tarball")
    parser.add_argument("--raw", action="store_true", help="Download official raw tarball")
    parser.add_argument("--extract", action="store_true", help="Extract downloaded tarballs")
    parser.add_argument(
        "--extract-nested-raw",
        action="store_true",
        help="After extracting MELD.Raw.tar.gz, also extract nested train/dev/test tarballs.",
    )
    parser.add_argument(
        "--no-check-certificate",
        action="store_true",
        help="Use only when the server CA store cannot verify the official UMich certificate.",
    )
    return parser.parse_args(argv)


def _download(url: str, output: Path, *, context: ssl.SSLContext | None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_size > 0:
        print(f"present: {output}")
        return
    tmp = output.with_suffix(output.suffix + ".part")
    print(f"download: {url}")
    with urllib.request.urlopen(url, context=context) as response, tmp.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    tmp.replace(output)
    print(f"wrote: {output}")


def _extract(archive: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    marker = output_dir / ".extract-complete"
    if marker.exists():
        print(f"extract present: {output_dir}")
        return
    print(f"extract: {archive} -> {output_dir}")
    with tarfile.open(archive, "r:gz") as handle:
        handle.extractall(output_dir)
    marker.write_text("ok\n", encoding="utf-8")


def _extract_nested_raw(raw_output_dir: Path) -> None:
    archives = sorted(raw_output_dir.rglob("*.tar.gz"))
    for archive in archives:
        if archive.name == "MELD.Raw.tar.gz":
            continue
        split_name = archive.name.replace(".tar.gz", "")
        output_dir = archive.parent / split_name
        marker = output_dir / ".extract-complete"
        if marker.exists():
            print(f"nested extract present: {output_dir}")
            continue
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"nested extract: {archive} -> {output_dir}")
        with tarfile.open(archive, "r:gz") as handle:
            handle.extractall(output_dir)
        marker.write_text("ok\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
