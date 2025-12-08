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
    rev = "950c3eeea791d10b040abbb54164b7d860d13fb2";
    hash = "sha256-zG3UpsZX+uwJGOVheIn9q/J4yRTTgyaDELoN2FF62RI=";
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
