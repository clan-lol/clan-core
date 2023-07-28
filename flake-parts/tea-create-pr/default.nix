{
  perSystem =
    { config
    , pkgs
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
