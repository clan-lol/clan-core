{
  lib,
  config,
  pkgs,
  roles,
  instanceName,
  ...
}:
let
  controllerMachine = builtins.head (lib.attrNames roles.controller.machines or { });
  networkIdPath = "${config.clan.core.settings.directory}/vars/per-machine/${controllerMachine}/zerotier/zerotier-network-id/value";
  networkId =
    if builtins.pathExists networkIdPath then
      builtins.readFile networkIdPath
    else
      builtins.throw ''
        No zerotier network id found for ${controllerMachine}.
        Please run `clan vars generate ${controllerMachine}` first.
      '';
  moons = lib.attrNames (roles.moon.machines or { });
  moonIps = builtins.foldl' (
    ips: name:
    if
      builtins.pathExists "${config.clan.core.settings.directory}/vars/per-machine/${name}/zerotier/zerotier-ip/value"
    then
      ips
      ++ [
        (builtins.readFile "${config.clan.core.settings.directory}/vars/per-machine/${name}/zerotier/zerotier-ip/value")
      ]
    else
      ips
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
