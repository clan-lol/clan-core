## WARNING: Do not add core logic here.
## This is only a wrapper such that 'clan' can be called as a function.
{
  lib,
  clan-core,
  ...
}:
rec {
  buildClan =
    module: lib.warn "'buildClan' is deprecated. Use 'clan-core.lib.clan' instead" (clan module).config;

  clan =
    {
      self ? lib.warn "Argument: 'self' must be set when using 'buildClan'." null, # Reference to the current flake
      ...
    }@m:
    lib.evalModules {
      specialArgs = {
        inherit
          self
          ;
      };
      modules = [
        m
        clan-core.modules.clan.default
      ];
    };
}
