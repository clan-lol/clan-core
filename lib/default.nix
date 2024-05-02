{
  lib,
  clan-core,
  nixpkgs,
  ...
}:
{
  jsonschema = import ./jsonschema { inherit lib; };
  modules = import ./description.nix { inherit clan-core; };
  buildClan = import ./build-clan { inherit clan-core lib nixpkgs; };

  vm-user = ./vm-user;
  graphical = ./graphical;
  xfce-vm = {
    imports = [
      ./vm-user
      ./graphical
      ./xfce-vm
    ];
  };
}
