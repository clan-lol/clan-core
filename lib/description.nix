{ clan-core, ... }:

{
  getDescription =
    modulename:
    let
      readme = "${clan-core}/clanModules/${modulename}/README.md";
      readmeContents =
        if
          builtins.trace "Trying to get Module README.md for ${modulename} from ${readme}"
            # TODO: Edge cases
            (builtins.pathExists readme)
        then
          (builtins.readFile readme)
        else
          null;
    in
    readmeContents;
}
