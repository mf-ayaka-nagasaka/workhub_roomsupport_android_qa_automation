"""テスト実行結果とカバレッジを Qase へ送信する。

検証用リポジトリでは JUnit5 リスナーが実行結果を JSON に書き出していたが、本番リポジトリは
JUnit4 のためリスナーが使えない。代わりに次の2つを突き合わせる。

    extract_qase_annotations.py の出力  →  class#method → case_id
    JUnit の TEST-*.xml                →  class#method → 実行結果

使い方:
    python scripts/send_qase_results.py \
        --input build/qase/qase-cases.json \
        --test-results <TEST-*.xml があるディレクトリ> \
        --jacoco <JaCoCo XML があるディレクトリ>

    --dry-run を付けると Qase へ送信せず集計のみ行う。
"""

import argparse
import glob
import os
import sys
import xml.etree.ElementTree as ET

from qase_common import (
    COVERAGE_FIELD_ID,
    QASE_PROJECT_CODE,
    api,
    check_cases_exist,
    check_duplicate_ids,
    load_cases,
    require_token,
    warn_unannotated,
)


def collect_junit_results(results_dir):
    """TEST-*.xml を読み、"<class>#<method>" -> (status, time_ms) の辞書を作る。"""
    results = {}
    pattern = os.path.join(results_dir, "**", "TEST-*.xml")
    files = glob.glob(pattern, recursive=True)
    if not files:
        sys.exit(f"❌ {results_dir} 配下に TEST-*.xml が見つかりません。")

    for path in files:
        for testcase in ET.parse(path).getroot().iter("testcase"):
            class_name = testcase.attrib.get("classname", "")
            method = testcase.attrib.get("name", "")
            if testcase.find("failure") is not None or testcase.find("error") is not None:
                status = "failed"
            elif testcase.find("skipped") is not None:
                status = "skipped"
            else:
                status = "passed"
            time_ms = int(float(testcase.attrib.get("time", "0")) * 1000)
            results[f"{class_name}#{method}"] = (status, time_ms)
    return results, len(files)


def calculate_coverage(jacoco_dir):
    """JaCoCo XML の命令網羅率を全モジュール分合算して算出する。

    各XMLの <report> 直下の counter のみを使う。配下の package / class にも同じ
    counter があるため、全階層を拾うと二重計上になる。
    """
    files = glob.glob(os.path.join(jacoco_dir, "**", "*.xml"), recursive=True)
    covered = 0
    missed = 0
    used = 0
    for path in files:
        root = ET.parse(path).getroot()
        if root.tag != "report":
            continue
        counters = root.findall("counter[@type='INSTRUCTION']")
        if not counters:
            continue
        used += 1
        for counter in counters:
            missed += int(counter.attrib["missed"])
            covered += int(counter.attrib["covered"])

    total = missed + covered
    rate = round((covered / total) * 100, 2) if total > 0 else 0.0
    return rate, used


def main():
    parser = argparse.ArgumentParser(description="テスト結果とカバレッジを Qase へ送信する")
    parser.add_argument("--input", default="build/qase/qase-cases.json")
    parser.add_argument("--test-results", required=True, help="TEST-*.xml があるディレクトリ")
    parser.add_argument("--jacoco", default=None, help="JaCoCo XML があるディレクトリ")
    parser.add_argument("--title", default=None, help="Test Run のタイトル")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    require_token()

    # ==========================================================================
    # 1. ケース定義の読み込みと事前検証
    # ==========================================================================
    print("🔍 [1/4] ケース定義を読み込み、事前検証中...")
    tests, unannotated = load_cases(args.input)
    warn_unannotated(unannotated)

    if not tests:
        sys.exit("❌ @Qase が付いたテストが1件もありません。")

    # 中途半端な Run を残さないよう、送信前に全て検証しておく
    check_duplicate_ids(tests)
    if not args.dry_run:
        check_cases_exist(tests)
    print(f"   └─ ✅ 検証OK (対象 {len(tests)} 件)\n")

    # ==========================================================================
    # 2. 実行結果の突き合わせ
    # ==========================================================================
    print("🔗 [2/4] JUnit の実行結果と突き合わせ中...")
    junit_results, xml_count = collect_junit_results(args.test_results)

    matched = []
    unmatched = []
    for test in tests:
        key = f"{test['class']}#{test['method']}"
        if key in junit_results:
            status, time_ms = junit_results[key]
            matched.append({**test, "status": status, "duration_ms": time_ms})
        else:
            unmatched.append(key)

    print(f"   ├─ TEST-*.xml: {xml_count}件 / 実行済みテスト {len(junit_results)}件")
    print(f"   └─ 突合成功: {len(matched)}件 / 未実行: {len(unmatched)}件")
    if unmatched:
        print("\n⚠️  実行結果が見つからなかったケース（送信対象外）:")
        for key in unmatched[:20]:
            print(f"   ├─ {key}")
        if len(unmatched) > 20:
            print(f"   └─ ほか {len(unmatched) - 20} 件")
    if not matched:
        sys.exit("\n❌ 送信できる結果が1件もありません。テストが実行されているか確認してください。")
    print()

    # ==========================================================================
    # 3. カバレッジの算出
    # ==========================================================================
    coverage_rate = None
    if args.jacoco:
        print("📊 [3/4] JaCoCoレポートを解析中...")
        coverage_rate, report_count = calculate_coverage(args.jacoco)
        print(f"   └─ {report_count}モジュール分を合算: {coverage_rate}%\n")
    else:
        print("📊 [3/4] --jacoco 未指定のためカバレッジは送信しません\n")

    if args.dry_run:
        passed = sum(1 for t in matched if t["status"] == "passed")
        failed = sum(1 for t in matched if t["status"] == "failed")
        skipped = sum(1 for t in matched if t["status"] == "skipped")
        print("🧪 dry-run のため Qase へは送信していません。")
        print(f"   送信予定: {len(matched)}件（passed {passed} / failed {failed} / skipped {skipped}）")
        if coverage_rate is not None:
            print(f"   カバレッジ: {coverage_rate}%")
        return

    # ==========================================================================
    # 4. Run の作成と結果送信
    # ==========================================================================
    print("🚀 [4/4] Test Run を作成し、結果を送信中...")
    title = args.title or "Automated Test & Coverage Run"
    if coverage_rate is not None:
        title = f"{title} ({coverage_rate}%)"

    payload = {"title": title, "cases": [t["case_id"] for t in matched]}
    if coverage_rate is not None:
        payload["custom_field"] = {COVERAGE_FIELD_ID: str(coverage_rate)}

    run = api("POST", f"/run/{QASE_PROJECT_CODE}", payload)
    run_id = run["id"]
    print(f"   ├─ ✅ Run 作成 (Run ID: {run_id})")

    for test in matched:
        api("POST", f"/result/{QASE_PROJECT_CODE}/{run_id}", {
            "case_id": test["case_id"],
            "status": test["status"],
            "time_ms": test["duration_ms"],
        })
        icon = {"passed": "🟢", "failed": "🔴", "skipped": "⚪"}[test["status"]]
        print(f"   ├─ {icon} case {test['case_id']}: {test['title']} -> {test['status'].upper()}")

    failed_count = sum(1 for t in matched if t["status"] == "failed")
    print(f"\n🎉 送信完了! 計 {len(matched)} 件（失敗 {failed_count} 件）")
    print("   反映確認: curl -H \"Token: $QASE_API_TOKEN\" "
          f"\"https://api.qase.io/v1/run/{QASE_PROJECT_CODE}/{run_id}\"")

    # 結果は送りきったうえで、CI の成否判定は維持する
    if failed_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
