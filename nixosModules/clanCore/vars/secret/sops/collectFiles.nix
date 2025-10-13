# collectFiles helper function
{
  lib ? import <nixpkgs/lib>,
}:
let
  inherit (lib)
    filterAttrs
    mapAttrsToList
    ;

  relevantFiles = filterAttrs (
    _name: f: f.secret && f.deploy && (f.neededFor == "users" || f.neededFor == "services")
  );

  collectFiles =
    generators:
    builtins.concatLists (
      mapAttrsToList (
        gen_name: generator:
        mapAttrsToList (fname: file: {
          name = fname;
          generator = gen_name;
          neededForUsers = file.neededFor == "users";
          inherit (generator) share;
          inherit (file)
            owner
            group
            mode
            restartUnits
            ;
        }) (relevantFiles generator.files)
      ) generators
    );
in
collectFiles
