{
  writeShellApplication,
  util-linux,
  pnpm_12,
}:
writeShellApplication {
  name = "clan-site";
  runtimeInputs = [
    util-linux
    pnpm_12
  ];
  text = builtins.readFile ./cli.sh;
  passthru = {
    pnpm = pnpm_12;
  };
}
