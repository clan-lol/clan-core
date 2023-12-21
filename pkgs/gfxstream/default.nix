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
, lib
, vulkan-loader
}:

clangStdenv.mkDerivation {
  pname = "gfxstream";
  version = "unstable-2023-12-19";
  src = fetchgit {
    url = "https://android.googlesource.com/platform/hardware/google/gfxstream";
    rev = "5ef37b16f4777f6052903ffcdf96ad0bb87e1572";
    hash = "sha256-xUKDGTwF05oojuFhs1ruDPmRdOnkGuYo4IK7KdTYZ0k=";
  };
  postPatch = ''
    ln -s common/etc/etc.cpp host/compressedTextureFormats/etc.cpp
    ln -s common/etc/etc.cpp host/gl/glestranslator/GLcommon/etc.cpp
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
  postFixup = ''
    patchelf --set-rpath "$(patchelf --print-rpath "$f"):${vulkan-loader}/lib" "$out/lib/libgfxstream_backend.so"
  '';
  nativeBuildInputs = [
    meson
    pkg-config
    ninja
    python3
  ];

  meta = with lib; {
    description = "Graphics Streaming Kit is a code generator that makes it easier to serialize and forward graphics API calls i.e. for remote rendering.";
    homepage = "https://android.googlesource.com/platform/hardware/google/gfxstream";
    license = licenses.asl20;
    platforms = platforms.linux;
    maintainers = with maintainers; [ mic92 ];
  };
}
