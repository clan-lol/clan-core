{
  lib,
  ...
}:
{
  # A flake lock for offline use.
  # All flake inputs are locked to an existing store path
  mkOfflineFlakeLock =
    flakeRef:

    let
      flake =
        if lib.isAttrs flakeRef then
          flakeRef
        else
          throw "Cannot handle flake of type ${lib.typeOf flakeRef} yet.";
      flakePath = toString flake;
      flakeLock = lib.importJSON (flakePath + "/flake.lock");
      flakeInputs = builtins.removeAttrs flake.inputs [ "self" ];
      inputsToPaths =
        flakeLock:
        flakeLock
        // {
          nodes =
            flakeLock.nodes
            // (lib.mapAttrs (
              name: _:
              # remove follows and let 'nix flake lock' re-compute it later
              # (lib.removeAttrs flakeLock.nodes.${name} ["inputs"])
              flakeLock.nodes.${name}
              // {
                locked = {
                  inherit (flakeLock.nodes.${name}.locked) narHash;
                  lastModified =
                    # lol, nixpkgs has a different timestamp on the fs???
                    if name == "nixpkgs" then 0 else 1;
                  path = "${flake.inputs.${name}}";
                  type = "path";
                };
              }
            ) flakeInputs);
        };
      lockAttrs = inputsToPaths flakeLock;
    in
    builtins.toFile "offline-flake.lock" (builtins.toJSON lockAttrs);
}
