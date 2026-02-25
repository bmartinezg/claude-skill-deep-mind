---
name: deep-mind
description: Shared brain synchronization across multi-project organizations. Automatically analyzes a project, detects valuable shared elements (branding, env variables, tech stack, API contracts, business logic, etc.), and lets the user choose which verticals to sync into a shared matrix. Maintains consistency across all sibling projects (mobile app, landing, backend, iOS, Android). Use when the user says "deep-mind", "sync brain", "shared context", "sync projects", "matrix", or when working on a project that needs cross-project consistency. Also triggers when user wants to share context, brand, copies, colors, tone of voice, env variables, or business logic between related projects.
---

# Deep Mind

Shared brain that keeps all projects within an organization synchronized. Claude analyzes each project, extracts valuable shared elements, and the user decides what enters the matrix.

## Storage

All shared knowledge lives in `~/.claude/deep-mind/<matrix-name>/` with one `.md` file per vertical. The script `scripts/deep_mind.py` handles matrix/project management. Vertical content is read/edited directly by Claude.

## Workflow

### 1. First Run — Detection & Registration

Run `python3 <skill-path>/scripts/deep_mind.py detect` to check for `.deep-mind.json` in cwd.

**If not found** (new project):

1. Ask: "Does this project belong to a matrix — a group of related projects that share context?"
   - If no → stop
   - If yes → ask for the matrix name
2. Run `python3 <skill-path>/scripts/deep_mind.py list` to show existing matrices
3. If matrix is new:
   ```
   python3 <skill-path>/scripts/deep_mind.py init <matrix>
   ```
4. Ask for this project's name within the matrix, then register:
   ```
   python3 <skill-path>/scripts/deep_mind.py register <matrix> <project-name>
   ```
5. Proceed to **Project Analysis** (step 2)

**If found** (returning project):

1. Read the matrix name from the detected config
2. Run `python3 <skill-path>/scripts/deep_mind.py status <matrix>`
3. Read all vertical files from `~/.claude/deep-mind/<matrix>/` to load shared context
4. Present summary and ask what the user needs

### 2. Project Analysis

Perform a thorough scan of the project to identify shareable elements. Use Glob and Grep to find relevant files. For each vertical below, search for the listed patterns:

| Vertical | What to scan |
|----------|-------------|
| **branding** | CSS/SCSS color variables, Tailwind config (`theme.colors`, `theme.fontFamily`), design tokens, `globals.css`, theme files, logo/icon paths, style guides |
| **env-variables** | `.env`, `.env.example`, `.env.local`, `.env.production`, env validation schemas (zod/joi), `process.env.*` references, `import.meta.env.*` |
| **tech-stack** | `package.json`, `Cargo.toml`, `requirements.txt`, `go.mod`, `Gemfile`, `pubspec.yaml`, build configs (webpack, vite, next.config), Docker files |
| **api-contracts** | Route/endpoint definitions, OpenAPI/Swagger specs, GraphQL schemas, API type/interface files, REST client configs |
| **business-logic** | Domain models, validation rules, state machines, permission/role definitions, pricing logic, business rule comments |
| **data-models** | DB schemas, ORM models (Prisma, SQLAlchemy, TypeORM, Mongoose), type definitions for core entities |
| **auth-patterns** | Auth middleware, token handling, OAuth configs, permission/RBAC systems, session management |
| **copy-messaging** | i18n/l10n files, string constants, UI text files, error message catalogs, marketing copy |
| **architecture** | Folder structure conventions, module patterns, naming conventions, shared types/interfaces |
| **dependencies** | Shared internal packages, monorepo configs, version constraints, peer dependencies |

Do NOT search for all verticals blindly. Scan the project structure first (list root files and `src/` or equivalent), then only investigate verticals where there are clear signals.

### 3. Present Findings as Checklist

After analysis, present findings to the user in this format:

```
I've analyzed the project. Here are the verticals I've found with shareable value:

1. [branding] Primary: #FF5733, Secondary: #2196F3 | Fonts: Inter, Roboto
   Source: tailwind.config.js, src/styles/globals.css

2. [env-variables] 12 variables found (DB_HOST, API_URL, STRIPE_KEY, ...)
   Source: .env.example

3. [tech-stack] Next.js 14, TypeScript 5.3, Tailwind 3.4, Prisma 5.x
   Source: package.json

4. [api-contracts] 8 REST endpoints, JWT auth header pattern
   Source: src/app/api/

Which verticals do you want to sync to the matrix? (e.g. "1,2,3" or "all")
```

Only present verticals where actual content was found. Include the source files and a brief summary of what was detected.

### 4. Save Selected Verticals

For each vertical the user selects:

1. Register the vertical:
   ```
   python3 <skill-path>/scripts/deep_mind.py add-vertical <matrix> <vertical-name>
   ```
2. Write the extracted content to `~/.claude/deep-mind/<matrix>/<vertical-name>.md` using the Write/Edit tool. Structure the content as a clear, concise reference document. Other Claude instances working on sibling projects will read this file, so write it for that audience.
3. Log the change:
   ```
   python3 <skill-path>/scripts/deep_mind.py log <matrix> "Added <vertical> from <project>"
   ```

### 5. Proactive Updates (During Regular Work)

While working on a registered project, when you discover information that could benefit sibling projects:

1. Propose the update: "I found [X] that isn't in the matrix yet. Want me to sync it?"
2. If the user approves, update the relevant vertical file in `~/.claude/deep-mind/<matrix>/`
3. Log the change via the script

Examples of discoverable updates:
- New color or font added to the design system
- New env variable introduced
- New API endpoint created
- Business rule changed or added
- Architecture pattern established

## Script Reference

All commands: `python3 <skill-path>/scripts/deep_mind.py <command>`

| Command | Description |
|---------|-------------|
| `init <matrix>` | Create new matrix |
| `register <matrix> <project> [--path <p>]` | Register project (defaults to cwd) |
| `unregister <matrix> <project>` | Remove project |
| `status [<matrix>]` | Show matrix status |
| `list` | List all matrices |
| `projects <matrix>` | List projects in matrix |
| `add-vertical <matrix> <name>` | Register a vertical |
| `remove-vertical <matrix> <name>` | Remove a vertical and its file |
| `list-verticals <matrix>` | List registered verticals |
| `read <matrix> [<vertical>]` | Print brain content |
| `log <matrix> <message>` | Add changelog entry |
| `detect` | Check if cwd is a registered project |
| `path <matrix>` | Print matrix directory path |

## Behavioral Guidelines

- Always analyze the project before asking what to share — show, don't ask blindly
- Present findings as a numbered checklist, never dump raw file contents
- Write vertical files for consumption by other Claude instances — concise, structured, actionable
- Never silently update the matrix — always propose and wait for user confirmation
- When loading context from a returning project, read only relevant verticals for the task at hand
- Keep vertical files lean — they are loaded into context across all sibling projects
