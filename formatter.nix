{ lib, inputs, ... }:
{
  imports = [ inputs.treefmt-nix.flakeModule ];
  perSystem =
    { self', pkgs, ... }:
    {
      treefmt.projectRootFile = "flake.nix";
      treefmt.programs.shellcheck.enable = true;

      treefmt.programs.mypy.enable = true;
      treefmt.programs.mypy.directories = {
        "pkgs/clan-cli".extraPythonPackages = self'.packages.clan-cli.testDependencies;
        "pkgs/clan-app".extraPythonPackages =
          # clan-app currently only exists on linux
          (self'.packages.clan-app.externalTestDeps or [ ]) ++ self'.packages.clan-cli.testDependencies;
      };

      treefmt.settings.formatter.nix = {
        command = "sh";
        options = [
          "-eucx"
          ''
            # First deadnix
            ${lib.getExe pkgs.deadnix} --edit "$@"
            # Then nixpkgs-fmt
            ${lib.getExe pkgs.nixfmt-rfc-style} "$@"
          ''
          "--" # this argument is ignored by bash
        ];
        includes = [ "*.nix" ];
        excludes = [
          # Was copied from nixpkgs. Keep diff minimal to simplify upstreaming.
          "pkgs/builders/script-writers.nix"
        ];
      };
      treefmt.settings.formatter.python = {
        command = "sh";
        options = [
          "-eucx"
          ''
            ${lib.getExe pkgs.ruff} check --fix "$@"
            ${lib.getExe pkgs.ruff} format "$@"
          ''
          "--" # this argument is ignored by bash
        ];
        includes = [ "*.py" ];
      };
    };
}
