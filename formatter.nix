{ inputs, ... }:
{
  imports = [ inputs.treefmt-nix.flakeModule ];
  perSystem =
    { self', pkgs, ... }:
    {
      treefmt.projectRootFile = ".git/config";
      treefmt.programs.shellcheck.enable = true;

      treefmt.programs.mypy.enable = true;
      treefmt.programs.nixfmt.enable = true;
      treefmt.programs.nixfmt.package = pkgs.nixfmt-rfc-style;
      treefmt.programs.deadnix.enable = true;
      treefmt.settings.global.excludes = [
        "*.png"
        "*.jpeg"
        "*.gitignore"
        ".vscode/*"
        "*.toml"
        "*.clan-flake"
        "*.code-workspace"
        "*.pub"
        "*.typed"
        "*.age"
        "*.list"
        "*.desktop"
      ];
      treefmt.programs.prettier = {
        enable = true;
        includes = [
          "*.cjs"
          "*.css"
          "*.html"
          "*.js"
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
        # plugins = [
        #   "${self'.packages.prettier-plugin-tailwindcss}/lib/node_modules/prettier-plugin-tailwindcss/dist/index.mjs"
        # ];
      };
      treefmt.programs.mypy.directories =
        {
          "pkgs/clan-cli" = {
            extraPythonPackages = self'.packages.clan-cli.testDependencies;
            modules = [ "clan_cli" ];
          };
          "pkgs/clan-app" = {
            extraPythonPackages =
              (self'.packages.clan-app.externalTestDeps or [ ]) ++ self'.packages.clan-cli.testDependencies;
            extraPythonPaths = [ "../clan-cli" ];
            modules = [ "clan_app" ];
          };
        }
        // (
          if pkgs.stdenv.isLinux then
            {
              "pkgs/clan-vm-manager" = {
                extraPythonPackages =
                  self'.packages.clan-vm-manager.externalTestDeps ++ self'.packages.clan-cli.testDependencies;
                extraPythonPaths = [ "../clan-cli" ];
                modules = [ "clan_vm_manager" ];
              };
            }
          else
            { }
        );
      treefmt.programs.ruff.check = true;
      treefmt.programs.ruff.format = true;

    };
}
