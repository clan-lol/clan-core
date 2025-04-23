{
  extraPythonPackages ? (_ps: [ ]),
  python3Packages,
  python3,
  buildPythonApplication,
  setuptools,
  util-linux,
  systemd,
  nix,
  colorama,
  junit-xml,
  mkShell,
}:
let
  package = buildPythonApplication {
    pname = "test-driver";
    version = "0.0.1";
    propagatedBuildInputs = [
      util-linux
      systemd
      colorama
      junit-xml
      nix
    ] ++ extraPythonPackages python3Packages;
    nativeBuildInputs = [ setuptools ];
    format = "pyproject";
    src = ./.;
    passthru.devShell = mkShell {
      packages = [
        (python3.withPackages (_ps: package.propagatedBuildInputs))
        package.propagatedBuildInputs
        python3.pkgs.pytest
      ];
      shellHook = ''
        export PYTHONPATH="$(realpath .):$PYTHONPATH"
      '';
    };
  };
in
package
