{ self, ... }: {
  perSystem = { pkgs, lib, self', ... }:
    let
      impureChecks = {
        check-clan-template = pkgs.writeShellScriptBin "check-clan-template" ''
          #!${pkgs.bash}/bin/bash
          set -euo pipefail

          export TMPDIR=$(${pkgs.coreutils}/bin/mktemp -d)
          trap "${pkgs.coreutils}/bin/chmod -R +w '$TMPDIR'; ${pkgs.coreutils}/bin/rm -rf '$TMPDIR'" EXIT

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

          cd $TMPDIR

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
              ${impureChecks.${name}}/bin/*
            '') (lib.attrNames impureChecks)}
          '';
        };
    };
}
