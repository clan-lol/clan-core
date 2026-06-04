{
  lib,
  stdenv,
  python3,
  runCommand,
  zerotierone,
}:
let
  src = ./.;
in
python3.pkgs.buildPythonApplication {
  pname = "zerotier-tools";
  version = "0.1.0";

  inherit src;
  pyproject = true;

  build-system = [ python3.pkgs.setuptools ];

  passthru.tests = {
    zerotier-tools-pytest =
      runCommand "zerotier-tools-pytest"
        {
          nativeBuildInputs = [
            (python3.withPackages (ps: [
              ps.pytest
            ]))
          ]
          ++ lib.optionals stdenv.hostPlatform.isLinux [ zerotierone ];
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
    description = "ZeroTier identity, network, and member management tools for clan";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux ++ lib.platforms.darwin;
  };
}
