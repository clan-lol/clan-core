{ lib }:
/**
  Function to assert clan configuration checks.

  Arguments:

  - 'checks' attribute of clan configuration
  - Any: the returned configuration (can be anything, is just passed through)
*/
checks:
lib.deepSeq (
  lib.mapAttrs (
    id: check:
    if check.ignore || check.assertion then
      null
    else
      throw "clan.checks.${id} failed with message\n${check.message}"
  ) checks
)
