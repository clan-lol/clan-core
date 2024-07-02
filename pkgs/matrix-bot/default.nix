{
  python3,
  setuptools,
  matrix-nio,
  aiofiles,
  aiohttp,
  markdown2,
  ...
}:

let

  pythonDependencies = [
    matrix-nio
    aiofiles
    aiohttp
    markdown2
  ];

  runtimeDependencies = [ ];

  testDependencies = pythonDependencies ++ runtimeDependencies ++ [ ];

in
python3.pkgs.buildPythonApplication {
  name = "matrix-bot";
  src = ./.;
  format = "pyproject";

  nativeBuildInputs = [ setuptools ];

  propagatedBuildInputs = pythonDependencies;

  passthru.testDependencies = testDependencies;

  # Clean up after the package to avoid leaking python packages into a devshell
  postFixup = ''
    rm $out/nix-support/propagated-build-inputs
  '';

  meta.mainProgram = "matrix-bot";
}
