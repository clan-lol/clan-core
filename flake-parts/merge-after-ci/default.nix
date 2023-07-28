{
  perSystem =
    { pkgs
    , self'
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
          self'.packages.tea-create-pr
        ];
        text = ''
          bash ${./script.sh} "$@"
        '';
      };
    in
    {
      packages.${name} = script;
    };
}
