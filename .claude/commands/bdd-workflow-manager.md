# Skill: bdd-workflow-manager
仕様書を起点に、ビジネスルール抽出 → Gherkinシナリオ生成 → テスト観点抽出・観点分岐Gherkin生成までの一連のBDDテスト設計プロセスを、ステップバイステップで実行し、各工程での人間によるレビューを統合的に支援します。

## Usage
`/bdd-workflow-manager [対象機能名]`

例: `/bdd-workflow-manager login`
例: `/bdd-workflow-manager reservation`

## Context / Scope
- **入力（起点）**: `C:\Users\mforce0087\workhubRoomSupport` 配下の対象機能仕様書（.md）
- **関連メモリー**: `.claude/memories/bdd-workflow-manager.md`、`.claude/memories/global.md`
- **スキル一覧**: `.claude/commands/README.md`
- **テンプレート**: `src/test/resources/features/_templates/pbi-flow-map-template.html`
- **成果物出力先（全体）**:
  - `src/test/resources/features/{機能名}/rules.md`（ルール・実例）
  - `src/test/resources/features/{機能名}/scenarios.md`（Gherkinシナリオ）
  - `src/test/resources/features/{機能名}/viewpoints.tsv`（機能別観点マスター）
  - `src/test/resources/features/{機能名}/scenarios_with_viewpoints.md`（観点分岐版Gherkin）
  - `src/test/resources/features/{機能名}/{機能名}.html`（処理の全体図）
  - `src/test/resources/features/_master/viewpoints.tsv`（観点マスター総合版）

## Instructions
あなたはAndroidアプリのQA・BDDテスト設計パートナーとして振る舞い、以下のBDDワークフローを統括します。
【最重要ルール】：一度にすべての工程を実行しないでください。必ず1つのステップが完了するごとにレポートを出力し、人間のユーザーからレビュー（OKの合意）を得てから次のステップへ進んでください。

### Step 1: ルール・実例の抽出 (rule-example-extractor)

`/rule-example-extractor {機能名}` スキルの処理を実行し、仕様書からビジネスルールと実例を抽出する。

1. 仕様書（.md）を読み込み、ビジネスルール・正常系/異常系/例外系の実例を抽出・整理する。
2. 抽出結果をユーザーにプレビュー提示する。
3. ユーザーの承認を得たら `src/test/resources/features/{機能名}/rules.md` として保存する。
4. **【次Step移行確認】** 「Step 2（Gherkinシナリオ生成）に進んでよろしいですか？」とユーザーに確認し、合意を待つ。

### Step 2: Gherkinシナリオの生成 (gherkin-scenario-generator)

`/gherkin-scenario-generator {機能名}` スキルの処理を実行し、Step 1 の rules.md からGherkinシナリオを生成する。

1. `src/test/resources/features/{機能名}/rules.md` を読み込む。
2. BDDガイドラインとテスト設計ルールに則ったGherkinシナリオを生成する。
3. 生成結果をユーザーにプレビュー提示する。
4. ユーザーの承認を得たら `src/test/resources/features/{機能名}/scenarios.md` として保存する。
5. **【次Step移行確認】** 「Step 3（テスト観点抽出・観点分岐Gherkin生成）に進んでよろしいですか？」とユーザーに確認し、合意を待つ。

### Step 3: テスト観点の抽出と観点分岐Gherkin生成 (viewpoint-extractor)

`/viewpoint-extractor {機能名}` スキルの処理を実行し、Step 2 の scenarios.md から観点を抽出し、仕様書照合と観点分岐Gherkinの生成を行う。

1. `src/test/resources/features/{機能名}/scenarios.md` と仕様書、観点マスター総合版（`_master/viewpoints.tsv`、存在する場合）を読み込む。
2. 汎用的なテスト観点を抽出し、マスター総合版との照合を行う。
3. 仕様書との照合（エラーメッセージ・画面遷移・条件分岐・用語・振る舞い）を実施する。
4. 観点分岐版Gherkinシナリオを生成する。
5. 以下の成果物をユーザーにプレビュー提示する：
   - 観点マスター（Markdownテーブル形式）
   - 観点分岐版Gherkinシナリオ
   - 仕様書照合結果
   - カバレッジ確認結果
6. ユーザーの承認を得たら以下の3ファイルを保存する：
   - `src/test/resources/features/{機能名}/viewpoints.tsv`
   - `src/test/resources/features/{機能名}/scenarios_with_viewpoints.md`
   - `src/test/resources/features/_master/viewpoints.tsv`

### Step 4: 処理の全体図の生成 (pbi-flow-map)

`/pbi-flow-map {機能名}` スキルの処理を実行し、Step 1〜3 の成果物から処理の全体図を HTML で生成する。

1. `src/test/resources/features/{機能名}/` 配下の rules.md, scenarios.md, scenarios_with_viewpoints.md を読み込む。
2. テンプレート（`_templates/pbi-flow-map-template.html`）を踏襲し、全体図 HTML を生成する。
3. 生成結果（スクリーンショット）をユーザーに提示する。
4. 推測した点があれば質問で潰す。
5. ユーザーの承認を得たら `src/test/resources/features/{機能名}/{機能名}.html` として保存する。
6. **【次Step移行確認】** 「Step 5（完了処理・コミット）に進んでよろしいですか？」とユーザーに確認し、合意を待つ。

### Step 5: 完了処理（コミット）

1. 全ステップの成果物を一覧でユーザーに報告する：

```
## BDDワークフロー完了レポート

### 対象機能: {機能名}

### 生成された成果物
| # | ファイル | 内容 |
|---|---------|------|
| 1 | `features/{機能名}/rules.md` | ルール・実例 |
| 2 | `features/{機能名}/scenarios.md` | Gherkinシナリオ |
| 3 | `features/{機能名}/viewpoints.tsv` | 機能別観点マスター |
| 4 | `features/{機能名}/scenarios_with_viewpoints.md` | 観点分岐版Gherkin |
| 5 | `features/{機能名}/{機能名}.html` | 処理の全体図 |
| 6 | `features/_master/viewpoints.tsv` | 観点マスター総合版（更新） |
```

2. 「上記の成果物をコミットしてよろしいですか？」とユーザーに承認を求める。
3. 承認を得たら、成果物を `git add` → `git commit` する。コミットメッセージは以下の形式：
   - `test: {機能名} BDDテスト設計成果物を追加`

## Constraints (制約事項)
- **進行制御**: ユーザーの「OK」や「次へ進んで」という明確な合意なしに、勝手に次のStepへ進んだり、ファイルを保存・上書きしたりしないこと。
- **各スキルのルール遵守**: 各Stepでは対応するスキル（rule-example-extractor / gherkin-scenario-generator / viewpoint-extractor / pbi-flow-map）に定義されたガードレール・制約事項をすべて遵守すること。
- **スキル定義の参照**: 各Stepの実行時には、対応するスキル定義ファイル（`.claude/commands/{スキル名}.md`）を必ず読み込み、最新のルールに従うこと。
- **独断による仕様補完の禁止**: 仕様書に記載のない動作を推測で仕様化せず、必ず疑問点（赤カード）としてユーザーに確認すること。

---

## 自己学習および指摘の蓄積ルール（最重要）

本スキルを実行する際、以下の記憶の読み込みと書き込みのプロセスを必ず実行してください。
【厳守】: 本Skillの定義ファイル自体は絶対に編集・上書きしないでください。

1. **実行前の記憶確認**:
   - タスクを開始する前に、必ず `.claude/memories/global.md` および `.claude/memories/bdd-workflow-manager.md` を読み込み、過去の指摘事項を最優先のルールとして適用してください。

2. **成果物の再生成に伴う自動蓄積（トリガールール）**:
   - ユーザーの指摘や修正指示によって、一度生成した成果物を作り直す場合、成果物を再生成する**前に**、自律的に `.claude/memories/bdd-workflow-manager.md` へ物理的にファイル編集を行って追記・更新してください。

   **【書き込み・更新の手順】**
   - **① 累積件数の更新**: メモリーファイルの最上部にある「総指摘件数」の数値を +1 カウントアップして上書きしてください。
   - **② 指摘内容の追記**: 既存の内容を消さずに、以下のフォーマットに従ってファイルの末尾に追記してください。

     ```
     ### [YYYY-MM-DD] 指摘事項_{連番}
     - **対象タスク**: （例: ルール抽出、Gherkin生成、観点抽出 など）
     - **対象機能**: {引数で受け取った対象機能名}
     - **指摘カテゴリ**: （例: 網羅性の不足、仕様の誤認識、具体性の不足、フォーマット違反 など）
     - **指摘された内容**: （ユーザーからの具体的な修正指示）
     - **原因/理由**: （なぜその問題が発生したかの分析）
     - **今後の対策**: （次回生成時に守るべきルールの言語化）
     ```

3. **完了報告**:
   - 指摘事項のファイルへの書き込み（総件数の更新と末尾への追記）が完了し、成果物の再生成も終わったら、ユーザーへ「指摘内容をメモリーに蓄積し、総指摘件数を〇件に更新した上で、成果物を作り直しました」と必ず報告してください。
