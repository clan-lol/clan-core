{ clan-core, lib }:
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
      content = getReadme modulename;
      parts = lib.splitString "---" content;
      # Partition the parts into the first part (the readme content) and the rest (the metadata)
      parsed = builtins.partition ({ index, ... }: if index >= 2 then false else true) (
        lib.filter ({ index, ... }: index != 0) (lib.imap0 (index: part: { inherit index part; }) parts)
      );

      # Use this if the content is needed
      # readmeContent = lib.concatMapStrings (v: "---" + v.part) parsed.wrong;

      meta = builtins.fromTOML (builtins.head parsed.right).part;
    in
    if (builtins.length parts >= 3) then
      meta.description
    else
      throw "Short description delimiter `---` not found in README.md for module ${modulename}";
}
