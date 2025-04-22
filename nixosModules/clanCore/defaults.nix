{
  _class,
  lib,
  config,
  pkgs,
  ...
}:
{
  imports = lib.optional (_class == "nixos") (
    lib.mkIf config.clan.core.enableRecommendedDefaults {
      # Use systemd during boot as well except:
      # - systems with raids as this currently require manual configuration: https://github.com/NixOS/nixpkgs/issues/210210
      # - for containers we currently rely on the `stage-2` init script that sets up our /etc
      boot.initrd.systemd.enable = lib.mkDefault (!config.boot.swraid.enable && !config.boot.isContainer);

      # Don't install the /lib/ld-linux.so.2 stub. This saves one instance of nixpkgs.
      environment.ldso32 = null;

      environment.systemPackages = [
        pkgs.nixos-facter # for `clan machines update-hardware-config --backend nixos-facter`
      ];
    }
  );

  options.clan.core.enableRecommendedDefaults = lib.mkOption {
    type = lib.types.bool;
    description = ''
      Whether to enable recommended default settings for NixOS by Clan.

      These settings are entirely optional and are not necessary for using Clan.

      This enables the new systemd in stage-1, disables some options that increase the closure size
      and adds some extra packages for debugging like `tcpdump` and `dnsutils`.
    '';
    default = true;
    example = false;
  };

  config = lib.mkIf config.clan.core.enableRecommendedDefaults {
    # This disables the HTML manual and `nixos-help` command but leaves
    # `man configuration.nix`
    documentation.doc.enable = lib.mkDefault false;

    # Work around for https://github.com/NixOS/nixpkgs/issues/124215
    documentation.info.enable = lib.mkDefault false;

    environment.systemPackages = [
      # essential debugging tools for networked services
      pkgs.dnsutils
      pkgs.tcpdump
      pkgs.curl
      pkgs.jq
      pkgs.htop

      pkgs.gitMinimal
    ];
  };
}
