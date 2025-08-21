{ pkgs, deno }:
let
  src = ./.;
in
pkgs.writeShellApplication {
  name = "update";

  runtimeInputs = [ deno ];
  runtimeEnv = {
    FIGMA_ICON_FILE_ID = "uyl2qJ78r6ISagQQlT4tr7";
    FRAME_ID = "689-1390";
  };

  text = ''
    REPO_ROOT="$(git rev-parse --show-toplevel)"
    OUT_DIR="$(realpath "$REPO_ROOT"/pkgs/clan-app/ui/icons)"
    export OUT_DIR
    deno run --allow-all ${src}/main.ts
  '';
}
