{ config
, ...
}: {
  services.prosody = {
    enable = true;
    modules.bosh = true;
    extraModules = [ "private" "vcard" "privacy" "compression" "component" "muc" "pep" "adhoc" "lastactivity" "admin_adhoc" "blocklist" ];
    virtualHosts = {
      "${config.clanCore.machineName}.local" = {
        domain = "${config.clanCore.machineName}.local";
        enabled = true;
      };
    };
    extraConfig = ''
      allow_unencrypted_plain_auth = true
    '';
    c2sRequireEncryption = false;
    s2sRequireEncryption = false;
    muc = [{
      domain = "muc.${config.clanCore.machineName}.local";
      maxHistoryMessages = 10000;
      name = "${config.clanCore.machineName} Prosody";
    }];
    uploadHttp = {
      domain = "upload.${config.clanCore.machineName}.local";
    };
  };
  # xmpp-server
  networking.firewall.allowedTCPPorts = [ 5269 ];
}
