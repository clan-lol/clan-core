{ lib, pkgs, ... }: {
  options.clanCore = {
    clanName = lib.mkOption {
      type = lib.types.str;
      description = ''
        the name of the clan
      '';
    };
    clanDir = lib.mkOption {
      type = lib.types.either lib.types.path lib.types.str;
      description = ''
        the location of the flake repo, used to calculate the location of facts and secrets
      '';
    };
    clanIcon = lib.mkOption {
      type = lib.types.nullOr lib.types.path;
      description = ''
        the location of the clan icon
      '';
    };
    machineName = lib.mkOption {
      type = lib.types.str;
      description = ''
        the name of the machine
      '';
    };
    clanPkgs = lib.mkOption {
      defaultText = "self.packages.${pkgs.system}";
      internal = true;
    };
  };
}
