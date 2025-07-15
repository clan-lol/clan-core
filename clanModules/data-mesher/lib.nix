lib: {

  machines =
    config:
    let
      instanceNames = builtins.attrNames config.clan.inventory.services.data-mesher;
      instanceName = builtins.head instanceNames;
      dataMesherInstances = config.clan.inventory.services.data-mesher.${instanceName};

      uniqueStrings = list: builtins.attrNames (builtins.groupBy lib.id list);
    in
    rec {
      admins = dataMesherInstances.roles.admin.machines or [ ];
      signers = dataMesherInstances.roles.signer.machines or [ ];
      peers = dataMesherInstances.roles.peer.machines or [ ];
      bootstrap = uniqueStrings (admins ++ signers);
    };

}
