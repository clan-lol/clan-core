let
  flake = builtins.getFlake "https://git.clan.lol/clan/clan-core/archive/main.tar.gz";
  nixpkgs = flake.inputs.nixpkgs;
  pkgs = nixpkgs.legacyPackages.${builtins.currentSystem};
  clanCore = flake.outputs.nixosModules.clanCore;
  clanModules = flake.outputs.clanModules;
  allNixosModules = (import "${nixpkgs}/nixos/modules/module-list.nix") ++ [
    "${nixpkgs}/nixos/modules/misc/assertions.nix"
    { nixpkgs.hostPlatform = "x86_64-linux"; }
  ];
  clanCoreNixosModules = [
    clanCore
    # { clanCore.clanDir = ./.; }
  ] ++ allNixosModules ++ (builtins.attrValues clanModules);
  clanCoreNixos = pkgs.nixos { imports = clanCoreNixosModules; };
in
clanCoreNixos.options
