{ packages }:
{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/hello-word";
  manifest.description = "This is a test";

  roles.peer = {
    interface =
      { lib, ... }:
      {
        options.foo = lib.mkOption {
          type = lib.types.str;
          # default = "";
          description = "Some option";
        };
      };
  };

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
