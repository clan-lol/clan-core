{
  settingsOption ? null,
  nestedSettingsOption ? null,
}:
{ lib, clanLib, ... }:
let
  inherit (lib)
    types
    ;
in
{
  options = {
    # TODO: deduplicate
    machines = lib.mkOption {
      type = types.attrsOf (
        types.submodule {
          options.settings =
            if nestedSettingsOption != null then
              nestedSettingsOption
            else
              lib.mkOption {
                default = { };
                type = clanLib.types.uniqueDeferredSerializableModule;
              };
        }
      );
      default = { };
    };
    tags = lib.mkOption {
      type = types.coercedTo (types.listOf types.str) (t: lib.genAttrs t (_: { })) (
        types.attrsOf (types.submodule { })
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

        !!! Note
            **The import only happens if the machine is part of the service or role.**

        Other types are passed through to the nixos configuration.

        ???+ Example
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
      '';
      default = [ ];
      type = types.listOf types.raw;
    };
  };
}
