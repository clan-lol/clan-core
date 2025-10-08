{ inputs, ... }:
{
  imports = [ inputs.treefmt-nix.flakeModule ];
  perSystem =
    { self', pkgs, ... }:
    {
      treefmt.projectRootFile = "LICENSE.md";
      treefmt.programs.shellcheck.enable = true;

      treefmt.programs.mypy.enable = true;
      treefmt.programs.nixfmt.enable = true;
      treefmt.programs.nixfmt.package = pkgs.nixfmt-rfc-style;
      treefmt.programs.deadnix.enable = true;
      treefmt.programs.sizelint.enable = true;
      treefmt.programs.sizelint.failOnWarn = true;
      treefmt.programs.clang-format.enable = true;
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
        # prettier messes up our mkdocs flavoured markdown
        "*.md"
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
        "pkgs/clan-vm-manager/.vscode/lhebendanz.weaudit"
        "pkgs/clan-vm-manager/bin/clan-vm-manager"
        "clanServices/hello-world/default.nix"
        "sops/secrets/test-backup-age.key/secret"
      ];
      treefmt.settings.formatter.ruff-format.includes = [
        "*/bin/clan"
        "*/bin/clan-app"
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
      };
      treefmt.programs.mypy.directories = {
        "clan-cli" = {
          directory = "pkgs/clan-cli";
          extraPythonPackages = (self'.packages.clan-cli.devshellPyDeps pkgs.python3Packages);
        };
        "clan-app" = {
          directory = "pkgs/ui/clan-app";
          extraPythonPackages = (self'.packages.clan-app.devshellPyDeps pkgs.python3Packages);
          extraPythonPaths = [ "../../clan-cli" ];
        };
      }
      // (
        if pkgs.stdenv.isLinux then
          {
            "clan-vm-manager" = {
              directory = "pkgs/clan-vm-manager";
              extraPythonPackages = self'.packages.clan-vm-manager.externalTestDeps ++ [
                (pkgs.python3.withPackages (ps: self'.packages.clan-cli.devshellPyDeps ps))
              ];
              extraPythonPaths = [ "../clan-cli" ];
            };
          }
        else
          { }
      );
      treefmt.programs.ruff.check = true;
      treefmt.programs.ruff.format = true;
    };
}
