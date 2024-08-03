{ self, inputs, ... }:
{
  flake.templates = {
    new-clan = {
      description = "Initialize a new clan flake";
      path = ./new-clan;
    };
    default = self.templates.new-clan;
    minimal = {
      description = "for clans managed via (G)UI";
      path = ./minimal;
    };
  };
  flake.checks.x86_64-linux.template-minimal =
    let
      path = self.templates.minimal.path;
      initialized = inputs.nixpkgs.legacyPackages.x86_64-linux.runCommand "minimal-clan-flake" { } ''
        mkdir $out
        cp -r ${path}/* $out
        rm $out/inventory.json

        # TODO: Instead create a machine by calling the API, this wont break in future tests and is much closer to what the user performs
        echo '{ "machines": { "foo": {  "name": "foo" } } }' > $out/inventory.json
      '';
      evaled = (import "${initialized}/flake.nix").outputs {
        self = evaled // {
          outPath = initialized;
        };
        clan-core = self;
      };
    in
    {
      type = "derivation";
      name = "minimal-clan-flake-check";
      inherit (evaled.nixosConfigurations.foo.config.system.build.vm) drvPath outPath;
    };
}
