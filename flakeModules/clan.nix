clan-core:
{
  config,
  lib,
  self,
  ...
}:
let
  inherit (lib) types;

in
{
  # Backwards compatibility
  imports = [
    (lib.mkRenamedOptionModule [ "clan" ] [ "flake" "clan" ])
  ];
  # Our module is completely public, so we dont need to map it
  # Mapped top level outputs
  options.flake = {
    # Backwards compat
    clanInternals = lib.mkOption {
      description = "Internals as needed by the clan cli.";
      default = config.flake.clan.clanInternals;
    };
    # The one and only clan module
    clan = lib.mkOption {
      description = "The evaluated clan module";
      default = { };
      type = types.submoduleWith {
        specialArgs = {
          inherit self;
        };
        modules = [
          clan-core.modules.clan.default
        ];
      };
    };

    # Mapped flake toplevel outputs
    darwinConfigurations = lib.mkOption {
      type = types.lazyAttrsOf types.raw;
      description = "darwinConfigurations produced by clan for a specific machine";
      apply = lib.mapAttrs (
        k: v: {
          _file = "#nixosModules.${k}";
          imports = [ v ];
        }
      );
    };
    darwinModules = lib.mkOption {
      type = types.lazyAttrsOf types.deferredModule;
      description = "darwinModules produced by clan for a specific machine";
      apply = lib.mapAttrs (
        k: v: {
          _file = "#nixosModules.${k}";
          imports = [ v ];
        }
      );
    };
  };
  # Use normal prio, to allow merging with user values
  config.flake = {
    inherit (config.flake.clan)
      nixosConfigurations
      nixosModules
      darwinConfigurations
      darwinModules
      ;
  };

  _file = __curPos.file;
}
