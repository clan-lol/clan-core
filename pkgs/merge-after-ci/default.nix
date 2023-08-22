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
    remoteName="''${1:-origin}"
    targetBranch="''${2:-main}"
    shift && shift
    tea-create-pr "$remoteName" "$targetBranch" --assignees clan-bot "$@"
  '';
}
