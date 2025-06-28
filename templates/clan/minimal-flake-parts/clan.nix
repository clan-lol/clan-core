{ self, inputs, ... }:
{
  imports = [
    inputs.clan.flakeModules.default
  ];
  clan = {
    meta.name = "__CHANGE_ME__";
    inherit self;
    specialArgs = {
      inherit inputs;
    };
  };
}
