{
  writeShellApplication,
  bash,
  coreutils,
  git,
  tea,
  gawk,
  openssh,
}:
writeShellApplication {
  name = "tea-create-pr";
  runtimeInputs = [
    bash
    coreutils
    git
    tea
    openssh
    gawk
  ];
  text = builtins.readFile ./script.sh;
}
