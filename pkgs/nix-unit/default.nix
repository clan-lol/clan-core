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
, difftastic
}:

stdenv.mkDerivation {
  pname = "nix-unit";
  version = "0.1";
  src = fetchFromGitHub {
    owner = "adisbladis";
    repo = "nix-unit";
    rev = "7e2ee1c70f930b9b65b9fc33c3f3eca0dfae00d1";
    sha256 = "sha256-UaUkh+/lxzNCRH64YB6SbyRIvvDhgY98izX9CvWgJA4=";
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

  postInstall = ''
    wrapProgram "$out/bin/nix-unit" --prefix PATH : ${difftastic}/bin
  '';

  meta = {
    description = "Nix unit test runner";
    homepage = "https://github.com/adisbladis/nix-unit";
    license = lib.licenses.gpl3;
    maintainers = with lib.maintainers; [ adisbladis ];
    platforms = lib.platforms.unix;
  };
}
