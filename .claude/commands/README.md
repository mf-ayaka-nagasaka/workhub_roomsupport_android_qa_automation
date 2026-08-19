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

### 📦 `/submit-qa-work` - QA作業提出
Git操作（ブランチ作成、コミット、プッシュ、PR作成）を対話的にガイドし、QA作業の成果物を提出します。

### 🔄 `/sync-work-branch` - ブランチ同期
作業ブランチをmainブランチの最新状態と同期します。  
コンフリクトが発生した場合の解決もガイドします。

### 📑 `/sync-qa-docs` - QAドキュメント同期
外部リポジトリ（ソースコード、ドキュメント）から最新の仕様情報を同期します。

### 🧪 `/gherkin-scenario-generator` - Gherkinシナリオ自動生成
iOS仕様書（Markdown）からビジネスルール・実例を抽出し、BDDガイドラインとテスト設計ルールに則ったGherkinシナリオ（.feature）を一括生成します。  
宣言的記述（What）の徹底、決定性の担保、観測可能な結果の検証をガードレールとして適用します。

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
/submit-qa-work       → 成果物の提出（Git操作）
```

上記の一連の流れは `/qa-workflow-manager` で統合的に管理できます。

## 補助Skill

| Skill | 用途 |
|---|---|
| `/qa-feature-extractor` | ソースコードからの機能情報抽出 |
| `/qa-domain-element-manager` | テスト用パラメータの管理 |
| `/sync-work-branch` | ブランチの同期 |
| `/sync-qa-docs` | ドキュメントの同期 |
| `/skill-improver` | Skill自体の改善 |
