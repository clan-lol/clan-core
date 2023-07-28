{
  perSystem =
    { pkgs
    , ...
    }:
    let
      name = builtins.baseNameOf ./.;
      script = pkgs.writeShellApplication {
        inherit name;
        runtimeInputs = [
          pkgs.bash
          pkgs.coreutils
          pkgs.git
          pkgs.tea
          pkgs.openssh
        ];
        text = ''
          export EDITOR=${pkgs.vim}/bin/vim
          bash ${./script.sh} "$@"
        '';
      };
    in
    {
      packages.${name} = script;
    };
}
