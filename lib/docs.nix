{ lib, ... }:
{
  # Strip store paths from option declarations to make docs more stable
  # This prevents documentation from rebuilding when store paths change
  # but the actual content remains the same
  stripStorePathsFromDeclarations = opt:
    opt // {
      declarations = map (decl:
        if lib.isString decl && lib.hasPrefix "/nix/store/" decl then
          let
            parts = lib.splitString "/" decl;
          in
            if builtins.length parts > 4 then
              "/" + lib.concatStringsSep "/" (lib.drop 4 parts)
            else
              decl
        else
          decl
      ) opt.declarations;
    };
}