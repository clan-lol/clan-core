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
  evalClan = import ./eval-clan-modules {
    inherit lib;
    clan-core = self;
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
  };
  buildClan = import ./build-clan {
    inherit lib nixpkgs;
    clan-core = self;
  };
  inventory = import ./inventory {
    inherit lib;
    clan-core = self;
  };
  modules = import ./frontmatter {
    inherit lib self;
  };
  # ------------------------------------
  # Lib functions that don't depend on 'self'
  facts = import ./facts.nix { inherit lib; };
  values = import ./values { inherit lib; };
  jsonschema = import ./jsonschema { inherit lib; };
  select = import ./select.nix;
})
