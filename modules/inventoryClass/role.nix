{
  settingsOption ? null,
  nestedSettingsOption ? null,
}:
{ lib, clanLib, ... }:
let
  inherit (lib) types;
  nestedSettings =
    if nestedSettingsOption != null then
      nestedSettingsOption
    else
      lib.mkOption {
        default = { };
        type = clanLib.types.uniqueDeferredSerializableModule;
      };
in

{
  options = {
    # machines and tags both use nestedSettings

    machines = lib.mkOption {
      type = types.attrsOf (
        types.submodule {
          options.settings = nestedSettings;

        }
      );
      default = { };
    };
    tags = lib.mkOption {
      type = types.coercedTo (types.listOf types.str) (t: lib.genAttrs t (_: { })) (
        types.attrsOf (
          types.submodule {
            options.settings = nestedSettings;
          }
        )
      );

      default = { };
    };
    settings =
      if settingsOption != null then
        settingsOption
      else
        lib.mkOption {
          default = { };
          type = clanLib.types.uniqueDeferredSerializableModule;
        };
    extraModules = lib.mkOption {
      description = ''
        List of additionally imported `.nix` expressions.

        :::admonition[Note]{type=note}
        **The import only happens if the machine is part of the service or role.**

        :::
        Other types are passed through to the nixos configuration.

        :::admonition[Example]{type=example collapsible open}
        To import the `special.nix` file

        ```
        . Clan Directory
        ├── flake.nix
        ...
        └── modules
            ├── special.nix
            └── ...
        ```

        ```nix
        {
          extraModules = [ "modules/special.nix" ];
        }
        ```
        :::
      '';
      default = [ ];
      type = types.listOf types.raw;
    };
  };
}
