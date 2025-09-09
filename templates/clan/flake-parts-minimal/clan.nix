{ inputs, ... }:
{
  imports = [
    inputs.clan-core.flakeModules.default
  ];
  clan = {
    meta.name = "__CHANGE_ME__";
  };
}
