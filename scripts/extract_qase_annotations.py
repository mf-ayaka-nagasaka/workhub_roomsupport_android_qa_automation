"""テストソースを静的に解析し、@Qase アノテーションの内容を JSON へ書き出す。

検証用リポジトリでは JUnit5 のリスナーが実行時にアノテーションを収集していたが、
本番リポジトリは JUnit4 のためリスナーが動作しない。本スクリプトはソースを直接読み、
同じ形式の JSON を生成することでリスナーを不要にする。

使い方:
    python scripts/extract_qase_annotations.py \
        --source-root "C:/Users/<user>/workhubRoomSupport-Android" \
        --out build/qase/qase-cases.json

出力:
    {"tests": [{case_id, class, method, title, description, level,
                level_option_id, has_steps, steps: [{action, expected, data}],
                file, line}],
     "unannotated": ["<class>#<method>", ...]}
"""

import argparse
import json
import os
import re
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_LEVEL_OPTION_IDS = {"UNIT": 1, "INTEGRATION": 2, "E2E": 3, "MANUAL": 4}

# レビュー・同期の対象外（基準書 §1.2 と揃える）
EXCLUDED_FILE_NAMES = {"ExampleUnitTest.kt"}

_CLASS_RE = re.compile(r"^\s*(?:(?:internal|private|open|abstract|sealed)\s+)*class\s+(\w+)", re.M)
_FUN_RE = re.compile(r"\bfun\s+`?([A-Za-z_][\w$]*)`?\s*\(")
_TEST_ANNOTATION_RE = re.compile(r"@Test\b")


def find_test_files(source_root):
    """単体テストの .kt ファイルを列挙する（androidTest は対象外）。"""
    found = []
    for dirpath, dirnames, filenames in os.walk(source_root):
        normalized = dirpath.replace("\\", "/")
        if "/build/" in normalized or "/.git" in normalized:
            dirnames[:] = []
            continue
        if "/src/test/" not in normalized + "/":
            continue
        for name in filenames:
            if name.endswith(".kt") and name not in EXCLUDED_FILE_NAMES:
                found.append(os.path.join(dirpath, name))
    return sorted(found)


def load_level_option_ids(source_root):
    """対象リポジトリの Qase.kt から TestLevel の選択肢IDを読み取る。"""
    for dirpath, dirnames, filenames in os.walk(source_root):
        if "/build/" in dirpath.replace("\\", "/"):
            dirnames[:] = []
            continue
        if "Qase.kt" not in filenames:
            continue
        with open(os.path.join(dirpath, "Qase.kt"), encoding="utf-8") as f:
            text = f.read()
        pairs = re.findall(r"\b(UNIT|INTEGRATION|E2E|MANUAL)\s*\(\s*(\d+)\s*\)", text)
        if pairs:
            return {name: int(value) for name, value in pairs}
    return dict(DEFAULT_LEVEL_OPTION_IDS)


def read_string_literal(text, index):
    """index 位置の文字列リテラルを読み、(値, 次の位置) を返す。"""
    if text.startswith('"""', index):
        end = text.find('"""', index + 3)
        if end == -1:
            raise ValueError("閉じられていない raw 文字列があります")
        return text[index + 3:end], end + 3

    if text[index] != '"':
        raise ValueError("文字列リテラルではありません")

    buffer = []
    position = index + 1
    while position < len(text):
        char = text[position]
        if char == "\\":
            nxt = text[position + 1]
            buffer.append({"n": "\n", "t": "\t", "r": "\r"}.get(nxt, nxt))
            position += 2
            continue
        if char == '"':
            return "".join(buffer), position + 1
        buffer.append(char)
        position += 1
    raise ValueError("閉じられていない文字列があります")


def skip_literals(text, index):
    """文字列リテラルやコメントを飛ばす。飛ばせない場合は None を返す。"""
    if text.startswith('"""', index):
        end = text.find('"""', index + 3)
        return len(text) if end == -1 else end + 3
    if text[index] == '"':
        try:
            _, nxt = read_string_literal(text, index)
            return nxt
        except ValueError:
            return len(text)
    if text.startswith("//", index):
        end = text.find("\n", index)
        return len(text) if end == -1 else end
    if text.startswith("/*", index):
        end = text.find("*/", index + 2)
        return len(text) if end == -1 else end + 2
    return None


def read_balanced(text, open_index, open_char="(", close_char=")"):
    """open_index の括弧に対応する閉じ括弧までの中身と、閉じ括弧の次の位置を返す。"""
    depth = 0
    position = open_index
    while position < len(text):
        skipped = skip_literals(text, position)
        if skipped is not None:
            position = skipped
            continue
        char = text[position]
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return text[open_index + 1:position], position + 1
        position += 1
    raise ValueError("括弧が閉じられていません")


def split_top_level(text, separator=","):
    """括弧・文字列を考慮して、トップレベルの区切り文字で分割する。"""
    parts = []
    depth = 0
    start = 0
    position = 0
    while position < len(text):
        skipped = skip_literals(text, position)
        if skipped is not None:
            position = skipped
            continue
        char = text[position]
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == separator and depth == 0:
            parts.append(text[start:position])
            start = position + 1
        position += 1
    parts.append(text[start:])
    return [part.strip() for part in parts if part.strip()]


def parse_named_args(text):
    """`name = value` の並びを辞書にする。"""
    args = {}
    for part in split_top_level(text):
        match = re.match(r"^(\w+)\s*=\s*(.*)$", part, re.S)
        if match:
            args[match.group(1)] = match.group(2).strip()
    return args


def parse_string_value(raw):
    """値の式から文字列リテラルを取り出す（連結は未対応）。"""
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith('"'):
        value, _ = read_string_literal(raw, 0)
        return value.strip() if raw.startswith('"""') else value
    raise ValueError(f"文字列リテラルとして解釈できません: {raw[:60]}")


def parse_steps(raw):
    """steps = [QaseStep(...), ...] を辞書のリストにする。"""
    raw = raw.strip()
    if not raw.startswith("["):
        return []
    inner, _ = read_balanced(raw, 0, "[", "]")
    steps = []
    for element in split_top_level(inner):
        open_paren = element.find("(")
        if open_paren == -1:
            continue
        args_text, _ = read_balanced(element, open_paren)
        args = parse_named_args(args_text)
        steps.append({
            "action": parse_string_value(args.get("action", '""')),
            "expected": parse_string_value(args.get("expected", '""')),
            "data": parse_string_value(args.get("data", '""')),
        })
    return steps


def enclosing_class(text, position, fallback):
    """position より前にある直近の class 宣言名を返す。"""
    name = fallback
    for match in _CLASS_RE.finditer(text):
        if match.start() > position:
            break
        name = match.group(1)
    return name


def parse_file(path, level_option_ids):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    package_match = re.search(r"^\s*package\s+([\w.]+)", text, re.M)
    package = package_match.group(1) if package_match else ""
    fallback_class = os.path.splitext(os.path.basename(path))[0]

    tests = []
    annotated_positions = []
    errors = []

    for match in re.finditer(r"@Qase\s*\(", text):
        open_paren = text.index("(", match.start())
        try:
            args_text, after = read_balanced(text, open_paren)
            args = parse_named_args(args_text)

            fun_match = _FUN_RE.search(text, after)
            if fun_match is None:
                raise ValueError("@Qase の直後にテスト関数が見つかりません")

            level_name = args.get("level", "TestLevel.UNIT").split(".")[-1].strip()
            if level_name not in level_option_ids:
                raise ValueError(f"未知の TestLevel です: {level_name}")

            steps = parse_steps(args.get("steps", ""))
            class_name = enclosing_class(text, match.start(), fallback_class)

            tests.append({
                "case_id": int(re.sub(r"[^\d]", "", args.get("id", ""))),
                "class": f"{package}.{class_name}" if package else class_name,
                "method": fun_match.group(1),
                "title": parse_string_value(args.get("title", '""')),
                "description": parse_string_value(args.get("description", '""')),
                "level": level_name,
                "level_option_id": level_option_ids[level_name],
                "has_steps": bool(steps),
                "steps": steps,
                "file": path.replace("\\", "/"),
                "line": text.count("\n", 0, match.start()) + 1,
            })
            annotated_positions.append(fun_match.start())
        except (ValueError, KeyError) as e:
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{path}:{line} {e}")

    unannotated = []
    for match in _TEST_ANNOTATION_RE.finditer(text):
        fun_match = _FUN_RE.search(text, match.end())
        if fun_match is None or fun_match.start() in annotated_positions:
            continue
        class_name = enclosing_class(text, match.start(), fallback_class)
        qualified = f"{package}.{class_name}" if package else class_name
        unannotated.append(f"{qualified}#{fun_match.group(1)}")

    return tests, sorted(set(unannotated)), errors


def main():
    parser = argparse.ArgumentParser(description="テストソースから @Qase を抽出する")
    parser.add_argument("--source-root", required=True, help="対象リポジトリのルート")
    parser.add_argument("--out", default="build/qase/qase-cases.json", help="出力先JSON")
    parser.add_argument("--module", default=None, help="対象を特定モジュールに絞る（パスの部分一致）")
    args = parser.parse_args()

    if not os.path.isdir(args.source_root):
        sys.exit(f"❌ ソースルートが見つかりません: {args.source_root}")

    level_option_ids = load_level_option_ids(args.source_root)
    print(f"🔍 TestLevel の選択肢ID: {level_option_ids}")

    files = find_test_files(args.source_root)
    if args.module:
        needle = args.module.replace("\\", "/")
        files = [f for f in files if needle in f.replace("\\", "/")]
    print(f"🔍 対象ファイル: {len(files)} 件\n")

    all_tests = []
    all_unannotated = []
    all_errors = []
    for path in files:
        tests, unannotated, errors = parse_file(path, level_option_ids)
        all_tests.extend(tests)
        all_unannotated.extend(unannotated)
        all_errors.extend(errors)

    if all_errors:
        print("❌ 解析できなかった @Qase があります:")
        for error in all_errors:
            print(f"   ├─ {error}")
        print("\n   記述を修正してから再実行してください（docs/qase_annotation_rules.md 参照）。")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(
            {"tests": all_tests, "unannotated": sorted(set(all_unannotated))},
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"✅ @Qase 付与済み : {len(all_tests)} 件")
    print(f"⚠️  @Qase 未付与   : {len(set(all_unannotated))} 件")
    print(f"📄 出力先         : {args.out}")


if __name__ == "__main__":
    main()
