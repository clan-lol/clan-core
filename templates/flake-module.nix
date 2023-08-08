{
  imports = [
    ./python-project/flake-module.nix
  ];
  flake.templates = {
    new-clan = {
      description = "Initialize a new clan flake";
      path = ./new-clan;
    };
    python-project = {
      description = "Initialize a new internal python project";
      path = ./python-project;
    };
  };
}
