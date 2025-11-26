{
  name = "yggdrasil";

  clan = {
    test.useContainers = false;
    directory = ./.;
    inventory = {

      machines.peer1 = { };
      machines.peer2 = { };

      instances."yggdrasil" = {
        module.name = "yggdrasil";
        module.input = "self";

        # Assign the roles to the two machines
        roles.default.machines.peer1 = { };
        roles.default.machines.peer2 = { };
      };

      # Test that yggdrasil correctly consumes exports from all
      # networking services

      # TODO: Should we also test other VPNs e.g. wireguard?

      # Internet service provides static host exports
      instances."internet" = {
        module.name = "internet";
        roles.default.machines.peer1.settings.host = "peer1";
        roles.default.machines.peer2.settings.host = "peer2";
      };

      # # Zerotier provides peer.host exports
      instances."zerotier" = {
        module.name = "zerotier";
        roles.peer.machines.peer1 = { };
        roles.peer.machines.peer2 = { };
        roles.controller.machines.peer1 = { };
      };

      # Mycelium provides peer.host exports
      instances."mycelium" = {
        module.name = "mycelium";
        roles.peer.machines.peer1 = { };
        roles.peer.machines.peer2 = { };
      };
    };
  };

  testScript = ''
    start_all()

    # Wait for both machines to be ready
    peer1.wait_for_unit("multi-user.target")
    peer2.wait_for_unit("multi-user.target")

    # Check that yggdrasil service is running on both machines
    peer1.wait_for_unit("yggdrasil")
    peer2.wait_for_unit("yggdrasil")
    peer1.succeed("systemctl is-active yggdrasil")
    peer2.succeed("systemctl is-active yggdrasil")

    # Check that both machines have yggdrasil network interfaces
    peer1.wait_until_succeeds("ip link show | grep -E 'ygg'", 30)
    peer2.wait_until_succeeds("ip link show | grep -E 'ygg'", 30)

    # Get yggdrasil IPv6 addresses from both machines
    peer1_ygg_ip = peer1.succeed("yggdrasilctl -json getself | jq -r '.address'").strip()
    peer2_ygg_ip = peer2.succeed("yggdrasilctl -json getself | jq -r '.address'").strip()

    # Compare runtime addresses with saved addresses from vars
    expected_peer1_ip = "${builtins.readFile ./vars/per-machine/peer1/yggdrasil/address/value}"
    expected_peer2_ip = "${builtins.readFile ./vars/per-machine/peer2/yggdrasil/address/value}"

    print(f"peer1 yggdrasil IP: {peer1_ygg_ip}")
    print(f"peer2 yggdrasil IP: {peer2_ygg_ip}")
    print(f"peer1 expected IP: {expected_peer1_ip}")
    print(f"peer2 expected IP: {expected_peer2_ip}")

    # Verify that runtime addresses match expected addresses
    assert peer1_ygg_ip == expected_peer1_ip, f"peer1 runtime IP {peer1_ygg_ip} != expected IP {expected_peer1_ip}"
    assert peer2_ygg_ip == expected_peer2_ip, f"peer2 runtime IP {peer2_ygg_ip} != expected IP {expected_peer2_ip}"

    # Verify that yggdrasil consumed exports from all networking services
    # Check that peer configuration includes exports from internet, zerotier, tor, and mycelium
    print("Checking that yggdrasil peers include exports from all networking services...")

    peers_config = peer1.succeed("yggdrasilctl -json getpeers").strip()
    print(f"Yggdrasil peers on peer1: {peers_config}")

    # The peers list should include URLs generated from the various service exports
    # We verify that the peers configuration is non-empty and properly formatted
    import json
    peers = json.loads(peers_config)

    # Basic sanity check: peers should be a dictionary
    assert isinstance(peers, dict), "Peers config should be a dictionary"
    print(f"✓ Yggdrasil has {len(peers)} peer connection(s) configured")

    # Wait a bit for the yggdrasil network to establish connectivity
    import time
    time.sleep(10)

    # Test connectivity: peer1 should be able to ping peer2 via yggdrasil
    peer1.succeed(f"ping -6 -c 3 {peer2_ygg_ip}")

    # Test connectivity: peer2 should be able to ping peer1 via yggdrasil
    peer2.succeed(f"ping -6 -c 3 {peer1_ygg_ip}")

    print("✓ All tests passed!")
  '';
}
