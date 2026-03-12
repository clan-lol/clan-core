# Unit-test for the 'generators-to-sops.nix' bridge
# These tests are essential
# tests/unit/vars/generator-to-sops.nix
{
  lib ? import <nixpkgs/lib>,
}:
let
  # Import the module under test with mocked pathExists
  mkMapGeneratorsToSopsSecrets =
    pathExists:
    import ./generators-to-sops.nix {
      inherit lib pathExists;
      # Create a fake nix-store path
      path = p: p;
    };

  # Helper to create test generator structure
  mkGenerator =
    {
      name,
      share ? false,
      files ? { },
    }:
    {
      ${name} = {
        inherit share files;
      };
    };

  # Helper to create file definition
  mkFile =
    {
      secret ? true,
      deploy ? true,
      neededFor ? "services",
      owner ? "root",
      group ? "root",
      mode ? "0400",
      restartUnits ? [ ],
    }:
    {
      inherit
        secret
        deploy
        neededFor
        owner
        group
        mode
        restartUnits
        ;
    };

in
{
  testSharedSecretPath = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".sopsFile.path;
    expected = "/test/vars/shared/gen1/secret1/secret";
  };

  testPerMachineSecretPath = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = false;
          files.secret1 = mkFile { };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".sopsFile.path;
    expected = "/test/vars/per-machine/machine1/gen1/secret1/secret";
  };

  testSopsFileNameConstruction = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".sopsFile.name;
    expected = "gen1_secret1";
  };

  # Secret Filtering Tests (relevantFiles)
  testFiltersSecretTrue = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            included = mkFile { secret = true; };
            excluded = mkFile { secret = false; };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.attrNames result;
    expected = [ "vars/gen1/included" ];
  };

  testFiltersDeployTrue = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            included = mkFile { deploy = true; };
            excluded = mkFile { deploy = false; };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.attrNames result;
    expected = [ "vars/gen1/included" ];
  };

  testFiltersNeededForUsers = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            users = mkFile { neededFor = "users"; };
            activation = mkFile { neededFor = "activation"; };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.attrNames result;
    expected = [ "vars/gen1/users" ];
  };

  testFiltersNeededForServices = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            services = mkFile { neededFor = "services"; };
            activation = mkFile { neededFor = "activation"; };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.attrNames result;
    expected = [ "vars/gen1/services" ];
  };

  testFiltersCombinedConditions = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            valid = mkFile {
              secret = true;
              deploy = true;
              neededFor = "services";
            };
            noSecret = mkFile {
              secret = false;
              deploy = true;
              neededFor = "services";
            };
            noDeploy = mkFile {
              secret = true;
              deploy = false;
              neededFor = "services";
            };
            wrongNeededFor = mkFile {
              secret = true;
              deploy = true;
              neededFor = "activation";
            };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.attrNames result;
    expected = [ "vars/gen1/valid" ];
  };

  # Secret Definition Extraction Tests
  testExtractsMultipleGenerators = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = {
          gen1 = {
            share = true;
            files.secret1 = mkFile { };
          };
          gen2 = {
            share = false;
            files.secret2 = mkFile { };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.sort builtins.lessThan (builtins.attrNames result);
    expected = [
      "vars/gen1/secret1"
      "vars/gen2/secret2"
    ];
  };

  testExtractsMultipleFilesPerGenerator = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            secret1 = mkFile { };
            secret2 = mkFile { };
            secret3 = mkFile { };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.length (builtins.attrNames result);
    expected = 3;
  };

  testNeededForUsersCorrectlySet = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            userSecret = mkFile { neededFor = "users"; };
            serviceSecret = mkFile { neededFor = "services"; };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      {
        userSecret = result."vars/gen1/userSecret".neededForUsers;
        serviceSecret = result."vars/gen1/serviceSecret".neededForUsers;
      };
    expected = {
      userSecret = true;
      serviceSecret = false;
    };
  };

  # Class-Specific Behavior Tests
  testNixosIncludesRestartUnits = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile {
            restartUnits = [ "nginx.service" ];
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".restartUnits or null;
    expected = [ "nginx.service" ];
  };

  testDarwinExcludesRestartUnits = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile {
            restartUnits = [ "nginx.service" ];
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "darwin";
          inherit generators;
        };
      in
      builtins.hasAttr "restartUnits" result."vars/gen1/secret1";
    expected = false;
  };

  testClassAssertionNixos = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { };
        };
      in
      mapFn {
        machineName = "machine1";
        directory = "/test";
        class = "nixos";
        inherit generators;
      };
    expected = {
      "vars/gen1/secret1" = {
        owner = "root";
        group = "root";
        mode = "0400";
        neededForUsers = false;
        restartUnits = [ ];
        sopsFile = {
          name = "gen1_secret1";
          path = "/test/vars/shared/gen1/secret1/secret";
        };
        format = "binary";
      };

    };
  };

  testClassAssertionDarwin = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { };
        };
      in
      mapFn {
        machineName = "machine1";
        directory = "/test";
        class = "darwin";
        inherit generators;
      };
    expected = {
      "vars/gen1/secret1" = {
        owner = "root";
        group = "root";
        mode = "0400";
        neededForUsers = false;
        sopsFile = {
          name = "gen1_secret1";
          path = "/test/vars/shared/gen1/secret1/secret";
        };
        format = "binary";
      };

    };
  };

  testClassAssertionInvalid = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { };
        };
      in
      mapFn {
        machineName = "machine1";
        directory = "/test";
        class = "invalid"; # nixos | darwin
        inherit generators;
      };
    expectedError.type = "ThrownError";
  };

  # Attribute Preservation Tests
  testPreservesOwner = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { owner = "nginx"; };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".owner;
    expected = "nginx";
  };

  testPreservesGroup = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { group = "nginx"; };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".group;
    expected = "nginx";
  };

  testPreservesMode = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { mode = "0440"; };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".mode;
    expected = "0440";
  };

  testPreservesRestartUnits = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile {
            restartUnits = [
              "nginx.service"
              "php-fpm.service"
            ];
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".restartUnits;
    expected = [
      "nginx.service"
      "php-fpm.service"
    ];
  };

  # Output Format Tests
  testOutputAttributeNameFormat = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "myGenerator";
          share = true;
          files.mySecret = mkFile { };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.attrNames result;
    expected = [ "vars/myGenerator/mySecret" ];
  };

  testOutputFormatIsBinary = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".format;
    expected = "binary";
  };

  testOutputUsesBuiltinsPath = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
        sopsFile = result."vars/gen1/secret1".sopsFile;
      in
      builtins.isAttrs sopsFile && builtins.hasAttr "name" sopsFile && builtins.hasAttr "path" sopsFile;
    expected = true;
  };

  # Path Existence Filtering Tests
  testFiltersByPathExists = {
    expr =
      let
        # Mock pathExists to only return true for specific paths
        pathExists = path: path == "/test/vars/shared/gen1/exists/secret";

        mapFn = mkMapGeneratorsToSopsSecrets pathExists;
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            exists = mkFile { };
            notExists = mkFile { };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      builtins.attrNames result;
    expected = [ "vars/gen1/exists" ];
  };

  testAllSecretsFilteredWhenNoneExist = {
    expr =
      let
        pathExists = _: false;
        mapFn = mkMapGeneratorsToSopsSecrets pathExists;
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            secret1 = mkFile { };
            secret2 = mkFile { };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result;
    expected = { };
  };

  testPathExistsCalledWithCorrectPaths = {
    expr =
      let
        pathExists = _path: true;

        mapFn = mkMapGeneratorsToSopsSecrets pathExists;
        generators = {
          gen1 = {
            share = true;
            files.secret1 = mkFile { };
          };
          gen2 = {
            share = false;
            files.secret2 = mkFile { };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      # We can't capture traced values in tests, but we can verify
      # the function runs without error and produces expected output
      builtins.length (builtins.attrNames result);
    expected = 2;
  };

  # Edge Cases
  testEmptyGenerators = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          generators = { };
        };
      in
      result;
    expected = { };
  };

  testGeneratorWithNoFiles = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          generators = {
            gen1 = {
              share = true;
              files = { };
            };
          };
        };
      in
      result;
    expected = { };
  };

  testGeneratorWithNoRelevantFiles = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files = {
            notDeployed = mkFile { deploy = false; };
            notSecret = mkFile { secret = false; };
            activation = mkFile { neededFor = "activation"; };
          };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result;
    expected = { };
  };

  testEmptyRestartUnits = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen1";
          share = true;
          files.secret1 = mkFile { restartUnits = [ ]; };
        };
        result = mapFn {
          machineName = "machine1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      result."vars/gen1/secret1".restartUnits;
    expected = [ ];
  };

  testSpecialCharactersInNames = {
    expr =
      let
        mapFn = mkMapGeneratorsToSopsSecrets (_: true);
        generators = mkGenerator {
          name = "gen-with-dash";
          share = true;
          files."secret_with_underscore" = mkFile { };
        };
        result = mapFn {
          machineName = "machine-1";
          directory = "/test";
          class = "nixos";
          inherit generators;
        };
      in
      {
        hasSecret = builtins.hasAttr "vars/gen-with-dash/secret_with_underscore" result;
        pathCorrect =
          result."vars/gen-with-dash/secret_with_underscore".sopsFile.path
          == "/test/vars/shared/gen-with-dash/secret_with_underscore/secret";
      };
    expected = {
      hasSecret = true;
      pathCorrect = true;
    };
  };

  # Integration-style Tests
  testComplexScenario = {
    expr =
      let
        pathExists =
          path:
          builtins.elem path [
            "/clan/vars/shared/passwords/root/secret"
            "/clan/vars/per-machine/server1/certificates/ssl/secret"
          ];

        mapFn = mkMapGeneratorsToSopsSecrets pathExists;
        generators = {
          passwords = {
            share = true;
            files = {
              root = mkFile {
                owner = "root";
                group = "root";
                mode = "0400";
                neededFor = "users";
              };
              postgres = mkFile {
                owner = "postgres";
                group = "postgres";
                mode = "0400";
                neededFor = "services";
              };
            };
          };
          certificates = {
            share = false;
            files = {
              ssl = mkFile {
                owner = "nginx";
                group = "nginx";
                mode = "0440";
                restartUnits = [ "nginx.service" ];
                neededFor = "services";
              };
            };
          };
        };
        result = mapFn {
          machineName = "server1";
          directory = "/clan";
          class = "nixos";
          inherit generators;
        };
      in
      {
        secretCount = builtins.length (builtins.attrNames result);
        hasRootPassword = builtins.hasAttr "vars/passwords/root" result;
        hasSSLCert = builtins.hasAttr "vars/certificates/ssl" result;
        noPostgresPassword = !builtins.hasAttr "vars/passwords/postgres" result;
        rootIsForUsers = result."vars/passwords/root".neededForUsers;
        sslOwner = result."vars/certificates/ssl".owner;
        sslRestarts = result."vars/certificates/ssl".restartUnits;
      };
    expected = {
      secretCount = 2;
      hasRootPassword = true;
      hasSSLCert = true;
      noPostgresPassword = true;
      rootIsForUsers = true;
      sslOwner = "nginx";
      sslRestarts = [ "nginx.service" ];
    };
  };
}
