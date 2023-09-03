{
  description = "<Put your description here>";

  inputs.clan-core.url = "git+https://git.clan.lol/clan/clan-core";

  outputs = { self, clan-core, ... }:
    let
      system = "x86_64-linux";
      pkgs = clan-core.inputs.nixpkgs.legacyPackages.${system};
    in
    {
      # all machines managed by cLAN
      nixosConfigurations = clan-core.lib.buildClan {
        directory = self;
      };
      # add the cLAN cli tool to the dev shell
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          clan-core.packages.${system}.clan-cli
        ];
      };
    };
}
