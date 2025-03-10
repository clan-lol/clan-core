(import ../lib/test-base.nix) (
  { self, lib, ... }:
  let

    inherit (self.lib.inventory) buildInventory;

    machines = [
      "signer"
      "admin"
      "peer"
    ];

    serviceConfigs = buildInventory {
      inventory = {
        machines = lib.genAttrs machines (_: { });
        services = {
          data-mesher.default = {
            roles.peer.machines = [ "peer" ];
            roles.admin.machines = [ "admin" ];
            roles.signer.machines = [ "signer" ];
          };
        };
        modules = {
          data-mesher = self.clanModules.data-mesher;
        };
      };
      directory = ./.;
    };

    commonConfig =
      { config, ... }:
      {

        imports = [ self.nixosModules.clanCore ];

        clan.core.settings.directory = builtins.toString ./.;

        environment.systemPackages = [
          config.services.data-mesher.package
        ];

        clan.core.vars.settings.publicStore = "in_repo";
        clan.core.vars.settings.secretStore = "vm";

        clan.data-mesher.network.interface = "eth1";
        clan.data-mesher.bootstrapNodes = [
          "[2001:db8:1::1]:7946" # peer1
          "[2001:db8:1::2]:7946" # peer2
        ];

        # speed up for testing
        services.data-mesher.settings = {
          cluster.join_interval = lib.mkForce "2s";
          cluster.push_pull_interval = lib.mkForce "5s";
        };

        systemd.tmpfiles.settings."vmsecrets" = {
          "/etc/secrets" = {
            C.argument = "${./vars/secret/${config.clan.core.settings.machine.name}}";
            z = {
              mode = "0700";
              user = "data-mesher";
            };
          };
        };
      };

    adminConfig = {
      imports = serviceConfigs.machines.admin.machineImports;

      config.clan.data-mesher.network.tld = "foo";
      config.clan.core.settings.machine.name = "admin";
    };

    peerConfig = {
      imports = serviceConfigs.machines.peer.machineImports;
      config.clan.core.settings.machine.name = "peer";
    };

    signerConfig = {
      imports = serviceConfigs.machines.signer.machineImports;
      clan.core.settings.machine.name = "signer";
    };

  in
  {
    name = "data-mesher";

    nodes = {
      peer = {
        imports = [
          peerConfig
          commonConfig
        ];
      };

      admin = {
        imports = [
          adminConfig
          commonConfig
        ];
      };

      signer = {
        imports = [
          signerConfig
          commonConfig
        ];
      };
    };

    # TODO Add better test script.
    testScript = ''

      def resolve(node, success = {}, fail = [], timeout = 60):
        for hostname, ips in success.items():
            for ip in ips:
                node.wait_until_succeeds(f"getent ahosts {hostname} | grep {ip}", timeout)

        for hostname in fail:
            node.wait_until_fails(f"getent ahosts {hostname}")

      start_all()

      admin.wait_for_unit("data-mesher")
      signer.wait_for_unit("data-mesher")
      peer.wait_for_unit("data-mesher")

      # check dns resolution
      for node in [admin, signer, peer]:
        resolve(node, {
            "admin.foo": ["2001:db8:1::1", "192.168.1.1"],
            "peer.foo": ["2001:db8:1::2", "192.168.1.2"],
            "signer.foo": ["2001:db8:1::3", "192.168.1.3"]
        })
    '';
  }
)
