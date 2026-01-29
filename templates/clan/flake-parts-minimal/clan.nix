{ inputs, ... }:
{
  imports = [
    inputs.clan-core.flakeModules.default
  ];
  clan = {
    meta.name = "{{name}}";
    meta.domain = "{{domain}}";
  };
}
