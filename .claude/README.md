# `.claude/` ディレクトリ

このディレクトリには、Claude Code をQAワークフローに特化させるためのカスタマイズファイルが格納されています。

## ディレクトリ構成

```
.claude/
├── README.md                         # ← このファイル
├── commands/                         # Custom Slash Commands (Skills)
│   ├── README.md                     # 全Skillの一覧と概要
│   ├── qa-workflow-manager.md        # 🎯 QAワークフロー管理 (オーケストレーター)
│   ├── qa-impact-analyzer.md         # 📊 影響範囲分析
│   ├── qa-viewpoint-manager.md       # 🔍 テスト観点管理
│   ├── qa-matrix-generator.md        # 📋 デシジョンテーブル生成
│   ├── qa-case-exporter.md           # 📤 テストケースCSVエクスポート
│   ├── qa-feature-extractor.md       # 🏗️ 機能抽出
│   ├── qa-domain-element-manager.md  # 🌐 ドメイン要素管理
│   ├── review-test-cases.md          # 📝 テストケースレビュー
│   ├── check-qa-prs.md               # 🔎 QAレビュー対象PRの抽出
│   ├── review-unit-tests.md          # 🧫 単体テストレビュー
│   ├── qase-annotation-writer.md     # 🏷️ @Qase アノテーション追記
│   ├── qase-sync.md                  # 🔁 Qase同期
│   ├── unit-test-review-workflow.md  # 🔬 単体テストレビューワークフロー
│   ├── feature-map.md                # 🗺️ 全体マップ・責務の確定
│   ├── bdd-workflow-manager.md       # 🔗 BDDテスト設計ワークフロー (オーケストレーター)
│   ├── bdd-artifact-updater.md       # ♻️ BDD成果物の修正反映
│   ├── review-bdd-artifacts.md       # 🪞 BDD成果物セルフレビュー
│   ├── rule-example-extractor.md     # 📐 ルール・実例抽出
│   ├── gherkin-scenario-generator.md # 🧪 Gherkinシナリオ生成
│   ├── viewpoint-extractor.md        # 🔭 テスト観点抽出・観点分岐Gherkin生成
│   ├── e2e-org-seeding.md            # 🌱 E2E用組織へのテストデータ投入
│   ├── pbi-flow-map.md               # 🗺️ 処理の全体図（HTML）生成
│   ├── end.md                        # 📦 QA作業提出
│   ├── start.md                      # 🔄 ブランチ同期
│   ├── sync-qa-docs.md               # 📑 QAドキュメント同期
│   ├── quality-criteria-generator.md # 📏 品質評価計画書生成
│   └── skill-improver.md             # 🛠️ Skill改善メタスキル
└── memories/                         # 自己学習メモリー
    ├── global.md                     # 全体共通の学習メモリー
    ├── qa-workflow-manager.md         # ワークフロー管理の学習ログ
    ├── quality-criteria-generator.md  # 品質評価計画書生成の学習ログ
    ├── skill-improver.md              # Skill改善の学習ログ
    ├── qa-case-exporter.md            # CSVエクスポートの学習ログ
    ├── qa-impact-analyzer.md          # 影響範囲分析の学習ログ
    ├── review-test-cases.md           # テストケースレビューの学習ログ
    ├── check-qa-prs.md                # PR抽出の学習ログ
    ├── review-unit-tests.md           # 単体テストレビューの学習ログ
    ├── qase-annotation-writer.md      # @Qase 追記の学習ログ
    ├── qase-sync.md                   # Qase同期の学習ログ
    ├── unit-test-review-workflow.md   # 単体テストレビュー工程管理の学習ログ
    ├── feature-map.md                 # 全体マップ・責務確定の学習ログ
    ├── bdd-workflow-manager.md        # BDDテスト設計ワークフローの学習ログ
    ├── bdd-artifact-updater.md        # BDD成果物の修正反映の学習ログ
    ├── review-bdd-artifacts.md        # BDD成果物セルフレビューの学習ログ
    ├── rule-example-extractor.md      # ルール・実例抽出の学習ログ
    ├── gherkin-scenario-generator.md  # Gherkinシナリオ生成の学習ログ
    ├── viewpoint-extractor.md         # テスト観点抽出の学習ログ
    ├── e2e-org-seeding.md             # テストデータ投入の学習ログ
    └── start.md                       # ブランチ同期の学習ログ
```

## Skill一覧（概要）

| Skill名 | コマンド | 役割 |
|---|---|---|
| QAワークフロー管理 | `/qa-workflow-manager` | 全Skillを統合するオーケストレーター |
| 影響範囲分析 | `/qa-impact-analyzer` | チケットから影響範囲を特定 |
| テスト観点管理 | `/qa-viewpoint-manager` | テスト観点の作成・レビュー |
| デシジョンテーブル生成 | `/qa-matrix-generator` | テスト条件の組み合わせ表を生成 |
| テストケースCSVエクスポート | `/qa-case-exporter` | Qase用CSVファイルを出力 |
| 機能抽出 | `/qa-feature-extractor` | ソースコードから機能情報を抽出 |
| ドメイン要素管理 | `/qa-domain-element-manager` | テスト用のドメイン固有パラメータを管理 |
| テストケースレビュー | `/review-test-cases` | 既存テストケースの品質レビュー・断捨離 |
| QAレビュー対象PR抽出 | `/check-qa-prs` | レビュー対象の単体テストPRを抽出 |
| 単体テストレビュー | `/review-unit-tests` | 単体テストコードのQA視点レビュー |
| `@Qase` 追記 | `/qase-annotation-writer` | テストコードへのQaseケース紐づけとPRブランチへのpush |
| Qase同期 | `/qase-sync` | ケース本体のQaseへの同期（実行結果の送信はCIが自動実行） |
| 単体テストレビューワークフロー | `/unit-test-review-workflow` | PR探索からQase同期までの工程を統合管理 |
| QA作業提出 | `/end` | Git操作でQA作業成果を提出 |
| ブランチ同期 | `/start` | 作業ブランチをmainと同期 |
| QAドキュメント同期 | `/sync-qa-docs` | 外部ドキュメントとの同期 |
| 品質評価計画書生成 | `/quality-criteria-generator` | 利用文脈から品質評価計画書ドラフトを生成 |
| 全体マップ・責務の確定 | `/feature-map` | チケットの責務を確定し決定台帳へ記録 |
| BDDテスト設計ワークフロー | `/bdd-workflow-manager` | 責務の確定から全体図生成までを統合管理 |
| BDD成果物の修正反映 | `/bdd-artifact-updater` | 作成済みBDD成果物の部分更新 |
| BDD成果物セルフレビュー | `/review-bdd-artifacts` | 作成した成果物の食い違い・不足観点を外部レビュー前に自己点検 |
| ルール・実例抽出 | `/rule-example-extractor` | 仕様書からビジネスルールと実例を抽出 |
| Gherkinシナリオ生成 | `/gherkin-scenario-generator` | ルール・実例からGherkinシナリオを生成 |
| テスト観点抽出 | `/viewpoint-extractor` | 観点マスターと観点分岐Gherkinを生成 |
| 処理の全体図生成 | `/pbi-flow-map` | テスト仕様から機能単位の全体図HTMLを生成 |
| テストデータ投入 | `/e2e-org-seeding` | E2E用3組織へのメンバー投入・アクティベート |
| Skill改善 | `/skill-improver` | Skill自体の改善提案・実行 |

## 自己学習メモリーシステム

### 概要
各Skillは実行中にユーザーからのフィードバック（指摘・修正指示）を受けると、その内容を `.claude/memories/` 配下の対応するメモリーファイルに蓄積します。蓄積された指摘事項は、次回以降の同Skill実行時に自動的に参照され、同じ間違いの再発を防止します。

### メモリーファイルの構造
各メモリーファイルは以下の構造で管理されます：
- **総指摘件数**: 蓄積された指摘の総数
- **指摘事項**: 日付、対象タスク、対象機能、指摘カテゴリ、指摘内容、原因/理由、今後の対策

### メモリーの参照タイミング
- Skill実行開始時に対応するメモリーファイルを読み込み
- 過去の指摘事項を考慮した上で処理を実行
- これにより、同じ指摘を繰り返すことなく品質が継続的に向上

### メモリーの更新タイミング
- ユーザーからの指摘・修正指示を受けた際に該当するメモリーファイルに追記
- 更新は各Skillの責務として実装されている
