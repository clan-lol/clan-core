#!/usr/bin/env bash
# nix eval \
# 	--json \
# 	--impure \
# 	--expr \
# "(let pkgs = import <nixpkgs> { }; in (pkgs.lib.evalModules { modules =  (import <nixpkgs/nixos/modules/module-list.nix>) ++ [ ({...}: { nixpkgs.hostPlatform = builtins.currentSystem;} ) ] ; })).options"

# nix eval \
# 	--json \
# 	--impure \
# 	--expr \
# 	"(let pkgs = import <nixpkgs> { }; in (pkgs.lib.evalModules { modules = (import <nixpkgs/nixos/modules/module-list.nix>) ++ [(import <nixpkgs/nixos/modules/misc/assertions.nix>)] ++ [ (builtins.getFlake https://git.clan.lol/clan/clan-core/archive/main.tar.gz).clanModules (builtins.getFlake https://git.clan.lol/clan/clan-core/archive/main.tar.gz).nixosModules.clanCore ({...}: { nixpkgs.hostPlatform = builtins.currentSystem;} ) ] ; })).options"

# nix eval \
# 	--json \
# 	--impure \
# 	--expr \
# 	"(let pkgs = import <nixpkgs> { }; allNixosModules = (import <nixpkgs/nixos/modules/module-list.nix>) ++ [(import <nixpkgs/nixos/modules/misc/assertions.nix>) { nixpkgs.hostPlatform = \"x86_64-linux\"; }]; in (pkgs.lib.evalModules { modules = allNixosModules ++ [ (builtins.getFlake https://git.clan.lol/clan/clan-core/archive/main.tar.gz).clanModules (builtins.getFlake https://git.clan.lol/clan/clan-core/archive/main.tar.gz).nixosModules.clanCore ({...}: { nixpkgs.hostPlatform = builtins.currentSystem;} ) ] ; })).options"
#
#
nix eval \
	--json \
	--impure \
	--file \
	./options.nix
