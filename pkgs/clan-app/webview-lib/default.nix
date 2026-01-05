{
  libadwaita,
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
    rev = "7e956adcd8fd1ea83f11b3cbc378c12dcd5fe998";
    hash = "sha256-Kfw00NOD+CQC+03QTbzlg3f5AC8XjcaJ6fjZS60YwLk=";
  };

  outputs = [
    "out"
    "dev"
  ];

  enableParallelBuilding = true;

  cmakeFlags = [
    "-DWEBVIEW_ENABLE_CLANG_FORMAT=OFF"
    "-DWEBVIEW_ENABLE_CLANG_TIDY=OFF"
    "-DWEBVIEW_BUILD_AMALGAMATION=OFF"
    "-DWEBVIEW_USE_LIBADWAITA=ON"
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
    libadwaita
    gtk4
  ];

  meta = with lib; {
    description = "Tiny cross-platform webview library for C/C++. Uses WebKit (GTK/Cocoa) and Edge WebView2 (Windows)";
    homepage = "https://github.com/webview/webview";
    license = licenses.mit;
    platforms = platforms.linux ++ platforms.darwin;
  };
}
