{ lib
, inputs
, ...
}: {
  imports = [
    inputs.pre-commit-hooks-nix.flakeModule
    inputs.treefmt-nix.flakeModule
  ];
  perSystem = { pkgs, config, ... }: {
    treefmt.projectRootFile = "flake.nix";
    treefmt.flakeCheck = true;
    treefmt.flakeFormatter = true;
    treefmt.programs.shellcheck.enable = true;
    treefmt.settings.formatter.nix = {
      command = "sh";
      options = [
        "-eucx"
        ''
          # First deadnix
          ${lib.getExe pkgs.deadnix} --edit "$@"
          # Then nixpkgs-fmt
          ${lib.getExe pkgs.nixpkgs-fmt} "$@"
        ''
        "--" # this argument is ignored by bash
      ];
      includes = [ "*.nix" ];
    };
    treefmt.settings.formatter.python = {
      command = "sh";
      options = [
        "-eucx"
        ''
          ${lib.getExe pkgs.ruff} --fix "$@"
          ${lib.getExe pkgs.black} "$@"
        ''
        "--" # this argument is ignored by bash
      ];
      includes = [ "*.py" ];
    };

    # we already run treefmt in ci
    pre-commit.check.enable = false;
    # activated in devShells via inputsFrom = [config.pre-commit.devShell];
    pre-commit.settings.hooks.format-all = {
      name = "format-all";
      enable = true;
      pass_filenames = true;
      entry = toString (pkgs.writeScript "treefmt" ''
        #!${pkgs.bash}/bin/bash
        ${config.treefmt.build.wrapper}/bin/treefmt --clear-cache --fail-on-change "$@"
      '');
    };
  };
}
