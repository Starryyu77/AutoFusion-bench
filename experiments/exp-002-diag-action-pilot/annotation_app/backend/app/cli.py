"""CLI for local exp-002 annotation import, export, and merge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .merge import merge_exports
from .storage import export_annotations, import_sheet, summary


def cmd_import(args: argparse.Namespace) -> int:
    result = import_sheet(
        db_path=args.db,
        sheet_path=args.sheet,
        annotator=args.annotator,
        session_name=args.session_name,
        replace=not args.no_replace,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    result = export_annotations(db_path=args.db, output_path=args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    result = merge_exports(
        annotation_paths=args.annotations,
        output_path=args.output,
        report_path=args.report,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    result = summary(args.db)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("state/annotations.sqlite"))
    subparsers = parser.add_subparsers(required=True)

    import_parser = subparsers.add_parser("import-sheet", help="Import a draft/gold annotation JSONL sheet.")
    import_parser.add_argument("--sheet", required=True, type=Path)
    import_parser.add_argument("--annotator", required=True)
    import_parser.add_argument("--session-name")
    import_parser.add_argument("--no-replace", action="store_true")
    import_parser.set_defaults(func=cmd_import)

    export_parser = subparsers.add_parser("export", help="Export SQLite state to scorer-compatible JSONL.")
    export_parser.add_argument("--output", required=True, type=Path)
    export_parser.set_defaults(func=cmd_export)

    merge_parser = subparsers.add_parser("merge", help="Merge annotator JSONL exports and write disagreements.")
    merge_parser.add_argument("--annotations", required=True, type=Path, nargs="+")
    merge_parser.add_argument("--output", required=True, type=Path)
    merge_parser.add_argument("--report", type=Path)
    merge_parser.set_defaults(func=cmd_merge)

    summary_parser = subparsers.add_parser("summary", help="Show local SQLite annotation status.")
    summary_parser.set_defaults(func=cmd_summary)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

