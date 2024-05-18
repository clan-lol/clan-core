{ inputs, ... }:
{
  perSystem =
    {
      system,
      pkgs,
      config,
      ...
    }:
    let
      node_modules-dev = config.packages.webview-ui.prepared-dev;
    in
    {
      packages.webview-ui = inputs.dream2nix.lib.evalModules {
        packageSets.nixpkgs = inputs.dream2nix.inputs.nixpkgs.legacyPackages.${system};
        modules = [ ./default.nix ];
      };
      devShells.webview-ui = pkgs.mkShell {
        inputsFrom = [ config.packages.webview-ui.out ];
        shellHook = ''
          ID=${node_modules-dev}
          currID=$(cat .dream2nix/.node_modules_id 2> /dev/null)

          mkdir -p .dream2nix
          if [[ "$ID" != "$currID" || ! -d "app/node_modules"  ]];
          then
            ${pkgs.rsync}/bin/rsync -a --chmod=ug+w  --delete ${node_modules-dev}/node_modules/ ./app/node_modules/
            echo -n $ID > .dream2nix/.node_modules_id
            echo "Ok: node_modules updated"
          fi
        '';
      };
    };
}
