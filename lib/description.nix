{ ... }:

rec {
  # getReadme =
  #   modulename:
  #   let
  #     readme = "${clan-core}/clanModules/${modulename}/README.md";
  #     readmeContents =
  #       if (builtins.pathExists readme) then
  #         (builtins.readFile readme)
  #       else
  #         throw "No README.md found for module ${modulename}";
  #   in
  #   readmeContents;

  # getShortDescription =
  #   modulename:
  #   let
  #     content = (getReadme modulename);
  #     parts = lib.splitString "---" content;
  #     description = builtins.head parts;
  #     number_of_newlines = builtins.length (lib.splitString "\n" description);
  #   in
  #   if (builtins.length parts) > 1 then
  #     if number_of_newlines > 4 then
  #       throw "Short description in README.md for module ${modulename} is too long. Max 3 newlines."
  #     else if number_of_newlines <= 1 then
  #       throw "Missing short description in README.md for module ${modulename}."
  #     else
  #       description
  #   else
  #     throw "Short description delimiter `---` not found in README.md for module ${modulename}";
}
