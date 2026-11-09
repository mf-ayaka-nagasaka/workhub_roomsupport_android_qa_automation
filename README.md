# workhub_roomsupport_android_qa_automation

## ドキュメント

| ドキュメント | 内容 |
|---|---|
| [品質判定基準フレームワーク](docs/quality_criteria_framework/README.md) | ISO/IEC 25010:2023 に基づく品質判定基準の作成フレームワーク |
| [品質評価計画書（workhub Room Support）](docs/quality_criteria/workhub_roomsupport/criteria.md) | 本プロダクトの品質判定基準（18指標）。正本は Notion で、本ファイルは参照用の写し |
| [テスト観点 標準モデル](docs/test_viewpoints/standards/) | ISO 25010 / OWASP Mobile Top 10 の観点辞書 |
| [単体テストレビュー基準書](docs/unit_test_review_criteria.md) | 開発チームの単体テストをQA視点でレビューするための観点・チェックリスト |
| [BDDテスト設計成果物 レビュー基準書](docs/bdd_review_criteria.md) | 作成したGherkinシナリオ・ルール・観点をセルフレビューするための観点・チェックリスト |
| [`@Qase` アノテーション記述ルール](docs/qase_annotation_rules.md) | テストコードとQaseケースを紐づけるアノテーションの書き方 |
| [Qase連携セットアップ手順](docs/qase_integration_setup.md) | 本番リポジトリへのQase連携基盤の導入手順（開発チーム向け依頼内容を含む） |
| [Qase同期の運用手順](docs/qase_sync_operation.md) | `@Qase` の抽出・ケース同期の操作手順（結果送信はCIが自動実行） |
| [Claude Code Skill一覧](.claude/commands/README.md) | QAワークフロー支援Skill |
| [BDDテスト設計の全体マップ](src/test/resources/features/_master/feature-map.html) | 全チケットと画面・内部処理の対応、責務の決定台帳、カバレッジ、品質判定基準の担保先 |
