{ clanLib }:
{
  testMachineAccessToClanConfig =
    let
      eval = clanLib.clan {
        directory = ./.;
        meta.name = "test";
        self = {
          inputs = { };
        };
        machines = {
          testMachine = {
            nixpkgs.hostPlatform = "x86_64-linux";
          };
        };
      };
    in
    {
      inherit eval;
      # Attention: We need to access 'meta' via 'inventory' since clan.meta itself is a deferred module
      expr = eval.config.nixosConfigurations.testMachine.config.clanConfig.inventory.meta.name == "test";
      expected = true;
    };
}
