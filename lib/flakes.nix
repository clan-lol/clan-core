{
  lib,
  clan-core,
  ...
}:
{
  # A flake lock for offline use.
  # All flake inputs are locked to an existing store path
  mkOfflineFlakeLock =
    flakePath:
    let
      flakeLock = lib.importJSON (flakePath + "/flake.lock");
      flakeInputs = builtins.removeAttrs clan-core.inputs [ "self" ];
      inputsToPaths =
        flakeLock:
        flakeLock
        // {
          nodes =
            flakeLock.nodes
            // (lib.flip lib.mapAttrs flakeInputs (
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
                  path = "${clan-core.inputs.${name}}";
                  type = "path";
                };
              }
            ));
        };
      lockAttrs = inputsToPaths flakeLock;
    in
    builtins.toFile "offline-flake.lock" (builtins.toJSON lockAttrs);
}
