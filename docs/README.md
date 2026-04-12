# Documentation

## Local Development

Enter the docs dev shell (from the `docs/` directory, direnv will activate automatically):

```bash
cd docs
```

Or manually:

```bash
nix develop .#docs
```

Then start the dev server with hot module reloading:

```bash
clan-site
```

This watches `docs/src/` for markdown changes and automatically reloads the browser.

Add `-b` to open the site in a new browser tab:

```bash
clan-site dev -b
```

## Building

To create a production version of the site:

```bash
clan-site build
```

## Lint

```bash
clan-site lint
```
