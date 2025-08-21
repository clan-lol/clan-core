{ pkgs }:
pkgs.mkShell {
  name = "clan-icon-update";
  packages = with pkgs; [ deno ];
  env = {
    FIGMA_ICON_FILE_ID = "uyl2qJ78r6ISagQQlT4tr7";
    FRAME_ID = "709-324";
    OUT_DIR = "./icons";
  };
}
