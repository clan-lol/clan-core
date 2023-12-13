{ clangStdenv
, fetchgit
, aemu
, meson
, pkg-config
, ninja
, python3
, vulkan-headers
, vulkan-utility-libraries
, glm
, libglvnd
, xorg
}:

clangStdenv.mkDerivation {
  pname = "gfxstream";
  version = "unstable-2023-12-11";
  src = fetchgit {
    url = "https://android.googlesource.com/platform/hardware/google/gfxstream";
    rev = "000a701a0c52c90e0c1e1fcd605be94b85b55f92";
    hash = "sha256-j8oBT/7xnvIv6IhNrPxHG5fr2nodWbeHX7KalCGStY0=";
  };
  postPatch = ''
    ln common/etc/etc.cpp host/compressedTextureFormats/etc.cpp
    ln common/etc/etc.cpp host/gl/glestranslator/GLcommon/etc.cpp
  '';
  preConfigure = ''
    export NIX_CFLAGS_COMPILE="$NIX_CFLAGS_COMPILE -I$(pwd)/common/etc/include"
  '';
  buildInputs = [
    aemu
    glm
    libglvnd
    vulkan-headers
    vulkan-utility-libraries
    xorg.libX11
  ];
  mesonFlags = [
    "-Ddecoders=gles,vulkan,composer"
  ];
  nativeBuildInputs = [
    meson
    pkg-config
    ninja
    python3
  ];
}
