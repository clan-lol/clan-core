{ clan-core, ... }:

rec {
  getReadme =
    modulename:
    let
      readme = "${clan-core}/clanModules/${modulename}/README.md";
      readmeContents =
        if (builtins.pathExists readme) then
          (builtins.readFile readme)
        else
          throw "No README.md found for module ${modulename}";
    in
    readmeContents;

  getShortDescription =
    modulename:
    let
      content = (getReadme modulename);
      parts = builtins.split "---" content;
    in
    if (builtins.length parts) > 0 then
      builtins.head parts
    else
      throw "Short description delimiter `---` not found in README.md for module ${modulename}";
}
