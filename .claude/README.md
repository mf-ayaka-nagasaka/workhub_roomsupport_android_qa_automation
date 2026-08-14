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
│   ├── submit-qa-work.md             # 📦 QA作業提出
│   ├── sync-work-branch.md           # 🔄 ブランチ同期
│   ├── sync-qa-docs.md               # 📑 QAドキュメント同期
│   └── skill-improver.md             # 🛠️ Skill改善メタスキル
└── memories/                         # 自己学習メモリー
    ├── global.md                     # 全体共通の学習メモリー
    ├── qa-workflow-manager.md         # ワークフロー管理の学習ログ
    ├── skill-improver.md              # Skill改善の学習ログ
    ├── qa-case-exporter.md            # CSVエクスポートの学習ログ
    ├── qa-impact-analyzer.md          # 影響範囲分析の学習ログ
    └── review-test-cases.md           # テストケースレビューの学習ログ
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
| QA作業提出 | `/submit-qa-work` | Git操作でQA作業成果を提出 |
| ブランチ同期 | `/sync-work-branch` | 作業ブランチをmainと同期 |
| QAドキュメント同期 | `/sync-qa-docs` | 外部ドキュメントとの同期 |
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
