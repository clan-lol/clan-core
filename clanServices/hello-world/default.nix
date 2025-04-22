{ packages }:
{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/hello-word";

  roles.peer = { };

  perMachine =
    { machine, ... }:
    {
      nixosModule = {
        clan.core.vars.generators.hello = {
          files.hello = {
            secret = false;
          };
          script = ''
            echo "Hello world from ${machine.name}" > $out/hello
          '';
        };
      };
    };
}
