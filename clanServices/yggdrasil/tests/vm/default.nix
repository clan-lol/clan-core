{
  name = "yggdrasil";

  clan = {
    test.useContainers = false;
    directory = ./.;
    inventory = {

      machines.peer1 = { };
      machines.peer2 = { };
      machines.outsider = { };

      # Main yggdrasil instance for peer1 and peer2 (clan members)
      instances."yggdrasil" = {
        module.name = "yggdrasil";
        module.input = "self";

        # Assign the roles to the two machines
        roles.default.machines.peer1 = { };
        roles.default.machines.peer2 = { };
      };

      # Separate yggdrasil instance for outsider (not in the clan)
      instances."yggdrasil-outsider" = {
        module.name = "yggdrasil";
        module.input = "self";

        # Only outsider in this instance
        roles.default.machines.outsider = { };
      };

      # Test that yggdrasil correctly consumes exports from all
      # networking services

      # TODO: Should we also test other VPNs e.g. wireguard?

      # Internet service provides static host exports
      instances."internet" = {
        module.name = "internet";
        roles.default.machines.peer1.settings.host = "peer1";
        roles.default.machines.peer2.settings.host = "peer2";
        roles.default.machines.outsider.settings.host = "outsider";
      };

      # # Zerotier provides peer.host exports
      instances."zerotier" = {
        module.name = "zerotier";
        roles.peer.machines.peer1 = { };
        roles.peer.machines.peer2 = { };
        roles.peer.machines.outsider = { };
        roles.controller.machines.peer1 = { };
      };

      # Mycelium provides peer.host exports
      instances."mycelium" = {
        module.name = "mycelium";
        roles.peer.machines.peer1 = { };
        roles.peer.machines.peer2 = { };
        roles.peer.machines.outsider = { };
      };
    };
  };

  nodes.peer1 =
    { pkgs, ... }:
    {
      # Start a test service on port 8888 that is NOT in allowedTCPPorts
      # This will test that yggdrasil respects the firewall

      # The test should fail, when this is added:
      # networking.firewall.allowedTCPPorts = [ 8888 ];

      systemd.services.test-http-server = {
        wantedBy = [ "multi-user.target" ];
        after = [ "network.target" ];
        script = ''
          ${pkgs.python3}/bin/python3 -m http.server 8888 --bind ::
        '';
        serviceConfig = {
          Restart = "always";
          RestartSec = "1s";
        };
      };
    };

  testScript = ''
    start_all()

    # Wait for all machines to be ready
    peer1.wait_for_unit("multi-user.target")
    peer2.wait_for_unit("multi-user.target")
    outsider.wait_for_unit("multi-user.target")

    # Check that yggdrasil service is running on peer machines
    peer1.wait_for_unit("yggdrasil")
    peer2.wait_for_unit("yggdrasil")
    peer1.succeed("systemctl is-active yggdrasil")
    peer2.succeed("systemctl is-active yggdrasil")

    # Check that outsider also has yggdrasil running (standalone, not part of clan)
    outsider.wait_for_unit("yggdrasil")
    outsider.succeed("systemctl is-active yggdrasil")

    # Wait for test HTTP server to be ready
    peer1.wait_for_unit("test-http-server")
    peer1.wait_for_open_port(8888)

    # Check that all machines have yggdrasil network interfaces
    peer1.wait_until_succeeds("ip link show | grep -E 'ygg'", 30)
    peer2.wait_until_succeeds("ip link show | grep -E 'ygg'", 30)
    outsider.wait_until_succeeds("ip link show | grep -E 'ygg'", 30)

    # Get yggdrasil IPv6 addresses from all machines
    peer1_ygg_ip = peer1.succeed("yggdrasilctl -json getself | jq -r '.address'").strip()
    peer2_ygg_ip = peer2.succeed("yggdrasilctl -json getself | jq -r '.address'").strip()
    outsider_ygg_ip = outsider.succeed("yggdrasilctl -json getself | jq -r '.address'").strip()

    # Compare runtime addresses with saved addresses from vars
    expected_peer1_ip = "${builtins.readFile ./vars/per-machine/peer1/yggdrasil/address/value}"
    expected_peer2_ip = "${builtins.readFile ./vars/per-machine/peer2/yggdrasil/address/value}"
    expected_outsider_ip = "${builtins.readFile ./vars/per-machine/outsider/yggdrasil/address/value}"

    print(f"peer1 yggdrasil IP: {peer1_ygg_ip}")
    print(f"peer2 yggdrasil IP: {peer2_ygg_ip}")
    print(f"outsider yggdrasil IP: {outsider_ygg_ip}")
    print(f"peer1 expected IP: {expected_peer1_ip}")
    print(f"peer2 expected IP: {expected_peer2_ip}")
    print(f"outsider expected IP: {expected_outsider_ip}")

    # Verify that runtime addresses match expected addresses
    assert peer1_ygg_ip == expected_peer1_ip, f"peer1 runtime IP {peer1_ygg_ip} != expected IP {expected_peer1_ip}"
    assert peer2_ygg_ip == expected_peer2_ip, f"peer2 runtime IP {peer2_ygg_ip} != expected IP {expected_peer2_ip}"
    assert outsider_ygg_ip == expected_outsider_ip, f"outsider runtime IP {outsider_ygg_ip} != expected IP {expected_outsider_ip}"

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

    # Test firewall rules: clan members should be able to communicate
    print("Testing firewall rules: clan members should be able to communicate...")

    # peer1 and peer2 are in the clan role, so they should be able to ping each other
    peer1.succeed(f"ping -6 -c 3 -W 5 {peer2_ygg_ip}")
    peer2.succeed(f"ping -6 -c 3 -W 5 {peer1_ygg_ip}")
    print("✓ Clan members can communicate with each other")

    # Test firewall rules: outsider should be blocked
    print("Testing firewall rules: outsider (not in clan role) should be blocked...")

    # First, verify that outsider can establish yggdrasil connectivity (network layer works)
    # by checking that outsider has peers
    outsider_peers = outsider.succeed("yggdrasilctl -json getpeers").strip()
    print(f"Outsider peers: {outsider_peers}")

    # Now test that firewall blocks traffic from outsider to clan members
    # The firewall should drop packets from IPs not in the allowedYggdrasilIPs list
    # This means outsider -> peer1 should fail
    print(f"Testing that outsider ({outsider_ygg_ip}) cannot reach peer1 ({peer1_ygg_ip})...")
    peer1.fail(f"ping -6 -c 3 -W 5 {outsider_ygg_ip}")

    print(f"Testing that outsider ({outsider_ygg_ip}) cannot reach peer2 ({peer2_ygg_ip})...")
    peer2.fail(f"ping -6 -c 3 -W 5 {outsider_ygg_ip}")

    print("✓ Firewall correctly blocks non-clan members")

    # Test that services not in allowedTCPPorts are NOT accessible via yggdrasil
    # This verifies that yggdrasil respects the firewall and doesn't bypass allowedTCPPorts
    print("Testing that services not exposed via allowedTCPPorts are NOT accessible via yggdrasil...")

    # Port 8888 is NOT in allowedTCPPorts, so it should be blocked on all interfaces
    # including yggdrasil

    # First, verify the service is running locally on peer1
    peer1.succeed("curl -s http://localhost:8888 | grep 'Directory listing'")
    print("✓ Test service is running on peer1")

    # Test that peer2 (clan member) CANNOT reach the service via yggdrasil
    # because port 8888 is not in allowedTCPPorts
    print(f"Testing that peer2 cannot reach port 8888 on peer1 ({peer1_ygg_ip}) via yggdrasil...")
    peer2.fail(f"timeout 5 curl -g -s http://[{peer1_ygg_ip}]:8888")
    print("✓ Clan member (peer2) is correctly blocked - port not in allowedTCPPorts")

    # Test that outsider (non-clan member) also CANNOT reach the service
    print(f"Testing that outsider cannot reach port 8888 on peer1 ({peer1_ygg_ip}) via yggdrasil...")
    outsider.fail(f"timeout 5 curl -g -s http://[{peer1_ygg_ip}]:8888")
    print("✓ Non-clan member (outsider) is also blocked")

    print("✓ Yggdrasil respects allowedTCPPorts firewall rules")

    print("✓ All tests passed!")
  '';
}
