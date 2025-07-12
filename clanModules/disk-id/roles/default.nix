{
  pkgs,
  ...
}:

{

  config = {

    warnings = [
      ''
        The clan.disk-id module is deprecated and will be removed on 2025-07-15.
        For migration see: https://docs.clan.lol/guides/migrations/disk-id/

        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        !!! Please migrate. Otherwise you may not be able to boot your system after that date.  !!!
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      ''
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
