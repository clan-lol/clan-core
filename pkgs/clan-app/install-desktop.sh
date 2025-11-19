#!/usr/bin/env bash

ALREADY_INSTALLED=$(nix profile list --json |  jq 'has("elements") and (.elements | has("clan-app"))')

if [ "$ALREADY_INSTALLED" = "true" ]; then
  echo "Upgrading installed clan-app"
  nix profile upgrade clan-app
else
  nix profile add .#clan-app
fi

# Check OS type
if [[ "$OSTYPE" == "linux-gnu"* ]]; then

  if ! command -v xdg-mime &> /dev/null; then
    echo "Warning: 'xdg-mime' is not available. The desktop file cannot be installed."
  fi

  # install desktop file on Linux
  set -eou pipefail
  DESKTOP_FILE_NAME=org.clan.app.desktop
  xdg-mime default "$DESKTOP_FILE_NAME" x-scheme-handler/clan

elif [[ "$OSTYPE" == "darwin"* ]]; then
  echo "macOS detected."
  mkdir -p ~/Applications
  ln -sf ~/.nix-profile/Applications/Clan\ App.app ~/Applications
  /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f ~/Applications/Clan\ App.app
else
  echo "Unsupported OS: $OSTYPE"
fi
