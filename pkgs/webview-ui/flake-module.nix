{ ... }:
{
  perSystem =
    { pkgs, config, ... }:
    {
      packages.webview-ui = pkgs.buildNpmPackage {
        pname = "clan-webview-ui";
        version = "0.0.1";

        src = ./app;

        # npmDepsHash = "sha256-bRD2vzijhdOOvcEi6XaG/neSqhkVQMqIX/8bxvRQkTc=";
        npmDeps = pkgs.fetchNpmDeps {
          src = ./app;
          hash = "sha256-bRD2vzijhdOOvcEi6XaG/neSqhkVQMqIX/8bxvRQkTc=";
        };
        # The prepack script runs the build script, which we'd rather do in the build phase.
        npmPackFlags = [ "--ignore-scripts" ];

        preBuild = ''
          mkdir -p api
          cat ${config.packages.clan-ts-api} > api/index.ts
        '';
      };
      devShells.webview-ui = pkgs.mkShell {
        inputsFrom = [ config.packages.webview-ui ];
        shellHook = ''
          mkdir -p ./app/api
          cat ${config.packages.clan-ts-api} > ./app/api/index.ts
        '';
      };
    };
}
