{ ... }:
{
  name = "monitoring";

  clan = {
    directory = ./.;
    inventory = {
      machines.peer1 = {
        deploy.targetHost = "[2001:db8:1::1]";
      };

      instances."test" = {
        module.name = "monitoring";
        module.input = "self";

        roles.telegraf.machines.peer1 = { };
        roles.telegraf.settings = {
          allowAllInterfaces = true;
        };
      };
    };
  };

  nodes = {
    peer1 =
      { lib, ... }:
      {
        services.telegraf.extraConfig = {
          agent.interval = lib.mkForce "1s";
          outputs.prometheus_client = {
            # BUG: We have to disable basic auth here because the prometheus_client
            # output plugin will otherwise deadlock Telegraf on startup.
            basic_password = lib.mkForce "";
            basic_username = lib.mkForce "";
          };
        };
      };
  };

  # !!! ANY CHANGES HERE MUST BE REFLECTED IN:
  # clan_lib/metrics/telegraf.py::get_metrics
  testScript =
    { nodes, ... }:
    ''
      import time
      import os
      import sys
      import subprocess 
      import ssl
      import json
      import shlex
      import urllib.request
      from base64 import b64encode
      start_all()

      peer1.wait_for_unit("network-online.target")
      peer1.wait_for_unit("telegraf.service")
      peer1.wait_for_unit("telegraf-json.service")

      # Fetch the basic auth password from the secret file
      password = peer1.succeed("cat ${nodes.peer1.clan.core.vars.generators.telegraf.files.password.path}").strip()
      credentials = f"prometheus:{password}"

      print("Using credentials:", credentials)
      peer1.succeed(f"curl -k -u {credentials}  https://localhost:9990/telegraf.json")
      peer1.succeed(f"curl -k -u {credentials}  https://localhost:9273/metrics")

      cert_path = "${nodes.peer1.clan.core.vars.generators.telegraf-certs.files.crt.path}"
      url = "https://192.168.1.1:9990/telegraf.json"  # HTTPS required

      print("Waiting for /var/run/telegraf-www/telegraf.json to be bigger then 200 bytes")
      peer1.wait_until_succeeds(f"test \"$(stat -c%s /var/run/telegraf-www/telegraf.json)\" -ge 200", timeout=30)

      encoded_credentials = b64encode(credentials.encode("utf-8")).decode("utf-8")
      headers = {"Authorization": f"Basic {encoded_credentials}"}
      req = urllib.request.Request(url, headers=headers)  # noqa: S310

      # Trust the provided CA/server certificate
      context = ssl.create_default_context(cafile=cert_path)
      context.check_hostname = False
      context.verify_mode = ssl.CERT_REQUIRED

      found_system = False
      with urllib.request.urlopen(req, context=context, timeout=5) as response:
          for raw_line in response:
              line_str = raw_line.decode("utf-8").strip()
              if not line_str:
                  continue
              obj = json.loads(line_str)
              if obj.get("name") == "nixos_systems":
                  found_system = True
                  print("Found nixos_systems metric in json output")
                  break

      assert found_system, "nixos_systems metric not found in json output"

    '';
}
