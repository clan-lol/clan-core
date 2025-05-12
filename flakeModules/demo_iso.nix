{ self, ... }:

let
  pkgs = self.inputs.nixpkgs.legacyPackages.x86_64-linux;

  demoModule = {
    imports = [
      "${self.clanModules.mycelium}/roles/peer.nix"
      # TODO do we need this? maybe not
      (
        { modulesPath, ... }:
        {
          imports = [ "${modulesPath}/installer/cd-dvd/iso-image.nix" ];
        }
      )
    ];
  };

  clan_welcome = pkgs.writeShellApplication {
    name = "clan_welcome";
    runtimeInputs = [
      pkgs.gum
      pkgs.gitMinimal
      pkgs.retry
      self.packages.${pkgs.system}.clan-cli
    ];
    text = ''
      set -efu

      gum confirm '
        Welcome to Clan, a NixOS-based operating system for the CLAN project.
        This installer can be used to try out clan on your machine, for that reason we setup a cooperative environment to play and hack together :)
      ' || exit 1
      until retry -t 5 ping -c 1 -W 1 git.clan.lol &> /dev/null; do
        # TODO make this nicer
        nmtui
      done
      if ! test -e ~/clan-core; then
        # git clone https://git.clan.lol/clan/clan-core.git ~/clan-core
        cp -rv ${self.checks.x86_64-linux.clan-core-for-checks} clan-core
      fi
      cd clan-core
      clan machines morph demo-template --i-will-be-fired-for-using-this
      exit
    '';
  };

  morphModule = {
    imports = [
      (
        { modulesPath, ... }:
        {
          imports = [ "${modulesPath}/image/images.nix" ];
        }
      )
    ];
    image.modules.iso.isoImage.squashfsCompression = "zstd -Xcompression-level 1";
    networking.networkmanager.enable = true;
    services.getty.autologinUser = "root";
    programs.bash.interactiveShellInit = ''
      if [[ "$(tty)" =~ /dev/(tty1|hvc0|ttyS0)$ ]]; then
        # workaround for https://github.com/NixOS/nixpkgs/issues/219239
        systemctl restart systemd-vconsole-setup.service

        reset

        ${clan_welcome}/bin/clan_welcome
      fi
    '';
  };
in
{
  clan.templates.machine.demo-template = {
    description = "Demo machine for the CLAN project";
    # path = pkgs.runCommand "demo-template" {} ''
    #   mkdir -p $out
    #   echo '{ self, ... }: { imports = [ self.nixosModules.demoModule ]; }' > $out/configuration.nix
    # '';
    path = ./demo_template;
  };
  flake.nixosModules = { inherit morphModule demoModule; };
  perSystem =
    { system, lib, ... }:
    {
      packages =
        lib.mkIf
          (lib.any (x: x == system) [
            "x86_64-linux"
            "aarch64-linux"
          ])
          {
            demo-iso =
              (self.inputs.nixpkgs.lib.nixosSystem {
                modules = [
                  { nixpkgs.hostPlatform = system; }
                  morphModule
                ];
              }).config.system.build.images.iso;
          };
    };
}
