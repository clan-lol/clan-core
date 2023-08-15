#!/usr/bin/env bash
set -euo pipefail

expr='let pkgs = import <nixpkgs> {}; lib = pkgs.lib; in (pkgs.nixosOptionsDoc {options = (lib.evalModules {modules=[./example-interface.nix];}).options;}).optionsJSON.options'

jq < "$(nix eval --impure --raw --expr "$expr")" > options.json
