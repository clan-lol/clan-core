{ inputs, ... }:
{
  perSystem =
    {
      pkgs,
      self',
      config,
      ...
    }:
    let
      writers = pkgs.callPackage ./pkgs/builders/script-writers.nix { };

      ansiEscapes = {
        reset = ''\033[0m'';
        green = ''\033[32m'';
      };

      # A python program to switch between dev-shells
      # usage: select-shell shell-name
      # the currently enabled dev-shell gets stored in ./.direnv/selected-shell
      select-shell = writers.writePython3Bin "select-shell" {
        flakeIgnore = [ "E501" ];
      } ./pkgs/scripts/select-shell.py;
    in
    {
      devShells.default = pkgs.mkShell {
        name = "clan";
        packages = [
          select-shell
          pkgs.nix-unit
          pkgs.tea
          pkgs.nix
          self'.packages.tea-create-pr
          self'.packages.merge-after-ci
          self'.packages.pending-reviews
          # treefmt with config defined in ./flake-parts/formatting.nix
          config.treefmt.build.wrapper
        ];
        shellHook = ''
          echo -e "${ansiEscapes.green}switch to another dev-shell using: select-shell${ansiEscapes.reset}"
          export PRJ_ROOT=$(git rev-parse --show-toplevel)

          # vendoring / needed for impure tests
          ln -sfT ${self'.packages.clan-cli.nixpkgs} "$PRJ_ROOT/pkgs/clan-cli/clan_cli/nixpkgs"
          ln -sfT ${inputs.nix-select} "$PRJ_ROOT/pkgs/clan-cli/clan_cli/select"
        '';
      };
    };
}
