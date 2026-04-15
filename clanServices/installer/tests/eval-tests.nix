{
  module,
  clanLib,
  ...
}:
let
  testClan = clanLib.clan {
    self = { };
    # Point to the folder of the module
    # TODO: make this optional
    directory = ./..;

    # Create some test machines
    machines.jon = {
      nixpkgs.hostPlatform = "x86_64-linux";
    };
    machines.sara = {
      nixpkgs.hostPlatform = "x86_64-linux";
    };

    # Register the module for the test
    modules.installer = module;

    # Use the module in the test
    inventory.instances = {
      "installer" = {
        module.name = "installer";
        module.input = "self";

        roles.iso.machines.jon = { };
      };
    };
  };
  # Extend the machine config through the iso image.modules so the filesystem
  # and bootloader are configured by the iso-image profile, matching what an
  # actual `clan machines build-machine jon --format iso` would evaluate.
  isoConfig = testClan.config.nixosConfigurations.jon.config.system.build.images.iso.passthru.config;

  failedIsoAssertions = map (a: a.message) (builtins.filter (a: !a.assertion) isoConfig.assertions);
in
{
  /**
    We highly advocate the usage of:
    https://github.com/nix-community/nix-unit

    If you use flake-parts you can use the native integration: https://flake.parts/options/nix-unit.html
  */
  test_variant_id = {
    inherit testClan;
    expr = testClan.config.nixosConfigurations.jon.config.system.nixos.variant_id;
    expected = "installer";
  };

  # Catches assertion failures (including mkRemovedOptionModule hits like
  # `services.kmscon.autologinUser`) that would only surface during a real
  # ISO build. We evaluate the iso-extended config so the assertions from
  # nixpkgs' iso-image profile (root filesystem, bootloader) are satisfied
  # and only genuinely failing assertions remain.
  test_iso_assertions = {
    expr = failedIsoAssertions;
    expected = [ ];
  };
}
