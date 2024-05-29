{ ... }:
{
  perSystem =
    { pkgs, config, ... }:
    {
      packages.webview-ui = pkgs.buildNpmPackage {
        pname = "clan-webview-ui";
        version = "0.0.1";

        src = ./app;

        npmDeps = pkgs.fetchNpmDeps {
          src = ./app;
          hash = "sha256-4ZurUbY5uMq7KeKnYRJ1+/Go9WoURFOpeZgLE0S6WZI=";
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
