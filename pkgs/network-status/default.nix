{
  lib,
  python3Minimal,
  iproute2,
  makeWrapper,
}:
python3Minimal.pkgs.buildPythonApplication {
  pname = "network-status";
  version = "0.1.0";
  src = ./.;
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
  meta = {
    description = "Display network status on terminal";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
    mainProgram = "network-status";
  };
}
