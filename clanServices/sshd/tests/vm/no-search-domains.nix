/*
  This is a regression test for the following error:
  error: attribute 'openssh-cert' missing
  at /nix/store/y1k4bqwjql6bhlry456cs4marpamiqlr-source/clanServices/sshd/default.nix:184:17:
    183|                 # this check needs to go first, as otherwise generators.openssh-cert does not exist
    184|                 config.clan.core.vars.generators.openssh-cert.files."ssh.id_ed25519-cert.pub".exists
        |                 ^
    185|                 && settings.certificate.searchDomains != [ ]
*/
{
  ...
}:
{
  name = "sshd";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };
      machines.client = { };

      instances = {
        sshd-test = {
          module.name = "@clan/sshd";
          module.input = "self";
          roles.server.machines."server".settings = {
            hostKeys.rsa.enable = true;
          };
          roles.client.machines."client".settings = {
          };
        };
      };
    };
  };

  nodes = {
    server = { };
    client = { };
  };

  testScript = ''
    # don't do anything, just evaluate the machines
    exit(0)
  '';
}
