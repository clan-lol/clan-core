{ lib, ... }:
let
  /**
    Creates a scope string for global exports

    At least one of serviceame or machineName must be set.

    The scope string has the format:

    "SERVICE:INSTANCE:ROLE:MACHINE"

    If the parameter is not set, the corresponding part is left empty.
    Semantically this means "all".

    Examples:
    buildScopeKey { service = "A"; }
    -> "A:::"

    buildScopeKey { machine = "jon"; }
    -> ":::jon"

    buildScopeKey { service = "A"; instance = "i1"; role = "peer"; machine = "jon"; }
    -> "A:i1:peer:jon"
  */
  buildScopeKey =
    {
      serviceName ? "",
      instanceName ? "",
      roleName ? "",
      machineName ? "",
    }:
    let
      parts = [
        serviceName
        instanceName
        roleName
        machineName
      ];
      checkedParts = lib.map (
        part:
        lib.throwIf (builtins.match ".?:.?" part != null) ''
          exports.mkExportsScope: ${part} cannot contain the ":" character
        '' part
      ) parts;
    in
    lib.throwIf ((serviceName == "" && machineName == "")) ''
      buildScopeKey requires at least 'serviceName' or 'machineName'

      Examples:
      - { serviceName = "myservice"; ... }
      - { machineName = "server01"; ... }

      If you need a scope with neither service nor machine, please file an issue
      explaining your use case at: https://git.clan.lol/clan/clan-core/issues
    '' (lib.join ":" checkedParts);

  mkExports = scope: value: {
    ${buildScopeKey scope} = value;
  };

  /**
    Parses a scope string into its components

    Returns an attribute set with the keys:
    - serviceName
    - instanceName
    - roleName
    - machineName

    Example:
    parseScope "A:i1:peer:jon"
    ->
    {
      serviceName = "A";
      instanceName = "i1";
      roleName = "peer";
      machineName = "jon";
    }
  */
  parseScope =
    scopeStr:
    let
      parts = lib.splitString ":" scopeStr;
      checkedParts = lib.throwIf (lib.length parts != 4) ''
        clanLib.exports.parseScope: invalid scope string format.
        Got '${scopeStr}'

        fix:
        - use the provided 'mkExports' utility or
        - use clanLib.exports.buildScopeKey
      '' (parts);
    in
    {
      serviceName = lib.elemAt checkedParts 0;
      instanceName = lib.elemAt checkedParts 1;
      roleName = lib.elemAt checkedParts 2;
      machineName = lib.elemAt checkedParts 3;
    };

  /**
    Checks if the given scope string matches the expected components
    Returns the parsed scope if all checks pass, otherwise throws an error.

    If a parameter is '""' or omited, it is not checked.
  */
  checkScope =
    {
      serviceName ? "",
      instanceName ? "",
      roleName ? "",
      machineName ? "",
      whitelist ? [ ],
      errorDetails ? "",
    }:
    scope:
    let
      parsed = (parseScope scope);
      checked = (
        if lib.elem scope whitelist then
          null
        else
          lib.throwIf (serviceName != "" && parsed.serviceName != serviceName)
            ''
              Export scope mismatch: incorrect service name

              Scope key: "${scope}"
              Expected: "${serviceName}:..."

              ${errorDetails}
            ''

            lib.throwIf
            (instanceName != "" && parsed.instanceName != instanceName)
            ''
              Export scope mismatch: incorrect instance name

              Scope key: "${scope}"
              Expected: ":...:${instanceName}:..."

              ${errorDetails}
            ''
            lib.throwIf
            (roleName != "" && parsed.roleName != roleName)
            ''
              Export scope mismatch: incorrect role name

              Scope key: "${scope}"
                          ^
              Expected: ":...:${roleName}:..."

              ${errorDetails}
            ''

            lib.throwIf
            (machineName != "" && parsed.machineName != machineName)
            ''
              Export scope mismatch: incorrect machine name

              Scope key: "${scope}"
                          ^
              Expected: ":...:${machineName}"

              ${errorDetails}
            ''
            parsed
      );
    in
    lib.seq checked scope;

  /**
    Checks export attributes
    in the form of  { ":::" = ... ; ... }

    Against the given scope constraint `c`
    See 'checkScope' for details.
  */
  checkExports = c: scope: lib.mapAttrs (name: v: lib.seq (checkScope c name) v) scope;

  /**
    filters an attribute set by name predicate

    Vendored from nixpks to make it more safe for self-recusion
    In contrast the 'value' is not passed to the predicate.
    This ensures maximum value lazyness
  */
  filterAttrsByName = pred: set: removeAttrs set (lib.filter (name: !pred name) (lib.attrNames set));

  /**
    Filters exports by scope parts

    Parameters are optional, if set to "" or omited it includes all.

    Some important equivalences:

    Selecting all exports is equivalent to just exports

    selectExports { } exports := exports

    Selecting by service only returns all exports for that service
    including all instances and machines

    selectExports {
      service = "A";
    } {
      "A:::" = { ... };
      "A:::jon" = { ... };
      "A:iA:peer:machineA" = { ... };
      "B:iB:peer:machineB" = { ... };
      ...
    } =>
    {
      "A:::" = { ... };
      "A:::jon" = { ... };
      "A:iA:peer:machineA" = { ... };
    }

    Selecting by machine returns all exports for that machine
    including all services and instances

    selectExports {
      machine = "A";
    } {
      "A:::" = { ... };
      "A::jon" = { ... };
      "A:iA:peer:jon" = { ... };
      "B:iB:peer:jon" = { ... };
      ...
    } =>
    {
      "A::jon" = { ... };
      "A:iA:peer:jon" = { ... };
      "B:iB:peer:jon" = { ... };
    }
  */
  selectExports =
    {
      serviceName ? "*",
      instanceName ? "*",
      roleName ? "*",
      machineName ? "*",
    }:
    filterAttrsByName (
      scopeKey:
      matchesFullScope {
        inherit
          machineName
          roleName
          instanceName
          serviceName
          ;
      } scopeKey
    );

  matchesFullScope =
    c: scopeKey:
    let
      parsed = parseScope scopeKey;
      matchesPart = part: expected: expected == "*" || part == expected;
    in
    matchesPart parsed.serviceName c.serviceName
    && matchesPart parsed.instanceName c.instanceName
    && matchesPart parsed.roleName c.roleName
    && matchesPart parsed.machineName c.machineName;

  /**
    Helper to get a single export by scope

    Examples:

    Get the global exports

    getExport { } exports
    -> exports.":::"

    Get service A exports
    getExport { serviceName = "A"; } exports
    -> exports."A:::"

    Get instance machine A of service A exports
    getExport { serviceName = "A"; machineName = "A"; } exports
  */
  getExport =
    scope: exports:
    let
      scopeKey = buildScopeKey scope;
    in
    exports.${scopeKey} or (throw ''
      getExport: export not found

      Requested scope: "${scopeKey}"

      Scope components:
        serviceName:  "${scope.serviceName or ""}"
        instanceName: "${scope.instanceName or ""}"
        roleName:     "${scope.roleName or ""}"
        machineName:  "${scope.machineName or ""}"

      Available exports:
      ${lib.concatStringsSep "\n" (map (key: "  • ${key}") (lib.attrNames exports))}

      Common causes:
        • The exact instance:role:machine combination doesn't exist
        • The data needs to be aggregated from multiple exports
        • Typo in one of the scope parameters

      Tip: Inspect all exports in the nix repl
        nix-repl> clan.exports
        => {
          "myservice:::" = ...;
          "myservice:i1:role1:machineA" = ...;
          ...
        }
    '');

in
{
  inherit
    buildScopeKey
    checkExports
    checkScope
    getExport
    mkExports
    parseScope
    selectExports
    ;
}
