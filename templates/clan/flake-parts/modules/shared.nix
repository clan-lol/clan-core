{
  clan-core,
  # Optional, if you want to access other flakes:
  # self,
  ...
}:
{
  imports = [
    clan-core.clanModules.sshd
    clan-core.clanModules.root-password
    # You can access other flakes imported in your flake via `self` like this:
    # self.inputs.nix-index-database.nixosModules.nix-index
  ];
}
