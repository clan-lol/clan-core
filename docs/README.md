# Documentation

## Local Development

Serve documentation locally:

```bash
nix develop .#docs -c mkdocs serve
```

## Working with Versions

Serve documentation locally with version selector:
```bash
nix develop .#docs -c mike serve
```

Build and manage versioned documentation using Mike:

```bash
nix develop .#docs -c mike deploy main # Deploy to the main development version
nix develop .#docs -c mike deploy 1.0 latest # Deploy version 1.0 and mark as 'latest'
```
List all deployed versions (from the `gh-pages` branch):
```
nix develop .#docs -c mike list
```

Version structure:
- **latest**: Alias for the most recent stable release (default)
- **main**: Latest development version from the main branch
- **XX.YY**: Specific stable releases (e.g., 25.11)
