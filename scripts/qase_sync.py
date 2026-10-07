"""テストコード側の @Qase を正本として、Qase のケース内容を上書き同期する。

同期する項目   : タイトル / 説明 / Test Level / 自動化状態(Automated) / ステップ
同期しない項目 : スイート配置（Qase UI 管理）

使い方:
    python scripts/qase_sync.py --input build/qase/qase-cases.json
    python scripts/qase_sync.py --input build/qase/qase-cases.json --dry-run
"""

import argparse
import sys

from qase_common import (
    AUTOMATION_AUTOMATED,
    QASE_PROJECT_CODE,
    TEST_LEVEL_FIELD_ID,
    api,
    check_cases_exist,
    check_duplicate_ids,
    fetch_all_cases,
    load_cases,
    require_allowed_project,
    require_token,
    warn_unannotated,
)


def build_payload(test):
    payload = {
        "title": test["title"],
        "automation": AUTOMATION_AUTOMATED,
        # キー名は custom_field (単数形)。複数形だと Qase 側で黙って無視される
        "custom_field": {TEST_LEVEL_FIELD_ID: str(test["level_option_id"])},
    }
    if test["description"]:
        payload["description"] = test["description"]

    # steps 省略時は Qase 側のステップに触れない（空で消さないため）
    if test["has_steps"]:
        payload["steps"] = [
            {
                "position": position,
                "action": step["action"],
                # キー名は expected_result。expected では反映されない
                "expected_result": step["expected"],
                "data": step["data"],
            }
            for position, step in enumerate(test["steps"], start=1)
        ]
    return payload


def main():
    parser = argparse.ArgumentParser(description="@Qase の内容を Qase へ同期する")
    parser.add_argument("--input", default="build/qase/qase-cases.json")
    parser.add_argument("--dry-run", action="store_true", help="送信せず内容のみ表示する")
    args = parser.parse_args()

    require_token()
    require_allowed_project()

    tests, unannotated = load_cases(args.input)
    warn_unannotated(unannotated)

    if not tests:
        sys.exit("❌ @Qase が付いたテストが1件もありません。")

    print(f"🔍 [1/2] 事前検証中... (対象 {len(tests)} 件)")
    check_duplicate_ids(tests)
    if not args.dry_run:
        check_cases_exist(tests)
    print("   └─ ✅ ケースIDの重複なし / 全て Qase 上に存在\n")

    label = "（dry-run）" if args.dry_run else ""
    print(f"🔄 [2/2] ケース内容を Qase へ同期中...{label}")
    for test in tests:
        payload = build_payload(test)
        if not args.dry_run:
            api("PATCH", f"/case/{QASE_PROJECT_CODE}/{test['case_id']}", payload)
        steps_note = f", steps {len(test['steps'])}件" if test["has_steps"] else ""
        print(f"   ├─ ✅ case {test['case_id']}: {test['title']} [{test['level']}{steps_note}]")

    if args.dry_run:
        print("\n🧪 dry-run のため、Qase へは送信していません。")
        return

    # コードに対応するテストが無い自動化ケースを孤児候補として報告する（削除はしない）
    code_ids = {test["case_id"] for test in tests}
    orphans = [
        case for case in fetch_all_cases()
        if case["id"] not in code_ids and case.get("automation") == AUTOMATION_AUTOMATED
    ]
    if orphans:
        print(f"\n⚠️  コードに対応するテストが無い自動化ケースが {len(orphans)} 件あります（自動削除はしません）:")
        for case in orphans:
            print(f"   ├─ case {case['id']}: {case['title']}")
        print("   └─ 不要であれば Qase UI で削除してください。")

    print(f"\n🎉 同期完了! 計 {len(tests)} 件のケースを更新しました。")
    print("   反映確認: curl -H \"Token: $QASE_API_TOKEN\" "
          f"\"https://api.qase.io/v1/case/{QASE_PROJECT_CODE}/<ID>\"")


if __name__ == "__main__":
    main()
