{
  lib,
  python3,
  python3Minimal,
  iproute2,
  makeWrapper,
  runCommand,
}:

let
  src = ./.;
in
python3Minimal.pkgs.buildPythonApplication {
  pname = "network-status";
  version = "0.1.0";

  inherit src;
  format = "other";

  nativeBuildInputs = [ makeWrapper ];

  installPhase = ''
    runHook preInstall

    mkdir -p $out/bin
    install -m755 network_status.py $out/bin/network-status

    wrapProgram $out/bin/network-status \
      --prefix PATH : ${lib.makeBinPath [ iproute2 ]}

    runHook postInstall
  '';

  passthru.tests = {
    pytest =
      runCommand "network-status-pytest"
        {
          nativeBuildInputs = [
            (python3.withPackages (ps: [
              ps.pytest
              ps.mypy
            ]))
          ];
        }
        ''
          cp -r ${src} ./src
          chmod +w -R ./src
          cd ./src

          echo "Running pytest..."
          python -m pytest tests/ -v

          echo "Running mypy..."
          mypy --strict network_status.py

          touch $out
        '';
  };

  meta = {
    description = "Display network status on terminal";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
    mainProgram = "network-status";
  };
}
