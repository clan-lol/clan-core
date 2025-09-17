{ packages, pkgs, ... }:
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
            basic_password = lib.mkForce "";
            basic_username = lib.mkForce "";
          };
        };
      };
  };

  extraPythonPackages = _p: [
    (pkgs.python3.pkgs.toPythonModule packages.${pkgs.system}.clan-cli)
  ];

  testScript =
    { ... }:
    ''
      import time
      import os
      import sys
      import subprocess 
      import json
      import shlex
      import urllib.request
      from base64 import b64encode
      start_all()

      peer1.wait_for_unit("network-online.target")
      peer1.wait_for_unit("telegraf.service")
      peer1.wait_for_unit("telegraf-json.service")
      peer1.succeed("curl http://localhost:9990")
      peer1.succeed("curl http://localhost:9273/metrics")

      # Fetch the basic auth password from the secret file
      password = peer1.succeed("cat /var/run/secrets/vars/telegraf/password")
      url = f"http://192.168.1.1:9990"
      credentials = f"prometheus:{password}"
      print("Using credentials:", credentials)
      time.sleep(10)  # wait a bit for telegraf to collect some data

      # Fetch the json output from miniserve
      encoded_credentials = b64encode(credentials.encode("utf-8")).decode("utf-8")
      headers = {"Authorization": f"Basic {encoded_credentials}"}
      req = urllib.request.Request(url, headers=headers)  # noqa: S310
      response = urllib.request.urlopen(req)

      # Look for the nixos_systems metric in the json output
      found_system = False
      for line in response:
        line_str = line.decode("utf-8").strip()
        line = json.loads(line_str)
        if line["name"] == "nixos_systems":
            found_system = True
            print("Found nixos_systems metric in json output")
            break
        print(line)
      assert found_system, "nixos_systems metric not found in json output"

      # TODO: I would like to test the python code here but it's not working yet
      # Missing: I need a way to get the encrypted var from the clan
      #from clan_lib.metrics.version import get_nixos_systems
      #from clan_lib.machines.machines import Machine as ClanMachine
      #from clan_lib.flake import Flake
      #from clan_lib.ssh.remote import Remote
      #target_host = Remote("peer1", "192.168.1.1")
      #machine = ClanMachine("peer1", flake=Flake("${./.}"))
      # data = get_nixos_systems(mymachine, target_host)
      # assert data["current_system"] is not None

    '';
}
