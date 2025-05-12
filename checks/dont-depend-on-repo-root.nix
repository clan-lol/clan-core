{
  ...
}:
{
  perSystem =
    {
      system,
      pkgs,
      self',
      lib,
      ...
    }:
    let
      clanCore = self'.packages.clan-core-flake;
      clanCoreHash = lib.substring 0 12 (builtins.hashString "sha256" "${clanCore}");
      /*
        construct a flake for the test which contains a single check which depends
        on all checks of clan-core.
      */
      testFlakeFile = pkgs.writeText "flake.nix" ''
        {
          inputs.clan-core.url = path:///to/nowhere;
          outputs = {clan-core, ...}:
            let
              checks =
                builtins.removeAttrs
                  clan-core.checks.${system}
                  [
                    "dont-depend-on-repo-root"
                    "package-dont-depend-on-repo-root"
                    "package-clan-core-flake"
                  ];
              checksOutPaths = map (x: "''${x}") (builtins.attrValues checks);
            in
            {
              checks.${system}.check = builtins.derivation {
                name = "all-clan-core-checks";
                system = "${system}";
                builder = "/bin/sh";
                args = ["-c" '''
                  of outPath in ''${toString checksOutPaths}; do
                    echo "$outPath" >> $out
                  done
                '''];
              };
            };
        }
      '';
    in
    lib.optionalAttrs (system == "x86_64-linux") {
      packages.dont-depend-on-repo-root =
        pkgs.runCommand
          # append repo hash to this tests name to ensure it gets invalidated on each chain
          # This is needed because this test is an FOD (due to networking) and would get cached indefinitely.
          "check-dont-depend-on-repo-root-${clanCoreHash}"
          {
            buildInputs = [
              pkgs.nix
              pkgs.cacert
              pkgs.nix-diff
            ];
            outputHashAlgo = "sha256";
            outputHash = "sha256-47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=";
          }
          ''
            mkdir clanCore testFlake store
            clanCore=$(realpath clanCore)
            testFlake=$(realpath testFlake)

            # copy clan core flake and make writable
            cp -r ${clanCore}/* clanCore/
            chmod +w -R clanCore\

            # copy test flake and make writable
            cp ${testFlakeFile} testFlake/flake.nix
            chmod +w -R testFlake

            # enable flakes
            export NIX_CONFIG="experimental-features = nix-command flakes"

            # give nix a $HOME
            export HOME=$(realpath ./store)

            # override clan-core flake input to point to $clanCore\
            echo "locking clan-core to $clanCore"
            nix flake lock --override-input clan-core "path://$clanCore" "$testFlake" --store "$HOME"

            # evaluate all tests
            echo "evaluating all tests for clan core"
            nix eval "$testFlake"#checks.${system}.check.drvPath --store "$HOME" --raw > drvPath1 &

            # slightly modify clan core
            cp -r $clanCore clanCore2
            cp -r $testFlake testFlake2
            export clanCore2=$(realpath clanCore2)
            export testFlake2=$(realpath testFlake2)
            touch clanCore2/fly-fpv

            # re-evaluate all tests
            echo "locking clan-core to $clanCore2"
            nix flake lock --override-input clan-core "path://$clanCore2" "$testFlake2" --store "$HOME"
            echo "evaluating all tests for clan core with added file"
            nix eval "$testFlake2"#checks.${system}.check.drvPath --store "$HOME" --raw > drvPath2

            # wait for first nix eval to return as well
            while ! grep -q drv drvPath1; do sleep 1; done

            # raise error if outputs are different
            if [ "$(cat drvPath1)" != "$(cat drvPath2)" ]; then
              echo -e "\n\nERROR: Something in clan-core depends on the whole repo" > /dev/stderr
              echo -e "See details in the nix-diff below which shows the difference between two evaluations:"
              echo -e "  1. Evaluation of clan-core checks without any changes"
              echo -e "  1. Evaluation of clan-core checks after adding a file to the top-level of the repo"
              echo "nix-diff:"
              export NIX_REMOTE="$HOME"
              nix-diff $(cat drvPath1) $(cat drvPath2)
              exit 1
            fi
            touch $out
          '';
    };
}
