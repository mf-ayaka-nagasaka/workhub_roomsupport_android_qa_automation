#!/usr/bin/env python3
"""品質判定基準フレームワークの配布用Zipを作成する。

リポジトリ内の以下をソースとして、自己完結したパッケージを組み立てる。
  - docs/quality_criteria_framework/*.md   -> docs/ および README.md / INSTALL.md
  - .claude/commands/quality-criteria-generator.md -> skills/

使い方:
    python scripts/build_quality_criteria_framework.py
    python scripts/build_quality_criteria_framework.py --version 1.0.0

出力先:
    dist/quality-criteria-framework-<version>.zip
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import shutil
import sys
import zipfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DOCS = REPO_ROOT / "docs" / "quality_criteria_framework"
SRC_SKILL = REPO_ROOT / ".claude" / "commands" / "quality-criteria-generator.md"
DIST_DIR = REPO_ROOT / "dist"

PACKAGE_NAME = "quality-criteria-framework"

# パッケージ直下に置くファイル（docs/ ではなくルート）
ROOT_FILES = ["README.md", "INSTALL.md"]

# docs/ に入れるファイル（この順序で並ぶ）
DOC_FILES = [
    "00_tutorial_first_criteria.md",
    "01_what_is_quality_criteria.md",
    "02_operation_rules.md",
    "03_metrics_catalog.md",
    "04_context_profile.md",
    "05_criteria_template.md",
    "06_default_severity_model.md",
    "07_how_to_prefill_from_source.md",
    "08_how_to_use_skill.md",
]

# assets/ に入れるファイル
ASSET_FILES = [
    "metrics_catalog.csv",
]


def resolve_version(explicit: str | None) -> str:
    if explicit:
        return explicit
    return dt.date.today().strftime("%Y.%m.%d")


def collect_files() -> list[tuple[pathlib.Path, str]]:
    """(実ファイルパス, パッケージ内パス) の一覧を返す。"""
    entries: list[tuple[pathlib.Path, str]] = []

    for name in ROOT_FILES:
        entries.append((SRC_DOCS / name, f"{PACKAGE_NAME}/{name}"))

    for name in DOC_FILES:
        entries.append((SRC_DOCS / name, f"{PACKAGE_NAME}/docs/{name}"))

    for name in ASSET_FILES:
        entries.append((SRC_DOCS / "assets" / name, f"{PACKAGE_NAME}/assets/{name}"))

    entries.append((SRC_SKILL, f"{PACKAGE_NAME}/skills/quality-criteria-generator.md"))

    return entries


def verify(entries: list[tuple[pathlib.Path, str]]) -> list[str]:
    """ソースの存在確認と、パッケージ外への参照が残っていないかの検査。"""
    problems: list[str] = []

    # 外部リポジトリのパスやプロダクト名が残っていないかを検査する
    forbidden = [
        "docs/test_viewpoints",
        ".claude/commands/qa-case-exporter",
        "workhub_roomsupport",
    ]

    for src, packaged in entries:
        if not src.is_file():
            problems.append(f"ソースが見つかりません: {src}")
            continue
        if src.suffix.lower() == ".csv":
            continue
        text = src.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                problems.append(f"パッケージ外への参照が残っています: {packaged} -> '{token}'")

    return problems


def build(version: str, entries: list[tuple[pathlib.Path, str]]) -> pathlib.Path:
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"{PACKAGE_NAME}-{version}.zip"

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, packaged in entries:
            zf.write(src, packaged)
        zf.writestr(
            f"{PACKAGE_NAME}/VERSION",
            f"quality-criteria-framework {version}\nbuilt: {dt.datetime.now().isoformat(timespec='seconds')}\n",
        )

    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="バージョン文字列（省略時は当日の日付）")
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="パッケージ外参照の検査をスキップする（非推奨）",
    )
    args = parser.parse_args()

    version = resolve_version(args.version)
    entries = collect_files()

    problems = verify(entries)
    if problems and not args.skip_verify:
        print("ビルドを中止しました。以下を解消してください:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    for p in problems:
        print(f"[警告] {p}", file=sys.stderr)

    zip_path = build(version, entries)

    size_kb = zip_path.stat().st_size / 1024
    print(f"作成しました: {zip_path.relative_to(REPO_ROOT)}  ({size_kb:.1f} KB)")
    print(f"収録ファイル数: {len(entries) + 1}（VERSION を含む）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
