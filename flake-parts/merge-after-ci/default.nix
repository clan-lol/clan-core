{
  perSystem =
    { config
    , pkgs
    , self'
    , ...
    }:
    let
      name = builtins.baseNameOf ./.;
      script = config.writers.writePureShellScriptBin
        name
        [
          pkgs.bash
          pkgs.coreutils
          pkgs.git
          pkgs.tea
          pkgs.openssh
          self'.packages.tea-create-pr
        ]
        ''
          export EDITOR=${pkgs.vim}/bin/vim
          bash ${./script.sh} "$@"
        '';
    in
    {
      packages.${name} = script;
    };
}
