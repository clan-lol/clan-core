{ lib
, inputs
, ...
}: {
  imports = [
    inputs.treefmt-nix.flakeModule
  ];
  perSystem = { pkgs, ... }: {
    treefmt.projectRootFile = "flake.nix";
    treefmt.flakeCheck = true;
    treefmt.flakeFormatter = true;
    treefmt.programs.nixpkgs-fmt.enable = true;
    treefmt.programs.shellcheck.enable = true;
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
  };
}
