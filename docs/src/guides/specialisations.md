# NixOS specialisations

Specialisations let you define named variations of your system configuration. Each specialisation produces a separate system closure that you can switch to at boot or at runtime, without rebuilding.

A common use case is GPU drivers. If you rarely need your discrete GPU, you can keep drivers disabled in your base configuration and create a specialisation that enables them. At boot, you pick which configuration to start. The same idea applies to desktop environments, kernel parameters, or any set of options you want to toggle as a group.

## Defining specialisations

Add a `specialisation` block to your NixOS configuration. Each entry names a variation and provides the NixOS module options that differ from the base system.

```nix
{ lib, ... }:
{
  # Base configuration: GNOME desktop, no Nvidia drivers
  services.xserver.desktopManager.gnome.enable = true;
  hardware.nvidia.modesetting.enable = lib.mkDefault false;

  specialisation = {
    nvidia.configuration = {
      hardware.nvidia.modesetting.enable = true;
      hardware.nvidia.open = true;
      services.xserver.videoDrivers = [ "nvidia" ];
    };

    plasma.configuration = {
      services.xserver.desktopManager.plasma5.enable = true;
    };
  };
}
```

The `nvidia` specialisation inherits the full parent configuration and layers Nvidia driver options on top. The `plasma` specialisation does the same, adding Plasma alongside the base GNOME setup. Both appear as separate boot entries after you rebuild.

:::admonition[Overriding parent values]{type=tip}
Specialisations receive the parent config by default. If the parent sets a value that a specialisation needs to change, mark the parent value with `lib.mkDefault` so the specialisation can override it without priority conflicts. In the example above, `hardware.nvidia.modesetting.enable = lib.mkDefault false;` allows the `nvidia` specialisation to set it to `true`.
:::

## Starting from scratch with inheritParentConfig

By default, every specialisation inherits the parent configuration. If you want a specialisation that defines its own system independently, set `inheritParentConfig = false`:

```nix
specialisation = {
  minimal = {
    inheritParentConfig = false;
    configuration = {
      system.nixos.tags = [ "minimal" ];
      boot.loader.grub.enable = true;
      fileSystems."/" = { device = "/dev/sda1"; fsType = "ext4"; };
      # ... everything else must be specified explicitly
    };
  };
};
```

This is useful for creating a stripped-down recovery configuration or a fundamentally different system variant. Be aware that `inheritParentConfig = false` means you must provide a complete, bootable NixOS configuration within the `configuration` block.

## Excluding options from specialisations

Sometimes the base configuration should include options that specialisations should not inherit. Use `config.specialisation != {}` as a condition to restrict options to the default (non-specialised) entry:

```nix
{
  lib,
  config,
  pkgs,
  ...
}:
{
  config = lib.mkIf (config.specialisation != { }) {
    # Only applies to the default system, not to specialisations
    hardware.graphics.extraPackages = with pkgs; [
      vaapiIntel
      vaapiVdpau
    ];
  };
}
```

:::admonition[Condition requires specialisations]{type=warning}
The expression `config.specialisation != {}` evaluates to `false` when no specialisations are defined. The conditional block only takes effect when at least one specialisation exists in the configuration.
:::

## Activating a specialisation at boot

After rebuilding your system (with `clan machines update` or `nixos-rebuild switch`), each specialisation appears as a separate entry in your bootloader menu. Select one during boot to start that configuration.

## Switching at runtime with Clan

Clan supports switching specialisations at runtime through the `--specialisation` flag on `clan machines update`:

```bash
clan machines update my-machine --specialisation nvidia
```

This builds the system configuration and activates the named specialisation on the target machine. The specialisation's `switch-to-configuration switch` script runs on the target, applying the configuration without a reboot.

:::admonition[Runtime limitations]{type=warning}
Not all configuration changes can take effect at runtime. If a specialisation uses a different kernel, for example, the running kernel will not change until you reboot and select the specialisation from the boot menu.
:::

You can also switch specialisations directly on the target machine using `nixos-rebuild`:

```bash
sudo nixos-rebuild switch --specialisation nvidia
```

## When to use specialisations

Specialisations work well when you have a small number of pre-defined system variants that share most of their configuration. Typical examples:

- GPU driver toggles (enable/disable proprietary drivers)
- Desktop environment alternatives (GNOME vs. Plasma)
- Performance profiles (power-saving vs. high-performance kernel parameters)
- Debug configurations (verbose logging, extra diagnostic tools)

For configuration differences that are more granular or need to compose independently, NixOS module options with `lib.mkDefault` and `lib.mkForce` may be a better fit than specialisations.
