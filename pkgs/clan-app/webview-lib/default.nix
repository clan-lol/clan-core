{
  gtk4,
  webkitgtk_6_0,
  lib,
  llvmPackages,
  fetchFromGitea,
  gnumake,
  cmake,
  clang-tools,
  pkg-config,
  stdenv,
  ...
}:

llvmPackages.stdenv.mkDerivation {
  pname = "webview";
  version = "nightly";

  # We add the function id to the promise to be able to cancel it through the UI
  # We disallow remote connections from the UI on Linux
  # TODO: Disallow remote connections on MacOS

  src = fetchFromGitea {
    domain = "git.clan.lol";
    owner = "clan";
    repo = "webview";
    rev = "5220e2e3afe1c69c510229956bb7eb331cd6fa98";
    hash = "sha256-0zZW35nkKljIGMBh92Trw8mT4b5/zAMiAcTjy9YYCSI=";
  };

  outputs = [
    "out"
    "dev"
  ];

  enableParallelBuilding = true;

  cmakeFlags = [
    "-DWEBVIEW_BUILD_TESTS=OFF"
    "-DWEBVIEW_ENABLE_CHECKS=OFF"
  ];

  # Dependencies used during the build process, if any
  nativeBuildInputs = [
    gnumake
    cmake
    clang-tools
    pkg-config
  ];

  buildInputs = lib.optionals stdenv.isLinux [
    webkitgtk_6_0
    gtk4
  ];

  meta = with lib; {
    description = "Tiny cross-platform webview library for C/C++. Uses WebKit (GTK/Cocoa) and Edge WebView2 (Windows)";
    homepage = "https://github.com/webview/webview";
    license = licenses.mit;
    platforms = platforms.linux ++ platforms.darwin;
  };
}
