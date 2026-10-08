# Skill: qase-annotation-writer
レビュー済みの単体テストコードに、Qaseのテストケースと紐づける `@Qase` アノテーションを追記します。

## Usage
`/qase-annotation-writer [pr_number|file_path] [feature_name]`
例: `/qase-annotation-writer 185 login`
例: `/qase-annotation-writer core/data/src/test/kotlin/.../AuthServiceImplTest.kt login`

- `pr_number`: 対象PRの番号（`gh pr diff` で対象テストを特定）
- `file_path`: ファイルパスを直接指定することも可能
- `feature_name`: 対象機能のディレクトリ名

**前提**: `/review-unit-tests` でのレビューが完了していること。レビュー前のテストに追記しないでください。

## Context / Scope
- **Gherkinシナリオ（記載内容の唯一の正本）**: `src/test/resources/features/{feature_name}/scenarios_with_viewpoints.md`
- **レビュー基準書（UT-6 の判定基準）**: `docs/unit_test_review_criteria.md`
- **記述ルール**: `docs/qase_annotation_rules.md`
- **対象リポジトリ**: `C:\Users\mforce0087\gateaccess-android`（GitHub: `bitkey-service/gateaccess-android`）
- **コミット先**: 対象PRの head ブランチ。**カレントディレクトリはQAリポジトリのため、git 操作には必ず `-C C:/Users/mforce0087/gateaccess-android` を付与します**
- **学習メモリー**: `.claude/memories/global.md` および `.claude/memories/qase-annotation-writer.md`

## Instructions
あなたはQAエンジニアとして、テストコードへの `@Qase` 追記を行ってください。

【最重要ルール】:
1. **ケースIDを推測・仮置きしてはいけません。** Qase側で採番された実際のIDのみを使用します。
2. **テストロジックを変更してはいけません。** 追加してよいのはアノテーションと必要なimport文だけです。
3. **プロダクトコード（`src/main/`）を変更してはいけません。**
4. **ユーザーの承認なしに、ファイルの編集・コミット・pushを行わないでください。**

実行前に `.claude/memories/global.md` と `.claude/memories/qase-annotation-writer.md` を読み込み、過去の指摘事項を適用してください。

---

### Step 1: 前提の確認

#### 1-0. 対象PRと作業ブランチの確認

**この確認を飛ばして Step 5 の編集へ進んではいけません。** `gateaccess-android` のカレントブランチは通常 `develop` です。確認しないまま進めると、**共有ブランチへ直接コミットする事故**になります。

**1. PRの状態を取得する**

```
gh pr view {pr_number} -R bitkey-service/gateaccess-android --json state,headRefName,isCrossRepository
```

- `state` が `MERGED` / `CLOSED` の場合は **処理を中断** し、push先が無いことを報告してユーザーに確認してください
- `isCrossRepository` が `true`（フォークからのPR）の場合も **処理を中断** してください。push 権限が無い可能性が高いため、対応方針をユーザーに確認します

**2. 作業ツリーの確認**

```
git -C C:/Users/mforce0087/gateaccess-android status --porcelain
```

- 出力がある場合は **処理を中断** し、内容を提示してユーザーの指示を仰いでください
- **`git stash` / `git checkout --` 等の破壊的操作を無断で実行してはいけません。** 開発チームの作業中の変更である可能性があります

**3. 現在のブランチを記録する**（Step 7-4 の復帰用）

```
git -C C:/Users/mforce0087/gateaccess-android branch --show-current
```

**4. PRブランチへの切り替え（承認必須）**

切り替え先（`headRefName`）を提示し、承認を得てから実行してください。

```
gh pr checkout {pr_number} -R bitkey-service/gateaccess-android
```

- 実行は `gateaccess-android` ディレクトリをカレントとして行います
- 切り替え後、`branch --show-current` が `headRefName` と一致することを確認し、報告してください

> `file_path` 指定（PR番号なし）で実行された場合、本手順はスキップします。その場合は **Step 7 のコミット・push も行いません**（対象ブランチを特定できないため）。

#### 1-1. アノテーション定義の存在確認
対象リポジトリに `Qase.kt`（`annotation class Qase`）が配置されているかを検索してください。

見つからない場合は **処理を中断** します。

> ⛔ `@Qase` の型定義が対象リポジトリに見つかりません。
> アノテーションを追記してもコンパイルが通らないため、処理を中断します。
> 開発チームへの配置依頼が完了してから、再度実行してください。

見つかった場合は、**完全修飾名（パッケージ）を記録**してください。import文の生成に使用します。

#### 1-2. 対象テストの特定
- `pr_number` 指定時: `gh pr diff {pr_number} -R bitkey-service/gateaccess-android --name-only` でテストファイルを絞り込みます
- `file_path` 指定時: そのファイルを読み込みます
- `src/androidTest/` 配下、`ExampleUnitTest.kt` は対象外です

#### 1-3. レビュー完了の確認
ユーザーに確認してください。

> 対象のテストは `/review-unit-tests` でのレビューが完了していますか？
> 未レビューの場合は、先にレビューを実施することを推奨します。

---

### Step 2: アノテーション内容の生成

Gherkinと対象テストを突き合わせ、テストごとに `@Qase` の中身を組み立てます。**ケースIDはまだ埋めません。**

#### 2-1. 各フィールドの生成ルール

| フィールド | 生成元 | ルール |
|---|---|---|
| `title` | Gherkinの**シナリオ名** | そのまま転記します。要約・言い換えをしないでください |
| `level` | Gherkinの `# @TestLevel:` | 下表に従って変換します |
| `description` | Gherkinの**ルール名・観点名** | `feature: {feature_name} / {ルール名} / 観点: {観点名}` の形式 |
| `steps` | Gherkinの Given/When/Then | `前提` + `もし` → `action`、`ならば` → `expected` |
| `id` | **Qase UIでの採番値** | Step 3 でユーザーから受け取ります |

#### 2-2. TestLevel の変換

| Gherkin記載 | `TestLevel` |
|---|---|
| `ApplicationUnit (JVM)` | `UNIT` |
| `PresentationUnit (JVM / Turbine)` | `UNIT` |
| `E2E (Cloud実機 / Nightly)` | **対象外**（追記しない） |

> Qase の Test Level は Unit / Integration / E2E / Manual の4択のため、ApplicationUnit と PresentationUnit は区別できず、いずれも `UNIT` に寄せます。

#### 2-3. steps の粒度

- **1テスト＝1ステップを基本**とします。単体テストはコード自体が手順であるため、細かく分割しても冗長になります。
- `action` には「何を準備し、何を呼び出したか」を、`expected` には「何が返る/起きるか」を日本語で記述します。
- 対応するGherkinの記述が読み取れない場合は `steps` を**省略**してください。省略するとQase側の既存ステップが保持され、空で上書きされる事故を防げます。

#### 2-4. 禁止事項

- Gherkinに書かれていない内容を創作しないこと
- シナリオ名を要約・短縮しないこと
- 英訳しないこと（日本語のまま転記します）

---

### Step 3: ケースIDの取得

#### 3-1. Qase UIでのケース作成を依頼
生成したタイトル一覧を提示し、Qase UIでのケース作成を依頼してください。

> 📋 以下のケースを Qase UI で作成し、採番されたIDを教えてください。
> 作成先は feature に対応する機能スイート配下の、該当するルールスイートです。
> （中身は空で構いません。ID採番が目的です）
>
> | # | 作成するケースのタイトル | 配置先ルールスイート |
> |---|---|---|
> | 1 | {title} | {ルール名} |
>
> 採番後、「1→{id}, 2→{id}」の形式で入力してください。
> すでにケースが存在する場合は、その既存IDを指定してください。

#### 3-2. ID未確定時の扱い
**IDが分からないテストには、絶対に仮のIDを入れないでください。** 該当テストはスキップし、レポートに「ID未採番のため見送り」と記載します。

---

### Step 4: 追記内容のプレビューと承認

追記後のコードを、テストごとに差分形式で提示してください。

```kotlin
// {ファイルパス}:{行番号}
    @Test
+   @Qase(
+       id = 101,
+       title = "単一組織のアカウントで正しい認証情報を入力するとログインが完了する",
+       level = TestLevel.UNIT,
+       description = "feature: login / ルール①: 有効な認証情報を持つユーザーはWorkhubにログインできる / 観点: 認証成功",
+       steps = [
+           QaseStep(
+               action = "単一組織に所属するユーザーで、正しいメールアドレスとパスワードを指定してログインを実行する",
+               expected = "ログインが成功し、設定読み込み画面への遷移を示す結果が返る",
+           ),
+       ],
+   )
    fun login_singleOrganization_shouldSucceed() {
```

追加するimport文もあわせて提示してください。

```kotlin
+ import jp.bitkey.app.gateaccess.shared.testing.qase.Qase
+ import jp.bitkey.app.gateaccess.shared.testing.qase.QaseStep
+ import jp.bitkey.app.gateaccess.shared.testing.qase.TestLevel
```

提示後、以下を出力して**停止**してください。

> 上記の内容で `@Qase` を追記してよろしいですか？
> - **はい**: 全件追記します
> - **一部のみ**: 追記する番号を指定してください
> - **いいえ**: 追記をキャンセルします

---

### Step 5: 追記の実行

承認後にのみ実行します。

- 対象ファイルへアノテーションとimport文を追記します。
- **既存のテストロジック・アサーション・セットアップを変更しないでください。**
- import文は既存の並び順に従って挿入してください。

---

### Step 6: コンパイル確認

追記後、対象モジュールのテストコードがコンパイルできることを確認します。

```
./gradlew :{module}:compileDevelopDebugUnitTestKotlin
```

- 失敗した場合は、エラー内容を報告し、原因（import誤り・パッケージ不一致・依存未追加など）を切り分けてください。
- **`testImplementation(projects.shared.testing)` が未追加のモジュール**ではコンパイルが通りません。その場合は「開発チームへの依存追加依頼が必要」と報告し、**自分でビルド設定を変更しないでください。**

---

### Step 7: 結果の報告とコミットの案内

#### 7-1. 結果の報告

| 項目 | 内容 |
|---|---|
| 追記したテスト | {n}件 |
| 見送ったテスト | {n}件（理由: ID未採番 / 対象外 など） |
| コンパイル確認 | 成功 / 失敗 |

#### 7-2. コミット

**コミット・pushは自動実行しません。各段階で承認を得てください。**

**1. ブランチの再確認**

```
git -C C:/Users/mforce0087/gateaccess-android branch --show-current
```

Step 1-0 で切り替えた `headRefName` と一致することを確認します。**一致しない場合は中断してください。**

**2. 変更内容の提示**

```
git -C C:/Users/mforce0087/gateaccess-android diff --stat
```

変更ファイルと行数を提示し、承認を求めます。

> 上記を `{headRefName}` へコミットしてよろしいですか？
> コミットメッセージ: `test: add @Qase annotations for {feature_name}`

**3. 実行**

承認後にのみ実行します。**`git add` には追記したテストファイルのみを明示的に指定してください。`git add -A` / `git add .` を使ってはいけません**（開発チームの無関係な変更を巻き込みます）。

#### 7-3. push

**1. リモートの取り込み**

```
git -C C:/Users/mforce0087/gateaccess-android pull --ff-only
```

- 失敗した場合（開発チームが後からコミットしている等）は **処理を中断** し、状況を報告してください
- **`--rebase` / `--force` / `push -f` を無断で実行してはいけません**

**2. 承認を求める**

> `{headRefName}` を origin へ push します。実行してよろしいですか？

**3. 実行と報告**

```
git -C C:/Users/mforce0087/gateaccess-android push origin HEAD
```

push後、対象PRのURLを報告してください。

#### 7-4. ブランチの復帰

Step 1-0 で記録した元のブランチ（通常 `develop`）へ戻すか、ユーザーに確認してください。**無断で切り替えないでください。**

#### 7-5. 残作業の案内

以下を必ず案内して終了してください。

> ⚠️ **Qaseへのケース同期はまだ完了していません。**
> developマージ後にCI（`qase_report_develop.yml`）が送るのは **実行結果とカバレッジのみ** です。
> ケース本体（title / description / Test Level / steps）の同期には `/qase-sync cases` の実行が必要です。

## Constraints (制約事項)
- **ID の厳格性**: ケースIDを推測・仮置き・連番生成しないこと。採番済みのIDのみ使用すること。
- **テストロジックの不変更**: 追加してよいのは `@Qase` アノテーションと必要なimport文のみ。アサーション・セットアップ・テスト名を変更しないこと。
- **プロダクトコードの保護**: `src/main/` 配下を変更しないこと。
- **ビルド設定の保護**: `build.gradle.kts` を変更しないこと（依存追加は開発チームの責務）。
- **進行制御**: 承認なしにファイル編集・ブランチ切り替え・コミット・pushを行わないこと。
- **ブランチの厳格性**: 編集前に必ず対象PRの head ブランチへ切り替えること。`develop` 等の共有ブランチへ直接コミットしないこと。マージ済みPR・フォークからのPRでは中断すること。
- **作業ツリーの保護**: `gateaccess-android` に未コミットの変更がある場合は中断すること。`git stash` / `git checkout --` 等を無断で実行しないこと。
- **ステージングの限定**: `git add` には追記したファイルのみを明示すること。`git add -A` / `git add .` を使わないこと。
- **履歴の保護**: `git pull --ff-only` が失敗した場合は中断すること。rebase・force push を行わないこと。
- **Gherkin準拠**: 記載内容はGherkinからの転記のみ。創作・要約・英訳をしないこと。
- **steps の省略**: 内容が読み取れない場合は `steps` を省略すること。空配列で上書きしないこと。
- **定義未配置時の中断**: `Qase.kt` が見つからない場合は、ファイルを作らず中断すること。
- **Qaseへの送信禁止**: 本スキルはコードへの追記までを行います。Qaseへの同期は別スキルの責務です。
- **リポジトリの明示**: `gh` コマンドには必ず `-R bitkey-service/gateaccess-android` を付与すること。

---

## 自己学習および指摘の蓄積ルール（最重要）

本スキルを実行する際、以下の記憶の読み込みと書き込みのプロセスを必ず実行してください。
【厳守】: 本Skillの定義ファイル自体は絶対に編集・上書きしないでください。

1. **実行前の記憶確認**:
   - タスクを開始する前に、必ず `.claude/memories/global.md` および `.claude/memories/qase-annotation-writer.md` を読み込み、過去の指摘事項を最優先のルールとして適用してください。

2. **成果物の再生成に伴う自動蓄積（トリガールール）**:
   - ユーザーの指摘や修正指示によって、一度生成した追記内容を作り直す場合、それは「初期出力に考慮漏れやルールの不一致があった」ことを意味します。
   - 追記内容を再生成する**前に**、自律的に `.claude/memories/qase-annotation-writer.md` へ物理的にファイル編集を行って追記・更新してください。

   **【書き込み・更新の手順】**
   - **① 累積件数の更新**: メモリーファイルの最上部にある「総指摘件数」の数値を +1 カウントアップして上書きしてください。
   - **② 指摘内容の追記**: 既存の内容を消さずに、以下のフォーマットに従ってファイルの末尾に追記してください。

     ### [YYYY-MM-DD] 指摘事項_{連番}
     - **対象タスク**: （例: title生成、description生成、steps生成、TestLevel変換 など）
     - **対象機能**: （例: login、initial_setup など）
     - **指摘カテゴリ**: （例: Gherkinからの転記誤り、stepsの粒度、創作の混入、import漏れ など）
     - **指摘された内容**:
     - **原因/理由**:
     - **今後の対策**:
