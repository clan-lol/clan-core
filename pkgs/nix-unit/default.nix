{ stdenv
, lib
, nixVersions
, fetchFromGitHub
, nlohmann_json
, boost
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
    rev = "6389f27c0a13df001d790adfaa08ec4d971ba34a";
    sha256 = "sha256-bwuiM+2sLrn+vvwW9fv/+s3oh0jN4y6gZV6Lx0pEEmM=";
  };
  buildInputs = [
    nlohmann_json
    nixVersions.stable
    boost
  ];
  nativeBuildInputs = [
    meson
    pkg-config
    ninja
    # nlohmann_json can be only discovered via cmake files
    cmake
  ] ++ (lib.optional stdenv.cc.isClang [ clang-tools ]);

  meta = {
    description = "Nix unit test runner";
    homepage = "https://github.com/adisbladis/nix-unit";
    license = lib.licenses.gpl3;
    maintainers = with lib.maintainers; [ adisbladis ];
    platforms = lib.platforms.unix;
  };
}
