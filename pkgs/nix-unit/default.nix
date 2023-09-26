{ stdenv
, lib
, nixVersions
, fetchFromGitHub
, nlohmann_json
, boost
, bear
, meson
, pkg-config
, ninja
, cmake
, clang-tools
}:

stdenv.mkDerivation {
  pname = "nix-unit";
  version = "0.1";
  src = fetchFromGitHub {
    owner = "adisbladis";
    repo = "nix-unit";
    rev = "3ed2378bddad85257fc508a291408f9ed9673d01";
    sha256 = "sha256-HvMq0TJGYSx37zHm4j2d+JUZx4/6X7xKEt/0DeCiwjQ=";
  };
  buildInputs = [
    nlohmann_json
    nixVersions.stable
    boost
  ];
  nativeBuildInputs = [
    bear
    meson
    pkg-config
    ninja
    # nlohmann_json can be only discovered via cmake files
    cmake
  ] ++ (lib.optional stdenv.cc.isClang [ bear clang-tools ]);

  meta = {
    description = "Nix unit test runner";
    homepage = "https://github.com/adisbladis/nix-unit";
    license = lib.licenses.gpl3;
    maintainers = with lib.maintainers; [ adisbladis ];
    platforms = lib.platforms.unix;
  };
}
