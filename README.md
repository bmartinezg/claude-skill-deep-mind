# Deep Mind

Shared brain that keeps all projects within an organization synchronized. Claude analyzes each project, extracts valuable shared elements (branding, env variables, tech stack, API contracts, business logic, etc.), and you decide what enters the matrix.

When you work on any sibling project, Claude already knows the shared context — colors, endpoints, data models, copy, architecture patterns — without you having to repeat yourself.

## Install

### 1. Download the skill file

Download `deep-mind.skill` from the [latest release](https://github.com/bmartinezg/deep-mind/releases) or clone the repo:

```bash
git clone https://github.com/bmartinezg/deep-mind.git
```

### 2. Install in Claude Code

```bash
claude install-skill /path/to/deep-mind
```

Or if you downloaded the `.skill` file directly:

```bash
claude install-skill /path/to/deep-mind.skill
```

### 3. Verify

Open Claude Code in any project and say:

```
deep-mind
```

Claude will check if the project belongs to a matrix and guide you through the setup.

## How It Works

1. **Say "deep-mind"** in any project — Claude scans the codebase and detects shareable elements
2. **Pick what to sync** — you get a checklist of findings (branding, env vars, tech stack, etc.)
3. **Selected items enter the matrix** — stored in `~/.claude/deep-mind/<matrix-name>/`
4. **Open a sibling project** — Claude loads the shared context automatically
5. **Proactive updates** — when Claude spots new shareable info while working, it proposes syncing it

## Supported Verticals

| Vertical | Examples |
|----------|----------|
| branding | Colors, fonts, design tokens, logos |
| env-variables | API keys, DB hosts, feature flags |
| tech-stack | Frameworks, languages, versions |
| api-contracts | Endpoints, schemas, auth patterns |
| business-logic | Domain rules, pricing, permissions |
| data-models | DB schemas, ORM models, entities |
| auth-patterns | Auth middleware, RBAC, sessions |
| copy-messaging | i18n strings, UI text, error messages |
| architecture | Folder conventions, module patterns |
| dependencies | Shared packages, version constraints |

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI
- Python 3.8+

## License

MIT
