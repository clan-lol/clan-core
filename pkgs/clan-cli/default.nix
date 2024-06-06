{
  # Inputs for the package
  age,
  lib,
  argcomplete,
  installShellFiles,
  nix,
  openssh,
  pytest,
  pytest-cov,
  pytest-xdist,
  pytest-subprocess,
  pytest-timeout,
  python3,
  runCommand,
  setuptools,
  sops,
  stdenv,
  fakeroot,
  rsync,
  bash,
  sshpass,
  zbar,
  tor,
  git,
  qemu,
  gnupg,
  e2fsprogs,
  mypy,
  nixpkgs,
  clan-core-path,
  gitMinimal,
}:
let
  # Dependencies that are directly used in the project
  pythonDependencies = [
    argcomplete # Enables shell completion; without it, this feature won't work.
  ];

  # Runtime dependencies required by the application
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
    mypy
    qemu
    e2fsprogs
  ];

  # Dependencies required for running tests
  testDependencies =
    runtimeDependencies
    ++ [
      gnupg
      stdenv.cc # Compiler used for certain native extensions
    ]
    ++ pythonDependencies
    ++ [
      pytest # Testing framework
      pytest-cov # Generate coverage reports
      pytest-subprocess # fake the real subprocess behavior to make your tests more independent.
      pytest-xdist # Run tests in parallel on multiple cores
      pytest-timeout # Add timeouts to your tests
    ];

  # Convert runtimeDependencies into an attribute set for easier access
  runtimeDependenciesAsSet = builtins.listToAttrs (
    builtins.map (p: lib.nameValuePair (lib.getName p.name) p) runtimeDependencies
  );

  # Setup Python environment with all dependencies for running tests
  pythonWithTestDeps = python3.withPackages (_ps: testDependencies);

  # Prepare the source code for the project, including copying over jsonschema and nixpkgs
  source = runCommand "clan-cli-source" { } ''
    cp -r ${./.} $out
    chmod -R +w $out
    rm $out/clan_cli/config/jsonschema
    ln -sf ${nixpkgs'} $out/clan_cli/nixpkgs
    cp -r ${../../lib/jsonschema} $out/clan_cli/config/jsonschema
  '';

  # Create a custom nixpkgs for use within the project
  nixpkgs' = runCommand "nixpkgs" { nativeBuildInputs = [ nix ]; } ''
    mkdir $out
    cat > $out/flake.nix << EOF
    {
      description = "dependencies for the clan-cli";

      inputs = {
        nixpkgs.url = "path://${nixpkgs}";
      };

      outputs = _inputs: { };
    }
    EOF
    ln -sf ${nixpkgs} $out/path
    nix flake update $out \
      --store ./. \
      --extra-experimental-features 'nix-command flakes'
  '';
in
python3.pkgs.buildPythonApplication {
  name = "clan-cli";
  src = source;
  format = "pyproject";

  # Arguments for the wrapper to unset LD_LIBRARY_PATH to avoid glibc version issues
  makeWrapperArgs = [
    "--unset LD_LIBRARY_PATH"
    "--suffix"
    "PATH"
    ":"
    "${gitMinimal}/bin/git"
  ];

  # Build-time dependencies.
  nativeBuildInputs = [
    setuptools
    installShellFiles
  ];

  propagatedBuildInputs = pythonDependencies;

  # Define and expose the tests and checks to run in CI
  passthru.tests =
    (lib.mapAttrs' (n: lib.nameValuePair "clan-dep-${n}") runtimeDependenciesAsSet)
    // {
      clan-pytest-without-core =
        runCommand "clan-pytest-without-core"
          { nativeBuildInputs = [ pythonWithTestDeps ] ++ testDependencies; }
          ''
            cp -r ${source} ./src
            chmod +w -R ./src
            cd ./src

            export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1
            ${pythonWithTestDeps}/bin/python -m pytest -m "not impure and not with_core" ./tests
            touch $out
          '';
      clan-pytest-with-core =
        runCommand "clan-pytest-with-core"
          { nativeBuildInputs = [ pythonWithTestDeps ] ++ testDependencies; }
          ''
            cp -r ${source} ./src
            chmod +w -R ./src
            cd ./src

            export CLAN_CORE=${clan-core-path}
            export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1
            ${pythonWithTestDeps}/bin/python -m pytest -m "not impure and with_core" ./tests
            touch $out
          '';

      # Utility to check for leftover debugging breakpoints in the codebase
      check-for-breakpoints = runCommand "breakpoints" { } ''
        if grep --include \*.py -Rq "breakpoint()" ${source}; then
          echo "breakpoint() found in ${source}:"
          grep --include \*.py -Rn "breakpoint()" ${source}
          exit 1
        fi
        touch $out
      '';
    };

  # Additional pass-through attributes
  passthru.nixpkgs = nixpkgs';
  passthru.testDependencies = testDependencies;
  passthru.pythonWithTestDeps = pythonWithTestDeps;
  passthru.runtimeDependencies = runtimeDependencies;

  # Install shell completions for bash and fish using the argcomplete package
  postInstall = ''
    cp -r ${nixpkgs'} $out/${python3.sitePackages}/clan_cli/nixpkgs
    installShellCompletion --bash --name clan \
      <(${argcomplete}/bin/register-python-argcomplete --shell bash clan)
    installShellCompletion --fish --name clan.fish \
      <(${argcomplete}/bin/register-python-argcomplete --shell fish clan)
    installShellCompletion --zsh --name _clan \
      <(${argcomplete}/bin/register-python-argcomplete --shell bash clan)
  '';

  # Clean up after the package to avoid leaking python packages into a devshell
  postFixup = ''
    rm $out/nix-support/propagated-build-inputs
  '';

  # Run a basic check to ensure the application is executable
  checkPhase = ''
    PYTHONPATH= $out/bin/clan --help
  '';

  # Specify the main program for this package
  meta.mainProgram = "clan";
}
