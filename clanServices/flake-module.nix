{ ... }:
{
  imports =
    let
      # Get all subdirectories in the current directory
      dirContents = builtins.readDir ./.;

      # Filter to include only directories that have a flake-module.nix file
      # and exclude special directories like 'result'
      validModuleDirs = builtins.filter (
        name:
        name != "result"
        && dirContents.${name} == "directory"
        && builtins.pathExists (./. + "/${name}/flake-module.nix")
      ) (builtins.attrNames dirContents);

      # Create import paths for each valid directory
      imports = map (name: ./. + "/${name}/flake-module.nix") validModuleDirs;
    in
    imports;
}
