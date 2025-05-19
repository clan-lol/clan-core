#!/usr/bin/env bash

set -euo pipefail

getIso() {
  # get the ssh public key of the current user
  ssh_key=$(ssh-add -L)
  # TODO: make this cross platform compatible by downloading a pre-built image
  #   and injecting the ssh private key into it
  nix build --impure --expr "
    let
      pkgs = import <nixpkgs> { crossSystem = \"x86_64-linux\"; };
    in
    (pkgs.nixos {
      services.openssh.enable = true;
      environment.systemPackages = [ pkgs.nixos-facter ];
      users.users.root.openssh.authorizedKeys.keys = [ \"$ssh_key\" ];
      users.users.root.password = \"root\";
    }).config.system.build.images.iso
  " -o iso
  iso=$(realpath iso)
  # iso=/nix/store/xgkfnwhi3c2lcpsvlpcw3dygwgifinbq-nixos-minimal-23.05pre483386.f212785e1ed-x86_64-linux.iso
  # nix-store -r "$iso"
}

id="${1:-1}"

CPUS="${CPUS:-2}"
MEMORY="${MEMORY:-4096}"
IMAGE_SIZE="${IMAGE_SIZE:-10G}"
SSH_PORT="${SSH_PORT:-2200${id}}"

img_file="nixos-nvme${id}.img"
getIso
truncate -s"$IMAGE_SIZE" "$img_file"
set -x
qemu-system-x86_64 \
  -m "${MEMORY}" \
  -boot n \
  -smp "${CPUS}" \
  -enable-kvm \
  -cpu max \
  -netdev "user,id=mynet0,hostfwd=tcp::${SSH_PORT}-:22" \
  -device virtio-net-pci,netdev=mynet0 \
  -drive "file=$img_file,if=none,id=nvme1,format=raw" \
  -device nvme,serial=deadbeef1,drive=nvme1 \
  -cdrom "$iso"/iso/*.iso
