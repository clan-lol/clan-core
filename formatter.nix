{ inputs, ... }:
{
  imports = [ inputs.treefmt-nix.flakeModule ];
  perSystem =
    {
      self',
      pkgs,
      lib,
      ...
    }:
    let
      sizelintExcludes = [
        "pkgs/clan-app/ui/package-lock.json"
        "pkgs/clan-site/package-lock.json"
      ];
    in
    {
      treefmt.projectRootFile = "LICENSE.md";
      treefmt.programs.shellcheck.enable = true;

      treefmt.programs.mypy.enable = true;
      treefmt.programs.nixfmt.enable = true;
      treefmt.programs.deadnix.enable = true;
      treefmt.programs.flake-edit.enable = true;
      treefmt.programs.nixf-diagnose.enable = true;
      treefmt.programs.nixf-diagnose.ignore = [
        "sema-primop-removed-prefix"
        "sema-primop-overridden"
        "or-identifier"
      ];
      treefmt.settings.formatter.nixf-diagnose.excludes = [
        "pkgs/clan-cli/clan_cli/tests/test_flake_with_core/flake.nix"
      ];
      treefmt.programs.sizelint.enable = true;
      treefmt.programs.sizelint.failOnWarn = true;
      treefmt.programs.sizelint.settings = {
        max_file_size = "100kb";
        excludes = sizelintExcludes;
        rules.default.description = "File exceeds the maximum allowed size";
        rules.default.suggestion = "Add the file to 'sizelintExcludes' in formatter.nix";
      };
      treefmt.settings.formatter.sizelint.excludes = sizelintExcludes;
      treefmt.programs.clang-format.enable = true;
      treefmt.programs.typos = {
        enable = true;
        threads = 4;
        configFile = "./_typos.toml";
      };
      treefmt.settings.global.excludes = [
        "*.png"
        "*.svg"
        "package-lock.json"
        "*.jpeg"
        "*.gitignore"
        ".vscode/*"
        "*.toml"
        "*.clan-flake"
        "*.code-workspace"
        "*.pub"
        "*.priv"
        "*.typed"
        "*.age"
        "*.list"
        "*.desktop"
        # ignore symlink
        "docs/site/guides/contributing/CONTRIBUTING.md"
        "*_test_cert"
        "*_test_key"
        "*/gnupg-home/*"
        "*/sops/secrets/*"
        "vars/*"
        "**/node_modules/*"
        "**/.mypy_cache/*"

        "checks/data-mesher/vars/*"
        "checks/lib/ssh/privkey"
        "checks/lib/ssh/pubkey"
        "checks/matrix-synapse/synapse-registration_shared_secret"
        "checks/mumble/machines/peer1/facts/mumble-cert"
        "checks/mumble/machines/peer2/facts/mumble-cert"
        "checks/secrets/clan-secrets"
        "checks/secrets/sops/groups/group/machines/machine"
        "checks/syncthing/introducer/introducer_device_id"
        "checks/syncthing/introducer/introducer_test_api"
        "nixosModules/clanCore/vars/secret/sops/eval-tests/populated/vars/my_machine/my_generator/my_secret"
        "pkgs/clan-cli/clan_cli/tests/data/gnupg.conf"
        "pkgs/clan-cli/clan_cli/tests/data/password-store/.gpg-id"
        "pkgs/clan-cli/clan_cli/tests/data/ssh_host_ed25519_key"
        "pkgs/clan-cli/clan_cli/tests/data/sshd_config"
        "clanServices/hello-world/default.nix"
        "sops/secrets/test-backup-age.key/secret"
        "pkgs/clan-cli/clan_lib/nix_models/typing.py"
        # Clan site does its own fmt checking while linting
        # because of the difficult of supporting prettier plugins
        "pkgs/clan-site/*"
      ];
      treefmt.settings.formatter.ruff-format.includes = [
        "*/bin/clan"
        "*/bin/clan-config"
      ];
      treefmt.settings.formatter.ruff-format.excludes = [
        "*/clan_lib/nix_models/*"
      ];
      treefmt.settings.formatter.shellcheck.includes = [
        "scripts/pre-commit"
      ];
      treefmt.programs.prettier = {
        enable = true;
        includes = [
          "*.cjs"
          "*.css"
          "*.html"
          "*.js"
          "*.json"
          "*.json5"
          "*.jsx"
          "*.mdx"
          "*.mjs"
          "*.scss"
          "*.ts"
          "*.tsx"
          "*.vue"
          "*.yaml"
          "*.yml"
        ];
        # prettier messes up our mkdocs flavoured markdown
        excludes = [ "*.md" ];
      };
      treefmt.programs.mypy.directories = {
        "clan-cli" = {
          directory = "pkgs/clan-cli";
          extraPythonPackages = (self'.packages.clan-cli.devshellPyDeps pkgs.python3Packages);
          options = [
            "--config-file"
            "pyproject.toml"
          ];
        };
        "clan-app" = {
          directory = "pkgs/ui/clan-app";
          extraPythonPackages = (self'.packages.clan-app.devshellPyDeps pkgs.python3Packages);
          extraPythonPaths = [ "../../clan-cli" ];
        };
      };
      treefmt.programs.ruff.check = true;
      treefmt.programs.ruff.format = true;

      treefmt.settings.formatter.vale =
        let
          valeTermsRule = pkgs.writeText "Terms.yml" ''
            extends: existence
            message: "Use 'NixOS' instead of '%s'"
            level: error
            nonword: true
            raw:
              - '\b(nixos|Nixos|NIXOS|nixOS)\b(?![-a-zA-Z])'
          '';

          jargonLint = pkgs.fetchFromGitHub {
            owner = "jargonLint";
            repo = "jargonLint";
            rev = "f6c2cf752f0e20488dacc519014d29a8dea90e93";
            hash = "sha256-hILZXwq5kUeOBR7Q8cePlHMeXUI2Tlgz9INhgKd0X5w=";
          };

          valeStylesDir = pkgs.runCommand "vale-styles" { } ''
            mkdir -p $out/config/vocabularies/ClanCore
            mkdir -p $out/ClanCore
            cp ${valeTermsRule} $out/ClanCore/Terms.yml
            cp -r ${jargonLint}/vale/styles/jargonLint $out/
          '';

          valeConfig = pkgs.writeText "vale.ini" ''
            StylesPath = ${valeStylesDir}
            MinAlertLevel = suggestion

            Vocab = ClanCore

            [*.md]
            BasedOnStyles = ClanCore, jargonLint
          '';
        in
        {
          command = lib.getExe pkgs.vale;
          options = [ "--config=${valeConfig}" ];
          includes = [ "docs/**/*.md" ];
          excludes = [ ];
        };
    };
}
