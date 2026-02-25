{
  writeShellApplication,
  util-linux,
  # Do not add node and pnpm, because this cli used in both site-shell.nix and
  # shell.nix, they should provide these dependencies
}:
writeShellApplication {
  name = "clan-site";
  runtimeInputs = [
    util-linux
  ];
  text = builtins.readFile ./cli.sh;
}
