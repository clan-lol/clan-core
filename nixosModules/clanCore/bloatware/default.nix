{ lib, ... }: {
  options.clan.bloatware = lib.mkOption {
    type = lib.types.submodule {
      imports = [
        ../../../lib/jsonschema/example-interface.nix
      ];
    };
  };
}
