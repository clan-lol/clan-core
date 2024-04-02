#!/usr/bin/env bash

nix run --inputs-from .# nixpkgs#flatpak-builder -- --user --install --force-clean build-dir org.clan.cli.Devel.yml --require-changes
