---
name: playbook-generator
description: playbook スキル（ブラウザ操作の手順書管理スキル）をプロジェクトに導入・更新するジェネレータ。SKILL.md + フローファイル + リファレンスファイル一式を書き出し、データディレクトリを整える。「playbook スキル追加」「playbook 導入」「playbook セットアップ」「playbook-generator」などのキーワードで起動。
---

# playbook-generator

playbook スキル（ブラウザ操作の手順書管理スキル）をプロジェクトに導入・更新するメタスキル。

## 目的と特徴

このジェネレータは、プラグインとしてインストールされた playbook-generator 経由で、各プロジェクトに**マルチファイル構成の playbook スキル**を生成する。生成されたファイルは git 管理でき、チームメンバーと共有できる。プラグイン本体を更新してジェネレータを再実行すれば、最新のテンプレートに追従できる。

## テンプレート構成

生成される playbook スキルは**マルチファイル構成**。テンプレートは `references/templates/` に配置されており、以下のファイルマッピングで配置先にコピーする：

| テンプレート | 配置先（相対パス） | 役割 |
|---|---|---|
| `templates/SKILL.md` | `SKILL.md` | サブコマンドディスパッチャ |
| `templates/references/preflight.md` | `references/preflight.md` | ブラウザ操作前の環境チェック |
| `templates/references/agent-browser-cheatsheet.md` | `references/agent-browser-cheatsheet.md` | agent-browser CLI コマンドリファレンス |
| `templates/references/flows/init.md` | `references/flows/init.md` | UI Map 生成フロー |
| `templates/references/flows/create.md` | `references/flows/create.md` | Playbook 作成フロー |
| `templates/references/flows/list.md` | `references/flows/list.md` | Playbook 一覧表示フロー |
| `templates/references/flows/resync.md` | `references/flows/resync.md` | UI Map 再スキャンフロー |
| `templates/references/flows/update.md` | `references/flows/update.md` | Playbook 手動更新フロー |
| `templates/references/flows/execute.md` | `references/flows/execute.md` | Playbook 実行フロー |

加えて、ユーザー生成データ用の `data/` ディレクトリを**空の状態で**作成する。実際のデータファイル（`ui-map.md`、個別 Playbook）は `/playbook init` および `/playbook create` の実行時にユーザーの操作を通じて生成される。

## 実行フロー

### ステップ1：プロジェクト状態の検出

以下の順で「playbook スキルの配置先」を決定する。

1. **CLAUDE.md のヒント**
   - プロジェクトルートの `CLAUDE.md` と `~/.claude/CLAUDE.md` を読み、スキル配置に関する記述（`.agents/skills/`、`~/dev/byteflare-co/claude-skills/` など）があれば候補に挙げる
   - 例: 「`.agents/skills/` に実体を置き `.claude/skills/` から symlink」→ `.agents/skills/playbook/`

2. **ディレクトリの存在チェック**
   - `.agents/skills/`（symlink 方式）が存在 → `.agents/skills/playbook/` を候補
   - `~/dev/byteflare-co/claude-skills/`（ユーザーレベル一元管理）が存在 → 候補として提示
   - いずれも無い → デフォルト `.claude/skills/playbook/`

3. **既存の playbook スキルの検出**
   - 候補ディレクトリに `SKILL.md` が既存なら「更新モード」として扱う
   - 新規配置か更新か、ユーザーに明示する

### ステップ2：AskUserQuestion で配置先を確認

検出結果をもとに、AskUserQuestion で候補を提示する。選択肢の例：

```
検出したプロジェクト状態:
- .agents/skills/ ディレクトリあり（symlink 方式）
- 既存の .agents/skills/playbook/SKILL.md あり（更新日: ...）

playbook スキルをどこに配置しますか？
  [1] .agents/skills/playbook/（推奨: 既存を更新）
  [2] .claude/skills/playbook/（標準）
  [3] ~/dev/byteflare-co/claude-skills/playbook/（ユーザーレベル）
  [4] カスタムパスを入力
```

- 既存がある場合は、変更のあるファイルの diff を Bash の `diff` で見せてから上書き可否を確認する
- カスタムパスが選ばれたら、書き込み可否を確認する

### ステップ3：テンプレートファイル一式を書き込む

1. テンプレートマッピング表（上記）に従い、各テンプレートを `Read` で読み込む
2. 選択された配置先に対して、ディレクトリ構成を作成する:

   ```bash
   mkdir -p <配置先>/references/flows
   mkdir -p <配置先>/data
   ```

3. 各テンプレートファイルを配置先に書き込む
4. 既存ファイルがあり上書きが選ばれた場合、事前に `.bak` サフィックスでバックアップを取る

**パス置換**: テンプレート内の `<skill-root>` プレースホルダは、配置先が**デフォルト（`.claude/skills/playbook/`）以外**の場合に、テンプレート中のパス参照をユーザーに注意喚起する。テンプレート内のパスは相対パス（`references/flows/init.md`, `data/ui-map.md`）で記述されており、Claude Code のスキル解決が配置先を認識するため、通常は置換不要。

### ステップ4：配置先の git 管理状態を確認

1. 選択された配置先が git 管理対象か確認する（`git check-ignore <path>` で ignore されていないか確認）
2. ignore されている場合はユーザーに通知し、`.gitignore` の whitelist 追加を提案する
3. `.agents/skills/` に配置した場合は、プロジェクトで symlink-skills 方式が使われているか確認する。`.claude/skills` が `.agents/skills` への symlink になっていない場合は、その旨を通知する

### ステップ5：完了レポート

以下のフォーマットで報告する:

```
playbook スキルを導入しました

配置先: <パス>/
  SKILL.md                              ← ディスパッチャ
  references/preflight.md               ← 環境チェック
  references/agent-browser-cheatsheet.md ← CLI リファレンス
  references/flows/                     ← フローファイル（6ファイル）
  data/                                 ← ユーザー生成データ（init で作成）

使い方:
  /playbook init [URL]   - 対象プロダクトを巡回して UI Map を生成
  /playbook create       - 新しい Playbook を作成
  /playbook list         - 登録済み Playbook を一覧表示
  /playbook resync       - UI を再スキャンして差分を反映
  /playbook update       - Playbook を手動で更新
  /playbook [操作名]     - Playbook を実行

次のアクション:
  - チームに共有する場合: git add <配置先ディレクトリ> && git commit
  - すぐ使う場合: /playbook init https://example.com
  - agent-browser の導入: npm install -g agent-browser（または mise で管理）
```

## 更新時の挙動

既存の playbook スキルが存在する場合、ジェネレータは「更新モード」として動作する。

1. 既存の `SKILL.md` の冒頭の `name:` フィールドを確認し、本当に playbook スキルかを検証
2. テンプレートマッピング表の各ファイルについて、既存ファイルとテンプレートの差分を Bash `diff` で確認
3. 変更のないファイルはスキップし、変更のあるファイルのリストを提示:

   ```
   更新対象ファイル（N件）:
     [変更あり] SKILL.md
     [変更あり] references/flows/execute.md
     [変更なし] references/preflight.md（スキップ）
     ...
   ```

4. AskUserQuestion で以下を提示:
   - [1] 変更ありの全ファイルを上書き（`.bak` にバックアップ）
   - [2] ファイルごとに個別確認
   - [3] スキップ（何も変更しない）

5. 「ファイルごとに個別確認」が選ばれた場合、各ファイルの diff を表示して y/n で確認

**注意**: `data/` ディレクトリ内のユーザー生成ファイル（`ui-map.md`、個別 Playbook）は**絶対に上書きしない**。更新対象はテンプレートから生成されたファイルのみ。

## 設計上の注意

- このジェネレータは**テンプレートディレクトリを配置先にコピーする**のが基本。テンプレートへの動的な置換は必要最小限に留める
- 生成したファイル群はプロジェクトのリポジトリに git commit されることを前提にする
- プラグインの更新＝テンプレートの更新なので、ユーザーは `npx skills update playbook-generator` 後にこのジェネレータを再実行すれば最新版に追従できる
- **生成される playbook はブラウザ操作実行を Subagent (Sonnet) に委譲する設計**:
  Opus セッションから `model: "sonnet"` 指定の `general-purpose` Subagent に
  execute / create / resync フローを逃がすことで、ルーチンなブラウザ操作のコスト最適化と
  メインコンテキストの保護を両立する。詳細はテンプレートの SKILL.md「Dispatch contract」参照。
  Claude Code の per-invocation `model` override 仕様
  （https://code.claude.com/docs/en/sub-agents#choose-a-model）に依拠している

## アンチパターン

- ❌ テンプレートを直接編集する（テンプレート更新はジェネレータの責務でなく、元のマーケットプレイスリポジトリで行うこと）
- ❌ 配置先の `.gitignore` 設定を確認せずに書き込む（意図せず ignore された場所に書いてしまう事故を防ぐ）
- ❌ 既存 SKILL.md を無断で上書きする（必ず diff 確認と確認を挟む）
- ❌ `data/` ディレクトリ内のユーザー生成ファイルを上書き・削除する（ユーザーのデータを破壊する事故を防ぐ）
