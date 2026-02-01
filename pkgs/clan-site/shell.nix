{
  mkShellNoCC,
  clan-site,
  writeShellApplication,
  util-linux,
}:
mkShellNoCC {
  inputsFrom = [
    clan-site
  ];
  packages = [
    (writeShellApplication {
      name = "clan-site";
      runtimeInputs = [
        util-linux
      ];
      text = ''
        arg=$(getopt -n clan-site -o 'b' -- "$@")
        eval set -- "$arg"
        unset arg
        browser=
        while true; do
          case $1 in
            -b)
              browser=1
              shift
            ;;
            --)
              shift
              break
            ;;
            *)
              echo >&2 "Unhandled flag $1"
              exit 1
          esac
        done
        case ''${1-} in
        "" | dev)
          if [[ -n $browser ]]; then
            set -- --open
          fi
          if [[ ! -e node_modules ]]; then
            npm install
          fi
          npm run dev -- "$@"
          ;;
        build)
          if [[ ! -e node_modules ]]; then
            npm install
          fi
          npm run build
          if [[ -n $browser ]]; then
            npm run preview -- --open
          fi
        esac
      '';
    })
  ];
  shellHook = clan-site.preBuild;
}
