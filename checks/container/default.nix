(
  { ... }:
  {
    name = "container";

    nodes.machine1 =
      { ... }:
      {
        networking.hostName = "machine1";
        services.openssh.enable = true;
        services.openssh.startWhenNeeded = false;
      };

    nodes.machine2 =
      { ... }:
      {
        networking.hostName = "machine2";
        services.openssh.enable = true;
        services.openssh.startWhenNeeded = false;
      };

    testScript = ''
      import subprocess
      start_all()
      machine1.succeed("systemctl status sshd")
      machine2.succeed("systemctl status sshd")
      machine1.wait_for_unit("sshd")
      machine2.wait_for_unit("sshd")

      p1 = subprocess.run(["ip", "a"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      assert p1.returncode == 0
      bridge_output = p1.stdout.decode("utf-8")
      assert "br0" in bridge_output, f"bridge not found in ip a output: {bridge_output}"

      for m in [machine1, machine2]:
          out = machine1.succeed("ip addr show eth1")
          assert "UP" in out, f"UP not found in ip addr show output: {out}"
          assert "inet" in out, f"inet not found in ip addr show output: {out}"
          assert "inet6" in out, f"inet6 not found in ip addr show output: {out}"

      machine1.succeed("ping -c 1 machine2")
    '';
  }
)
