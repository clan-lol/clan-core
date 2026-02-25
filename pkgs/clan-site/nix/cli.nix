{
  writeShellApplication,
  util-linux,
}:
writeShellApplication {
  name = "clan-site-cli";
  runtimeInputs = [
    util-linux
  ];
  text = builtins.readFile ./cli.sh;
}
