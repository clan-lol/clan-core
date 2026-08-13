{
  lib,
  ...
}:

let
  machines = [
    "ctrl1"
    "ctrl2"
    "peer1"
    "peer2"
    "peer3"
  ];
in
{
  name = "wireguard";

  clan = {
    directory = ./.;
    inventory = {

      machines = lib.genAttrs machines (_: { });

      instances = {

        /*
                        wg-test-one
          ┌───────────────────────────────┐
          │            ◄─────────────     │
          │ ctrl2              ctrl1
          │    ▲       ─────────────►    ▲     ▲
          │    │ │ │ │                 │ │   │ │
          │    │ │ │ │                 │ │   │ │
          │    │ │ │ │                 │ │   │ │
          │    │ │ │ └───────────────┐ │ │   │ │
          │    │ │ └──────────────┐  │ │ │   │ │
          │      ▼                │  ▼ ▼     ▼
          └─► peer2               │  peer1  peer3
                                  │          ▲
                                  └──────────┘
        */

        wg-test-one = {

          module.name = "@clan/wireguard";
          module.input = "self";

          roles.controller.machines."ctrl1".settings = {
            endpoint = "192.168.1.1";
          };

          roles.controller.machines."ctrl2".settings = {
            endpoint = "192.168.1.2";
          };

          roles.peer.machines = {
            peer1.settings.controller = "ctrl1";
            peer2.settings.controller = "ctrl2";
            peer3.settings.controller = "ctrl1";
          };
        };

        # TODO: Will this actually work with conflicting ports? Can we re-use interfaces?
        #wg-test-two = {
        #  module.name = "@clan/wireguard";

        #  roles.controller.machines."ctrl1".settings = {
        #    endpoint = "192.168.1.1";
        #    port = 51922;
        #  };

        #  roles.peer.machines = {
        #    peer1 = { };
        #  };
        #};
      };
    };
  };

  testScript = ''
    start_all()

    # Show all addresses
    machines = [peer1, peer2, peer3, ctrl1, ctrl2]
    for m in machines:
        m.systemctl("start network-online.target")

    for m in machines:
        m.wait_for_unit("network-online.target")
        m.wait_for_unit("systemd-networkd.service")

    print("\n\n" + "="*60)
    print("STARTING PING TESTS")
    print("="*60)

    for m1 in machines:
        for m2 in machines:
            if m1 != m2:
                print(f"\n--- Pinging from {m1.name} to {m2.name}.wg-test-one ---")
                m1.wait_until_succeeds(f"ping -c1 {m2.name}.wg-test-one >&2")
  '';
}
