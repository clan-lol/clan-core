{ lib, ... }:
clanDir:
let

  allMachineNames = lib.mapAttrsToList (name: _: name) (builtins.readDir clanDir);

  getFactPath = machine: fact: "${clanDir}/machines/${machine}/facts/${fact}";

  readFact =
    machine: fact:
    let
      path = getFactPath machine fact;
    in
    if builtins.pathExists path then builtins.readFile path else null;

  # Example:
  #
  # readFactFromAllMachines zerotier-ip
  # => {
  #   machineA = "1.2.3.4";
  #   machineB = "5.6.7.8";
  # };
  readFactFromAllMachines =
    fact:
    let
      machines = allMachineNames;
      facts = lib.genAttrs machines (machine: readFact machine fact);
      filteredFacts = lib.filterAttrs (_machine: fact: fact != null) facts;
    in
    filteredFacts;

  # all given facts are are set and factvalues are never null.
  #
  # Example:
  #
  # readFactsFromAllMachines [ "zerotier-ip" "syncthing.pub" ]
  # => {
  #   machineA =
  #     {
  #       "zerotier-ip" = "1.2.3.4";
  #       "synching.pub" = "1234";
  #     };
  #   machineB =
  #     {
  #       "zerotier-ip" = "5.6.7.8";
  #       "synching.pub" = "23456719";
  #     };
  # };
  readFactsFromAllMachines =
    facts:
    let
      # machine -> fact -> factvalue
      machinesFactsAttrs = lib.genAttrs allMachineNames (
        machine: lib.genAttrs facts (fact: readFact machine fact)
      );
      # remove all machines which don't have all facts set
      filteredMachineFactAttrs = lib.filterAttrs (
        _machine: values: builtins.all (fact: values.${fact} != null) facts
      ) machinesFactsAttrs;
    in
    filteredMachineFactAttrs;
in
{
  inherit
    allMachineNames
    getFactPath
    readFact
    readFactFromAllMachines
    readFactsFromAllMachines
    ;
}
