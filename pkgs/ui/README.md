# cLan - awesome UI

## Updating dependencies

After changing dependencies with

`npm <dep> i --package-lock-only`

Update floco dependencies:

`nix run github:aakropotkin/floco -- translate -pt -o ./nix/pdefs.nix`

The prettier tailwind class sorting is not yet working properly with our devShell integration.

To sort classnames manually:

`cd /clan-core/pkgs/ui/`

## Upload ui to gitea

Create a gitea token here: https://git.clan.lol/user/settings/applications

Than run this command:

```
GITEA_TOKEN=<YOUR_TOKEN> nix run .#update-ui-assets
```
