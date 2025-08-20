{ packages, pkgs, ... }:
{
  name = "monitoring";

  clan = {
    directory = ./.;
    inventory = {
      machines.peer1 = { };

      instances."test" = {
        module.name = "monitoring";
        module.input = "self";

        roles.telegraf.machines.peer1 = { };

      };
    };
  };

  extraPythonPackages = _p: [
    (pkgs.python3.pkgs.toPythonModule packages.${pkgs.system}.clan-cli)
  ];

  testScript =
    { ... }:
    ''
      import time
      start_all()
      time.sleep(99999)
      peer1.wait_for_unit("network-online.target")
      peer1.wait_for_unit("telegraf.service")

      from clan_lib.metrics.version import get_nixos_systems
      from clan_lib.machines.machines import Machine as ClanMachine
      from clan_lib.flake import Flake

      # mymachine = ClanMachine("peer1", Flake("."))
      # data = get_nixos_systems(mymachine, )
      # assert data["current_system"] is not None

      time.sleep(99999)
    '';
}
