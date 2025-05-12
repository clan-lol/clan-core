{ pkgs, ... }:

pkgs.clangStdenv.mkDerivation {
  pname = "webview";
  version = "nightly";

  src = pkgs.fetchFromGitHub {
    owner = "webview";
    repo = "webview";
    rev = "f1a9d6b6fb8bcc2e266057224887a3d628f30f90";
    sha256 = "sha256-sK7GXDbb2zEntWH5ylC2B39zW+gXvqQ1l843gvziDZo=";
  };

  # We add the function id to the promise to be able to cancel it through the UI
  # We disallow remote connections from the UI on Linux
  # TODO: Disallow remote connections on MacOS
  patches = [ ./fixes.patch ];

  outputs = [
    "out"
    "dev"
  ];

  # Dependencies used during the build process, if any
  nativeBuildInputs = with pkgs; [
    gnumake
    cmake
    clang-tools
    pkg-config
  ];

  buildInputs =
    with pkgs;
    [
    ]
    ++ pkgs.lib.optionals stdenv.isLinux [
      webkitgtk_6_0
      gtk4
    ];

  meta = with pkgs.lib; {
    description = "Tiny cross-platform webview library for C/C++. Uses WebKit (GTK/Cocoa) and Edge WebView2 (Windows)";
    homepage = "https://github.com/webview/webview";
    license = licenses.mit;
    platforms = platforms.linux ++ platforms.darwin;
  };
}
