{
  clanLib,
  lib,
  config,
  pkgs,
  roles,
  instanceName,
  ...
}:
let
  controllerMachine = builtins.head (lib.attrNames roles.controller.machines or { });
  networkId = clanLib.getPublicValue {
    flake = config.clan.core.settings.directory;
    machine = controllerMachine;
    generator = "zerotier";
    file = "zerotier-network-id";
    default = null;
  };
  moons = lib.attrNames (roles.moon.machines or { });
  moonIps = builtins.foldl' (
    ips: name:
    let
      moonIp = clanLib.getPublicValue {
        flake = config.clan.core.settings.directory;
        machine = name;
        generator = "zerotier";
        file = "zerotier-ip";
        default = null;
      };
    in
    if moonIp != null then ips ++ [ moonIp ] else ips
  ) [ ] moons;
in
{
  config = {
    clan.core.networking.zerotier.networkId = networkId;
    clan.core.networking.zerotier.name = instanceName;

    systemd.services.zerotierone.serviceConfig.ExecStartPost = lib.mkIf (moonIps != [ ]) (
      lib.mkAfter [
        "+${pkgs.writeScript "orbit-moons-by-ip" ''
          #!${pkgs.python3.interpreter}
          import json
          import ipaddress
          import subprocess

          def compute_member_id(ipv6_addr: str) -> str:
              addr = ipaddress.IPv6Address(ipv6_addr)
              addr_bytes = bytearray(addr.packed)

              # Extract the bytes corresponding to the member_id (node_id)
              node_id_bytes = addr_bytes[10:16]
              node_id = int.from_bytes(node_id_bytes, byteorder="big")

              member_id = format(node_id, "x").zfill(10)[-10:]

              return member_id
          def main() -> None:
              ips = json.loads(${builtins.toJSON (builtins.toJSON moonIps)})
              for ip in ips:
                  member_id = compute_member_id(ip)
                  res = subprocess.run(["zerotier-cli", "orbit", member_id, member_id])
                  if res.returncode != 0:
                      print(f"Failed to add {member_id} to orbit")
          if __name__ == "__main__":
              main()
        ''}"
      ]
    );

  };
}
