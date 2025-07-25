{
  pkgs,
  config,
  lib,
  ...
}:
{
  options = {
    clan.mycelium.openFirewall = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Open the firewall for mycelium";
    };

    clan.mycelium.addHostedPublicNodes = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Add hosted Public nodes";
    };
  };

  config.warnings = [
    "The clan.mycelium module is deprecated and will be removed on 2025-07-15.
      Please migrate to user-maintained configuration or the new equivalent clan services
      (https://docs.clan.lol/reference/clanServices)."
  ];

  config.services.mycelium = {
    enable = true;
    addHostedPublicNodes = lib.mkDefault config.clan.mycelium.addHostedPublicNodes;
    openFirewall = lib.mkDefault config.clan.mycelium.openFirewall;
    keyFile = config.clan.core.vars.generators.mycelium.files.key.path;
  };

  config.clan.core.vars.generators.mycelium = {
    files."key" = { };
    files."ip".secret = false;
    files."pubkey".secret = false;
    runtimeInputs = [
      pkgs.mycelium
      pkgs.coreutils
      pkgs.jq
    ];
    script = ''
      timeout 5 mycelium --key-file "$out"/key || :
      mycelium inspect --key-file "$out"/key --json | jq -r .publicKey > "$out"/pubkey
      mycelium inspect --key-file "$out"/key --json | jq -r .address > "$out"/ip
    '';
  };

}
