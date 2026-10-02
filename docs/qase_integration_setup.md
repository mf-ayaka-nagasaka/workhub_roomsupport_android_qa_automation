# Qase連携セットアップ手順（workhubRoomSupport-Android 向け）

| 項目 | 内容 |
|---|---|
| **象限** | 🛠️ ハウツー |
| **対象者** | 開発チーム（配置作業の担当者）、QA担当 |
| **ゴール** | 本番リポジトリに `@Qase` アノテーションの基盤を導入し、テストケースの同期と実行結果・カバレッジの連携ができる状態になります |

本書は **workhubRoomSupport-Android** に Qase連携を導入する手順です。検証用リポジトリ（RSAcoveragetesting）向けの手順書とは**前提条件が異なります**。本番リポジトリへの導入では本書に従ってください。

---

## 1. 責務分担

| 作業 | 担当 | 頻度 |
|---|---|---|
| `Qase.kt`（アノテーション型定義）の配置 | **開発チーム** | 初回のみ |
| 各モジュールへの依存追加 | **開発チーム** | 初回のみ |
| CIでの成果物（テスト結果XML・カバレッジXML）出力 | **開発チーム** | 初回のみ |
| テストコードへの `@Qase` 追記 | **QA担当** | PRごと |
| Qaseへのケース同期・結果送信 | **QA担当** | 随時 |

> 開発チームにお願いするのは**初回の配置作業のみ**です。日常の運用はQA側で行います。

---

## 2. 前提条件と、検証環境との違い

### 2.1 本番リポジトリの構成

| 項目 | 内容 |
|---|---|
| テストフレームワーク | **JUnit 4**（`kotlin.test` 経由。JUnit 5 は未導入） |
| モジュール構成 | マルチモジュール。単体テストを持つモジュールは **9つ** |
| テスト実行タスク | `./gradlew testDevelopDebugUnitTest` |
| カバレッジ | JaCoCo。規約プラグイン（`gateconnector.library.jacoco` 等）で設定済み |
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

この方式により、**JUnit 5 への移行もJUnit 4 用リスナーの実装も不要**になります。突き合わせを行うスクリプトはQA側で管理します。

---

## 3. 導入手順（開発チーム作業）

### 3.1 `Qase.kt` の配置

次のファイルを新規追加します。

**配置先**: `core/testing/src/main/kotlin/jp/bitkey/app/gateconnector/core/testing/qase/Qase.kt`

```kotlin
package jp.bitkey.app.gateconnector.core.testing.qase

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

> **配置先の相談**: `core/testing` は compose / hilt に依存しているため、各モジュールへの依存追加が重い場合は、`core/qase-annotations` のような軽量モジュール（`java-library`）を新設する形でも構いません。その場合は上記のパッケージ宣言を配置先に合わせてください。

### 3.2 各モジュールへの依存追加

単体テストを持つモジュールから `Qase.kt` を参照できるようにします。

```kotlin
dependencies {
    testImplementation(projects.core.testing)
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

### 3.3 CIでの成果物出力

QA側で実行結果とカバレッジを取得するため、CIの成果物をartifactとして出力します。

**対象ワークフロー**: `.github/workflows/test.yml`

```yaml
      - name: Run unit test
        run: ./gradlew testDevelopDebugUnitTest

      # ↓ 追記
      - name: Generate coverage report
        run: ./gradlew createDevelopDebugCombinedCoverageReport

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

> `if: always()` を付けるのは、**テストが失敗した場合も結果を取得する**ためです。失敗した結果もQaseに記録します。
>
> カバレッジXMLはモジュール単位で出力されます。集約レポートは不要です。QA側のスクリプトが全モジュール分を合算します。

### 3.4 コンパイル確認

依存を追加したモジュールで、テストコードがコンパイルできることを確認します。

```bash
./gradlew :core:data:compileDevelopDebugUnitTestKotlin
```

---

## 4. Qase側の準備（QA担当作業）

対象のQaseプロジェクトに、次のカスタムフィールドを用意します。

| 種別 | 名称 | 設定 |
|---|---|---|
| ケースのカスタムフィールド | `Test Level` | selectbox。選択肢に `Unit` / `Integration` / `E2E` / `Manual` |
| Runのカスタムフィールド | `Coverage Rate` | number |

作成後、**それぞれのフィールドIDと、Test Levelの選択肢IDを控えます。** 次のAPIで確認できます。

```bash
curl -H "Token: $QASE_API_TOKEN" "https://api.qase.io/v1/custom_field?limit=100"
```

控えたIDは、QA側の同期スクリプトの設定値（`QASE_PROJECT_CODE` / `TEST_LEVEL_FIELD_ID` / `COVERAGE_FIELD_ID`）と、`Qase.kt` の `TestLevel` の `optionId` に反映します。

> `Qase.kt` の `optionId` が実際の選択肢IDと異なる場合は、開発チームに修正を依頼するか、同期スクリプト側で読み替えます。

---

## 5. APIトークンの設定

**トークンはソースコードに書かないでください。** 環境変数 `QASE_API_TOKEN` から読み込みます。

```powershell
# ローカル（設定後、ターミナルやIDEの再起動が必要）
setx QASE_API_TOKEN "<your token>"
```

CI で使う場合は Secrets から環境変数として渡します。

---

## 6. 動作確認

| # | 確認内容 | 方法 |
|---|---|---|
| 1 | `@Qase` がコンパイルできる | テストに1つ付与して `./gradlew :{module}:compileDevelopDebugUnitTestKotlin` |
| 2 | 静的パースで対応表が作れる | QA側スクリプトを実行し、`class#method → case_id` が出力されるか |
| 3 | CIの成果物が取得できる | Actionsの実行結果から artifact をダウンロードし、`TEST-*.xml` と jacoco XML が含まれるか |
| 4 | Qaseに反映される | 同期後、API または Qase UI で読み取って確認 |

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
| `Unresolved reference: Qase` | import文の誤り、または対象モジュールに `testImplementation(projects.core.testing)` が未追加 |
| 型の不一致（`id`） | `id` は `Long`。整数リテラルで記述する |
| カバレッジXMLが生成されない | `createDevelopDebugCombinedCoverageReport` が実行されていない |
| テスト失敗時に artifact が無い | `if: always()` が付いていない |
| カスタムフィールドが反映されない | キー名が `custom_fields`（複数形）になっている |
| ステップの期待値が入らない | キー名が `expected` になっている（正: `expected_result`） |
| 日本語・絵文字が文字化けする | Windowsコンソールのcp932。スクリプト側でUTF-8に再設定する |
| `QASE_API_TOKEN が設定されていません` | `setx` 後にターミナル/IDEを再起動していない |

---

## 9. 検証環境との対応

検証用リポジトリ（RSAcoveragetesting）のファイルとの対応です。本番で使わないものも記録として残します。

| 検証環境のファイル | 本番での扱い |
|---|---|
| `template/kotlin/Qase.kt` | ✅ パッケージを変更して配置 |
| `template/kotlin/QaseResultCollector.kt` | ❌ **配置しない**（JUnit 4 では動作しない） |
| `template/resources/...TestExecutionListener` | ❌ **配置しない**（同上） |
| `template/python/qase_common.py` | ⚠️ QA側リポジトリで管理。設定値を差し替え |
| `template/python/qase_sync.py` | ⚠️ QA側リポジトリで管理。入力JSONの生成経路を変更 |
| `template/python/send_coverage.py` | ⚠️ QA側リポジトリで管理。複数モジュールのXML合算に対応 |
| `template/build.gradle.kts.snippet` | ❌ 不要（JaCoCoは規約プラグイン済み、タスク定義はQA側でスクリプトを直接実行） |
