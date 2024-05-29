{ self, ... }:
{
  perSystem =
    {
      nodes,
      pkgs,
      lib,
      ...
    }:
    let
      dependencies = [
        self
        pkgs.stdenv.drvPath
        pkgs.jq
        pkgs.disko
        pkgs.stdenvNoCC.drvPath
        pkgs.openssl
        pkgs.curl
        self.clanInternals.machines.${pkgs.hostPlatform.system}.test_install_machine.config.system.build.toplevel
        self.clanInternals.machines.${pkgs.hostPlatform.system}.test_install_machine.config.system.build.diskoScript
        self.clanInternals.machines.${pkgs.hostPlatform.system}.test_install_machine.config.system.clan.deployment.file
        self.clanInternals.machines.${pkgs.hostPlatform.system}.test_install_machine.pkgs.disko
      ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
      closureInfo = pkgs.closureInfo { rootPaths = dependencies; };
    in
    {
      # Currently disabled...
      checks = pkgs.lib.mkIf (false && pkgs.stdenv.isLinux) {
        flash = (import ../lib/test-base.nix) {
          name = "flash";
          nodes.target = {
            virtualisation.emptyDiskImages = [ 4096 ];
            virtualisation.memorySize = 3000;
            environment.systemPackages = [ self.packages.${pkgs.system}.clan-cli ];
            environment.etc."install-closure".source = "${closureInfo}/store-paths";

            nix.settings = {
              substituters = lib.mkForce [ ];
              hashed-mirrors = null;
              connect-timeout = lib.mkForce 3;
              flake-registry = pkgs.writeText "flake-registry" ''{"flakes":[],"version":2}'';
              experimental-features = [
                "nix-command"
                "flakes"
              ];
            };
          };
          testScript = ''
            start_all()
            machine.succeed("nix-store --verify-path ${
              self.clanInternals.machines.${pkgs.hostPlatform.system}.test_install_machine.config.system.build.diskoScript
            }")
            machine.execute("timeout 30 clan flash --debug --flake ${../..} --yes --disk main /dev/vdb test_install_machine")
          '';
        } { inherit pkgs self; };
      };
    };
}
