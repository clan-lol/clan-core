{ ... }: {
  perSystem = { pkgs, lib, ... }: {
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
        nix develop "$ROOT#clan-cli" -c bash -c "TMPDIR=/tmp python -m pytest -m impure -s ./tests $@"
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
