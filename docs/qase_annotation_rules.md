# `@Qase` アノテーション記述ルール

| 項目 | 内容 |
|---|---|
| **象限** | 📗 リファレンス |
| **対象者** | QA担当（テストコードへの `@Qase` 追記者） |
| **ゴール** | Gherkinシナリオから `@Qase` の各フィールドを一意に導出でき、Qaseへ同期しても意図どおりの内容になる書き方が分かるようになります |

本書は、単体テストコードに付与する `@Qase` アノテーションの**書き方の取り決め**です。アノテーションの型定義そのものは対象リポジトリ側（`core/testing`）にあり、本書はその**中身の書式**を定めます。

---

## 1. 前提

### 1.1 アノテーションの役割

`@Qase` は、**テストコードとQaseのテストケースを紐づける**ためのものです。付与された内容は同期スクリプトによってQaseへ反映され、**コード側が正本**になります。

> ⚠️ **同期はコード → Qase の一方向です。** Qase UI上でタイトルや説明を編集しても、次回の同期で上書きされます。これらの項目はコード側で編集してください。

### 1.2 誰が書くか

| 作業 | 担当 |
|---|---|
| アノテーション型定義（`Qase.kt`）の配置 | 開発チーム |
| テストコードへの `@Qase` 追記 | **QA担当** |
| Qaseへの同期実行 | QA担当 |

### 1.3 追記のタイミング

`/review-unit-tests` でのレビュー完了後、**PRがマージされる前**に追記します。レビュー前のテストに追記すると、レビューで修正が入った際に内容が合わなくなります。

---

## 2. 各フィールドの記述ルール

### 2.1 一覧

| フィールド | 必須 | 生成元 | 同期時の挙動 |
|---|---|---|---|
| `id` | ✅ | **Qase UIでの採番値** | 紐づけキー。同期対象外 |
| `title` | ✅ | Gherkinのシナリオ名 | Qase側を上書き |
| `level` | ✅ | Gherkinの `# @TestLevel:` | Qase側を上書き |
| `description` | 任意 | Gherkinのルール名・観点名 | Qase側を上書き |
| `steps` | 任意 | Gherkinの Given / When / Then | **省略時はQase側を変更しない** |

### 2.2 `id` — ケースID

**Qaseが採番した実際のIDのみを使用します。**

Qase はケース作成時にIDを指定できないため、**「Qase UIでケースを作成する → 採番されたIDをコードに転記する」** という手順が必須です。これが本運用で唯一残る手作業です。

- 採番前のテストには**仮のIDを入れないでください。** 存在しないIDは同期時のプリフライト検証で処理全体が中断されます
- IDが未確定のテストは、追記を見送ります

### 2.3 `title` — タイトル

**Gherkinのシナリオ名をそのまま転記します。**

```
シナリオ: 単一組織のアカウントで正しい認証情報を入力するとログインが完了する
   ↓
title = "単一組織のアカウントで正しい認証情報を入力するとログインが完了する"
```

- 要約・短縮・言い換えをしないでください
- 英訳しないでください（日本語のまま転記します）
- シナリオ名を変えたい場合は、**Gherkin側を直してから**転記します

### 2.4 `level` — テストレベル

Gherkinの `# @TestLevel:` コメントから変換します。

| Gherkin記載 | `TestLevel` |
|---|---|
| `ApplicationUnit (JVM)` | `UNIT` |
| `PresentationUnit (JVM / Turbine)` | `UNIT` |
| `E2E (Cloud実機 / Nightly)` | 追記対象外 |

> Qase の `Test Level` は Unit / Integration / E2E / Manual の4択です。ApplicationUnit と PresentationUnit を区別する選択肢が無いため、いずれも `UNIT` に寄せています。区別が必要になった場合は、Qase側の選択肢追加から検討します。

### 2.5 `description` — 説明

**トレーサビリティを確保するための項目**です。次の形式で記述します。

```
feature: {feature名} / {ルール名} / 観点: {観点名}
```

記述例:

```
feature: login / ルール①: 有効な認証情報を持つユーザーはWorkhubにログインできる / 観点: 認証成功
```

ケースIDの正本はテストコード側にあるため、**Gherkin側からは「どのテストがどのシナリオに対応するか」を辿れません。** `description` にこの参照を書くことで、Qase上からも対応関係が読めるようにします。

各要素の取得元:

| 要素 | Gherkin内の該当箇所 |
|---|---|
| feature名 | ファイルの配置ディレクトリ名 |
| ルール名 | `# ルール①: …` のコメント行 |
| 観点名 | `# 📐 観点：…` のコメント行 |

### 2.6 `steps` — ステップ

`action` に Arrange + Act、`expected` に Assert を対応させます。Gherkinでは `前提`（Given）と `もし`（When）が `action`、`ならば`（Then）が `expected` です。

```kotlin
steps = [
    QaseStep(
        action = "単一組織に所属するユーザーで、正しいメールアドレスとパスワードを指定してログインを実行する",
        expected = "ログインが成功し、設定読み込み画面への遷移を示す結果が返る",
    ),
]
```

**粒度は1テスト＝1ステップを基本とします。** 単体テストはコード自体が手順であり、細かく分割しても冗長になるためです。

> **内容が読み取れない場合は `steps` を省略してください。** 省略するとQase側の既存ステップが保持されます。空配列で上書きすると、Qase上のステップが消えます。

---

## 3. 記述例

```kotlin
import jp.bitkey.app.gateconnector.core.testing.qase.Qase
import jp.bitkey.app.gateconnector.core.testing.qase.QaseStep
import jp.bitkey.app.gateconnector.core.testing.qase.TestLevel

class LoginViewModelTest {

    @Test
    @Qase(
        id = 101,
        title = "単一組織のアカウントで正しい認証情報を入力するとログインが完了する",
        level = TestLevel.UNIT,
        description = "feature: login / ルール①: 有効な認証情報を持つユーザーはWorkhubにログインできる / 観点: 認証成功",
        steps = [
            QaseStep(
                action = "単一組織に所属するユーザーで、正しいメールアドレスとパスワードを指定してログインを実行する",
                expected = "ログインが成功し、設定読み込み画面への遷移を示す結果が返る",
            ),
        ],
    )
    fun login_singleOrganization_shouldSucceed() = runTest {
        // テストロジックは変更しない
    }
}
```

> `import` のパッケージは、対象リポジトリでの `Qase.kt` の実際の配置先に合わせてください。

---

## 4. やってはいけないこと

| 禁止事項 | 理由 |
|---|---|
| ケースIDの推測・仮置き・連番生成 | 存在しないIDは同期時のプリフライト検証で処理全体が中断されます |
| 同じIDを複数のテストに付与 | 同じくプリフライト検証で中断されます |
| Gherkinに無い内容の創作 | Gherkinが正本です。必要ならGherkin側を直してから転記します |
| シナリオ名の要約・英訳 | Qase上の表記が揺れ、対応関係が追えなくなります |
| `steps = []`（空配列）での上書き | Qase側の既存ステップが消えます。省略してください |
| テストロジックの変更 | 追記してよいのはアノテーションとimport文のみです |
| `build.gradle.kts` の変更 | 依存追加は開発チームの責務です |

---

## 5. 追記後の確認

| 確認項目 | 方法 |
|---|---|
| コンパイルが通るか | `./gradlew :{module}:compileDevelopDebugUnitTestKotlin` |
| IDの重複が無いか | 同期スクリプトのプリフライト検証で自動チェックされます |
| Qaseへの反映内容 | 同期実行後、Qase UIまたはAPIで読み取って確認します |

コンパイルエラーが出た場合の主な原因は次のとおりです。

| 症状 | 原因 |
|---|---|
| `Unresolved reference: Qase` | import文の誤り、または対象モジュールに `testImplementation(projects.core.testing)` が未追加 |
| `Unresolved reference: TestLevel` | 同上 |
| 型の不一致 | `id` は `Long` です。`id = 101` のように整数リテラルで記述します |
