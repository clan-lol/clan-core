{
  lib,
  python3,
  runCommand,
}:
python3.pkgs.buildPythonApplication {
  pname = "clan-release-diff";
  version = "0.1.0";

  src = ./.;
  pyproject = true;

  build-system = [ python3.pkgs.setuptools ];

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
          cp -r ${./.} ./src
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
