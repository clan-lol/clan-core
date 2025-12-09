{ lib, ... }:
{
  imports = [
    # secretUploadDirectory is renamed to the sops-specific option
    (lib.mkRenamedOptionModule
      [
        "clan"
        "core"
        "facts"
        "secretUploadDirectory"
      ]
      [
        "clan"
        "core"
        "vars"
        "sops"
        "secretUploadDirectory"
      ]
    )

    # All other facts options are removed
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "facts"
        "secretStore"
      ]
      "clan.core.facts has been removed. Use clan.core.vars instead. See https://docs.clan.lol/guides/migrations/migration-facts-vars/"
    )
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "facts"
        "secretModule"
      ]
      "clan.core.facts has been removed. Use clan.core.vars instead. See https://docs.clan.lol/guides/migrations/migration-facts-vars/"
    )
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "facts"
        "secretPathFunction"
      ]
      "clan.core.facts has been removed. Use clan.core.vars instead. See https://docs.clan.lol/guides/migrations/migration-facts-vars/"
    )
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "facts"
        "publicStore"
      ]
      "clan.core.facts has been removed. Use clan.core.vars instead. See https://docs.clan.lol/guides/migrations/migration-facts-vars/"
    )
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "facts"
        "publicModule"
      ]
      "clan.core.facts has been removed. Use clan.core.vars instead. See https://docs.clan.lol/guides/migrations/migration-facts-vars/"
    )
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "facts"
        "publicDirectory"
      ]
      "clan.core.facts has been removed. Use clan.core.vars instead. See https://docs.clan.lol/guides/migrations/migration-facts-vars/"
    )
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "facts"
        "services"
      ]
      "clan.core.facts has been removed. Use clan.core.vars.generators instead. See https://docs.clan.lol/guides/migrations/migration-facts-vars/"
    )

    # Legacy options from the old compat module
    (lib.mkRemovedOptionModule [
      "clan"
      "core"
      "secretStore"
    ] "clan.core.secretStore has been removed. Use clan.core.vars.settings.secretStore instead.")
    (lib.mkRemovedOptionModule [
      "clan"
      "core"
      "secretsPrefix"
    ] "clan.core.secretsPrefix has been removed.")
    (lib.mkRemovedOptionModule [
      "clan"
      "core"
      "secretsDirectory"
    ] "clan.core.secretsDirectory has been removed.")
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "secretsUploadDirectory"
      ]
      "clan.core.secretsUploadDirectory has been removed. Use clan.core.vars.sops.secretUploadDirectory instead."
    )
    (lib.mkRemovedOptionModule
      [
        "clan"
        "core"
        "secrets"
      ]
      "clan.core.secrets has been removed. Use clan.core.vars.generators instead. See https://docs.clan.lol/guides/migrations/migration-facts-vars/"
    )
  ];
}
