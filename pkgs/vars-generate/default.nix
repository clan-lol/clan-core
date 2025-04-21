{
  buildPythonApplication,
  python,
  clan-cli,
}:
buildPythonApplication {
  name = "vars-generate";
  src = ./.;
  format = "pyproject";
  buildInputs = [ (python.pkgs.toPythonModule clan-cli) ];
  nativeBuildInputs = [
    (python.withPackages (ps: [ ps.setuptools ]))
  ];
}
