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
    tag = "f4b240a37a227c71cd9eed26486e4e3bdb6b656f";
    hash = "sha256-ACKg5ev/ztvJUYiD8/7TdFb4vy4jGZ/mbmdJI1lLXTk=";
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

  disabledTests = [
    # remote testing, name resolution failure.
    "test_openapi_parser_parse_remote_ref"
  ];

  meta = {
    description = "Pydantic model and dataclasses.dataclass generator for easy conversion of JSON, OpenAPI, JSON Schema, and YAML data sources";
    homepage = "https://github.com/koxudaxi/datamodel-code-generator";
    license = lib.licenses.mit;
    mainProgram = "datamodel-code-generator";
  };
}
