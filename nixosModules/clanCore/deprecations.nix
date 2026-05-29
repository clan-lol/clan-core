{ lib, ... }:
let
  inherit (lib) mkRemovedOptionModule;
in
{
  imports = [
    # Legacy options from the old compat module
    (mkRemovedOptionModule [
      "clan"
      "core"
      "secretStore"
    ] "clan.core.secretStore has been removed. Use clan.core.vars.settings.secretStore instead.")
    (mkRemovedOptionModule [
      "clan"
      "core"
      "secretsPrefix"
    ] "clan.core.secretsPrefix has been removed.")
    (mkRemovedOptionModule [
      "clan"
      "core"
      "secretsDirectory"
    ] "clan.core.secretsDirectory has been removed.")
    (mkRemovedOptionModule
      [
        "clan"
        "core"
        "secretsUploadDirectory"
      ]
      "clan.core.secretsUploadDirectory has been removed. Use clan.core.vars.sops.secretUploadDirectory instead."
    )
  ];
}
