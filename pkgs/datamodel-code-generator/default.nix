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
  version = "0.52.2";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "koxudaxi";
    repo = "datamodel-code-generator";
    tag = version;
    hash = "sha256-+GKtwmp3pp4+c1SL76xgaIF2mf8py0p0HO3rqstkE0M=";
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
