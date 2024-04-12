{ docs, pkgs, ... }: pkgs.mkShell { inputsFrom = [ docs ]; }
