{ ... }:

let
  error = builtins.throw ''
    clanModules have been removed!

    Refer to https://docs.clan.lol/guides/migrations/migrate-inventory-services for migration.
  '';
in

{
  flake.clanModules = {
    outPath = "removed-clan-modules";
    value = error;
  };

  # builtins.listToAttrs (
  #   map (name: {
  #     inherit name;
  #     value = error;
  #   }) modnames
  # );
}
