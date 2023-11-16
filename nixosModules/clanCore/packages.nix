{ pkgs, ... }: {
  # essential debugging tools for networked services
  environment.systemPackages = [
    pkgs.dnsutils
    pkgs.tcpdump
    pkgs.curl
    pkgs.jq
    pkgs.htop
  ];
}
