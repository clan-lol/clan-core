{ pkgs, ... }:

pkgs.systemd.overrideAttrs (oldAttrs: {
  patches = (oldAttrs.patches or [ ]) ++ [
    ./nspawn-keep-unit.patch
  ];
})
