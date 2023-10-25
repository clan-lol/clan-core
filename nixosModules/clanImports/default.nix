{ lib
, ...
}: {
  /*
    Declaring imports inside the module system does not trigger an infinite
    recursion in this case because buildClan generates the imports from the
    settings.json file before calling out to evalModules.
  */
  options.clanImports = lib.mkOption {
    type = lib.types.listOf lib.types.str;
    description = ''
      A list of imported module names imported from clan-core.clanModules.<name>
      The buildClan function will automatically import these modules for the current machine.
    '';
  };
}
