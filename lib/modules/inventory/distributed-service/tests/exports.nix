{ lib, clanLib }:
let
  clan = clanLib.clan {
    self = { };
    directory = ./.;

    exportsModule = {
      options.vars.generators = lib.mkOption {
        type = lib.types.attrsOf (
          lib.types.submoduleWith {
            # TODO: import the vars submodule here
            modules = [
              {
                options.script = lib.mkOption { type = lib.types.str; };
              }
            ];
          }
        );
        default = { };
      };
    };

    machines.jon = { };
    machines.sara = { };
    # A module that adds exports perMachine
    modules.A =
      { exports', ... }:
      {
        manifest.name = "A";
        roles.peer.perInstance =
          { machine, ... }:
          {
            # Cross reference a perMachine exports
            exports.vars.generators."${machine.name}-network-ip".script =
              "A:" + exports'.machines.${machine.name}.vars.generators.key.script;
            # Cross reference a perInstance exports from a different service
            exports.vars.generators."${machine.name}-full-hostname".script =
              "A:" + exports'.instances."B-1".vars.generators.hostname.script;
          };
        roles.server = { };
        perMachine =
          { machine, ... }:
          {
            exports = {
              vars.generators.key.script = machine.name;
            };
          };
      };
    # A module that adds exports perInstance
    modules.B = {
      manifest.name = "B";
      roles.peer.perInstance =
        { instanceName, ... }:
        {
          exports = {
            vars.generators.hostname.script = instanceName;
          };
        };
    };

    inventory = {
      instances.B-1 = {
        module.name = "B";
        module.input = "self";
        roles.peer.tags.all = { };
      };
      instances.B-2 = {
        module.name = "B";
        module.input = "self";
        roles.peer.tags.all = { };
      };
      instances.A-1 = {
        module.name = "A";
        module.input = "self";
        roles.peer.tags.all = { };
        roles.server.tags.all = { };
      };
      instances.A-2 = {
        module.name = "A";
        module.input = "self";
        roles.peer.tags.all = { };
        roles.server.tags.all = { };
      };
    };
  };
in
{
  test_1 = {
    inherit clan;
    expr = clan.config.exports;
    expected = {
      instances = {
        A-1 = {
          vars = {
            generators = {
              jon-full-hostname = {
                script = "A:B-1";
              };
              jon-network-ip = {
                script = "A:jon";
              };
              sara-full-hostname = {
                script = "A:B-1";
              };
              sara-network-ip = {
                script = "A:sara";
              };
            };
          };
        };
        A-2 = {
          vars = {
            generators = {
              jon-full-hostname = {
                script = "A:B-1";
              };
              jon-network-ip = {
                script = "A:jon";
              };
              sara-full-hostname = {
                script = "A:B-1";
              };
              sara-network-ip = {
                script = "A:sara";
              };
            };
          };
        };
        B-1 = {
          vars = {
            generators = {
              hostname = {
                script = "B-1";
              };
            };
          };
        };
        B-2 = {
          vars = {
            generators = {
              hostname = {
                script = "B-2";
              };
            };
          };
        };
      };
      machines = {
        jon = {
          vars = {
            generators = {
              key = {
                script = "jon";
              };
            };
          };
        };
        sara = {
          vars = {
            generators = {
              key = {
                script = "sara";
              };
            };
          };
        };
      };
    };
  };
}
