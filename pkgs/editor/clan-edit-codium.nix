{
  lib,
  coreutils,
  nil,
  nixd,
  nixfmt-rfc-style,
  direnv,
  vscode-extensions,
  vscode-with-extensions,
  vscodium,
  writeShellApplication,
}:
let
  codium = vscode-with-extensions.override {
    vscode = vscodium;
    vscodeExtensions = [
      vscode-extensions.jnoortheen.nix-ide
      vscode-extensions.mkhl.direnv
    ];
  };
in
writeShellApplication {
  name = "clan-edit-codium";
  runtimeInputs = [
    coreutils
    nil
    nixd
    nixfmt-rfc-style
    direnv
  ];
  text = ''
    set -eux
    DATA_DIR="''${XDG_CACHE_HOME:-$HOME/.cache}/clan-edit-codium"
    SETTINGS="$DATA_DIR"/User/settings.json
    ${coreutils}/bin/mkdir -p "$DATA_DIR/User"
    cat ${./settings.json} > "$SETTINGS"

    exec ${lib.getExe codium} --user-data-dir "$DATA_DIR" "$@"
  '';
}
