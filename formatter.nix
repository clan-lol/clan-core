{ lib
, inputs
, ...
}: {
  imports = [
    inputs.treefmt-nix.flakeModule
  ];
  perSystem = { self', pkgs, ... }: {
    treefmt.projectRootFile = "flake.nix";
    treefmt.flakeCheck = true;
    treefmt.flakeFormatter = true;
    treefmt.programs.shellcheck.enable = true;
    treefmt.programs.prettier.enable = true;
    # TODO: add custom prettier package, that uses our ui/node_modules
    # treefmt.programs.prettier.settings.plugins = [
    #   "${self'.packages.prettier-plugin-tailwindcss}/lib/node_modules/prettier-plugin-tailwindcss/dist/index.mjs"
    # ];
    treefmt.settings.formatter.prettier.excludes = [
      "secrets.yaml"
      "key.json"
    ];

    treefmt.programs.mypy.enable = true;
    treefmt.programs.mypy.directories = {
      "pkgs/clan-cli".extraPythonPackages = self'.packages.clan-cli.pytestDependencies;
      "pkgs/clan-vm-manager".extraPythonPackages = self'.packages.clan-vm-manager.propagatedBuildInputs;
    };

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
      excludes = [ "pkgs/node-packages/*.nix" ];
    };
    treefmt.settings.formatter.python = {
      command = "sh";
      options = [
        "-eucx"
        ''
          ${lib.getExe pkgs.ruff} --fix "$@"
          ${lib.getExe pkgs.ruff} format "$@"
        ''
        "--" # this argument is ignored by bash
      ];
      includes = [ "*.py" ];
    };
  };
}
