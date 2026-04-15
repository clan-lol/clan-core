# Writing Documentation

This guide shows you how to preview, write, and ship documentation changes for Clan. The source for every docs page lives in `docs/src/`. The site itself is a SvelteKit app in `pkgs/clan-site` that reads those markdown files and renders them.

If you are about to write prose, read the [style guide](/docs/guides/contributing/styleguide) first. It is the source of truth for headings, admonitions, code blocks, capitalisation, and how Clan's docs handle tone.

:::admonition[Prerequisites]{type=note}
A working Clan checkout with Nix and direnv installed. See [Contributing](/docs/guides/contributing/CONTRIBUTING) if you have not set those up yet.
:::

## 1. Start the dev server

Enter the `docs/` directory and let direnv activate the docs devshell:

```bash
cd clan-core/docs
direnv allow
```

The `docs/.envrc` loads the `.#docs` devshell, which in turn runs a shell hook that `cd`s into `pkgs/clan-site`, sets `CLAN_SITE_DIR` to that path, and copies the site's generated assets into place. The result is that your shell is now sitting in `pkgs/clan-site` with every tool you need on `PATH`, even though you started from `docs/`.

:::admonition[Where is my shell?]{type=tip}
After `direnv allow`, your working directory changes to `pkgs/clan-site`. That is intentional. Documentation markdown still lives in `docs/src/`, and the dev server reads it from there.
:::

Start the dev server:

```bash
clan-site
```

This is a shortcut for `clan-site dev`. It launches Vite with hot module reloading, serves the site at a local URL that is printed in the terminal, and watches `docs/src/` for markdown changes. Edits show up in the browser within a second or two without a full reload.

To open the site in a new browser tab automatically:

```bash
clan-site dev -b
```

## 2. Find the right file to edit

Documentation pages live under `docs/src/`, grouped by section:

- `docs/src/getting-started/` — the install and quick-start guides.
- `docs/src/guides/` — longer how-to pages, split into topic folders (`inventory/`, `services/`, `vars/`, and so on).
- `docs/src/reference/` — auto-generated CLI and option references. Do not edit the generated files by hand.
- `docs/src/concepts/` and `docs/src/decisions/` — conceptual explainers and architecture decision records.

A page is either a single markdown file (`flake-parts.md`) or a folder with an `index.md` inside (`nixpkgs-flake-input/index.md`). Use a folder when the page will ship with its own images or sub-pages.

## 3. Register new pages in the navigation

Adding a markdown file is not enough on its own. The sidebar is driven by a hand-maintained tree in `pkgs/clan-site/clan-site.config.ts`, under the `docsNav` export. New pages have to be listed there, otherwise they will render but will not appear in the navigation.

For a single page, add its path (relative to `docs/src/`, without the `.md` suffix) to the matching section:

```ts
{
  label: "Guides",
  children: [
    "guides/flake-parts",
    "guides/writing-documentation",
  ],
},
```

For a nested group, use the `label` / `children` form:

```ts
{
  label: "Contributing",
  children: [
    "guides/contributing/CONTRIBUTING",
    "guides/contributing/writing-documentation",
    "guides/contributing/styleguide",
  ],
},
```

The dev server hot-reloads on changes to `clan-site.config.ts`, so you can rearrange the tree and see the result immediately.

## 4. Use the framework features

Clan's docs support a few markdown extensions beyond plain CommonMark. The full catalogue is in the [style guide](/docs/guides/contributing/styleguide). The ones you will reach for most often:

Admonitions for notes, tips, and warnings:

```md
:::admonition[Prerequisites]{type=note}
Nix installed, SSH key in place.
:::
```

Code blocks with a filename label and highlighted lines:

````md
```nix [flake.nix] {2,4-6}
{
  this line is highlighted
  this line is not
  this line is highlighted
  this line is highlighted
  this line is highlighted
}
```
````

Cross-links to other docs pages use the `/docs/...` prefix, without a file extension:

```md
See [Flake Parts](/docs/guides/flake-parts) for the full setup.
```

## 5. Check your work

Before you open a PR, run the linter from the same shell:

```bash
clan-site lint
```

This runs ESLint, Stylelint, and Svelte's own type checks against `pkgs/clan-site`. It does not validate your prose, but it will catch broken markdown syntax that leaks into the rendered HTML.

To see what the production site will look like, build it and preview:

```bash
clan-site build -s
```

`-s` serves the built output so you can click through it. Add `-b` to open it in a browser tab as well.

## Troubleshooting

**`direnv` does not activate when I `cd` into `docs/`.** Run `direnv allow` once. If the hook was never installed, follow step 2 of [Contributing](/docs/guides/contributing/CONTRIBUTING) and restart your shell.

**`clan-site` is not found.** You are outside the docs devshell. Re-enter `docs/` so direnv activates it, or run `nix develop .#docs` manually from the repository root.

**A new page does not show up in the sidebar.** It is not listed in `docsNav`. Add it to `pkgs/clan-site/clan-site.config.ts` under the right section.

**Edits in `docs/src/` do not reload the browser.** Check that the dev server is still running in the terminal where you ran `clan-site`. The watcher only picks up files under `docs/src/` and the generated docs directory, so a change elsewhere will not trigger HMR.
