# sustella-website
SUSTELLA公式ホームページ

## 構成

- `site/`：Cloudflareに公開するHP、PDF、フォント、アクセス解析の案内
- `site/data/note.json`：noteの最新3記事まで（現在は2記事）
- `site/assets/note.js`：タイトル・日付・サムネイルをカード表示
- `scripts/update_note.py`：公式RSSをJSONに変換。外部ライブラリー不要
- `.github/workflows/publish.yml`：定期更新・コミット・Cloudflareへの公開

公開済みの `sustella-home` と `www.sustella-jp.com` を継続して使います。
既存の手動アップロード用Pagesプロジェクトには後からGit連携を付けられないため、GitHub Actionsから同じPagesプロジェクトにファイルを送信します。GitHubに加えた記事の変更は、この方式で自動反映できます。

## 毎日の更新

日本時間9:00（仮設定）に `https://note.com/sustella_jp/rss` を取得します。
最新順に最大3件へ絞り、JSONが変わったときだけコミットします。
同じ実行内でCloudflareへ送信します。GitHub Actions自身のコミットでは別のpushワークフローが起動しないため、別ジョブの起動には依存しません。

RSSの取得失敗・不正なRSS・記事0件の場合は失敗として終了し、前回のデータと公開サイトを維持します。公開に失敗した場合は、Actionsで再実行するか、次の定期実行で再試行します。
**GitHubの定期実行は遅れることがあり、9:00ちょうどの反映は保証されません。** 公開リポジトリに60日間活動がない場合は定期実行が無効になることがあるため、その際はActions画面で再開してください。

## Cloudflare接続（まだ無効）

公開ファイルの準備と、実際の公開を分けています。初期状態では定期的なRSS更新だけが動作し、Cloudflareへの送信は行いません。

1. CloudflareでAPIトークンを作り、対象アカウントの **Account / Cloudflare Pages / Edit** 権限を付けます。
2. GitHubの **Settings → Secrets and variables → Actions → Secrets** に以下の2項目を保存します。
   - `CLOUDFLARE_ACCOUNT_ID`：現在のCloudflareアカウントID
   - `CLOUDFLARE_API_TOKEN`：上記トークン
3. 公開承認者2名の確認後、同画面の **Variables** に `ENABLE_CLOUDFLARE_DEPLOY` を作り、値を `true` にします。
4. **Actions → Update note and publish website → Run workflow** を実行します。
5. 完了後、`https://www.sustella-jp.com` で記事カード、PDF、スマホメニューを確認します。

APIトークンはコード・README・チャットに書かず、GitHub Secretsだけに保存してください。
既存プロジェクトのproduction branchはCloudflareから取得して使うため、公開先がプレビュー環境に変わることを防ぎます。
DNS・メール用レコードの再設定は不要です。

## 日常の変更と公開

文章・デザインは `site/` を修正します。自動公開を有効にした後はmainの変更が公開されるため、提案用ブランチで確認し、承認済みの変更だけをmainへ反映します。
記事はnote上で公開した最新3件を自動で掲載します。記事ごとの掲載承認を追加したい場合は、RSSの自動コミット先を確認用ブランチへ変更してください。

このリポジトリは公開用ファイルのみを含み、内部の制作メモ、過去の原稿、認証情報は含めません。
計測はGA4（`G-V0Z1WVBZR7`）で、公開ドメインのみ有効です。ローカル・pages.devでは計測しません。
現在は仮公開用の `noindex` / robots.txt設定を維持しています。

## 費用

公開リポジトリの標準Ubuntuランナーと、Cloudflare Pagesの静的配信を使います。大型ランナー、有料Functions、ストレージ追加、Actions成果物保存は使用しません。

## ローカル確認

Python 3.12以上で `python -m unittest discover -s tests -v` を実行します。
RSS更新は `python scripts/update_note.py`。ローカルのRSSで確認するときは `--input <RSSファイル>` を指定できます。
ブラウザーで `site/index.html` を直接開く場合は初期カードを表示し、HTTPで開いた場合は最新のJSONを読み込みます。

## 公式資料

- [Cloudflare PagesのCIからの公開](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/)
- [GitHub Actionsの定期実行](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [GitHub Actionsの料金](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
