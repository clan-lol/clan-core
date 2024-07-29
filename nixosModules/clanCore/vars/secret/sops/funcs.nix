{
  lib ? import <nixpkgs/lib>,
  ...
}:
let
  inherit (builtins) readDir;

  inherit (lib) concatMap flip;
in
rec {
  readDirNames =
    dir:
    if !(builtins.pathExists dir) then [ ] else lib.mapAttrsToList (name: _type: name) (readDir dir);

  listVars =
    varsDir:
    flip concatMap (readDirNames varsDir) (
      machine_name:
      flip concatMap (readDirNames (varsDir + "/${machine_name}")) (
        generator_name:
        flip map (readDirNames (varsDir + "/${machine_name}/${generator_name}")) (secret_name: {
          machine = machine_name;
          generator = generator_name;
          name = secret_name;
        })
      )
    );
}
