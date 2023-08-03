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
    rev = "a9d6f33e50d4dcd9cfc0c92253340437bbae282b";
    sha256 = "sha256-PCXQAQt8+i2pkUym9P1JY4JGoeZJLzzxWBhprHDdItM=";
  };
  buildInputs = [
    nlohmann_json
    nixVersions.unstable
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
