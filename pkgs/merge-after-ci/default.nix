{ writeShellApplication
, coreutils
, bash
, git
, tea
, openssh
, tea-create-pr
, ...
}:
writeShellApplication {
  name = "merge-after-ci";
  runtimeInputs = [
    bash
    coreutils
    git
    tea
    openssh
    tea-create-pr
  ];
  text = ''
    bash ${./script.sh} "$@"
  '';
}
