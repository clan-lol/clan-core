# Shared configuration for user firewall tests
{ self, pkgs, ... }:
{
  imports = [
    self.nixosModules.user-firewall
  ];

  networking.firewall.enable = true;

  # Configure the user firewall module
  # Test with default allowedInterfaces (which includes wg*)
  networking.user-firewall = {
    # Use defaults for allowedInterfaces to test that wg* is included by default
    exemptUsers = [
      "root"
      "alice"
    ];
  };

  # Create test users
  users.users = {
    alice = {
      isNormalUser = true;
      uid = 1001;
      initialPassword = "test";
    };

    bob = {
      isNormalUser = true;
      uid = 1002;
      initialPassword = "test";
    };
  };

  # Add tools for testing
  environment.systemPackages = with pkgs; [
    curl
    netcat
    iproute2
  ];

  # Add a local web server for testing
  services.nginx = {
    enable = true;
    virtualHosts = {
      "localhost" = {
        listen = [
          {
            addr = "127.0.0.1";
            port = 8080;
          }
        ];
        locations."/" = {
          return = "200 'test server response'";
          extraConfig = "add_header Content-Type text/plain;";
        };
      };
      "wg0-test" = {
        listen = [
          {
            addr = "10.100.0.2";
            port = 8081;
          }
          {
            addr = "[fd00::2]";
            port = 8081;
          }
        ];
        locations."/" = {
          return = "200 'wg0 interface test response'";
          extraConfig = "add_header Content-Type text/plain;";
        };
      };
    };
  };

  # Create a dummy interface to test allowed interface patterns
  systemd.services.setup-wg0-interface = {
    description = "Setup wg0 dummy interface";
    after = [ "network-pre.target" ];
    before = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = true;
    };
    script = ''
      ${pkgs.iproute2}/bin/ip link add wg0 type dummy || true
      ${pkgs.iproute2}/bin/ip addr add 10.100.0.2/24 dev wg0 || true
      ${pkgs.iproute2}/bin/ip addr add fd00::2/64 dev wg0 || true
      ${pkgs.iproute2}/bin/ip link set wg0 up || true
    '';
  };

  # Make nginx wait for the wg0 interface
  systemd.services.nginx = {
    after = [ "setup-wg0-interface.service" ];
    requires = [ "setup-wg0-interface.service" ];
  };
}
