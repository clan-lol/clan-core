{ self, inputs, ... }:
{
  flake = (import ./flake.nix).outputs { } // {
    checks.x86_64-linux.template-minimal =
      let
        path = self.templates.minimal.path;
        initialized = inputs.nixpkgs.legacyPackages.x86_64-linux.runCommand "minimal-clan-flake" { } ''
          mkdir $out
          cp -r ${path}/* $out
          mkdir -p $out/machines/foo
          echo '{ "nixpkgs": { "hostPlatform": "x86_64-linux" } }' > $out/machines/foo/settings.json
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
  };
}
