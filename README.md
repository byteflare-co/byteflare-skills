# byteflare-skills

Byteflare の Claude Code プラグインコレクション。

## Installation

```
/plugin marketplace add byteflare-co/byteflare-skills
```

インストール後、各プラグインを個別にインストール:

```
/plugin install spec-skills-generator@byteflare-skills
/plugin install playbook@byteflare-skills
```

## Plugins

### spec-skills-generator

Auto-generate 3-layer specification documents and maintenance skills for any codebase.

**Installation:**
```
/plugin install spec-skills-generator@byteflare-skills
```

**What It Does:**

- **3-layer specification documents**: Overview (`01_overview.md`), Business Spec (`02_business_spec.md`), Technical Spec (`03_technical_spec.md`)
- **`/spec` skill**: Q&A skill for querying your specifications
- **`/spec-maintenance` skill**: Keeps specs in sync with code changes
- **`check_spec_drift.py`**: Automated drift detection script
- **CLAUDE.md integration**: Impact mapping section for your project

**Usage:**
```
/spec-skills-generator:spec-skills-generator
```

The skill will:
1. Auto-detect your project structure (languages, entry points, IaC, tests, etc.)
2. Ask configuration questions (output directory, existing docs)
3. Deep-analyze your codebase
4. Generate 3-layer spec documents
5. Create `/spec` and `/spec-maintenance` skills
6. Set up drift detection and CLAUDE.md integration

**Generated Files:**

| File | Description |
|------|-------------|
| `docs/specification/01_overview.md` | Project overview, architecture, component catalog |
| `docs/specification/02_business_spec.md` | Business rules, domain model, use cases |
| `docs/specification/03_technical_spec.md` | API specs, data models, infrastructure |
| `.claude/skills/spec/SKILL.md` | `/spec` Q&A skill |
| `.claude/skills/spec-maintenance/SKILL.md` | `/spec-maintenance` skill |
| `scripts/check_spec_drift.py` | Spec-code drift checker |

**Requirements:**
- Claude Code CLI
- Python 3.10+

---

### playbook-generator

playbook スキル（ブラウザ操作の手順書管理スキル）を各プロジェクトに**ファイルベースで生成**するメタスキル。spec-skills-generator と同じパターンで、生成された SKILL.md は git 管理・チーム共有が可能。

**Installation:**
```
/plugin install playbook-generator@byteflare-skills
```

**Usage:**
```
/playbook-generator:playbook-generator
```

ジェネレータは以下を実行します:
1. プロジェクトの CLAUDE.md・ディレクトリ構造を検出し、配置先の候補を提示
2. `.agents/skills/playbook/` または `.claude/skills/playbook/` など、選択された場所に SKILL.md を書き出し
3. `./.claude/playbook/` データディレクトリを初期化
4. 必要に応じて `.gitignore` に whitelist エントリを追記

**Generated skill features:**

生成された playbook スキルは以下のサブコマンドを提供します:

| コマンド | 説明 |
|---------|-----|
| `/playbook init [URL]` | 対象プロダクトを巡回して UI Map を生成 |
| `/playbook create` | 新しい Playbook を作成 |
| `/playbook list` | 登録済み Playbook を一覧表示 |
| `/playbook update` | 既存の Playbook を更新 |
| `/playbook [操作名]` | 指定した Playbook を実行 |

**Data Storage:**

Playbook データはプロジェクトルートの `./.claude/playbook/` に保存されます:

- `./.claude/playbook/ui-map.md` — UI Map と Playbook の索引
- `./.claude/playbook/[name].md` — 個別の Playbook ファイル

**Updating:**

ジェネレータのテンプレートを更新した後、各プロジェクトで再実行すれば最新の SKILL.md に追従できます:

```
/plugin marketplace update byteflare-skills
/playbook-generator:playbook-generator
```

既存の SKILL.md と差分がある場合、diff を表示してから上書きします（バックアップ自動作成）。

---

## License

MIT
