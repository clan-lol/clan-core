{ self, ... }: {
  perSystem = { pkgs, lib, self', ... }: {
    packages = rec {
      # a script that executes all other checks
      impure-checks = pkgs.writeShellScriptBin "impure-checks" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        export PATH="${lib.makeBinPath [
          pkgs.gitMinimal
          pkgs.nix
          pkgs.rsync # needed to have rsync installed on the dummy ssh server
        ]}"
        ROOT=$(git rev-parse --show-toplevel)
        cd "$ROOT/pkgs/clan-cli"
        ${self'.packages.vm-persistence}/bin/vm-persistence
        nix develop "$ROOT#clan-cli" -c bash -c "TMPDIR=/tmp python -m pytest -m impure ./tests $@"
      '';

      # TODO: port this to python and make it pure
      vm-persistence =
        let
          machineConfigFile = builtins.toFile "vm-config.json" (builtins.toJSON {
            clanCore.state.my-state = {
              folders = [ "/var/my-state" ];
            };
            # powers off the machine after the state is created
            systemd.services.poweroff = {
              description = "Poweroff the machine";
              wantedBy = [ "multi-user.target" ];
              after = [ "my-state.service" ];
              script = ''
                echo "Powering off the machine"
                poweroff
              '';
            };
            # creates a file in the state folder
            systemd.services.my-state = {
              description = "Create a file in the state folder";
              wantedBy = [ "multi-user.target" ];
              script = ''
                echo "Creating a file in the state folder"
                echo "dream2nix" > /var/my-state/test
              '';
              serviceConfig.Type = "oneshot";
            };
            clan.virtualisation.graphics = false;
            users.users.root.password = "root";
          });
        in
        pkgs.writeShellScriptBin "vm-persistence" ''
          #!${pkgs.bash}/bin/bash
          set -euo pipefail

          export PATH="${lib.makeBinPath [
            pkgs.coreutils
            pkgs.gitMinimal
            pkgs.jq
            pkgs.nix
            pkgs.gnused
            self'.packages.clan-cli
          ]}"

          clanName=_test_vm_persistence
          testFile=~/".config/clan/vmstate/$clanName/my-machine/var/my-state/test"

          export TMPDIR=$(${pkgs.coreutils}/bin/mktemp -d)
          trap "${pkgs.coreutils}/bin/chmod -R +w '$TMPDIR'; ${pkgs.coreutils}/bin/rm -rf '$TMPDIR'" EXIT

          # clean up vmstate after test
          trap "${pkgs.coreutils}/bin/rm -rf ~/.config/clan/vmstate/$clanName" EXIT

          cd $TMPDIR
          mkdir ./clan
          cd ./clan
          nix flake init -t ${self}#templates.new-clan
          nix flake lock --override-input clan-core ${self}
          sed -i "s/__CHANGE_ME__/$clanName/g" flake.nix
          clan machines create my-machine

          cat ${machineConfigFile} | jq > ./machines/my-machine/settings.json

          # clear state from previous runs
          rm -rf "$testFile"

          # machine will automatically shutdown due to the shutdown service above
          clan vms run my-machine

          set -x
          if ! test -e "$testFile"; then
            echo "failed: file "$testFile" was not created"
            exit 1
          fi
        '';

      runMockApi = pkgs.writeShellScriptBin "run-mock-api" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        export PATH="${lib.makeBinPath [
          pkgs.gitMinimal
          pkgs.nix
          pkgs.rsync # needed to have rsync installed on the dummy ssh server
          pkgs.coreutils
          pkgs.procps
        ]}"
        ROOT=$(git rev-parse --show-toplevel)
        cd "$ROOT/pkgs/clan-cli"
        nix develop "$ROOT#clan-cli" -c bash -c 'TMPDIR=/tmp clan webui --no-open --port 5757'
      '';


      runSchemaTests = pkgs.writeShellScriptBin "runSchemaTests" ''
        #!${pkgs.bash}/bin/bash
        set -euo pipefail

        ${runMockApi}/bin/run-mock-api &
        MOCK_API_PID=$!
        echo "Started mock api with pid $MOCK_API_PID"
        function cleanup {
            echo "Stopping server..."
            pkill -9 -f "python -m clan webui --no-open --port 5757"
        }
        trap cleanup EXIT

        export PATH="${lib.makeBinPath [
          pkgs.gitMinimal
          pkgs.nix
          pkgs.rsync # needed to have rsync installed on the dummy ssh server
          pkgs.procps
          pkgs.coreutils
        ]}"

        sleep 3

        ROOT=$(git rev-parse --show-toplevel)
        cd "$ROOT/pkgs/clan-cli"
        nix develop "$ROOT#clan-cli" -c bash -c 'TMPDIR=/tmp st auth login RHtr8nLtz77tqRP8yUGyf-Flv_9SLI'
        nix develop "$ROOT#clan-cli" -c bash -c 'TMPDIR=/tmp st run http://localhost:5757/openapi.json --experimental=openapi-3.1 --report --workers 8 --max-response-time=50 --request-timeout=1000 -M GET'
      '';
    };
  };
}
