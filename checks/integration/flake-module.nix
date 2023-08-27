{ self, ... }: {
  perSystem = { pkgs, lib, self', ... }:
    let
      integrationTests = {
        check-clan-create = pkgs.writeShellScriptBin "check-clan-init" ''
          #!${pkgs.bash}/bin/bash
          set -euo pipefail
          export TMPDIR=$(${pkgs.coreutils}/bin/mktemp -d)
          trap "${pkgs.coreutils}/bin/chmod -R +w '$TMPDIR'; ${pkgs.coreutils}/bin/rm -rf '$TMPDIR'" EXIT
          export PATH="${lib.makeBinPath [
            pkgs.git
            pkgs.gnugrep
            pkgs.nix
            self'.packages.clan-cli
          ]}"

          cd $TMPDIR

          echo initialize new clan
          nix flake init -t ${self}#new-clan

          echo ensure flake outputs can be listed
          nix flake show

          echo create a machine
          clan machines create machine1

          echo check machine1 exists
          clan machines list | grep -q machine1

          echo check machine1 appears in flake output
          nix flake show | grep -q machine1
        '';
      };
    in
    {
      packages =
        integrationTests // {
          # a script that executes all other checks
          checks-impure = pkgs.writeShellScriptBin "checks-impure" ''
            #!${pkgs.bash}/bin/bash
            set -euo pipefail
            ${lib.concatMapStringsSep "\n" (name: ''
              echo -e "\n\nrunning check ${name}\n"
              ${integrationTests.${name}}/bin/*
            '') (lib.attrNames integrationTests)}
          '';
        };
    };
}
