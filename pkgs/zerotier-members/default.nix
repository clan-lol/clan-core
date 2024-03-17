{
  stdenv,
  python3,
  lib,
}:

stdenv.mkDerivation {
  name = "zerotier-members";
  src = ./.;
  buildInputs = [ python3 ];
  installPhase = ''
    install -Dm755 ${./zerotier-members.py} $out/bin/zerotier-members
  '';
  meta = with lib; {
    description = "A tool to list/allow members of a ZeroTier network";
    license = licenses.mit;
  };
}
