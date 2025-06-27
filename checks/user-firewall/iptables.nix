{
  name = "user-firewall-iptables";

  nodes = {
    router =
      { ... }:
      {
        imports = [ ./router.nix ];
      };

    machine =
      { ... }:
      {
        imports = [ ./common.nix ];

        # Force iptables backend
        networking.nftables.enable = false;
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

    # Test firewall restart
    machine.succeed("systemctl restart firewall")
    machine.wait_for_unit("firewall.service")

    # Verify rules are loaded
    machine.succeed("iptables -L user-firewall-output >&2")

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

    # Verify the rules are actually present for both IPv4 and IPv6
    rules4 = machine.succeed("iptables -L user-firewall-output -n -v")
    assert "REJECT" in rules4, "REJECT rule not found in iptables"
    rules6 = machine.succeed("ip6tables -L user-firewall-output -n -v")
    assert "REJECT" in rules6, "REJECT rule not found in ip6tables"

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

    # Verify that wg* interfaces are allowed in the firewall rules
    machine.succeed("iptables -L user-firewall-output -n -v | grep -E 'wg0|wg\\+' >&2")
  '';
}
