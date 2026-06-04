# Centurion AI OS — Branching Strategy

## Structure

```
main
  │
  ├── develop  ← daily integration
  │     │
  │     ├── feature/<name>      ← new work off develop
  │     └── release/v<version>  ← prep for main
  │
  └── hotfix/<name>             ← urgent fix off main
```

## Branch Rules

| Branch | Based On | Merges Into | Purpose |
|--------|----------|-------------|---------|
| `main` | — | — | Production. Always deployable. Never commit directly. |
| `develop` | `main` | `main` | Daily integration. Features merge here first. |
| `feature/<name>` | `develop` | `develop` | Isolated work. Delete after merge. |
| `release/v<version>` | `develop` | `main` + `develop` | Release prep. Bump version, final QA. Delete after merge. |
| `hotfix/<name>` | `main` | `main` + `develop` | Urgent fix. Delete after merge. |

## Naming Conventions

- `feature/add-fleet-auth` — lowercase, hyphens, no trailing slash
- `hotfix/fix-null-pointer-banner` — same convention
- `release/v1.1.0` — semantic versioning prefix

## Workflow

1. Branch off `develop` → `feature/your-thing`
2. Work, commit, push, open PR against `develop`
3. CI runs, review, squash-merge into `develop`
4. When `develop` is healthy → `release/vX.Y.Z` branch
5. Final checks, version bump, merge into `main` (merge commit)
6. Tag the merge commit on `main`
7. Back-merge `main` into `develop`

## Hotfix Flow

1. Branch off `main` → `hotfix/critical-fix`
2. Fix, PR against `main`, merge
3. Tag the fix
4. Immediately merge `main` back into `develop`

## Protected Branches (GitHub)

- `main` — requires PR review, passes CI, no direct pushes
- `develop` — requires passing CI, squash-merge only
