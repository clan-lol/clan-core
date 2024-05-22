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
      inherit (pkgs.callPackage inputs.git-hooks { }) lib;

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

      # run treefmt before each commit
      install-pre-commit-hook =
        with lib.git-hooks;
        pre-commit (wrap.abort-on-change config.treefmt.build.wrapper);
    in
    {
      devShells.default = pkgs.mkShell {
        packages = [
          select-shell
          pkgs.tea
          pkgs.nix
          self'.packages.tea-create-pr
          self'.packages.merge-after-ci
          self'.packages.pending-reviews
          # treefmt with config defined in ./flake-parts/formatting.nix
          config.treefmt.build.wrapper
        ];
        shellHook = ''
          ${install-pre-commit-hook}

          echo -e "${ansiEscapes.green}switch to another dev-shell using: select-shell${ansiEscapes.reset}"
        '';
      };
    };
}
