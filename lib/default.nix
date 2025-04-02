{
  lib,
  self,
  nixpkgs,
  ...
}:
# Produces the
# 'clanLib' attribute set
# Wrapped with fix, so we can depend on other clanLib functions without passing the whole flake
lib.fix (clanLib: {
  # TODO:
  # SSome bad lib functions that depend on something in 'self'.
  # We should reduce the dependency on 'self' aka the 'flake' object
  # This makes it easier to test
  # most of the time passing the whole flake is unnecessary
  callLib = file: args: import file ({ inherit lib clanLib; } // args);

  evalClan = import ./inventory/eval-clan-modules {
    inherit lib;
    clan-core = self;
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
  };
  buildClanModule = clanLib.callLib ./build-clan { inherit nixpkgs; };

  buildClan = clanLib.buildClanModule.buildClanWith { clan-core = self; };
  # ------------------------------------
  # Lib functions that don't depend on 'self'
  inventory = clanLib.callLib ./inventory { };
  modules = clanLib.callLib ./inventory/frontmatter { };
  values = import ./introspection { inherit lib; };
  jsonschema = import ./jsonschema { inherit lib; };
  select = import ./select.nix;
  facts = import ./facts.nix { inherit lib; };
})
