{ ... }:
{
  perSystem =
    { ... }:
    {
      # checks = pkgs.lib.mkIf (pkgs.stdenv.isLinux) {
      #   flash = (import ../lib/test-base.nix) {
      #     name = "flash";
      #     nodes.target = {
      #       virtualisation.emptyDiskImages = [ 4096 ];
      #       virtualisation.memorySize = 3000;
      #       environment.systemPackages = [ self.packages.${pkgs.system}.clan-cli ];
      #       environment.etc."install-closure".source = "${closureInfo}/store-paths"; 

      #       nix.settings = {
      #         substituters = lib.mkForce [ ];
      #         hashed-mirrors = null;
      #         connect-timeout = lib.mkForce 3;
      #         flake-registry = pkgs.writeText "flake-registry" ''{"flakes":[],"version":2}'';
      #         experimental-features = [
      #           "nix-command"
      #           "flakes"
      #         ];
      #       };
      #     };
      #     testScript = ''
      #       start_all()
      #       machine.succeed("clan --debug --flake ${../..} flash --yes --disk main /dev/vdb test_install_machine")
      #     '';
      #   } { inherit pkgs self; };
      # };
    };
}
