{
  config,
  clan-core,
  inputs,
  ...
}:
{
  imports = [
    ./disko.nix
    clan-core.nixosModules.installer
  ];

  # We don't need state-version in a live installer
  clan.core.settings.state-version.enable = false;

  clan.core.deployment.requireExplicitUpdate = true;

  nixpkgs.pkgs = inputs.nixpkgs.legacyPackages.x86_64-linux;
  system.stateVersion = config.system.nixos.release;
}
