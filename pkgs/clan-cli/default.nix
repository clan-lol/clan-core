{ age
, argcomplete
, fastapi
, uvicorn
, bubblewrap
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
, zerotierone
, rsync
, pkgs
, ui-assets
}:
let
  # This provides dummy options for testing clan config and prevents it from
  # evaluating the flake .#
  CLAN_OPTIONS_FILE = ./clan_cli/config/jsonschema/options.json;

  dependencies = [
    argcomplete # optional dependency: if not enabled, shell completion will not work
    fastapi
    uvicorn # optional dependencies: if not enabled, webui subcommand will not work
  ];

  testDependencies = [
    pytest
    pytest-cov
    pytest-subprocess
    pytest-parallel
    openssh
    stdenv.cc
  ];

  checkPython = python3.withPackages (_ps: dependencies ++ testDependencies);

  # - vendor the jsonschema nix lib (copy instead of symlink).
  source = runCommand "clan-cli-source" { } ''
    cp -r ${./.} $out
    chmod -R +w $out
    rm $out/clan_cli/config/jsonschema
    cp -r ${nixpkgs} $out/clan_cli/nixpkgs
    cp -r ${../../lib/jsonschema} $out/clan_cli/config/jsonschema
    ln -s ${ui-assets} $out/clan_cli/webui/assets
  '';
  nixpkgs = runCommand "nixpkgs" { nativeBuildInputs = [ pkgs.nix ]; } ''
    mkdir $out
    mkdir -p $out/unfree                                                                       
    cat > $out/unfree/default.nix <<EOF                                                        
    import "${pkgs.path}" { config = { allowUnfree = true; overlays = []; }; }                 
    EOF
    cat > $out/flake.nix << EOF
    {
      description = "dependencies for the clan-cli";

      inputs = {
        nixpkgs.url = "nixpkgs";
      };

      outputs = _inputs: { };
    }
    EOF
    ln -s ${pkgs.path} $out/path
    nix flake lock $out \
      --store ./. \
      --experimental-features 'nix-command flakes' \
      --override-input nixpkgs ${pkgs.path}
  '';
in
python3.pkgs.buildPythonPackage {
  name = "clan-cli";
  src = source;
  format = "pyproject";

  inherit CLAN_OPTIONS_FILE;

  nativeBuildInputs = [
    setuptools
    installShellFiles
  ];
  propagatedBuildInputs = dependencies;

  passthru.tests.clan-pytest = runCommand "clan-pytest"
    {
      nativeBuildInputs = [ age zerotierone bubblewrap sops nix openssh rsync stdenv.cc ];
    } ''
    export CLAN_OPTIONS_FILE="${CLAN_OPTIONS_FILE}"
    cp -r ${source} ./src
    chmod +w -R ./src
    cd ./src

    export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1 
    ${checkPython}/bin/python -m pytest -m "not impure" -s ./tests
    touch $out
  '';
  passthru.clan-openapi = runCommand "clan-openapi" { } ''
    cp -r ${source} ./src
    chmod +w -R ./src
    cd ./src
    ${checkPython}/bin/python ./bin/gen-openapi --out $out/openapi.json --app-dir . clan_cli.webui.app:app
    touch $out
  '';
  passthru.nixpkgs = nixpkgs;

  passthru.devDependencies = [
    setuptools
    wheel
  ] ++ testDependencies;

  passthru.testDependencies = dependencies ++ testDependencies;

  postInstall = ''
    cp -r ${nixpkgs} $out/${python3.sitePackages}/clan_cli/nixpkgs
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
