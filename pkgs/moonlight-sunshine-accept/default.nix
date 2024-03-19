{
  lib,
  python3Packages,
  makeDesktopItem,
  copyDesktopItems,
}:
let
  desktop-file = makeDesktopItem {
    name = "org.clan.moonlight-sunset-accept";
    exec = "moonlight-sunshine-accept moonlight join %u";
    desktopName = "moonlight-handler";
    startupWMClass = "moonlight-handler";
    mimeTypes = [ "x-scheme-handler/moonlight" ];
  };
in
python3Packages.buildPythonApplication {
  name = "moonlight-sunshine-accept";

  src = ./.;

  format = "pyproject";

  propagatedBuildInputs = [ python3Packages.cryptography ];
  nativeBuildInputs = [
    python3Packages.setuptools
    copyDesktopItems
  ];

  desktopItems = [ desktop-file ];

  meta = with lib; {
    description = "Moonlight Sunshine Bridge";
    license = licenses.mit;
    maintainers = with maintainers; [ a-kenji ];
    mainProgram = "moonlight-sunshine-accept";
  };
}
