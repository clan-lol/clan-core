{
  writeShellApplication,
  util-linux,
}:
writeShellApplication {
  name = "clan-site";
  runtimeInputs = [
    util-linux
  ];
  text = builtins.readFile ./cli.sh;
}
