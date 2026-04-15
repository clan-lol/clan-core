## Usage

```nix
inventory.instances = {
  installer = {
    module = {
      name = "installer";
      input = "clan-core";
    };
    roles.iso.machines."jon" = { };
  };
};
```

This turns the machine `jon` into an installer image. Build the ISO with
`clan machines build-machine jon --format iso`.

## Overview

The installer service configures a machine so it can be used as an installation ISO for physical installs. It imports the
nixpkgs installation-device profile, needed for nixos-anywhere. Pins the latest ZFS-compatible
kernel, configures kmscon with root autologin via agetty, and enables
both serial and VGA consoles with VGA as the primary /dev/console.

The image includes `nixos-install-tools`, `disko`, `nixos-facter`, and `rsync`,
which covers the tools needed by `nixos-anywhere` and Clan's hardware-config workflow.

## Roles

### iso

The only role. It imports the nixpkgs `installation-device.nix` profile, pins
the latest ZFS-compatible kernel, enables kmscon as the console terminal, and
forces getty autologin to `root`. Serial and VGA consoles are both enabled,
with VGA as the primary `/dev/console`.
