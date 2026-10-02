"""Qase 連携スクリプトの共通処理（設定値・API 呼び出し・事前検証）。

検証用リポジトリ（RSAcoveragetesting）の qase_common.py を本番リポジトリ向けに改修したもの。
主な変更点:
  - 設定値を環境変数で与えられるようにした（本番 Qase プロジェクトのID差異に対応）
  - 入力 JSON をリスナー出力ではなく静的パース結果（extract_qase_annotations.py）に変更
  - ケース一覧取得をページング対応にした（limit=100 の上限を超えるため）
"""

import json
import os
import sys
import urllib.error
import urllib.request

# Windows のコンソール既定 (cp932) だと絵文字や日本語が化けるため UTF-8 に固定する
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

# トークンは環境変数から取得する。ソースには絶対に書かないこと。
#   PowerShell: $env:QASE_API_TOKEN = "xxxxx"
QASE_API_TOKEN = os.environ.get("QASE_API_TOKEN")

# 本番 Qase プロジェクトの設定値。いずれも環境変数で上書きできる。
#   フィールドIDは次で確認する:
#     curl -H "Token: $QASE_API_TOKEN" "https://api.qase.io/v1/custom_field?limit=100"
QASE_PROJECT_CODE = os.environ.get("QASE_PROJECT_CODE", "RSA")
TEST_LEVEL_FIELD_ID = os.environ.get("QASE_TEST_LEVEL_FIELD_ID", "50")
COVERAGE_FIELD_ID = os.environ.get("QASE_COVERAGE_FIELD_ID", "49")

AUTOMATION_AUTOMATED = 2  # 0=Manual / 1=To be automated / 2=Automated

_BASE = "https://api.qase.io/v1"


def require_token():
    if not QASE_API_TOKEN:
        sys.exit(
            "❌ 環境変数 QASE_API_TOKEN が設定されていません。\n"
            '   PowerShell: $env:QASE_API_TOKEN = "<your token>"'
        )


def api(method, path, payload=None):
    """Qase API を呼ぶ。成功時は result 部分、404 は None、それ以外は例外。"""
    request = urllib.request.Request(
        f"{_BASE}{path}",
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={"Token": QASE_API_TOKEN, "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8")).get("result")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise RuntimeError(
            f"{method} {path} -> {e.code} {e.reason}: {e.read().decode()[:300]}"
        ) from None


def load_cases(path):
    """extract_qase_annotations.py が出力した JSON を読み込む。"""
    if not os.path.exists(path):
        sys.exit(
            f"❌ {path} がありません。\n"
            "   先に extract_qase_annotations.py を実行してください。"
        )
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("tests", []), data.get("unannotated", [])


def warn_unannotated(unannotated):
    if unannotated:
        print(f"⚠️  @Qase 未付与のテストが {len(unannotated)} 件あります（送信対象外）:")
        for name in unannotated[:20]:
            print(f"   ├─ {name}")
        if len(unannotated) > 20:
            print(f"   └─ ほか {len(unannotated) - 20} 件")
        print()


def check_duplicate_ids(tests):
    """複数テストが同じ caseID を指していないか検証する。"""
    seen = {}
    duplicates = {}
    for test in tests:
        case_id = test["case_id"]
        owner = f"{test['class']}#{test['method']}"
        if case_id in seen:
            duplicates.setdefault(case_id, [seen[case_id]]).append(owner)
        else:
            seen[case_id] = owner
    if duplicates:
        print("❌ ケースIDが重複しています:")
        for case_id, owners in duplicates.items():
            print(f"   ├─ case {case_id}: {', '.join(owners)}")
        sys.exit(1)


def check_cases_exist(tests):
    """全 caseID が Qase 上に存在するか事前検証する。1件でも欠けていれば中断。"""
    missing = []
    for test in tests:
        if api("GET", f"/case/{QASE_PROJECT_CODE}/{test['case_id']}") is None:
            missing.append(f"case {test['case_id']} ({test['class']}#{test['method']})")
    if missing:
        print("❌ Qase 上に存在しないケースIDが指定されています:")
        for item in missing:
            print(f"   ├─ {item}")
        print("\n   Qase UI でケースを作成し、採番されたIDを @Qase(id = ...) に転記してください。")
        sys.exit(1)


def fetch_all_cases():
    """プロジェクトの全ケースをページングして取得する。"""
    cases = []
    offset = 0
    limit = 100
    while True:
        result = api("GET", f"/case/{QASE_PROJECT_CODE}?limit={limit}&offset={offset}") or {}
        entities = result.get("entities", [])
        cases.extend(entities)
        total = result.get("total", len(cases))
        offset += limit
        if offset >= total or not entities:
            break
    return cases
