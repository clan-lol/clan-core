# cLan - awesome UI

## Prettier

To use prettier and the plugins using vscode/vscodium the `prettier.config.js` needs to be at the root level of the editor's file explorer

`cd clan-core/pkgs/ui && code .`

When inspecting `OUTPUT > Prettier` the config should've been loaded:

```sh
["INFO" - 1:47:43 PM] Formatting completed in 48ms.
["INFO" - 1:48:07 PM] Using config file at '.../clan-core/pkgs/ui/prettier.config.cjs'
```

If you have enabled `formatOnSave` the tailwind classes should get sorted into the officially recommended order.

`prettier -w ./src/ --config prettier.config.cjs`

## Commands

After changing dependencies with

`npm <dep> i --package-lock-only`

Update floco dependencies:

`nix run github:aakropotkin/floco -- translate -pt -o ./nix/pdefs.nix`


The prettier tailwind class sorting is not yet working properly with our devShell integration.

To sort classnames manually:

`cd /clan-core/pkgs/ui/`

