{
  lib,
  argcomplete,
  black,
  buildPythonPackage,
  fetchFromGitHub,
  freezegun,
  genson,
  graphql-core,
  hatch-vcs,
  hatchling,
  httpx,
  inflect,
  isort,
  jinja2,
  openapi-spec-validator,
  packaging,
  prance,
  ruff,
  pydantic,
  pytest-benchmark,
  pytest-mock,
  pytestCheckHook,
  pyyaml,
  toml,
  time-machine,
  inline-snapshot,
  watchfiles,
}:

buildPythonPackage rec {
  pname = "datamodel-code-generator";
  version = "0.46.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "koxudaxi";
    repo = "datamodel-code-generator";
    rev = "58e73ed8740d589623647008bb1fe230bac1aeda";
    hash = "sha256-sgyUVL6e8SXPFP1FxICQ+ibRdPCPdZXCue1H85Vl06s=";
  };

  pythonRelaxDeps = [
    "inflect"
    "isort"
  ];

  build-system = [
    hatchling
    hatch-vcs
  ];

  dependencies = [
    argcomplete
    black
    genson
    inflect
    isort
    jinja2
    packaging
    pydantic
    pyyaml
    toml
  ];

  optional-dependencies = {
    graphql = [ graphql-core ];
    http = [ httpx ];
    ruff = [ ruff ];
    validation = [
      openapi-spec-validator
      prance
    ];
  };

  nativeCheckInputs = [
    freezegun
    pytest-benchmark
    pytest-mock
    pytestCheckHook
    time-machine
    inline-snapshot
    watchfiles
  ]
  ++ lib.concatAttrValues optional-dependencies;

  pythonImportsCheck = [ "datamodel_code_generator" ];

  doCheck = false;

  meta = {
    description = "Pydantic model and dataclasses.dataclass generator for easy conversion of JSON, OpenAPI, JSON Schema, and YAML data sources";
    homepage = "https://github.com/koxudaxi/datamodel-code-generator";
    license = lib.licenses.mit;
    mainProgram = "datamodel-code-generator";
  };
}
