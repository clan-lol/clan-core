# Regression test for:
#   https://git.clan.lol/clan/clan-core/issues/<TODO>
#
# The clan.service docs say `meta` is available as a module argument in
# `roles.<name>.interface`, including for option defaults:
#
#   "meta is available as a module argument (e.g. for option defaults and examples)."
#   -- https://clan.lol/docs/unstable/reference/options/clan_service
#
# Since PR #7397 ("jsonschema: add defaults", commit 080eccc8) the API schema
# generation in `api-feature.nix` `deepSeq`s `result.api.schema`, which now
# includes `option.default`. `clanLib.jsonschema.fromModule` evaluates the
# interface module *without* specialArgs, so any `default` that references
# `meta` crashes with:
#
#   error: attribute 'meta' missing
#
# This test verifies that an interface with a `meta`-dependent default still
# evaluates successfully.
{ createTestClan, lib, ... }:
let
  res = createTestClan {
    meta.name = "test";
    meta.domain = "example.com";

    modules."A" = {
      _class = "clan.service";
      manifest = {
        name = "demo";
      };
      roles.default = {
        interface =
          { lib, meta, ... }:
          {
            options.host = lib.mkOption {
              type = lib.types.str;
              # The pattern documented in clan_service docs.
              default = "svc.${meta.domain}";
            };
          };
      };
    };

    inventory = {
      machines.jon = { };
      instances."demo_instance" = {
        module = {
          name = "A";
          input = "self";
        };
        roles.default.machines.jon = { };
      };
    };
  };

  service = res.config._services.allServices.self-A;
  assertions = service.result.assertions;
  schema = service.result.api.schema;

  # Sanity reference: an identical clan where the interface does NOT reference
  # `meta`. Used to confirm the failing tests above fail *only* because of the
  # `meta` reference in the option default, not for some other reason.
  resNoMeta = createTestClan {
    meta.name = "test";
    meta.domain = "example.com";

    modules."A" = {
      _class = "clan.service";
      manifest.name = "demo";
      roles.default = {
        interface =
          { lib, ... }:
          {
            options.host = lib.mkOption {
              type = lib.types.str;
              default = "svc.example.com";
            };
          };
      };
    };

    inventory = {
      machines.jon = { };
      instances."demo_instance" = {
        module = {
          name = "A";
          input = "self";
        };
        roles.default.machines.jon = { };
      };
    };
  };
  schemaNoMeta = resNoMeta.config._services.allServices.self-A.result.api.schema;
in
{
  # The API-feature assertion must not fire when `meta` is used in defaults.
  test_no_failing_assertion = {
    expr = lib.filterAttrs (_: v: !v.assertion) assertions;
    expected = { };
  };

  # The generated schema for the default role must be forceable end-to-end
  # (this is what `api-feature.nix` does via `lib.deepSeq`).
  test_schema_is_forceable = {
    expr = (builtins.tryEval (lib.deepSeq schema.default true)).success;
    expected = true;
  };

  # And the default itself should reflect the value derived from `meta`.
  test_default_resolves_meta = {
    expr = schema.default."$defs".Input.properties.host.default or null;
    expected = "svc.example.com";
  };

  # Sanity: an interface with a static default (no `meta`) works today.
  # This must keep passing both before and after the fix.
  test_static_default_still_works = {
    expr = schemaNoMeta.default."$defs".Input.properties.host.default or null;
    expected = "svc.example.com";
  };
}
