{
  extraPythonPackages ? (_ps: [ ]),
  python3Packages,
  python3,
  util-linux,
  systemd,
  nix,
  mkShell,
}:
let
  package = python3Packages.buildPythonApplication {
    pname = "test-driver";
    version = "0.0.1";
    propagatedBuildInputs = [
      util-linux
      systemd
      python3Packages.colorama
      python3Packages.junit-xml
      nix
    ]
    ++ extraPythonPackages python3Packages;
    nativeBuildInputs = [ python3Packages.setuptools ];
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
