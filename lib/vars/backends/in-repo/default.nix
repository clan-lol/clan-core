{ lib }:
let
  getPublicValue =
    {
      default ? throw "getPublicValue: Public value ${
        if machine == null then "shared" else machine
      }/${generator}/${file} not found!",
      generator,
      machine ? null,
      file,
      # TODO: Rename flake -> rootDir
      flake,
      # Deprecated parameter
      shared ? null,
    }@args:
    lib.warnIf (args ? backend) "Argument 'backend' to getPublicValue is deprecated. It can be omited."
      (
        let
          # Backwards compatibility: if shared is set, use it to determine machine value
          actualMachine =
            if shared != null then
              (lib.warn
                "'shared' parameter in getPublicValue is deprecated. It is now automatically inferred from 'machine == null'."
                (if shared then null else machine)
              )
            else
              machine;

          readFromFile =
            {
              generator,
              machine,
              file,
              rootDir,
            }:
            let
              path = getPath {
                inherit
                  generator
                  machine
                  file
                  rootDir
                  ;
              };
            in
            if builtins.pathExists path then builtins.readFile path else null; # Return null if not found

          result = readFromFile {
            machine = actualMachine;
            inherit
              generator
              file
              ;
            rootDir = flake;
          };
        in
        # readFile would return a string in any case
        # null is returned if the file doesn't exist
        if result != null then result else default
      );

  getPath =
    {
      generator,
      machine,
      file,
      rootDir,
    }:
    let
      relPath =
        if machine == null then
          "vars/shared/${generator}/${file}/value"
        else
          "vars/per-machine/${machine}/${generator}/${file}/value";

      # Concatenate with base path
      path = rootDir + "/${relPath}";
    in
    path;

  exists = throw ''Not implemented for in-repo yet'';
in
{
  inherit getPath getPublicValue exists;
}
