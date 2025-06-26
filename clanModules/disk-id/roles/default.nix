{
  config,
  pkgs,
  ...
}:

{

  config = {

    warnings = [
      "The clan.disk-id module is deprecated and will be removed on 2025-07-15.
      Please migrate to user-maintained configuration or the new equivalent clan services
      (https://docs.clan.lol/reference/clanServices)."
    ];
    clan.core.vars.generators.disk-id = {
      files.diskId.secret = false;
      runtimeInputs = [
        pkgs.coreutils
        pkgs.bash
      ];
      script = ''
        uuid=$(bash ${./uuid4.sh})

        # Remove the hyphens from the UUID
        uuid_no_hyphens=$(echo -n "$uuid" | tr -d '-')

        echo -n "$uuid_no_hyphens" > "$out/diskId"
      '';
    };
  };
}
