{
  name = "user-firewall-nftables";

  nodes = {
    router = {
      imports = [ ./router.nix ];
    };

    machine = {
      imports = [ ./common.nix ];

      # Force nftables backend
      networking.nftables.enable = true;
    };
  };

  testScript = ''
    start_all()
    router.wait_for_unit("multi-user.target")
    router.wait_for_unit("nginx.service")
    machine.wait_for_unit("multi-user.target")
    machine.wait_for_unit("nginx.service")

    # Get router IPs (both IPv4 and IPv6)
    router_ip = router.succeed("ip -4 addr show eth1 | grep -oP '(?<=inet\\s)\\d+(\\.\\d+){3}'").strip()
    router_ip6 = router.succeed("ip -6 addr show eth1 | grep -oP '(?<=inet6\\s)[0-9a-f:]+' | grep -v '^fe80' | head -1").strip()
    print(f"Router IPv4: {router_ip}")
    print(f"Router IPv6: {router_ip6}")

    # Test nftables restart
    machine.succeed("systemctl restart nftables")
    machine.wait_for_unit("nftables.service")

    # Verify rules are loaded
    machine.succeed("nft list table inet user-firewall >&2")

    # Test alice (exempt user) - should succeed both locally and to router
    machine.wait_until_succeeds("runuser -u alice -- curl -s http://127.0.0.1:8080")
    machine.succeed(f"runuser -u alice -- curl -s http://{router_ip}")
    machine.succeed(f"runuser -u alice -- curl -s http://[{router_ip6}]")

    # Test bob (restricted user) - localhost should work, external should fail
    machine.succeed("runuser -u bob -- curl -s http://127.0.0.1:8080")
    # This should be blocked by firewall - IPv4
    result = machine.succeed(f"runuser -u bob -- curl -s --connect-timeout 2 http://{router_ip} 2>&1 || echo 'EXIT_CODE='$?")
    assert "EXIT_CODE=7" in result, f"Bob should be blocked from external IPv4 access (expected EXIT_CODE=7) but got: {result}"
    # This should be blocked by firewall - IPv6
    result6 = machine.succeed(f"runuser -u bob -- curl -s --connect-timeout 2 http://[{router_ip6}] 2>&1 || echo 'EXIT_CODE='$?")
    assert "EXIT_CODE=7" in result6, f"Bob should be blocked from external IPv6 access (expected EXIT_CODE=7) but got: {result6}"

    # Verify the rules are actually present
    rules = machine.succeed("nft list table inet user-firewall")
    assert 'meta skuid 1002' in rules and 'reject' in rules, f"Reject rule for bob (uid 1002) not found in nftables. Actual rules:\n{rules}"
    assert "oifname" in rules, f"Interface rules not found in nftables. Actual rules:\n{rules}"

    # Wait for the dummy interface to be created
    machine.wait_for_unit("setup-wg0-interface.service")
    machine.wait_for_unit("nginx.service")
    machine.wait_for_open_port(8081, "10.100.0.2")

    # Check that wg0 interface exists
    machine.succeed("ip link show wg0")
    machine.succeed("ip addr show wg0")

    # The key test: users should be able to connect via wg0 interface
    # For alice (exempt user) - should work
    machine.succeed("runuser -u alice -- curl -s --interface wg0 http://10.100.0.2:8081/")
    machine.succeed("runuser -u alice -- curl -s --interface wg0 http://[fd00::2]:8081/")  # IPv6 test

    # For bob (restricted user) - should also work because wg* is in default allowedInterfaces
    machine.succeed("runuser -u bob -- curl -s --interface wg0 http://10.100.0.2:8081/")
    machine.succeed("runuser -u bob -- curl -s --interface wg0 http://[fd00::2]:8081/")  # IPv6 test

    # Verify that wg* interfaces are allowed in the nftables rules
    rules_with_wg = machine.succeed("nft list table inet user-firewall | grep -E 'oifname.*wg' >&2")
  '';
}
