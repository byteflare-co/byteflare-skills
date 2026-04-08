---
name: playbook-generator
description: playbook スキル（ブラウザ操作の手順書管理スキル）をプロジェクトに導入・更新するジェネレータ。`.claude/skills/playbook/SKILL.md` などに SKILL.md を書き出し、データディレクトリ（`.claude/playbook/`）と gitignore 設定を整える。「playbook スキル追加」「playbook 導入」「playbook セットアップ」「playbook-generator」などのキーワードで起動。
---

# playbook-generator

playbook スキル（ブラウザ操作の手順書管理スキル）をプロジェクトに導入・更新するメタスキル。

## 目的と特徴

このジェネレータは、プラグインとしてインストールされた playbook-generator 経由で、各プロジェクトに**ファイルベースの playbook スキル**を生成する。生成されたファイルは git 管理でき、チームメンバーと共有できる。プラグイン本体を更新してジェネレータを再実行すれば、最新の SKILL.md に追従できる。

## テンプレート

生成される playbook SKILL.md のテンプレートは、このスキルと同じディレクトリの `references/playbook-skill-template.md` に配置されている。ジェネレータはこのファイルを読み込んで、検出した配置先にコピーする。

## 実行フロー

### ステップ1：プロジェクト状態の検出

以下の順で「playbook SKILL.md の配置先」を決定する。

1. **CLAUDE.md のヒント**
   - プロジェクトルートの `CLAUDE.md` と `~/.claude/CLAUDE.md` を読み、スキル配置に関する記述（`.agents/skills/`、`~/dev/byteflare-co/claude-skills/` など）があれば候補に挙げる
   - 例: 「`.agents/skills/` に実体を置き `.claude/skills/` から symlink」→ `.agents/skills/playbook/SKILL.md`

2. **ディレクトリの存在チェック**
   - `.agents/skills/`（symlink 方式）が存在 → `.agents/skills/playbook/` を候補
   - `~/dev/byteflare-co/claude-skills/`（ユーザーレベル一元管理）が存在 → 候補として提示
   - いずれも無い → デフォルト `.claude/skills/playbook/`

3. **既存の playbook スキルの検出**
   - `.agents/skills/playbook/SKILL.md` または `.claude/skills/playbook/SKILL.md` が既存なら「更新モード」として扱う
   - 新規配置か更新か、ユーザーに明示する

### ステップ2：AskUserQuestion で配置先を確認

検出結果をもとに、AskUserQuestion で候補を提示する。選択肢の例：

```
検出したプロジェクト状態:
- .agents/skills/ ディレクトリあり（symlink 方式）
- 既存の .agents/skills/playbook/SKILL.md あり（バージョン: ..., 更新日: ...）

playbook スキルをどこに配置しますか？
  [1] .agents/skills/playbook/SKILL.md（推奨: 既存を更新）
  [2] .claude/skills/playbook/SKILL.md（標準）
  [3] ~/dev/byteflare-co/claude-skills/playbook/SKILL.md（ユーザーレベル）
  [4] カスタムパスを入力
```

- 既存がある場合は、既存のファイルとテンプレートの diff を Bash の `diff` で見せてから上書き可否を確認する
- カスタムパスが選ばれたら、書き込み可否を確認する

### ステップ3：SKILL.md を書き込む

1. `references/playbook-skill-template.md` の内容を読み込む
2. 選択された配置先に書き込む（親ディレクトリが存在しない場合は `mkdir -p` で作成）
3. 既存ファイルがあり上書きが選ばれた場合、事前に `.bak` サフィックスでバックアップを取る

生成される playbook SKILL.md は、UI Map や個別 Playbook データをスキル自身の `references/` サブディレクトリ（例: `.agents/skills/playbook/references/`）に保存する設計。スキル本体とデータが同じ場所にあるため、配置先のディレクトリが git 管理されていれば自動的にチーム共有できる（`.gitignore` の追加調整は不要）。

### ステップ4：配置先の git 管理状態を確認

1. 選択された配置先が git 管理対象か確認する（`git check-ignore <path>` で ignore されていないか確認）
2. ignore されている場合はユーザーに通知し、`.gitignore` の whitelist 追加を提案する
3. `.agents/skills/` に配置した場合は、プロジェクトで symlink-skills 方式が使われているか確認する。`.claude/skills` が `.agents/skills` への symlink になっていない場合は、その旨を通知する

### ステップ5：完了レポート

以下のフォーマットで報告する:

```
✅ playbook スキルを導入しました

📂 配置先:
  SKILL.md: <パス>
  データ保存場所: <パス>/references/

🚀 使い方:
  /playbook init [URL]   - 対象プロダクトを巡回して UI Map を生成
  /playbook create       - 新しい Playbook を作成
  /playbook list         - 登録済み Playbook を一覧表示
  /playbook [操作名]     - Playbook を実行
  /playbook update       - Playbook を更新

📝 次のアクション:
  - チームに共有する場合: `git add <配置先ディレクトリ> && git commit`
  - すぐ使う場合: `/playbook init https://example.com`
```

## 更新時の挙動

既存の SKILL.md が存在する場合、ジェネレータは「更新モード」として動作する。

1. 既存ファイルの冒頭の `name:` と `description:` フィールドを確認し、本当に playbook スキルかを検証
2. 既存ファイルとテンプレートの差分を Bash `diff` で表示
3. 差分が無ければ「既に最新です」と伝えて終了
4. 差分がある場合、AskUserQuestion で以下を提示:
   - [1] 上書き（`.bak` にバックアップ）
   - [2] スキップ
   - [3] 差分の一部だけ手動で適用する（対話的マージは不可なので、この場合は既存ファイルを Read して差分箇所をユーザーに指示してもらう）

## 設計上の注意

- このジェネレータは**テンプレートを機械的にコピーするだけ**が基本。テンプレートへの動的な置換は必要最小限に留める
- 生成した SKILL.md はプロジェクトのリポジトリに git commit されることを前提にする
- プラグインの更新＝テンプレートの更新なので、ユーザーは `claude plugin marketplace update byteflare-skills` 後にこのジェネレータを再実行すれば最新版に追従できる

## アンチパターン

- ❌ テンプレートを直接編集する（テンプレート更新はジェネレータの責務でなく、元のマーケットプレイスリポジトリで行うこと）
- ❌ 配置先の `.gitignore` 設定を確認せずに書き込む（意図せず ignore された場所に書いてしまう事故を防ぐ）
- ❌ 既存 SKILL.md を無断で上書きする（必ず diff 確認と確認を挟む）
