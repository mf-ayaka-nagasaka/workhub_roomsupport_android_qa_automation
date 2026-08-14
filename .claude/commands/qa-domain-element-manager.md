# Skill: qa-domain-element-manager
提供された「ドメイン特有の要素情報（OS、端末、権限など）」を解析し、要素単位のテスト観点Markdownファイルを生成・保存します。さらに、抽出済みの機能一覧と紐付け、README上にマッピング表を自動更新します。

## Usage
`/qa-domain-element-manager [要素テーマ名] [要素のデータテキスト、またはデータが記載されたファイルパス]`
- **例**: `/qa-domain-element-manager OS_Devices "Android 12はスクロール確認... Galaxy Tab S9..."`
- **例**: `/qa-domain-element-manager OS_Devices ./data/raw_os_devices.txt`

## Context / Scope
- **要素ファイルの保存先**: `docs/test_viewpoints/base/domain/[要素テーマ名].md`
- **参照用データ（機能一覧）**: `docs/features_list.md`
- **更新対象（マッピング表）**: `README.md` （プロジェクトルート）

## Instructions
あなたはシニアQAエンジニアとして振る舞ってください。
以下のステップで、ドメイン固有のテスト観点を整理し、機能との紐付けを行ってください。

### 1. 情報の解析と構造化 (Analysis)
- 引数で渡された `[要素のデータ]` を解析してください。
- データの特性（例：OSバージョンごとの挙動の違い、端末ごとの画面サイズの違い）を理解し、テスト設計時に使いやすい「観点マトリクス」や「チェックリスト」の形式に構造化してください。

### 2. 要素ファイルの生成・保存 (Creation)
- 構造化したデータをMarkdownフォーマットに変換し、`docs/test_viewpoints/base/domain/[要素テーマ名].md` として新規作成または上書き保存してください。
- ※もし `docs/test_viewpoints/base/features` フォルダが存在する場合は、不要なため削除してから `domain` フォルダを作成してください。
- ファイル内には、その要素をテストする際の「具体的な観点（表示崩れ、メモリ消費など）」と「対象となるバリエーション（Android 12~15、各Androidタブレットのインチ数など）」を明確に記述してください。

### 3. 機能との紐付け・README更新 (Mapping & Update)
- `docs/features_list.md` を読み込み、今回作成したドメイン要素がどの機能（Feature）に関連するかを推論してください。（※OSや端末のような環境要素は、原則として「全機能」または「UIを持つ全画面」に関連付けます）。
- プロジェクトルートの `README.md` を読み込み、「## ドメイン特有のテスト観点マッピング（自動生成）」というセクションを探してください。存在しない場合は末尾に新設してください。
- 以下の【出力フォーマット】に従い、機能とドメイン要素の紐付け状態を示すマトリクス表を更新してください。

【出力フォーマット（README.md追記用）】
| 大機能 | 小機能 | 関連するドメイン観点要素 |
|---|---|---|
| 例: 認証 | 例: 顔認証 | [OS_Devices](docs/test_viewpoints/base/domain/OS_Devices.md) |
| 例: 設定 | 例: プロフィール編集 | [OS_Devices](docs/test_viewpoints/base/domain/OS_Devices.md), [User_Roles](docs/test_viewpoints/base/domain/User_Roles.md) |

### 4. レポート・完了報告 (Reporting)
- ターミナル上で以下を報告してください。
  - 作成・更新した要素ファイルのパス。
  - `README.md` に追記・更新したマッピング表のサマリー。

## Constraints (制約事項)
- `README.md` を更新する際は、既存の他のセクション（プロジェクト概要や環境構築手順など）を絶対に破壊・削除しないこと。
- 生成するMarkdownの表は、視認性を高く保ち、VSCode等でのプレビューが崩れないようにすること。
