/**
  The templates submodule

  'clan.templates'

  Different kinds supported:

  - clan templates: 'clan.templates.clan'
  - disko templates: 'clan.templates.disko'
  - machine templates: 'clan.templates.machine'

  A template has the form:

  ```nix
  {
    description: string; # short summary what the template contains
    path: path; # path to the template
  }
  ```

  The clan API copies the template from the given 'path'
  into a target folder. For example,

  `./machines/<machine-name>` for 'machine' templates.
*/
{
  lib,
  ...
}:
let
  inherit (lib) types;

  templateType = types.submodule (
    { name, ... }:
    {
      options.description = lib.mkOption {
        type = types.str;
        default = name;
        description = ''
          The name of the template.
        '';
      };

      options.path = lib.mkOption {
        type = types.path;
        description = ''
          Holds the path to the clan template.
        '';
      };
    }
  );
in
{
  options = {
    # clan.templates.clan
    clan = lib.mkOption {
      type = types.attrsOf templateType;
      default = { };
      description = ''
        Holds the different clan templates.
      '';
    };

    # clan.templates.disko
    disko = lib.mkOption {
      type = types.attrsOf templateType;
      default = { };
      description = ''
        Holds different disko templates.
      '';
    };

    # clan.templates.machine
    machine = lib.mkOption {
      type = types.attrsOf templateType;
      default = { };
      description = ''
        Holds the different machine templates.
      '';
    };
  };
}
