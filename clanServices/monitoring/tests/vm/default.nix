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

  testScript =
    { ... }:
    ''
      start_all()
    '';
}
