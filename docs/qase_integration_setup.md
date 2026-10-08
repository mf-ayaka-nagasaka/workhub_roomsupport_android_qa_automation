# Qase連携セットアップ手順（gateaccess-android 向け）

| 項目 | 内容 |
|---|---|
| **象限** | 🛠️ ハウツー |
| **対象者** | 開発チーム（配置・CI設定・以降の保守の担当者）、QA担当 |
| **ゴール** | 本番リポジトリに `@Qase` アノテーションの基盤と連携スクリプトを配置し、テスト実行をトリガーに実行結果・カバレッジがQaseへ自動記録される状態になります |

本書は **gateaccess-android** に Qase連携を導入する手順です。検証用リポジトリ（RSAcoveragetesting）向けの手順書とは**前提条件が異なります**。本番リポジトリへの導入では本書に従ってください。

---

## 0. この依頼でお願いすること

開発チームへの依頼は、次の3点です。

| # | お願いしたいこと | 該当節 |
|---|---|---|
| 1 | `Qase.kt`（アノテーション型定義）と連携スクリプト3本の配置 | 3.1 / 3.2 / 3.3 |
| 2 | テストCIへの結果送信ステップの追加と、Secretsへのトークン登録 | 3.4 / 5 |
| 3 | **配置以降のスクリプト保守の引き取り** | 1 |

> 3について補足します。このスクリプトが動かなくなる原因は、Gradleタスク名の変更・モジュールの追加・出力パスの変更など、**いずれも本体リポジトリ側の変更**です。壊れたことに気づけるのも直せるのもCIを運用する開発チームであるため、配置以降の保守は本体リポジトリ側でお願いしたいと考えています。Qase側のケース定義・カスタムフィールド設計・`@Qase` の付与はQAが引き続き担当し、仕様変更が必要なときはQAから依頼します。

---

## 1. 責務分担

| 作業 | 担当 | 頻度 |
|---|---|---|
| `Qase.kt`（アノテーション型定義）の配置 | **開発チーム** | 初回のみ |
| 各モジュールへの依存追加 | **開発チーム** | 初回のみ |
| 連携スクリプト3本の `tools/qase/` への配置 | **開発チーム** | 初回のみ |
| CIへの結果送信ステップの追加・調整 | **開発チーム** | 随時 |
| 連携スクリプトの保守 | **開発チーム** | 随時 |
| テストコードへの `@Qase` 追記 | **QA担当** | PRごと |
| Qaseへのケース同期（`qase_sync.py`） | **QA担当** | 随時 |
| Qase側のフィールド設計・`@Qase` 付与ルールの策定 | **QA担当** | 随時 |
| 実行結果・カバレッジの送信 | **CI（自動）** | テスト実行ごと |

> **結果送信は実行者＝開発チーム側に寄せます。** テストを実行するのがCIである以上、送信もCIで完結させるのが自然で、QAが手元で送信する運用は再送・リカバリ時のみとします。
>
> QAが担当するのは、Qase側のケース定義（何をどう記録するか）と `@Qase` の付与です。スクリプトの初版はQAが用意しますが、**配置後の保守は本体リポジトリ側に移管**します。

---

## 2. 前提条件と、検証環境との違い

### 2.1 本番リポジトリの構成

| 項目 | 内容 |
|---|---|
| テストフレームワーク | **JUnit 4**（`kotlin.test` 経由。JUnit 5 は未導入） |
| モジュール構成 | マルチモジュール。単体テストを持つモジュールは **9つ** |
| テスト実行タスク | `./gradlew testDevelopDebugUnitTest` |
| カバレッジ | JaCoCo。規約プラグイン（`gateaccess.library.jacoco` 等）で設定済み |
| カバレッジタスク | `createDevelopDebugCombinedCoverageReport`（モジュール単位） |

### 2.2 検証環境の手順をそのまま使えない理由

検証環境の手順書は **JUnit 5 + 単一JVMモジュール**を前提としています。本番リポジトリは JUnit 4 のため、次の2ファイルは**配置しても動作しません。**

| 配置しないファイル | 理由 |
|---|---|
| `QaseResultCollector.kt` | JUnit Platform の `TestExecutionListener`。JUnit 4 では起動しません |
| `META-INF/services/org.junit.platform.launcher.TestExecutionListener` | 上記リスナーの起動スイッチ。同上 |

> ⚠️ **これらは配置してもエラーが出ません。** 黙って動かないため、「導入できたつもり」になるのが最も危険です。配置しないでください。

### 2.3 リスナーの代わりに何を使うか

リスナーが必要だったのは「JUnit の XML にアノテーションの値が入らない」ためでした。本番リポジトリでは、次の2つを突き合わせることで同じ情報を得ます。

```
テストソースの静的パース   →  class#method → case_id / title / level / steps の対応表
JUnit XML（TEST-*.xml）   →  class#method → 実行結果（passed / failed / skipped）
                 ↓ 突き合わせ
          case_id + 定義内容 + 実行結果
```

この方式により、**JUnit 5 への移行もJUnit 4 用リスナーの実装も不要**になります。突き合わせを行うスクリプトはQAが用意し、本体リポジトリの `tools/qase/` へ配置します（3.3）。

---

## 3. 導入手順（開発チーム作業）

### 3.1 `Qase.kt` の配置

> ✅ **配置済み（2026-10-08 確認）。** 以下は実際の配置内容です。新規作業は不要です。

次のファイルが追加されています。

**配置先**: `shared/testing/src/main/java/jp/bitkey/app/gateaccess/shared/testing/qase/Qase.kt`

```kotlin
package jp.bitkey.app.gateaccess.shared.testing.qase

/**
 * Qase のテストケースと自動テストを紐づけるアノテーション。
 *
 * [id] は Qase が採番したケースID。Qase側でケースを作成してから転記すること
 * （Qase はケース作成時にIDを指定できないため、この転記だけは手作業になる）。
 *
 * [title] / [level] / [description] / [steps] はコード側を正本とし、
 * QA側の同期スクリプトで Qase 側へ上書き同期される。
 * スイート配置と自動化状態は同期対象外（前者は Qase UI 管理、後者は常に Automated）。
 */
@Target(AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class Qase(
    val id: Long,
    val title: String,
    val level: TestLevel = TestLevel.UNIT,
    val description: String = "",
    /** 省略時は Qase 側のステップを変更しない（空で上書きしない）。 */
    val steps: Array<QaseStep> = [],
)

/** Arrange/Act を [action]、Assert を [expected] に対応させる。 */
@Retention(AnnotationRetention.RUNTIME)
annotation class QaseStep(
    val action: String,
    val expected: String = "",
    val data: String = "",
)

/** Qase カスタムフィールド "Test Level" の選択肢。[optionId] は Qase 側の選択肢ID。 */
enum class TestLevel(val optionId: Int) {
    UNIT(1),
    INTEGRATION(2),
    E2E(3),
    MANUAL(4),
}
```

> **配置先について**: 当初は `core/testing` への配置を提案していましたが、開発チームの判断で **`shared/testing`** へ配置されました。本書の記載は実際の配置に合わせています。

### 3.2 各モジュールへの依存追加

単体テストを持つモジュールから `Qase.kt` を参照できるようにします。

```kotlin
dependencies {
    testImplementation(projects.shared.testing)
}
```

**対象モジュール**（調査時点）:

| モジュール | 状況 |
|---|---|
| `core/data` | ✅ 依存済み（対応不要） |
| `camera-app` | ❌ 追加が必要 |
| `core/camera` | ❌ 追加が必要 |
| `core/common` | ❌ 追加が必要 |
| `FaceMe/lib` | ❌ 追加が必要 |
| `feature/admin` | ❌ 追加が必要 |
| `feature/camera` | ❌ 追加が必要 |
| `feature/setting` | ❌ 追加が必要 |
| `plugin-system` | ❌ 追加が必要 |

> すべてのモジュールに一度に追加する必要はありません。**`@Qase` を付与するモジュールから順次**で構いません。

### 3.3 連携スクリプトの配置

QAから提供する次の3本を配置します。**Python 3 の標準ライブラリのみで動作し、追加の依存はありません。**

**配置先**: `tools/qase/`

| ファイル | 役割 | 入力 | 出力 |
|---|---|---|---|
| `qase_common.py` | 設定値の読み込みとQase APIの呼び出し（共通部品） | 環境変数 | — |
| `extract_qase_annotations.py` | テストソースを静的パースし、`@Qase` の定義を抽出 | テストソース（`--source-root`） | 対応表JSON（`class#method` → `case_id` / title / level / steps） |
| `send_qase_results.py` | 対応表とテスト結果を突合し、QaseにRunを作成して送信 | 対応表JSON／`TEST-*.xml`／JaCoCo XML | Qase上のTest Run（実行結果＋カバレッジ率） |

> **静的パースを採用している理由**は 2.3 のとおりです。テストを実行せずにソースだけを読むため、ビルド構成には影響しません。
>
> ケース同期用の `qase_sync.py` は**配置しません。** Qaseへのケース登録はQA側リポジトリから実行します。

### 3.4 CIでの結果送信

テスト実行をトリガーに、結果とカバレッジをQaseへ自動送信します。

**対象ワークフロー**: `.github/workflows/test.yml`

```yaml
      - name: Run unit test
        run: ./gradlew testDevelopDebugUnitTest

      # ↓ 追記
      - name: Generate coverage report
        if: always()
        run: ./gradlew createDevelopDebugCombinedCoverageReport

      - name: Send results to Qase
        if: always()
        continue-on-error: true
        env:
          QASE_API_TOKEN: ${{ secrets.QASE_API_TOKEN }}
          QASE_PROJECT_CODE: RSA
        run: |
          python tools/qase/extract_qase_annotations.py --source-root . --out build/qase/qase-cases.json
          python tools/qase/send_qase_results.py \
            --input build/qase/qase-cases.json \
            --test-results . --jacoco . \
            --title "CI #${{ github.run_number }} (${{ github.ref_name }})"

      - name: Upload test results and coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-and-coverage
          path: |
            **/build/test-results/testDevelopDebugUnitTest/TEST-*.xml
            **/build/reports/jacoco/createDevelopDebugCombinedCoverageReport/*.xml
          retention-days: 14
```

> `if: always()` を付けるのは、**テストが失敗した場合も結果を記録する**ためです。失敗した結果もQaseに残します。
>
> `continue-on-error: true` は、テスト失敗があるとスクリプトが**「送信した上で」終了コード1を返す**ためです。送信の成否とCIの合否判定を切り離します。
>
> artifactのアップロードは送信が失敗したときの調査用に残します。QA側で再送する際の入力にもなります。
>
> カバレッジXMLはモジュール単位で出力されます。集約レポートは不要です。スクリプトが全モジュール分を合算します。
>
> `QASE_PROJECT_CODE` はスクリプト側の既定値も `RSA` ですが、**書き込み先が差分に現れるよう明示します。** フィールドID（`QASE_TEST_LEVEL_FIELD_ID` / `QASE_COVERAGE_FIELD_ID`）は確認済みの値が既定値に入っているため、指定不要です（4章）。
>
> スクリプトには、`RSA` 以外への書き込みを中断する**プロジェクトコードのガード**が入っています。対象を増やす場合は `QASE_ALLOWED_PROJECT_CODES` にカンマ区切りで追加してください。

### 3.5 コンパイル確認

依存を追加したモジュールで、テストコードがコンパイルできることを確認します。

```bash
./gradlew :core:data:compileDevelopDebugUnitTestKotlin
```

---

## 4. Qase側の準備（QA担当作業）

カスタムフィールドは**作成済みです**（2026-10-02 時点でAPIで確認）。新規に用意する作業はありません。

| 種別 | 名称 | フィールドID | 設定 |
|---|---|---|---|
| ケースのカスタムフィールド | `Test Level` | **50** | selectbox。選択肢ID `1=Unit` / `2=Integration` / `3=E2E` / `4=Manual` |
| Runのカスタムフィールド | `Coverage Rate` | **49** | number |

| 設定値 | 値 |
|---|---|
| `QASE_PROJECT_CODE` | `RSA`（workhub Room Support_Android） |
| `QASE_TEST_LEVEL_FIELD_ID` | `50` |
| `QASE_COVERAGE_FIELD_ID` | `49` |

上記はいずれも `qase_common.py` の既定値と一致しており、`Qase.kt` の `TestLevel` の `optionId`（1〜4）とも一致しています。**設定変更は不要です。**

> ⚠️ **フィールド50・49は `RSA` プロジェクト限定のスコープです**（`projects_codes: ["RSA"]`）。将来ケースを `ROOM`（workhub Room Support）など別プロジェクトへ移す場合は、**Qase側でフィールドのスコープにそのプロジェクトを追加する必要があります。** 忘れると7章のとおり「APIは200を返すが値は黙って無視される」状態になります。

値を再確認したい場合は次のAPIで取得できます。

```bash
curl -H "Token: $QASE_API_TOKEN" "https://api.qase.io/v1/custom_field?limit=100"
```

---

## 5. APIトークンの設定

**トークンはソースコードに書かないでください。** 環境変数 `QASE_API_TOKEN` から読み込みます。

```powershell
# ローカル（設定後、ターミナルやIDEの再起動が必要）
setx QASE_API_TOKEN "<your token>"
```

**本番リポジトリの Secrets に `QASE_API_TOKEN` を登録してください。** 3.4 の送信ステップが参照します。トークンは**CI専用のQaseアカウント**で発行したものを、QAから安全な経路でお渡しします。開発チームにお願いするのは **Secrets への登録のみ**で、発行・失効・ローテーションはQAが管理します。

> **なぜCI専用アカウントなのか**: QaseのAPIトークンは発行したユーザーの権限をそのまま引き継ぎ、トークン単位でプロジェクトを絞ることができません。個人のトークンを使うと全プロジェクトへの書き込み権限をCIに渡すことになるため、**アクセス範囲を `RSA` のみに限定した専用アカウント**を用意します。あわせてスクリプト側にもプロジェクトコードのガードを入れています（3.4）。
>
> ⚠️ **Secretsへの登録値は、チャンネルやチケットのコメントに貼らないでください。** 共有ボールト等の安全な経路でお渡しします。

`QASE_PROJECT_CODE` はワークフローに直接記載します（秘匿情報ではありません）。その他の設定値は4章のとおり既定値のままで動作します。

---

## 6. 動作確認

| # | 確認内容 | 方法 |
|---|---|---|
| 1 | `@Qase` がコンパイルできる | テストに1つ付与して `./gradlew :{module}:compileDevelopDebugUnitTestKotlin` |
| 2 | 静的パースで対応表が作れる | `python tools/qase/extract_qase_annotations.py --source-root .` を実行し、`class#method → case_id` が出力されるか |
| 3 | CIの成果物が取得できる | Actionsの実行結果から artifact をダウンロードし、`TEST-*.xml` と jacoco XML が含まれるか |
| 4 | CIから結果が送信される | 送信ステップのログに突合件数とカバレッジ率が出力され、Qase上にRunが作成されるか |
| 5 | Qaseに反映される | 同期・送信後、API または Qase UI で読み取って確認 |

### 反映確認（重要）

**Qase API は無視したフィールドについてエラーを返しません。** 必ず読み取りで確認してください。

```bash
curl -H "Token: $QASE_API_TOKEN" "https://api.qase.io/v1/case/<CODE>/<ID>"
curl -H "Token: $QASE_API_TOKEN" "https://api.qase.io/v1/run/<CODE>/<RUN_ID>"
```

| 対象 | 確認内容 |
|---|---|
| ケース | `title` / `description` が反映されているか |
| ケース | `custom_fields` に Test Level の値が入っているか |
| ケース | `automation` が `2`（Automated）か |
| ケース | `suite_id` が**変わっていない**か |
| Run | `custom_fields` に Coverage Rate が入っているか |

---

## 7. Qase API の注意点

実装時に踏みやすい落とし穴です。検証環境で実際に発生したものを含みます。

| 項目 | 内容 |
|---|---|
| カスタムフィールドのキー名 | **`custom_field`（単数形）**。`custom_fields`（複数形）を送ると **APIは200を返すが値は黙って無視される** |
| ステップの期待値のキー名 | **`expected_result`**（`expected` ではない） |
| カスタムフィールドの値 | **選択肢IDを文字列**で渡す（例: `{"50": "1"}`）。表示名ではない |
| 書き込み後 | **必ず読み取りで反映を確認する。** 無視されたフィールドのエラーは返らない |
| ケースの一覧取得 | `limit=100` が上限。ケース数が多い場合はページングが必要 |
| 同期の方向 | **コード → Qase の一方向。** Qase UI 上での編集は次回同期で上書きされる |

---

## 8. トラブルシューティング

| 症状 | 原因 |
|---|---|
| `Unresolved reference: Qase` | import文の誤り、または対象モジュールに `testImplementation(projects.shared.testing)` が未追加 |
| 型の不一致（`id`） | `id` は `Long`。整数リテラルで記述する |
| カバレッジXMLが生成されない | `createDevelopDebugCombinedCoverageReport` が実行されていない |
| テスト失敗時に artifact が無い | `if: always()` が付いていない |
| カスタムフィールドが反映されない | キー名が `custom_fields`（複数形）になっている |
| ステップの期待値が入らない | キー名が `expected` になっている（正: `expected_result`） |
| 日本語・絵文字が文字化けする | Windowsコンソールのcp932。スクリプト側でUTF-8に再設定する |
| `QASE_API_TOKEN が設定されていません` | ローカルは `setx` 後にターミナル/IDEを再起動していない。CIは Secrets が未登録、または `env:` への受け渡し漏れ |
| テスト失敗時にCIが送信ステップで止まる | 送信ステップに `continue-on-error: true` が付いていない（終了コード1は仕様。結果は送信済み） |
| CIの送信だけが失敗した | artifact をダウンロードし、QA側から再送する（`docs/qase_sync_operation.md` 参照） |

---

## 9. 検証環境との対応

検証用リポジトリ（RSAcoveragetesting）のファイルとの対応です。本番で使わないものも記録として残します。

| 検証環境のファイル | 本番での扱い |
|---|---|
| `template/kotlin/Qase.kt` | ✅ パッケージを変更して配置 |
| `template/kotlin/QaseResultCollector.kt` | ❌ **配置しない**（JUnit 4 では動作しない） |
| `template/resources/...TestExecutionListener` | ❌ **配置しない**（同上） |
| `template/python/qase_common.py` | ✅ 本体リポジトリ `tools/qase/` へ配置。設定値は環境変数から読み込み |
| `template/python/qase_sync.py` | ⚠️ QA側リポジトリで管理（ケース同期はQA主導のため配置しない） |
| `template/python/send_coverage.py` | ✅ `send_qase_results.py` として本体リポジトリ `tools/qase/` へ配置。複数モジュールのXML合算に対応 |
| `template/build.gradle.kts.snippet` | ❌ 不要（JaCoCoは規約プラグイン済み、スクリプトはCIから直接実行） |
| （新規）`extract_qase_annotations.py` | ✅ 本体リポジトリ `tools/qase/` へ配置。JUnit 4 対応のため新設 |

---

## 10. 移管後のQAリポジトリの扱い

配置が完了し、CIからの送信が確認できた時点で、**QA側リポジトリの同一スクリプトは削除します。** 正本を2箇所に置くと、どちらを直せばよいか分からなくなるためです。

| 対象 | 移管後の扱い |
|---|---|
| `scripts/qase_common.py` | 削除（正本は本体リポジトリ `tools/qase/`）※ |
| `scripts/extract_qase_annotations.py` | 削除（同上） |
| `scripts/send_qase_results.py` | 削除（同上） |
| `/qase-sync` スキルの `results` モード | 削除（CIが自動送信するため不要） |
| `scripts/qase_sync.py` | **残す**（ケース同期はQA主導） |

> ※ `qase_sync.py` が `qase_common.py` を参照しているため、共通部品はQA側にも必要な分だけ残します。削除範囲は移管時にあらためて確認します。

移管が完了するまでは、QA側から手元で送信する運用（`/qase-sync results`）を暫定手段として残します。
