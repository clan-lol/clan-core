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
      type = types.attrsOf (types.submodule { });
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

        Supported types:

        - **Strings**: Interpreted relative to the 'directory' passed to `lib.clan`.
        - **Paths**: should be relative to the current file.
        - **Any**: Nix expression must be serializable to JSON.

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
      apply = value: if lib.isString value then value else builtins.seq (builtins.toJSON value) value;
      default = [ ];
      type = types.listOf (
        types.oneOf [
          types.str
          types.path
          (types.attrsOf types.anything)
        ]
      );
    };
  };
}
