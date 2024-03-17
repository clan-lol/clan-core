{
  extraPythonPackages,
  python3Packages,
  buildPythonApplication,
  setuptools,
  util-linux,
  systemd,
}:
buildPythonApplication {
  pname = "test-driver";
  version = "0.0.1";
  propagatedBuildInputs = [
    util-linux
    systemd
  ] ++ extraPythonPackages python3Packages;
  nativeBuildInputs = [ setuptools ];
  format = "pyproject";
  src = ./.;
}
