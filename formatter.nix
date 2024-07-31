{ inputs, ... }:
{
  imports = [ inputs.treefmt-nix.flakeModule ];
  perSystem =
    { self', pkgs, ... }:
    {
      treefmt.projectRootFile = ".git/config";
      treefmt.programs.shellcheck.enable = true;

      treefmt.programs.mypy.enable = true;
      treefmt.programs.nixfmt.enable = true;
      treefmt.programs.nixfmt.package = pkgs.nixfmt-rfc-style;
      treefmt.programs.deadnix.enable = true;

      treefmt.programs.mypy.directories =
        {
          "pkgs/clan-cli" = {
            extraPythonPackages = self'.packages.clan-cli.testDependencies;
            modules = [ "clan_cli" ];
          };
          "pkgs/clan-app" = {
            extraPythonPackages =
              # clan-app currently only exists on linux
              (self'.packages.clan-app.externalTestDeps or [ ]) ++ self'.packages.clan-cli.testDependencies;
            modules = [ "clan_app" ];
          };
        }
        // (
          if pkgs.stdenv.isLinux then
            {
              "pkgs/clan-vm-manager" = {
                extraPythonPackages =
                  #   # clan-app currently only exists on linux
                  self'.packages.clan-vm-manager.testDependencies;
                modules = [ "clan_vm_manager" ];
              };
            }
          else
            { }
        );
      treefmt.programs.ruff.check = true;
      treefmt.programs.ruff.format = true;

    };
}
