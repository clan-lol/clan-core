{ extraPythonPackages, buildPythonApplication, self, setuptools, util-linux, systemd }:
buildPythonApplication {
  pname = "test-driver";
  version = "0.0.1";
  propagatedBuildInputs = [ util-linux systemd ] ++ extraPythonPackages self;
  nativeBuildInputs = [ setuptools ];
  format = "pyproject";
  src = ./.;
}
