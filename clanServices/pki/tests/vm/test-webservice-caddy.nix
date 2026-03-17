{ ... }:
{
  _class = "clan.service";
  manifest.name = "test-webservice-caddy";
  manifest.description = "Dummy caddy web service for pki testing";
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
            services.caddy = {
              enable = true;
              virtualHosts."${host}" = {
                extraConfig = ''
                  respond "pki test ok" 200
                '';
              };
            };
            networking.firewall.allowedTCPPorts = [ 443 ];
          };
      };
  };
}
