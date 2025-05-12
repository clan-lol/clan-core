{
  writeShellApplication,
  git,
  jq,
  nix-prefetch-git,
}:
writeShellApplication {
  name = "update-clan-core-for-checks";
  runtimeInputs = [
    git
    jq
    nix-prefetch-git
  ];
  text = ''
    reporoot=$(git rev-parse --show-toplevel)
    if [ -z "$reporoot" ]; then
      echo "Not in a git repository. Please run this script from the root of the repository."
      exit 1
    fi
    cd "$reporoot"
    # get latest commit of clan-core
    json=$(nix-prefetch-git "$(pwd)")
    sha256=$(jq -r '.sha256' <<< "$json")
    rev=$(jq -r '.rev' <<< "$json")

    cat > ./checks/clan-core-for-checks.nix <<EOF
    { fetchgit }:
    fetchgit {
      url = "https://git.clan.lol/clan/clan-core.git";
      rev = "$rev";
      sha256 = "$sha256";
    }
    EOF
  '';
}
