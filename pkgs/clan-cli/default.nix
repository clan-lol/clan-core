{ age
, lib
, argcomplete
, fastapi
, uvicorn
, installShellFiles
, nix
, openssh
, pytest
, pytest-cov
, pytest-subprocess
, pytest-parallel
, python3
, runCommand
, setuptools
, sops
, stdenv
, wheel
, fakeroot
, rsync
, ui-assets
, bash
, sshpass
, zbar
, tor
, git
, nixpkgs
}:
let

  dependencies = [
    argcomplete # optional dependency: if not enabled, shell completion will not work
    fastapi
    uvicorn # optional dependencies: if not enabled, webui subcommand will not work
  ];

  pytestDependencies = runtimeDependencies ++ dependencies ++ [
    pytest
    pytest-cov
    pytest-subprocess
    pytest-parallel
    openssh
    git
    stdenv.cc
  ];

  # Optional dependencies for clan cli, we re-expose them here to make sure they all build.
  runtimeDependencies = [
    bash
    nix
    fakeroot
    openssh
    sshpass
    zbar
    tor
    age
    rsync
    sops
    git
  ];

  runtimeDependenciesAsSet = builtins.listToAttrs (builtins.map (p: lib.nameValuePair (lib.getName p.name) p) runtimeDependencies);

  checkPython = python3.withPackages (_ps: pytestDependencies);

  # - vendor the jsonschema nix lib (copy instead of symlink).
  # Interesting fact: using nixpkgs from flakes instead of nixpkgs.path is reduces evaluation time by 5s.
  source = runCommand "clan-cli-source" { } ''
    cp -r ${./.} $out
    chmod -R +w $out
    rm $out/clan_cli/config/jsonschema
    ln -s ${nixpkgs'} $out/clan_cli/nixpkgs
    cp -r ${../../lib/jsonschema} $out/clan_cli/config/jsonschema
    ln -s ${ui-assets} $out/clan_cli/webui/assets
  '';
  nixpkgs' = runCommand "nixpkgs" { nativeBuildInputs = [ nix ]; } ''
    mkdir $out
    cat > $out/flake.nix << EOF
    {
      description = "dependencies for the clan-cli";

      inputs = {
        nixpkgs.url = "nixpkgs";
      };

      outputs = _inputs: { };
    }
    EOF
    ln -s ${nixpkgs} $out/path
    nix flake lock $out \
      --store ./. \
      --extra-experimental-features 'nix-command flakes' \
      --override-input nixpkgs ${nixpkgs}
  '';
in
python3.pkgs.buildPythonPackage {
  name = "clan-cli";
  src = source;
  format = "pyproject";

  nativeBuildInputs = [
    setuptools
    installShellFiles
  ];
  propagatedBuildInputs = dependencies;

  # also re-expose dependencies so we test them in CI
  passthru.tests = (lib.mapAttrs' (n: lib.nameValuePair "clan-dep-${n}") runtimeDependenciesAsSet) // {
    clan-pytest = runCommand "clan-pytest" { nativeBuildInputs = [ checkPython ] ++ pytestDependencies; } ''
      cp -r ${source} ./src
      chmod +w -R ./src
      cd ./src

      export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1
      ${checkPython}/bin/python -m pytest -m "not impure" -s ./tests
      touch $out
    '';
  };
  passthru.clan-openapi = runCommand "clan-openapi" { } ''
    cp -r ${source} ./src
    chmod +w -R ./src
    cd ./src
    export PATH=${checkPython}/bin:$PATH

    ${checkPython}/bin/python ./bin/gen-openapi --out $out/openapi.json --app-dir . clan_cli.webui.app:app
    touch $out
  '';
  passthru.nixpkgs = nixpkgs';
  passthru.checkPython = checkPython;

  passthru.devDependencies = [
    setuptools
    wheel
  ] ++ pytestDependencies;

  passthru.pytestDependencies = pytestDependencies;
  passthru.runtimeDependencies = runtimeDependencies;

  postInstall = ''
    cp -r ${nixpkgs'} $out/${python3.sitePackages}/clan_cli/nixpkgs
    installShellCompletion --bash --name clan \
      <(${argcomplete}/bin/register-python-argcomplete --shell bash clan)
    installShellCompletion --fish --name clan.fish \
      <(${argcomplete}/bin/register-python-argcomplete --shell fish clan)
  '';
  checkPhase = ''
    PYTHONPATH= $out/bin/clan --help
    if grep --include \*.py -Rq "breakpoint()" $out; then
      echo "breakpoint() found in $out:"
      grep --include \*.py -Rn "breakpoint()" $out
      exit 1
    fi
  '';
  meta.mainProgram = "clan";
}
