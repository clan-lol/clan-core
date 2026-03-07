{
  writeShellScriptBin,
  coreutils,
  openssh,
  rsync,
  git,
  nix,
  lib,
  docs,
}:

writeShellScriptBin "deploy-docs-v2" ''
  set -eu -o pipefail
  export PATH="${
    lib.makeBinPath [
      coreutils
      openssh
      rsync
      git
      nix
    ]
  }"

  usage() {
    echo "Usage: deploy-docs-v2 [--current] [<branch>...]"
    echo ""
    echo "Deploy versioned docs to clan.lol."
    echo ""
    echo "Options:"
    echo "  --current   Deploy the current checkout using pre-built docs."
    echo "              The version name is read from the VERSION file."
    echo ""
    echo "Arguments:"
    echo "  <branch>    One or more branch names to clone, build, and deploy."
    echo "              The version name is read from each branch's VERSION file."
    echo ""
    echo "Examples:"
    echo "  deploy-docs-v2 --current              Deploy only the current checkout"
    echo "  deploy-docs-v2 25.11                   Deploy only the 25.11 branch"
    echo "  deploy-docs-v2 --current 25.11         Deploy current checkout + 25.11 branch"
    exit 1
  }

  if [ $# -eq 0 ]; then
    usage
  fi

  REPO_ROOT="$(git rev-parse --show-toplevel)"
  cd "$REPO_ROOT"

  #########################################
  #                                       #
  # DO NOT PRINT THE SSH KEY TO THE LOGS  #
  #                                       #
  #########################################
  tmpdir=$(mktemp -d)

  if [ -n "''${SSH_HOMEPAGE_KEY-}" ]; then
    ( umask 0177 && echo "$SSH_HOMEPAGE_KEY" > "$tmpdir/ssh_key" )
    sshExtraArgs="-i $tmpdir/ssh_key"
  else
    sshExtraArgs=
  fi
  ###########################
  #                         #
  #    END OF DANGER ZONE   #
  #                         #
  ###########################

  trap 'rm -rf "$tmpdir"' EXIT

  deploy_version() {
    local version_name="$1"
    local docs_path="$2"

    echo "Deploying docs for version: $version_name"
    set -x
    rsync \
      --checksum \
      --delete \
      -e "ssh -o StrictHostKeyChecking=no $sshExtraArgs" \
      -a "$docs_path/" \
      --mkpath \
      "www@clan.lol:/var/www/versioned-docs/$version_name"
    set +x
  }

  # Parse arguments
  deploy_current=false
  branches=()

  for arg in "$@"; do
    case "$arg" in
      --current)
        deploy_current=true
        ;;
      --help|-h)
        usage
        ;;
      -*)
        echo "ERROR: Unknown option: $arg" >&2
        usage
        ;;
      *)
        if [[ "$arg" == */* ]] || [[ "$arg" == .* ]]; then
          echo "ERROR: Invalid branch name: $arg" >&2
          exit 1
        fi
        branches+=("$arg")
        ;;
    esac
  done

  # Deploy current checkout
  if [ "$deploy_current" = true ]; then
    VERSION_NAME=$(cat "$REPO_ROOT/VERSION")
    echo "========================================="
    echo "Deploying current checkout (version: $VERSION_NAME)"
    echo "========================================="
    deploy_version "$VERSION_NAME" "${docs}"
  fi

  # Deploy branches
  if [ ''${#branches[@]} -gt 0 ]; then
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "https://git.clan.lol/clan/clan-core.git")

    clone_base="$tmpdir/clones"
    mkdir -p "$clone_base"

    for branch in "''${branches[@]}"; do
      echo "========================================="
      echo "Building docs for branch: $branch"
      echo "========================================="

      clone_dir="$clone_base/$branch"

      git clone --depth 1 --branch "$branch" "$REMOTE_URL" "$clone_dir"

      VERSION_NAME=$(cat "$clone_dir/VERSION")
      echo "Version from branch $branch: $VERSION_NAME"

      docs_result=$(nix build "$clone_dir#clan-site" --no-link --print-out-paths)
      echo "Build output: $docs_result"

      deploy_version "$VERSION_NAME" "$docs_result"

      rm -rf "$clone_dir"
    done
  fi

  echo "Done."
''
