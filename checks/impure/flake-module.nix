{ self, ... }: {
  perSystem = { pkgs, lib, self', ... }:
    let
      impureChecks = {
        clan-pytest-impure = pkgs.writeShellScriptBin "clan-pytest-impure" ''
          #!${pkgs.bash}/bin/bash
          set -euo pipefail

          export PATH="${lib.makeBinPath [
            pkgs.gitMinimal
            pkgs.nix
          ]}"
          ROOT=$(git rev-parse --show-toplevel)
          cd "$ROOT/pkgs/clan-cli"
          nix develop "$ROOT#clan-cli" -c bash -c 'TMPDIR=/tmp python -m pytest -m impure -s ./tests'
        '';
        check-clan-template = pkgs.writeShellScriptBin "check-clan-template" ''
          #!${pkgs.bash}/bin/bash
          set -euox pipefail

          export CLANTMP=$(${pkgs.coreutils}/bin/mktemp -d)
          trap "${pkgs.coreutils}/bin/chmod -R +w '$CLANTMP'; ${pkgs.coreutils}/bin/rm -rf '$CLANTMP'" EXIT

          export PATH="${lib.makeBinPath [
            pkgs.coreutils
            pkgs.curl
            pkgs.gitMinimal
            pkgs.gnugrep
            pkgs.jq
            pkgs.openssh
            pkgs.nix
            self'.packages.clan-cli
          ]}"

          cd $CLANTMP

          echo initialize new clan
          nix flake init -t ${self}#new-clan

          echo override clan input to the current version
          nix flake lock --override-input clan-core ${self}
          nix flake lock --override-input nixpkgs ${self.inputs.nixpkgs}

          echo ensure flake outputs can be listed
          nix flake show

          echo create a machine
          clan machines create machine1

          echo check machine1 exists
          clan machines list | grep -q machine1

          echo check machine1 appears in nixosConfigurations
          nix flake show --json | jq '.nixosConfigurations' | grep -q machine1

          echo check machine1 jsonschema can be evaluated
          nix eval .#nixosConfigurations.machine1.config.clanSchema
        '';
      };
    in
    {
      packages =
        impureChecks // {
          # a script that executes all other checks
          impure-checks = pkgs.writeShellScriptBin "impure-checks" ''
            #!${pkgs.bash}/bin/bash
            set -euo pipefail
            ${lib.concatMapStringsSep "\n" (name: ''
              echo -e "\n\nrunning check ${name}\n"
              ${impureChecks.${name}}/bin/* "$@"
            '') (lib.attrNames impureChecks)}
          '';
        };
    };
}
