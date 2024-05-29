#! /bin/sh

# create temp dir and ensure it is always cleaned
trap 'clean_temp_dir' EXIT
temp_dir=$(mktemp -d)

clean_temp_dir() {
  rm -rf "$temp_dir"
}

is_nix_installed() {
  if [ -n "$(command -v nix)" ]; then
    return 0
  else
    return 1
  fi
}

install_nix() {
  curl --proto '=https' --tlsv1.2 -sSf -L \
      https://install.determinate.systems/nix \
    > "$temp_dir"/install_nix.sh
  NIX_INSTALLER_DIAGNOSTIC_ENDPOINT="" sh "$temp_dir"/install_nix.sh install
}

ask_then_install_nix() {
  echo "Clan requires Nix to be installed. Would you like to install it now? (y/n)"
  read -r response
  if [ "$response" = "y" ]; then
    install_nix
  else
    echo "Clan cannot run without Nix. Exiting."
    exit 1
  fi
}

ensure_nix_installed() {
  if ! is_nix_installed; then
    ask_then_install_nix
  fi
}

start_clan_gui() {
  exec nix run \
    https://git.clan.lol/clan/clan-core/archive/main.tar.gz#clan-vm-manager \
    --no-accept-flake-config \
    --extra-experimental-features flakes nix-command -- "$@"
}

main() {
  ensure_nix_installed
  start_clan_gui "$@"
}

main "$@"
