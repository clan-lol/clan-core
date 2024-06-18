{ pkgs, config, ... }:
let
  ms-accept = pkgs.callPackage ../pkgs/moonlight-sunshine-accept { };
  defaultPort = 48011;
in
{
  hardware.opengl.enable = true;
  environment.systemPackages = [
    pkgs.moonlight-qt
    ms-accept
  ];

  systemd.tmpfiles.rules = [
    "d '/var/lib/moonlight' 0770 'user' 'users' - -"
    "C '/var/lib/moonlight/moonlight.cert' 0644 'user' 'users' - ${
      config.clan.core.facts.services.moonlight.secret."moonlight.cert".path or ""
    }"
    "C '/var/lib/moonlight/moonlight.key' 0644 'user' 'users' - ${
      config.clan.core.facts.services.moonlight.secret."moonlight.key".path or ""
    }"
  ];

  systemd.user.services.init-moonlight = {
    enable = false;
    description = "Initializes moonlight";
    wantedBy = [ "graphical-session.target" ];
    script = ''
      ${ms-accept}/bin/moonlight-sunshine-accept moonlight init-config --key /var/lib/moonlight/moonlight.key --cert /var/lib/moonlight/moonlight.cert
    '';
    serviceConfig = {
      user = "user";
      Type = "oneshot";
      WorkingDirectory = "/home/user/";
      RunTimeDirectory = "moonlight";
      TimeoutSec = "infinity";
      Restart = "on-failure";
      RemainAfterExit = true;
      ReadOnlyPaths = [
        "/var/lib/moonlight/moonlight.key"
        "/var/lib/moonlight/moonlight.cert"
      ];
    };
  };

  systemd.user.services.moonlight-join = {
    description = "Join sunshine hosts";
    script = ''${ms-accept}/bin/moonlight-sunshine-accept moonlight join --port ${builtins.toString defaultPort} --cert '${
      config.clan.core.facts.services.moonlight.public."moonlight.cert".value or ""
    }' --host fd2e:25da:6035:c98f:cd99:93e0:b9b8:9ca1'';
    serviceConfig = {
      Type = "oneshot";
      TimeoutSec = "infinity";
      Restart = "on-failure";
      ReadOnlyPaths = [
        "/var/lib/moonlight/moonlight.key"
        "/var/lib/moonlight/moonlight.cert"
      ];
    };
  };
  systemd.user.timers.moonlight-join = {
    description = "Join sunshine hosts";
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnUnitActiveSec = "5min";
      OnBootSec = "0min";
      Persistent = true;
      Unit = "moonlight-join.service";
    };
  };

  clan.core.facts.services.moonlight = {
    secret."moonlight.key" = { };
    secret."moonlight.cert" = { };
    public."moonlight.cert" = { };
    generator.path = [
      pkgs.coreutils
      ms-accept
    ];
    generator.script = ''
      moonlight-sunshine-accept moonlight init
      mv credentials/cakey.pem "$secrets"/moonlight.key
      cp credentials/cacert.pem "$secrets"/moonlight.cert
      mv credentials/cacert.pem "$facts"/moonlight.cert
    '';
  };
}
