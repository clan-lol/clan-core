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
- **Service settings** (`roles.<role>.settings.*`) — added, removed, and type-changed settings on roles present in both versions, keyed `service/role/setting`
- **Service exports** (`manifest.exports.out`) — added/removed export interfaces a service projects into the global `exports.<name>.*` namespace, attributed to the owning service, for services present in both versions
- **Templates** (`clan.templates`) — added/removed templates (keyed `category/name`), description changes, and, for templates present in both versions, which files were added, removed, or modified

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | No differences |
| 1    | Differences found |
| 2    | Error |

## What it compares

For each **option layer**: added, removed, and type-changed options.
For **services**: added/removed services and added/removed roles per service.
For **service settings**: added, removed, and type-changed `settings.*` options on each role that exists in both versions (settings of added/removed services or roles are omitted — the services layer already reports those).
For **service exports**: added/removed export interface names per service, read from `manifest.exports.out`. The key is absent on releases predating the feature (25.11), where it is treated as empty — so the whole current export surface reads as added against an old ref.
For **templates**: added/removed templates keyed `category/name`, description changes, and per-template file content changes (added/removed/modified files) for templates present in both versions. File content is compared by sha256 of each file's bytes, keyed by path relative to the template root, so it is independent of the absolute store path each version was realised under.

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
