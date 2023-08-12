# cLan - awesome UI

## Commands

After changing dependencies with

`npm <dep> i --package-lock-only`

Update floco dependencies:

`nix run github:aakropotkin/floco -- translate -pt -o ./nix/pdefs.nix`


The prettier tailwind class sorting is not yet working properly with our devShell integration.

To sort classnames manually:

`cd /clan-core/pkgs/ui/`

`prettier -w ./src/ --config pconf.cjs`
