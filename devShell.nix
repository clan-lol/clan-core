{
  perSystem =
    { pkgs
    , self'
    , config
    , ...
    }:
    let
      writers = pkgs.callPackage ./pkgs/builders/script-writers.nix { };

      ansiEscapes = {
        reset = ''\033[0m'';
        green = ''\033[32m'';
      };

      # a python program using argparse to enable and disable dev shells
      # synopsis: select-shell enable|disable shell-name
      # enabled devshells are written as a newline separated list into ./.direnv/selected-shells
      select-shell = writers.writePython3Bin "select-shell"
        {
          flakeIgnore = [ "E501" ];
        } ./pkgs/scripts/select-shell.py;
    in
    {
      devShells.default = pkgs.mkShell {
        # inputsFrom = [ self'.devShells.python ];
        packages = [
          select-shell
          pkgs.tea
          self'.packages.tea-create-pr
          self'.packages.merge-after-ci
          self'.packages.pending-reviews
          # treefmt with config defined in ./flake-parts/formatting.nix
          config.treefmt.build.wrapper
        ];
        shellHook = ''
          # no longer used
          rm -f "$(git rev-parse --show-toplevel)/.git/hooks/pre-commit"

          echo -e "${ansiEscapes.green}switch to another dev-shell using: select-shell${ansiEscapes.reset}"
        '';
      };
    };
}
