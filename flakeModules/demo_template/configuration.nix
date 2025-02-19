{ pkgs, config, ... }:
{
  fileSystems."/".device = "nodev";
  boot.loader.grub.device = "nodev";
  clan.core.vars.settings.secretStore = "fs";
  clan.core.vars.generators.mycelium = {
    files."key" = { };
    files."ip".secret = false;
    files."pubkey".secret = false;
    runtimeInputs = [
      pkgs.mycelium
      pkgs.coreutils
      pkgs.jq
    ];
    script = ''
      timeout 5 mycelium --key-file "$out"/key || :
      mycelium inspect --key-file "$out"/key --json | jq -r .publicKey > "$out"/pubkey
      mycelium inspect --key-file "$out"/key --json | jq -r .address > "$out"/ip
    '';
  };
  services.mycelium = {
    enable = true;
    addHostedPublicNodes = true;
    openFirewall = true;
    keyFile = config.clan.core.vars.generators.mycelium.files.key.path;
  };
  services.getty.autologinUser = "root";
  programs.bash.interactiveShellInit = ''
    if [[ "$(tty)" =~ /dev/(tty1|hvc0|ttyS0)$ ]]; then
      # workaround for https://github.com/NixOS/nixpkgs/issues/219239
      systemctl restart systemd-vconsole-setup.service

      reset

      your mycelium IP is: $(cat /var/lib/mycelium/ip)
    fi
  '';
}
