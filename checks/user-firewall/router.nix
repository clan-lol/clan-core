# Shared router configuration for user firewall tests
{ ... }:
{
  networking.firewall.enable = false;
  networking.useNetworkd = true;

  # Simple web server to test connectivity
  services.nginx = {
    enable = true;
    virtualHosts."router" = {
      listen = [
        {
          addr = "0.0.0.0";
          port = 80;
        }
        {
          addr = "[::]";
          port = 80;
        }
        {
          addr = "10.100.0.1";
          port = 80;
        }
      ];
      locations."/" = {
        return = "200 'router response'";
        extraConfig = "add_header Content-Type text/plain;";
      };
    };
  };

}
