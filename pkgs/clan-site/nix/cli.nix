{
  writeShellApplication,
  util-linux,
  pnpm_10,
}:
writeShellApplication {
  name = "clan-site";
  runtimeInputs = [
    util-linux
    pnpm_10
  ];
  text = builtins.readFile ./cli.sh;
  passthru = {
    pnpm = pnpm_10;
  };
}
