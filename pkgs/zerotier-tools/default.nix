{
  lib,
  python3,
}:

python3.pkgs.buildPythonApplication {
  pname = "zerotier-tools";
  version = "0.1.0";

  src = ./.;
  pyproject = true;

  build-system = [ python3.pkgs.setuptools ];

  meta = {
    description = "ZeroTier member management tools for clan";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
  };
}
