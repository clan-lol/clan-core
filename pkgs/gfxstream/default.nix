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
  version = "unstable-2023-11-29";
  src = fetchgit {
    url = "https://android.googlesource.com/platform/hardware/google/gfxstream";
    rev = "45c27965ee5121651946f54a42b3297b26047955";
    hash = "sha256-nJVVePNro+sL7jC+ehe5Am2jWo9BK6H1AUSzoP7J1ss=";
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
