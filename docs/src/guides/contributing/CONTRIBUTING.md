# Contributing

This guide walks you through setting up a Clan development environment from scratch. By the end you will have a working checkout, a devshell that provides the `clan` CLI, and pre-commit hooks that keep your changes formatted.

Clan supports development on Linux and macOS.

:::admonition[How changes get tested]{type=note}
Every pull request runs through Gitea CI. If a check fails, the PR is blocked until the failure is resolved. Running `nix fmt` and the pre-commit hook locally will catch most of what CI cares about before you push.
:::

## 1. Install Nix and direnv

If you do not have them yet, follow [Install Nix and direnv](/docs/getting-started/install-nix) and come back here once `nix --version` works and direnv is hooked into your shell.

## 2. Fork and clone clan-core

Register an account at [git.clan.lol](https://git.clan.lol) and fork [clan-core](https://git.clan.lol/clan/clan-core). Clone your fork, then add the upstream remote so you can pull in changes from `main`:

```bash
git remote add upstream gitea@git.clan.lol:clan/clan-core.git
```

## 3. Activate the devshell

`cd` into the directory that corresponds to the area you are working on and allow its `.envrc`. For most CLI work, that is `pkgs/clan-cli`:

```bash
cd clan-core/pkgs/clan-cli
direnv allow
```

On the first `direnv allow` you will usually see a message like this:

```bash
direnv: error .envrc is blocked. Run `direnv allow` to approve its content
```

`direnv allow` approves the `.envrc` so that direnv can execute it on every entry. The devshell brings in every tool you need (`clan`, Python, formatters, test runners) and sets up the symlinks that let `clan-cli` run from the checkout. From now on, entering the directory re-enters the devshell automatically.

## 4. (Optional) Install the pre-commit hook

To format and lint your changes before each commit:

```bash
./scripts/pre-commit
```

This installs a git hook that runs `nix fmt` and the lint checks on staged files. You can always run the formatter manually:

```bash
nix fmt
```

## Working on documentation

Documentation changes have their own workflow. The source lives in `docs/src/` and the dev server lives in `pkgs/clan-site`. See [Writing Documentation](/docs/guides/contributing/writing-documentation) for how to preview your changes with hot reload, register new pages in the navigation, and follow the [style guide](/docs/guides/contributing/styleguide).

## Overriding related projects for local development

Clan depends on several sibling projects that you may want to patch alongside your changes:

- [data-mesher](https://git.clan.lol/clan/data-mesher)
- [nixos-facter](https://github.com/nix-community/nixos-facter)
- [nixos-anywhere](https://github.com/nix-community/nixos-anywhere)
- [disko](https://github.com/nix-community/disko)

If your fix touches one of these, clone it locally and point Clan at your checkout instead of the pinned version. For example, `clan-cli` invokes `nixos-anywhere` like this:

```python
run(
    nix_shell(
        ["nixos-anywhere"],
        cmd,
    ),
    RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
)
```

Replace the package reference with a local path:

```python
run(
    nix_shell(
        ["<path_to_local_src>#nixos-anywhere"],
        cmd,
    ),
    RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
)
```

`<path_to_local_src>` is any valid [flake reference](https://nix.dev/manual/nix/2.26/command-ref/new-cli/nix3-flake.html#flake-references), so it does not have to be a local directory. You can point it at a branch on a fork or even an open PR to test a patch end-to-end before merging.

## Backporting fixes to release branches

Bug and security fixes that are still relevant for an existing release should be backported to the matching release branch (for example `25.11`). Use `scripts/backport-pr` to cherry-pick and open a Gitea PR in one step:

```bash
scripts/backport-pr 25.11 <commit> [<commit>...]
```

The script does the bookkeeping for you:

- It skips commits that are already on the target branch or that only touch files that never shipped on that release.
- It cherry-picks the remaining commits onto a `backport/<target>/<sha>` branch.
- It pushes the branch and opens a `[<target>] …` PR through `tea`.
- It deletes the throwaway branch if nothing applied cleanly.

If a cherry-pick conflicts, the script leaves you on the backport branch and prints the remaining `git` and `tea` commands so you can finish by hand. Pass `-n` / `--dry-run` (or set `DRY_RUN=1`) to preview what it would do without touching any branches.

## Coding standards

A few conventions that CI and reviewers will flag if you miss them:

- New module names are kebab-case.
- `vars` definitions are kebab-case wherever the surrounding code allows it.
- CLI help strings start with a capital letter and do not end in a period.

## Documentation style

When you write or edit docs, follow the [style guide](/docs/guides/contributing/styleguide). It covers admonition syntax, code block highlighting, capitalisation, and the writing principles Clan's docs are built around.
