{ self, ... }: {
  perSystem = { pkgs, lib, ... }:
    let
      impureChecks = {
        check-clan-template = pkgs.writeShellScriptBin "check-clan-template" ''
          #!${pkgs.bash}/bin/bash
          set -euo pipefail
          export TMPDIR=$(${pkgs.coreutils}/bin/mktemp -d)
          trap "${pkgs.coreutils}/bin/chmod -R +w '$TMPDIR'; ${pkgs.coreutils}/bin/rm -rf '$TMPDIR'" EXIT
          export PATH="${lib.makeBinPath [
            pkgs.gitMinimal
            pkgs.openssh
            pkgs.nix
          ]}"

          cd $TMPDIR

          echo initialize new clan
          nix flake init -t ${self}#new-clan

          echo ensure flake outputs can be listed
          nix flake show
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
