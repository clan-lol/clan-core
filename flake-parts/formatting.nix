{
  self,
  inputs,
  ...
}: {
  imports = [
    inputs.treefmt-nix.flakeModule
  ];
  perSystem = {pkgs, ...}: {
    treefmt.projectRootFile = "flake.nix";
    treefmt.flakeCheck = true;
    treefmt.flakeFormatter = true;
    treefmt.programs.alejandra.enable = true;
    treefmt.programs.shellcheck.enable = true;
  };
}
