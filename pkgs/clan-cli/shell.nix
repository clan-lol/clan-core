{ pkgs }:
let
  package = pkgs.callPackage ./default.nix { };
  pythonWithDeps = pkgs.python3.withPackages (
    ps:
    package.propagatedBuildInputs
    ++ package.devDependencies
    ++ [
      ps.pip
    ]
  );
  checkScript = pkgs.writeScriptBin "check" ''
    nix build -f . tests -L "$@"
  '';
in
pkgs.mkShell {
  packages = [
    pkgs.ruff
    pythonWithDeps
  ];
  # sets up an editable install and add enty points to $PATH
  CLAN_NIXPKGS = pkgs.path;
  shellHook = ''
    tmp_path=$(realpath ./.pythonenv)
    repo_root=$(realpath .)
    rm -rf $tmp_path
    mkdir -p "$tmp_path/${pythonWithDeps.sitePackages}"

    ${pythonWithDeps.interpreter} -m pip install \
      --quiet \
      --disable-pip-version-check \
      --no-index \
      --no-build-isolation \
      --prefix "$tmp_path" \
      --editable $repo_root

    export PATH="$tmp_path/bin:${checkScript}/bin:$PATH"
    export PYTHONPATH="$repo_root:$tmp_path/${pythonWithDeps.sitePackages}"

    export XDG_DATA_DIRS="$tmp_path/share''${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"
    export fish_complete_path="$tmp_path/share/fish/vendor_completions.d''${fish_complete_path:+:$fish_complete_path}"
    mkdir -p \
      $tmp_path/share/fish/vendor_completions.d \
      $tmp_path/share/bash-completion/completions \
      $tmp_path/share/zsh/site-functions
    register-python-argcomplete --shell fish clan > $tmp_path/share/fish/vendor_completions.d/clan.fish
    register-python-argcomplete --shell bash clan > $tmp_path/share/bash-completion/completions/clan
  '';
}
