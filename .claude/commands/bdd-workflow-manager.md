# Skill: bdd-workflow-manager
**そのチケットでどこまでを見るのかの確定（責務の確定）**を起点に、ビジネスルール抽出 → Gherkinシナリオ生成 → テスト観点抽出・観点分岐Gherkin生成までの一連のBDDテスト設計プロセスを、ステップバイステップで実行し、各工程での人間によるレビューを統合的に支援します。

## Usage
`/bdd-workflow-manager [対象機能名]`

例: `/bdd-workflow-manager Login`
例: `/bdd-workflow-manager reservation`

## Context / Scope
- **入力（起点）**: 対象チケットの受け入れ条件（AC）と、`C:\Users\mforce0087\workhubRoomSupport` 配下の対象機能仕様書（.md）
- **責務の正本**: `src/test/resources/features/_master/feature-map.html`（全体マップ・責務の決定台帳）
- **関連メモリー**: `.claude/memories/bdd-workflow-manager.md`、`.claude/memories/feature-map.md`、`.claude/memories/global.md`
- **スキル一覧**: `.claude/commands/README.md`
- **テンプレート**: `src/test/resources/features/_templates/pbi-flow-map-template.html`
- **成果物出力先（全体）**:
  - `src/test/resources/features/{機能名}/rules.md`（ルール・実例）
  - `src/test/resources/features/{機能名}/scenarios.md`（Gherkinシナリオ）
  - `src/test/resources/features/{機能名}/viewpoints.tsv`（機能別観点マスター）
  - `src/test/resources/features/{機能名}/scenarios_with_viewpoints.md`（観点分岐版Gherkin）
  - `src/test/resources/features/{機能名}/{機能名}.html`（処理の全体図）
  - `src/test/resources/features/_master/viewpoints.tsv`（観点マスター総合版）
  - `src/test/resources/features/_master/feature-map.html`（全体マップ・責務の決定台帳）

## Instructions
あなたはAndroidアプリのQA・BDDテスト設計パートナーとして振る舞い、以下のBDDワークフローを統括します。
【最重要ルール】：一度にすべての工程を実行しないでください。必ず1つのステップが完了するごとにレポートを出力し、人間のユーザーからレビュー（OKの合意）を得てから次のステップへ進んでください。

### Step 0: 責務の確定 (feature-map)

`/feature-map scope {チケット名}` スキルの処理を実行し、**そのチケットでどこまでを見るのかを先に確定する**。
ここを飛ばすと、他チケットと責務が重複した成果物を作ってしまい、後から大きな手戻りになる。

1. `src/test/resources/features/_master/feature-map.html` の**決定台帳**と**チケット一覧**を読み、着手するチケットが既存の決定に触れていないかを確認する。
2. 受け入れ条件（AC）を**1項目1分岐まで分解**し、各項目の処理が実際にどの画面にあるかを仕様書・ソースで確認して「対象／対象外／要判断」に仕分ける。
3. 対象画面のエントリポイント（`initialize()` 等）の処理を先頭から順に列挙し、**ACに書かれていない処理**を観測可能性つきで洗い出す。ACは検証項目の宣言であって実装の網羅ではないため、必ず差分が出る前提で確認すること。
4. 既存チケットと境界が重なる項目を**論点**として提示し、ユーザーと合意する。決めきれないものは**赤カード**として開発チームへの確認事項にする。
5. 合意内容を決定台帳へ追記する（要承認）。
6. **【次Step移行確認】** 確定した責務の範囲を一覧で提示し、「この範囲で Step 1（ルール・実例の抽出）に進んでよろしいですか？」と確認し、合意を待つ。

> 既に責務が確定済みのチケット（決定台帳に記載があり、ACとの対応に疑義がない）の場合は、確定内容をユーザーに提示したうえで「Step 0 は確定済みとして Step 1 へ進みます」と確認を取り、スキップしてよい。

### Step 1: ルール・実例の抽出 (rule-example-extractor)

`/rule-example-extractor {機能名}` スキルの処理を実行し、仕様書からビジネスルールと実例を抽出する。

1. 仕様書（.md）を読み込み、**Step 0 で確定した責務の範囲に限定して**ビジネスルール・正常系/異常系/例外系の実例を抽出・整理する。対象外と決めた処理はルール化せず、rules.md の冒頭に「対象外とする処理」と移管先の表を記載する。
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
6. **【次Step移行確認】** 「Step 5（セルフレビュー）に進んでよろしいですか？」とユーザーに確認し、合意を待つ。

### Step 5: セルフレビュー (review-bdd-artifacts)

`/review-bdd-artifacts {機能名}` スキルの処理を実行し、**外部レビューに出す前に**成果物を自己点検する。
ここを飛ばすと、チケット本文と成果物の食い違い・検証力の弱いシナリオ・不足観点を、外部レビューで初めて指摘されることになる。

1. `docs/bdd_review_criteria.md` の観点（第1層〜第5層）に沿ってレビューを実施する。
2. **チケット本文（概要・受け入れ条件）を必ず入力に含める。** 第1層の観点はチケット本文との突き合わせでしか出ないため、欠けると収穫の過半を失う。
3. レビュー結果を提示し、ユーザーと **対応する／対応しない** の分類を合意する。
4. 「対応する」と判定した指摘は `/bdd-artifact-updater {機能名}` の処理で成果物へ反映する。
5. 「仕様担当」「実装確認」に振り分けた指摘は**赤カード**として、他チケットの責務と判定したものは**申し送り**として、それぞれ一覧に残す。
6. **【次Step移行確認】** 「Step 6（完了処理・コミット）に進んでよろしいですか？」とユーザーに確認し、合意を待つ。

> 指摘が0件になるまで繰り返す必要はない。確認先が「仕様担当」「実装確認」のものは、赤カードとして残したまま Step 6 へ進んでよい。

### Step 6: 完了処理（全体マップの更新とコミット）

1. `/feature-map update {機能名}` スキルの処理を実行し、全体マップを更新する（要承認）。
   - チケット一覧の**状態**と**成果物**の欄を更新する
   - カバレッジのルール数・シナリオ数を、実際の成果物から数えて更新する
   - 着手中に判明した責務の決定・赤カードを決定台帳へ追記する
2. 全ステップの成果物を一覧でユーザーに報告する：

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
- **責務の確定を飛ばさない**: Step 0 を経ずに Step 1 以降へ進まないこと。責務が未確定のままルールを抽出すると、他チケットと重複した成果物になる。
- **確定した責務の範囲を超えない**: Step 0 で対象外と決めた処理は、仕様書やソースに記載があってもルール化・シナリオ化しないこと。気づいた点は赤カードとして記載するに留める。
- **認証モードの区別**: 本プロダクトは予約認証モードのみが対象。常時認証モード専用の画面・処理は成果物に含めないこと。
- **参照元がiOSであること**: 仕様書・ソースはiOS版。呼称はAndroid版プロダクトの決定を優先し、iOS版の用語定義との不一致を赤カードにしないこと。iOS版は振る舞いの裏取りにのみ用いる。
- **各スキルのルール遵守**: 各Stepでは対応するスキル（rule-example-extractor / gherkin-scenario-generator / viewpoint-extractor / pbi-flow-map / review-bdd-artifacts）に定義されたガードレール・制約事項をすべて遵守すること。
- **セルフレビューを飛ばさない**: Step 5 を経ずに完了処理へ進まないこと。成果物を作った直後は食い違いに気づきにくく、外部レビューでの手戻りが大きくなる。
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
