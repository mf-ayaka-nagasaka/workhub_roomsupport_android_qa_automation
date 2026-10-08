# Claude Code Custom Skills（Slash Commands）

## 概要
このディレクトリには、`workhub_roomsupport_android_qa_automation` リポジトリ専用のClaude Code Skillが格納されています。  
各Skillは `/コマンド名` で呼び出し可能で、QAワークフローの各工程を自動化・支援します。

---

## Skill一覧

### 🎯 `/qa-workflow-manager` - QAワークフロー管理
QAの全工程を統合管理するオーケストレーターSkill。  
影響範囲分析→テスト観点作成→デシジョンテーブル→テストケースCSV出力の一連の流れを、対話的に進行管理します。

### 📊 `/qa-impact-analyzer` - 影響範囲分析
Notionチケットの変更内容から、テストが必要な影響範囲を分析します。  
ソースコードの差分やコミット履歴を参照し、変更が波及する機能・画面を特定します。

### 🔍 `/qa-viewpoint-manager` - テスト観点管理
影響範囲分析の結果をもとに、テスト観点を作成・レビューします。  
ISO 25010品質モデルやOWASP Mobile Top 10などの標準モデルを参照し、網羅性を担保します。

### 📋 `/qa-matrix-generator` - デシジョンテーブル生成
テスト観点からデシジョンテーブル（条件組み合わせ表）をHTML形式で生成します。  
組み合わせ爆発を防ぎつつ、効率的なテスト条件の組み合わせを導出します。

### 📤 `/qa-case-exporter` - テストケースCSVエクスポート
デシジョンテーブルの内容をQase用CSVフォーマットに変換・出力します。  
前提条件マスターを参照し、統一された書式でテストケースを生成します。

### 🏗️ `/qa-feature-extractor` - 機能抽出
ソースコードから画面構成・機能一覧・UI要素を抽出し、構造化されたデータとして出力します。  
テスト観点作成の入力データとして活用されます。

### 🌐 `/qa-domain-element-manager` - ドメイン要素管理
テストで使用するドメイン固有のパラメータ（端末モデル、OSバージョン、画面サイズ等）を管理します。  
デシジョンテーブル生成時の入力値として参照されます。

### 📝 `/review-test-cases` - テストケースレビュー
既存のテストケース（CSV）を読み込み、品質レビュー・断捨離（冗長ケースの削除提案）を行います。  
マクロ分析（構造的冗長の検出）とミクロ分析（個別ケースの品質チェック）を組み合わせます。

### 🔎 `/check-qa-prs` - QAレビュー対象PRの抽出
開発チームのPRから、QAがレビューすべき単体テスト関連のPRを抽出して一覧表示します。  
レビュー依頼の有無とテストコード変更の有無で判定し、対象外のPRは表示しません。レビュー自体は行わず、一覧提示までで停止します。

### 🧫 `/review-unit-tests` - 単体テストレビュー
開発チームが作成した単体テストコードを、Gherkinシナリオとの突合を軸にQA視点でレビューします。  
観点の網羅性（UT-0）とテストコードの品質（UT-1〜UT-6）を判定し、PRコメント用のレポート草案を作成します。投稿前に必ず承認を挟みます。  
レビュー単位はシナリオです。同じPRに過去のレビューコメントがある場合は**再レビューモード**で動作し、前回指摘の対応状況を突き合わせます。  
判定基準: `docs/unit_test_review_criteria.md`

### 🏷️ `/qase-annotation-writer` - `@Qase` アノテーション追記
レビュー済みの単体テストコードに、Qaseのケースと紐づける `@Qase` アノテーションを追記します。  
タイトル・Test Level・ステップはGherkinから生成し、ケースIDはQase UIで採番した値を転記します。テストロジックは変更しません。  
対象は指定シナリオに対応するテストのみです。追記後、**対象PRのブランチへ commit & push** まで行います（各操作で承認を挟みます）。  
記述ルール: `docs/qase_annotation_rules.md`

### 🔁 `/qase-sync` - Qase同期
テストコードの `@Qase` を静的解析してQaseへ同期します。  
送信前に必ず dry-run で内容を提示し、承認を得てから実行します。  
実行結果とカバレッジの送信は本体リポジトリのCIが自動で行うため、`results` モードは再送・リカバリ用の暫定手段です。  
運用手順: `docs/qase_sync_operation.md`

### 🔬 `/unit-test-review-workflow` - 単体テストレビューワークフロー
単体テストPRの探索からレビュー・`@Qase` 追記・Qase同期までを統合管理するオーケストレーターSkill。
作業ブランチ `unit-test/qa-review` の準備から始まり、各工程で承認を挟みながら個別Skillへ委譲します。
PRが見つからない場合は、PRのURLを直接指定して進めることもできます。

### 📦 `/end` - QA作業提出
Git操作（ブランチ作成、コミット、プッシュ、PR作成）を対話的にガイドし、QA作業の成果物を提出します。

### 🔄 `/start` - ブランチ同期
作業ブランチをmainブランチの最新状態と同期します。  
コンフリクトが発生した場合の解決もガイドします。

### 📑 `/sync-qa-docs` - QAドキュメント同期
外部リポジトリ（ソースコード、ドキュメント）から最新の仕様情報を同期します。

### 🔗 `/bdd-workflow-manager` - BDDテスト設計ワークフロー
仕様書を起点に、ルール・実例抽出 → Gherkinシナリオ生成 → テスト観点抽出・観点分岐Gherkin生成までの一連のBDDテスト設計プロセスを統合的に実行します。  
各工程で人間のレビューを挟みながらステップバイステップで進行し、最終的に全成果物をコミットします。

### ♻️ `/bdd-artifact-updater` - BDD成果物の修正反映
`/bdd-workflow-manager` で作成済みのBDD成果物に対し、リファインメント後に発生した修正・追加を反映します。  
修正要求を構造化 → 影響分析 → 影響のある成果物だけを部分更新、という流れで進行し、修正点以外の既存記述（文言・並び順・採番）は一切変更しません。  
各Stepの保存後に `git diff` で計画外の差分がないことを自己検証します。成果物が未作成の機能には使わず、`/bdd-workflow-manager` を使用します。

### 📐 `/rule-example-extractor` - ルール・実例抽出
仕様書（Markdown）からビジネスルール・実例（正常系・異常系・例外系）を抽出・整理し、テスト設計の基盤となるルール・実例ドキュメント（rules.md）を生成します。  
`/gherkin-scenario-generator` の入力データを作成する上流工程のSkillです。

### 🧪 `/gherkin-scenario-generator` - Gherkinシナリオ生成
`/rule-example-extractor` で作成したルール・実例ドキュメント（rules.md）を入力として、BDDガイドラインとテスト設計ルールに則ったGherkinシナリオ（scenarios.md）を生成します。  
宣言的記述（What）の徹底、決定性の担保、観測可能な結果の検証をガードレールとして適用します。

### 🔭 `/viewpoint-extractor` - テスト観点抽出・観点分岐Gherkin生成
`/gherkin-scenario-generator` で作成したGherkinシナリオ（scenarios.md）を入力として、汎用的なテスト観点を抽出し、仕様書との照合を経て機能別観点マスター（viewpoints.tsv）と観点分岐版Gherkinシナリオ（scenarios_with_viewpoints.md）を生成します。  
観点マスターはNotionDBへのコピー＆ペーストに対応したTSV形式で出力します。全機能横断の観点マスター総合版（`_master/viewpoints.tsv`）も自動で蓄積・更新します。

### 🗺️ `/pbi-flow-map` - 処理の全体図（HTML）生成
テスト仕様（rules.md, scenarios.md）から、非エンジニア向けの「処理の全体図」を1枚の HTML に生成します。  
画面／裏側の処理／残るものを段に分けた流れ図と、テストケースをクリックすると図の該当箇所が光る対応表、エラー文言の逆引き表を含みます。  
テンプレート（完成例）: `src/test/resources/features/_templates/pbi-flow-map-template.html`

### 📏 `/quality-criteria-generator` - 品質判定基準生成
プロダクトの利用文脈（コンテキストプロファイル）への回答をもとに、ISO/IEC 25010:2023 に基づく品質判定基準のドラフトを生成します。  
指標カタログから該当指標を導出し、閾値の根拠・測定方法・データソースを明示した判定基準ドキュメントとCSVを出力します。  
質問票は対象プラットフォーム（モバイル／Web）で分岐し、ソースコードがある場合はコードから回答の下書きを作成できます。  
フレームワーク定義: `docs/quality_criteria_framework/`

### 🛠️ `/skill-improver` - Skill改善メタスキル
Skill自体の改善を提案・実行するメタスキル。  
メモリーに蓄積された指摘事項を分析し、Skillのプロンプトやロジックの改善を行います。

---

## ワークフロー概要

```
[チケット受領]
    ↓
/qa-impact-analyzer   → 影響範囲の特定
    ↓
/qa-viewpoint-manager → テスト観点の作成
    ↓
/qa-matrix-generator  → デシジョンテーブルの生成
    ↓
/qa-case-exporter     → テストケースCSVの出力
    ↓
/review-test-cases    → レビュー・断捨離（任意）
    ↓
/end                  → 成果物の提出（Git操作）
```

上記の一連の流れは `/qa-workflow-manager` で統合的に管理できます。

## ワークフロー概要（単体テストレビュー）

開発チームが作成した単体テストをレビューし、Qaseへ連携するまでの流れです。  
上記の手動テスト設計フローとは独立しています。

```
[開発がテストコード変更PRを作成]
    ↓
/check-qa-prs            → レビュー対象PRの抽出
    ↓                       （0件ならPRのURLを直接指定）
/review-unit-tests       → Gherkin突合＋品質レビュー → PRコメント（要承認）
    ↓                       （修正後の再実行で再レビューモード）
[Qase UIでケースを作成しID採番]
    ↓
/qase-annotation-writer  → @Qase を追記し、PRブランチへ commit & push（要承認）
    ↓
/qase-sync cases         → ケース本体をQaseへ同期（要承認）
                            ※実行結果とカバレッジはdevelopマージ後にCIが自動送信
```

上記の一連の流れは `/unit-test-review-workflow` で統合的に管理できます。
作業ブランチ `unit-test/qa-review` の準備も同Skillが行います。

判定基準は `docs/unit_test_review_criteria.md` に集約しています。
レビュー対象リポジトリは `bitkey-service/gateaccess-android` です。

## 補助Skill

| Skill | 用途 |
|---|---|
| `/qa-feature-extractor` | ソースコードからの機能情報抽出 |
| `/qa-domain-element-manager` | テスト用パラメータの管理 |
| `/start` | ブランチの同期 |
| `/sync-qa-docs` | ドキュメントの同期 |
| `/skill-improver` | Skill自体の改善 |
| `/quality-criteria-generator` | 品質判定基準ドラフトの生成 |
| `/bdd-artifact-updater` | BDD成果物の修正反映（リファインメント後） |
