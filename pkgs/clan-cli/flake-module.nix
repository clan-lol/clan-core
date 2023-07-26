{
  perSystem = { pkgs, ... }:
    let
      pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
      name = pyproject.project.name;
      package = pkgs.callPackage ./default.nix { };
      shell = pkgs.callPackage ./shell.nix { };
    in
    {
      packages.${name} = package;
      devShells.${name} = shell;
      packages.default = package;
      checks = package.tests;
    };
}
