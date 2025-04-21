{
  buildPythonApplication,
  python,
  clan-cli,
}:
buildPythonApplication {
  name = "generate-test-vars";
  src = ./.;
  format = "pyproject";
  dependencies = [ (python.pkgs.toPythonModule clan-cli) ];
  nativeBuildInputs = [
    (python.withPackages (ps: [ ps.setuptools ]))
  ];
}
