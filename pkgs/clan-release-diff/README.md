# clan-release-diff

Compare NixOS/clan options between two branches.

## Usage

```bash
# Diff 25.11 against your current working tree
nix run .#clan-release-diff -- 25.11

# Diff between two branches
nix run .#clan-release-diff -- 25.11 main
```

The tool builds option/service metadata from both versions automatically via `nix build`, then reports changes across multiple aspects:

- **Clan (flake) options** (`clan.*`) — added, removed, and type-changed options
- **NixOS options** (`clan.core.*`) — added, removed, and type-changed options
- **Services** (`clanServices`) — added/removed services and role set changes

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | No differences |
| 1    | Differences found |
| 2    | Error |

## What it compares

For each **option layer**: added, removed, and type-changed options.
For **services**: added/removed services and added/removed roles per service.

## Development

```bash
cd pkgs/clan-release-diff

# Run tests
python -m pytest tests/ -v

# Type check
mypy clan_release_diff/ tests/

# Lint
ruff check clan_release_diff/ tests/

# Run tests via Nix
nix build .#checks.x86_64-linux.clan-release-diff-pytest -L
```
