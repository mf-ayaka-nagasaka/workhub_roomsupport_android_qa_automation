# Qase同期の運用手順

| 項目 | 内容 |
|---|---|
| **象限** | 🛠️ ハウツー |
| **対象者** | QA担当（Qase同期の実行者） |
| **ゴール** | テストコードの `@Qase` をQaseへ同期し、実行結果とカバレッジを記録できるようになります |

本書は、QA側で実行するQase同期スクリプトの操作手順です。スクリプトは `scripts/` 配下にあり、対象リポジトリ（workhubRoomSupport-Android）のテストソースを**読み取るだけ**で、変更は行いません。

---

## 1. 全体の流れ

```
テストコード (.kt)
   @Qase(id = 101, title = ..., steps = [...])
        │
        │  ① extract_qase_annotations.py（静的パース・Gradle実行不要）
        ▼
   build/qase/qase-cases.json
        │
        ├──────────────────────┬──────────────────────┐
        │                      │                      │
        ▼ ② qase_sync.py       ▼ ③ send_qase_results.py
   ケース内容を同期          実行結果＋カバレッジを送信
   （タイトル/説明/          （TEST-*.xml と JaCoCo XML を突き合わせ）
     Test Level/steps）
        │                      │
        └──────────┬───────────┘
                   ▼
               Qase API
```

| スクリプト | 役割 | 実行頻度 |
|---|---|---|
| `extract_qase_annotations.py` | テストソースから `@Qase` を抽出しJSON化 | ②③の前に毎回 |
| `qase_sync.py` | ケース内容（タイトル・説明・Test Level・ステップ）を同期 | `@Qase` を追記・変更したとき |
| `send_qase_results.py` | Run作成・実行結果の送信・カバレッジ記録 | テスト実行結果を記録したいとき |

> **②と③は別のタイミングで実行します。** ケース同期は仕様変更時のみ、結果送信は実行結果を残したいときです。

---

## 2. 事前準備

### 2.1 環境変数

| 変数 | 必須 | 既定値 | 内容 |
|---|---|---|---|
| `QASE_API_TOKEN` | ✅ | — | APIトークン。**ソースに書かないこと** |
| `QASE_PROJECT_CODE` | | `RSA` | Qaseのプロジェクトコード |
| `QASE_TEST_LEVEL_FIELD_ID` | | `50` | ケースのカスタムフィールド `Test Level` のID |
| `QASE_COVERAGE_FIELD_ID` | | `49` | Runのカスタムフィールド `Coverage Rate` のID |

```powershell
setx QASE_API_TOKEN "<your token>"
$env:QASE_PROJECT_CODE = "<本番プロジェクトコード>"
```

> 既定値は検証用リポジトリの値です。**本番プロジェクトのIDは必ず確認して設定してください。** 確認方法は `qase_integration_setup.md` の「4. Qase側の準備」にあります。

### 2.2 必要なもの

| 項目 | 内容 |
|---|---|
| Python | 3.8以降（標準ライブラリのみ使用） |
| 対象リポジトリ | ローカルにクローン済みであること（読み取りのみ） |
| テスト結果 | ③を実行する場合のみ。CIのartifact、またはローカル実行の出力 |

---

## 3. 手順

### 3.1 ① アノテーションの抽出

```bash
python scripts/extract_qase_annotations.py \
  --source-root "C:/Users/<user>/workhubRoomSupport-Android" \
  --out build/qase/qase-cases.json
```

| オプション | 内容 |
|---|---|
| `--source-root` | 対象リポジトリのルート（必須） |
| `--out` | 出力先JSON（既定: `build/qase/qase-cases.json`） |
| `--module` | 対象を絞る（パスの部分一致。例: `core/data`） |

出力例:

```
🔍 TestLevel の選択肢ID: {'UNIT': 1, 'INTEGRATION': 2, 'E2E': 3, 'MANUAL': 4}
🔍 対象ファイル: 42 件

✅ @Qase 付与済み : 12 件
⚠️  @Qase 未付与   : 113 件
📄 出力先         : build/qase/qase-cases.json
```

- 選択肢IDは、対象リポジトリの `Qase.kt` から自動で読み取ります
- `src/androidTest/` と `ExampleUnitTest.kt` は対象外です
- `@Qase` の記述に誤りがあると、**ファイル名と行番号を示して中断**します

### 3.2 ② ケース内容の同期

```bash
# まず送信せずに内容を確認する
python scripts/qase_sync.py --input build/qase/qase-cases.json --dry-run

# 問題なければ送信
python scripts/qase_sync.py --input build/qase/qase-cases.json
```

**送信前に次の検証が走り、問題があれば中断します。**

| 検証 | 挙動 |
|---|---|
| ケースIDの重複 | 中断 |
| ケースIDがQase上に存在するか | 中断 |
| `@Qase` 未付与のテスト | 警告のみ（対象外として継続） |

同期後、コードに対応するテストが無い自動化ケースを**孤児候補として報告**します。削除はしません。判断は人が行い、Qase UI上で実施してください。

### 3.3 ③ 実行結果とカバレッジの送信

```bash
python scripts/send_qase_results.py \
  --input build/qase/qase-cases.json \
  --test-results <TEST-*.xml があるディレクトリ> \
  --jacoco <JaCoCo XML があるディレクトリ> \
  --title "PR #185 / develop" \
  --dry-run
```

| オプション | 内容 |
|---|---|
| `--test-results` | `TEST-*.xml` を再帰的に探すディレクトリ（必須） |
| `--jacoco` | JaCoCo XMLを再帰的に探すディレクトリ（省略時はカバレッジを送信しない） |
| `--title` | Runのタイトル。ブランチ名やPR番号を入れると識別しやすくなります |
| `--dry-run` | 集計のみ行い、送信しない |

**テスト結果の取得元:**

| 取得元 | 方法 |
|---|---|
| CI（推奨） | GitHub Actions の artifact `test-results-and-coverage` をダウンロードして展開 |
| ローカル実行 | 対象リポジトリで `./gradlew testDevelopDebugUnitTest createDevelopDebugCombinedCoverageReport` を実行 |

---

## 4. 仕組みの要点

### 4.1 なぜリスナーを使わないか

検証用リポジトリでは、JUnit5のリスナーが実行時に `@Qase` を読んで中間JSONを出力していました。本番リポジトリは**JUnit4のためリスナーが動作しません**（配置してもエラーが出ず、黙って動かない）。

代わりに、次の2つを突き合わせています。

| 情報源 | 得られるもの |
|---|---|
| テストソースの静的パース | `class#method` → `case_id` / タイトル / Test Level / ステップ |
| JUnit の `TEST-*.xml` | `class#method` → 実行結果（passed / failed / skipped）と所要時間 |

この方式により、JUnit5への移行もJUnit4用リスナーの実装も不要になります。

### 4.2 カバレッジの算出方法

JaCoCo XML の **`<report>` 直下の `counter` のみ**を使い、全モジュール分を合算します。

> ⚠️ 配下の `package` / `class` 要素にも同じ `counter` があるため、`.//counter` のように全階層を拾うと**二重計上**になります。検証用リポジトリのスクリプトはこの書き方でしたが、本スクリプトでは修正しています。

### 4.3 カバレッジ指標についての注意

JaCoCoが算出するのは**コードカバレッジ（命令網羅率）**です。「ビジネスルールに対するテストカバー率」とは**別の指標**であり、後者は「ルールスイート配下にテストケースが存在するか」で測るものです。混同しないよう、指標を分けて扱ってください。

---

## 5. Qase API の注意点

| 項目 | 内容 |
|---|---|
| カスタムフィールドのキー名 | **`custom_field`（単数形）**。複数形だと **200が返るが値は黙って無視される** |
| ステップの期待値のキー名 | **`expected_result`**（`expected` ではない） |
| カスタムフィールドの値 | **選択肢IDを文字列**で渡す |
| 書き込み後 | **必ず読み取りで反映を確認する** |
| 同期の方向 | **コード → Qase の一方向。** Qase UI上の編集は次回同期で上書きされる |
| スイート配置 | 同期対象外。Qase UIで管理する |
| 削除されたテスト | Qase上のケースは**自動削除しない**（実行履歴が失われるため）。孤児候補として報告するのみ |

---

## 6. トラブルシューティング

| 症状 | 原因・対処 |
|---|---|
| `@Qase が付いたテストが1件もありません` | `--source-root` が誤っている、または `--module` で絞りすぎている |
| `解析できなかった @Qase があります` | 記述の誤り。示された行を `qase_annotation_rules.md` に従って修正 |
| `Qase 上に存在しないケースIDが指定されています` | Qase UIでケースを作成し、採番されたIDを転記する |
| `ケースIDが重複しています` | 複数のテストが同じIDを指している。どちらかを修正 |
| `TEST-*.xml が見つかりません` | `--test-results` のパス誤り。CIのartifactを展開したか確認 |
| 実行結果が「未実行」になる | テストが実行されていないか、クラス名が一致していない（内部クラスなど） |
| カバレッジが0% | JaCoCo XMLが見つかっていない。`createDevelopDebugCombinedCoverageReport` の実行を確認 |
| 日本語が文字化けする | Windowsコンソールのcp932。スクリプト側でUTF-8に再設定済み |
| `QASE_API_TOKEN が設定されていません` | `setx` 後にターミナルを再起動していない |
