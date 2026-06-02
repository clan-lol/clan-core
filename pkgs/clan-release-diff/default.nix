{
  lib,
  python3,
  runCommand,
  makeWrapper,
  nix,
}:
let
  src = ./.;

  pythonTool = python3.pkgs.buildPythonApplication {
    pname = "clan-release-diff-python";
    version = "0.1.0";

    inherit src;
    pyproject = true;

    build-system = [ python3.pkgs.setuptools ];

    meta = {
      description = "Options diff engine for clan-release-diff";
      license = lib.licenses.mit;
    };
  };
in
runCommand "clan-release-diff"
  {
    nativeBuildInputs = [ makeWrapper ];
    passthru.tests = {
      clan-release-diff-pytest =
        runCommand "clan-release-diff-pytest"
          {
            nativeBuildInputs = [
              (python3.withPackages (ps: [
                ps.pytest
              ]))
            ];
          }
          ''
            cp -r ${src} ./src
            chmod +w -R ./src
            cd ./src

            echo "Running pytest..."
            python -m pytest tests/ -v

            touch $out
          '';
    };
    meta = {
      mainProgram = "clan-release-diff";
      description = "Compare NixOS/clan options between branches";
      license = lib.licenses.mit;
      platforms = [ "x86_64-linux" ];
    };
  }
  ''
    install -Dm755 ${./clan-release-diff.sh} $out/bin/clan-release-diff
    substituteInPlace $out/bin/clan-release-diff \
      --replace-fail '@diff@' '${pythonTool}/bin/clan-release-diff'
    wrapProgram $out/bin/clan-release-diff \
      --prefix PATH : ${lib.makeBinPath [ nix ]}
  ''
