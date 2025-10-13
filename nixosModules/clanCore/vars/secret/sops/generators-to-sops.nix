# This file maps generators to sops.secrets
# TODO(@davHau): add tests
{
  lib ? import <nixpkgs/lib>,
  # Can be mocked for testing
  pathExists ? builtins.pathExists,
}:
let
  inherit (lib)
    filterAttrs
    mapAttrsToList
    ;

  relevantFiles = filterAttrs (
    _name: f: f.secret && f.deploy && (f.neededFor == "users" || f.neededFor == "services")
  );

  extractSecretDefinitions =
    generators:
    builtins.concatLists (
      mapAttrsToList (
        gen_name: generator:
        mapAttrsToList (fname: file: {
          name = fname;
          generator = gen_name;
          neededForUsers = file.neededFor == "users";
          inherit (generator) share;
          inherit (file)
            owner
            group
            mode
            restartUnits
            ;
        }) (relevantFiles generator.files)
      ) generators
    );

  mapGeneratorsToSopsSecrets =
    {
      machineName,
      directory,
      class,
      generators,
    }:
    assert lib.assertMsg (class == "nixos" || class == "darwin")
      "Error trying to map 'var.generators' to 'sops.secrets': class must be 'nixos' or 'darwin', got: ${class}";
    let
      getSecretPath =
        secret:
        let
          scope = if secret.share then "shared" else "per-machine/${machineName}";
        in
        "${directory}/vars/${scope}/${secret.generator}/${secret.name}/secret";
    in
    lib.listToAttrs (
      map (secret: {
        name = "vars/${secret.generator}/${secret.name}";
        value = {
          inherit (secret)
            owner
            group
            mode
            neededForUsers
            ;
          sopsFile = builtins.path {
            name = "${secret.generator}_${secret.name}";
            path = getSecretPath secret;
          };
          format = "binary";
        }
        // (lib.optionalAttrs (class == "nixos") {
          inherit (secret) restartUnits;
        });
      }) (builtins.filter (x: pathExists (getSecretPath x)) (extractSecretDefinitions generators))
    );
in
mapGeneratorsToSopsSecrets
