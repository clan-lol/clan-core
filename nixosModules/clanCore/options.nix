{
  pkgs,
  options,
  lib,
  ...
}:
{
  options.clanCore.optionsNix = lib.mkOption {
    type = lib.types.raw;
    internal = true;
    readOnly = true;
    default = (pkgs.nixosOptionsDoc { inherit options; }).optionsNix;
    defaultText = "optionsNix";
    description = ''
      This is to export nixos options used for `clan config`
    '';
  };
}
