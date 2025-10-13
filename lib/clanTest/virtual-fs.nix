{ lib }:
let
  sanitizePath =
    rootPath: path:
    let
      storePrefix = builtins.unsafeDiscardStringContext ("${rootPath}");
      pathStr = lib.removePrefix "/" (
        lib.removePrefix storePrefix (builtins.unsafeDiscardStringContext (toString path))
      );
    in
    pathStr;

  mkFunctions = rootPath: passthru: virtual_fs: {
    # Some functions to override lib functions
    pathExists =
      path:
      let
        pathStr = sanitizePath rootPath path;
        isPassthru = builtins.any (exclude: (builtins.match exclude pathStr) != null) passthru;
      in
      if isPassthru then
        builtins.pathExists path
      else
        let
          res = virtual_fs ? ${pathStr};
        in
        lib.trace "pathExists: '${pathStr}' -> '${lib.generators.toPretty { } res}'" res;
    readDir =
      path:
      let
        pathStr = sanitizePath rootPath path;
        base = (pathStr + "/");
        res = lib.mapAttrs' (name: fileInfo: {
          name = lib.removePrefix base name;
          value = fileInfo.type;
        }) (lib.filterAttrs (n: _: lib.hasPrefix base n) virtual_fs);
        isPassthru = builtins.any (exclude: (builtins.match exclude pathStr) != null) passthru;
      in
      if isPassthru then
        builtins.readDir path
      else
        lib.trace "readDir: '${pathStr}' -> '${lib.generators.toPretty { } res}'" res;
  };
in
{
  virtual_fs,
  rootPath,
  # Patterns
  passthru ? [ ],
}:
mkFunctions rootPath passthru virtual_fs
