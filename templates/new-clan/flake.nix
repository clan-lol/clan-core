{
  description = "<Put your description here>";

  inputs.clan-core.url = "git+https://git.clan.lol/clan/clan-core";

  outputs = { clan-core, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
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
