{
  perSystem =
    {
      lib,
      pkgs,
      self',
      ...
    }:
    let

      getMdPages =
        prefix:
        let
          mdDocs' = lib.filterAttrs (name: _: lib.hasPrefix prefix name) self'.packages;
          mdDocs = lib.mapAttrs' (name: pkg: lib.nameValuePair (lib.removePrefix prefix name) pkg) mdDocs';
        in
        if mdDocs != { } then
          mdDocs
        else
          throw ''
            Error: no markdown files found in clan-core.packages' with prefix "${prefix}"
          '';

      makeZolaIndexMd =
        title: weight:
        pkgs.writeText "_index.md" ''
          +++
          title = "${title}"
          template = "docs/section.html"
          weight = ${toString weight}
          sort_by = "title"
          draft = false
          +++
        '';

      makeZolaPages =
        {
          sectionTitle,
          files,
          makeIntro ? _name: "",
          weight ? 9999,
        }:
        pkgs.runCommand "zola-pages-clan-core" { } ''
          mkdir $out
          # create new section via _index.md
          cp ${makeZolaIndexMd sectionTitle weight} $out/_index.md
          # generate zola compatible md files for each nixos options md
          ${lib.concatStringsSep "\n" (
            lib.flip lib.mapAttrsToList files (
              name: md: ''
                # generate header for zola with title, template, weight
                title="${name}"
                echo -e "+++\ntitle = \"$title\"\ntemplate = \"docs/page.html\"\n+++" > "$out/${name}.md"
                cat <<EOF >> "$out/${name}.md"
                ${makeIntro name}
                EOF
                # append everything from the nixpkgs generated md file
                cat "${md}" >> "$out/${name}.md"
              ''
            )
          )}
        '';
    in
    {
      packages.docs-zola-pages-core = makeZolaPages {
        sectionTitle = "cLAN Core Reference";
        files = getMdPages "docs-md-core-";
        weight = 20;
      };

      packages.docs-zola-pages-modules = makeZolaPages {
        sectionTitle = "cLAN Modules Reference";
        files = getMdPages "docs-md-module-";
        weight = 25;
        makeIntro = name: ''
          To use this module, import it like this:

          \`\`\`nix
            {config, lib, inputs, ...}: {
              imports = [inputs.clan-core.clanModules.${name}];
              # ...
            }
          \`\`\`

        '';
      };
    };
}
