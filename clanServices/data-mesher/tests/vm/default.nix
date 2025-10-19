{
  ...
}:
{
  name = "data-mesher";

  clan = {
    directory = ./.;
    test.useContainers = true;
    inventory = {

      machines.peer = { };
      machines.admin = { };
      machines.signer = { };

      instances = {
        data-mesher =
          let
            bootstrapNodes = [
              "[2001:db8:1::1]:7946" # admin
              "[2001:db8:1::2]:7946" # peer
              # "2001:db8:1::3:7946" #signer
            ];
          in
          {
            roles.peer.machines.peer.settings = {
              network.interface = "eth1";
              inherit bootstrapNodes;
            };
            roles.signer.machines.signer.settings = {
              network.interface = "eth1";
              inherit bootstrapNodes;
            };
            roles.admin.machines.admin.settings = {
              network.tld = "foo";
              network.interface = "eth1";
              inherit bootstrapNodes;
            };
          };
      };
    };
  };

  nodes =
    let
      commonConfig =
        { lib, config, ... }:
        {
          environment.systemPackages = [
            config.services.data-mesher.package
          ];

          # speed up for testing
          services.data-mesher.settings = {
            cluster.join_interval = lib.mkForce "2s";
            cluster.push_pull_interval = lib.mkForce "5s";
          };

        };
    in
    {
      peer = commonConfig;
      admin = commonConfig;
      signer = commonConfig;
    };

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
