{ lib, ... }:
let
  backends = {

    # In repo backend
    in_repo = {
      getPublicValue =
        {
          generator,
          machine,
          file,
          flake,
        }:
        let
          shared = machine == null;
          relPath =
            if shared then
              "vars/shared/${generator}/${file}/value"
            else
              "vars/per-machine/${machine}/${generator}/${file}/value";

          # Concatenate with flake path
          path = flake + "/${relPath}";
        in
        if builtins.pathExists path then builtins.readFile path else null; # Return null if not found
    };

    # Add new backends here
    # ...
  };
in
{
  getPublicValue =
    {
      backend ? "in_repo",
      default ? throw "getPublicValue: Public value ${
        if machine == null then "shared" else machine
      }/${generator}/${file} not found!",
      generator,
      machine ? null,
      file,
      flake,
      # Deprecated parameter
      shared ? null,
    }:
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

      backendImpl = backends.${backend} or (throw "Unknown backend: ${backend}");
      result = backendImpl.getPublicValue {
        machine = actualMachine;
        inherit
          generator
          file
          flake
          ;
      };
    in
    # readFile would return a string in any case
    # null is returned if the file doesn't exist
    if result != null then result else default;
}
