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

### playbook

ブラウザ操作の手順書（Playbook）を管理・実行する統合スキル。UI Map を自動生成し、繰り返し使う操作を再利用可能な Playbook として記録・実行できる。

**Installation:**
```
/plugin install playbook@byteflare-skills
```

**Subcommands:**

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

プラグインを更新しても既存の Playbook データは影響を受けません。

**Features:**
- テキストラベル（role + name）ベースの安定した要素指定
- 制約・制限事項の事前チェック（アンチパターン回避）
- 公式ドキュメント参照による実行可否判断
- ドメイン知識のインタビューで UI に現れない業務ロジックも記録

---

## License

MIT
