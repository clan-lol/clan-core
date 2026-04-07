{ ... }:
{
  _class = "clan.service";
  manifest.name = "test-webservice-nginx";
  manifest.description = "Dummy nginx web service for pki testing";
  manifest.readme = "Dummy readme to silence eval warnings.";
  manifest.exports.out = [ "endpoints" ];

  roles.default = {
    description = "Dummy description to silence eval warnings.";

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
