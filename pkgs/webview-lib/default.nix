{ pkgs, ... }:

pkgs.clangStdenv.mkDerivation {
  pname = "webview";
  version = "nightly";

  # We add the function id to the promise to be able to cancel it through the UI
  # We disallow remote connections from the UI on Linux
  # TODO: Disallow remote connections on MacOS

  src = pkgs.fetchFromGitHub {
    owner = "clan-lol";
    repo = "webview";
    rev = "33374e1030c5e243dac491e6c0e84d32e895c2e5";
    sha256 = "sha256-8BgfQL0V3f2n5lq5MDwJCJo6MkVSYvJkwpKCj2tBRz8=";
  };

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
