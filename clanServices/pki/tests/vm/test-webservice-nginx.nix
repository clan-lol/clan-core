{ ... }:
{
  _class = "clan.service";
  manifest.name = "test-webservice-nginx";
  manifest.description = "Dummy nginx web service for pki testing";
  manifest.exports.out = [ "endpoints" ];

  roles.default = {
    perInstance =
      { machine, mkExports, ... }:
      let
        host = "website.${machine.name}.test";
      in
      {
        exports = mkExports {
          endpoints.hosts = [ host ];
        };

        nixosModule =
          { ... }:
          {
            services.nginx = {
              enable = true;
              virtualHosts."${host}" = {
                onlySSL = true;
                locations."/" = {
                  return = "200 'pki test ok'";
                  extraConfig = "add_header Content-Type text/plain;";
                };
              };
            };
            networking.firewall.allowedTCPPorts = [ 443 ];
          };
      };
  };
}
