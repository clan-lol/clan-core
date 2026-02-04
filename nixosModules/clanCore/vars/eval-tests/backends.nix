# Test that password-store backend options are available for all machine classes.
# This catches the issue where vars/default.nix only imported password-store.nix for NixOS,
# causing Darwin machines to fail when using password-store backend.
{ lib, pkgs }:
let
  # All machine classes that should support password-store
  classes = [
    "nixos"
    "darwin"
  ];

  # Common mocks needed for all classes
  commonMockModule = {
    options = {
      # Mock clan.core.vars.settings and generators
      clan.core.vars = {
        settings = {
          secretStore = lib.mkOption {
            type = lib.types.str;
            default = "password-store";
          };
          fileModule = lib.mkOption {
            type = lib.types.raw;
            default = _: { };
          };
        };
        generators = lib.mkOption {
          type = lib.types.attrsOf lib.types.raw;
          default = { };
        };
      };
    };
  };

  # NixOS-specific mocks - only used when _class == "nixos"
  nixosMockModule = {
    options = {
      system.activationScripts = lib.mkOption {
        type = lib.types.raw;
        default = { };
      };
      systemd.services = lib.mkOption {
        type = lib.types.raw;
        default = { };
      };
      systemd.sysusers.enable = lib.mkOption {
        type = lib.types.bool;
        default = false;
      };
      services.userborn.enable = lib.mkOption {
        type = lib.types.bool;
        default = false;
      };
    };
  };

  # Evaluate the password-store module for each class using realistic mocks.
  evalVars =
    _class:
    let
      passwordStoreImports = [ ../secret/password-store.nix ];
      # Only include NixOS mocks for nixos class - Darwin doesn't have these options
      classMocks = lib.optionals (_class == "nixos") [ nixosMockModule ];
    in
    lib.evalModules {
      specialArgs = {
        inherit _class pkgs;
      };
      modules = [ commonMockModule ] ++ classMocks ++ passwordStoreImports;
    };

  # Generate a test for each class - evaluates both options and config
  mkTest = _class: {
    name = "test_password_store_for_${_class}";
    value = {
      expr =
        let
          eval = evalVars _class;
          # Check options exist AND config evaluates without error
          hasOptions = eval.options.clan.core.vars ? "password-store";
          # Force evaluation of config to catch runtime errors
          configEvaluates = eval.config.clan.core.vars.password-store.passCommand != null;
        in
        hasOptions && configEvaluates;
      expected = true;
    };
  };
in
lib.listToAttrs (map mkTest classes)
