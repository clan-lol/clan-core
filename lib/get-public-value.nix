{ lib }:
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
/**
  Retrieve a public value from a backend storage system.

  This function abstracts value retrieval across different backend implementations.
  Currently supports the 'in_repo' backend which reads values from the flake's
  filesystem at standardized paths.

  # Type
  ```
  getPublicValue :: AttrSet -> String
  ```

  # Arguments

  Attributes

  - [backend] (String, default: "in_repo"): Backend implementation to use
  - [default] (Any, default: throws): Fallback value if the requested value doesn't exist
  - [generator] (String): Name of the generator that produced this value
  - [machine] (String, optional): Machine name for per-machine values, or omitted for shared values
  - [file] (String): Filename of the value to retrieve
  - [flake] (Path or String): Path to the flake root directory

  # Returns

  The string content of the requested value file, or the default value if not found.

  # Backend Paths

  The storage paths are internal implementation details and subject to change.
  Use this function or other clanLib functions for stable access.

  # Example
  ```nix
    # Retrieve a shared value
    getPublicValue {
      generator = "myGenerator";
      file = "config";
      flake = ./.;
    }

    # Retrieve a machine-specific value with custom default
    getPublicValue {
      generator = "secrets";
      machine = "server01";
      file = "api-key";
      flake = inputs.self;
      default = "default-key";
    }
  ```
*/
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
if result != null then result else default
