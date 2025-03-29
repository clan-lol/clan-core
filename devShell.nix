{ inputs, ... }:
{
  perSystem =
    {
      lib,
      pkgs,
      self',
      config,
      system,
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
        packages =
          [
            select-shell
            pkgs.nix-unit
            pkgs.tea
            # Better error messages than nix 2.18
            pkgs.nixVersions.latest
            self'.packages.tea-create-pr
            self'.packages.merge-after-ci
            self'.packages.pending-reviews
            # treefmt with config defined in ./flake-parts/formatting.nix
            config.treefmt.build.wrapper
          ]
          # bring in data-mesher for the cli which can help with things like key generation
          ++ (
            let
              data-mesher = inputs.data-mesher.packages.${system}.data-mesher or null;
            in
            lib.optional (data-mesher != null) data-mesher
          );
        shellHook = ''
          echo -e "${ansiEscapes.green}switch to another dev-shell using: select-shell${ansiEscapes.reset}"
          export PRJ_ROOT=$(git rev-parse --show-toplevel)
        '';
      };
    };
}
