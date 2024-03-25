{ pkgs, ... }:
{
  environment.systemPackages = [
    # essential debugging tools for networked services
    pkgs.dnsutils
    pkgs.tcpdump
    pkgs.curl
    pkgs.jq
    pkgs.htop
    # needed to deploy via `clan machines update` if the flake has a git input
    pkgs.gitMinimal
  ];
}
