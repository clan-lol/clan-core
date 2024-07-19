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

      treefmt.programs.mypy.directories = {
        "pkgs/clan-cli" = {
          extraPythonPackages = self'.packages.clan-cli.testDependencies;
          modules = [ "clan_cli" ];
        };
        "pkgs/clan-app" = {
          extraPythonPackages =
            # clan-app currently only exists on linux
            (self'.packages.clan-app.externalTestDeps or [ ]) ++ self'.packages.clan-cli.testDependencies;
          modules = [ "clan_app" ];
        };
        "pkgs/clan-vm-manager" = {
          extraPythonPackages =
            # clan-app currently only exists on linux

            self'.packages.clan-vm-manager.testDependencies ++ self'.packages.clan-cli.testDependencies;
          modules = [ "clan_vm_manager" ];
        };
      };
      treefmt.programs.ruff.check = true;
      treefmt.programs.ruff.format = true;

      # FIXME: currently broken in CI
      #treefmt.settings.formatter.vale =
      #  let
      #    vocab = "cLAN";
      #    style = "Docs";
      #    config = pkgs.writeText "vale.ini" ''
      #      StylesPath = ${styles}
      #      Vocab = ${vocab}

      #      [*.md]
      #      BasedOnStyles = Vale, ${style}
      #      Vale.Terms = No
      #    '';
      #    styles = pkgs.symlinkJoin {
      #      name = "vale-style";
      #      paths = [
      #        accept
      #        headings
      #      ];
      #    };
      #    accept = pkgs.writeTextDir "config/vocabularies/${vocab}/accept.txt" ''
      #      Nix
      #      NixOS
      #      Nixpkgs
      #      clan.lol
      #      Clan
      #      monorepo
      #    '';
      #    headings = pkgs.writeTextDir "${style}/headings.yml" ''
      #      extends: capitalization
      #      message: "'%s' should be in sentence case"
      #      level: error
      #      scope: heading
      #      # $title, $sentence, $lower, $upper, or a pattern.
      #      match: $sentence
      #    '';
      #  in
      #  {
      #    command = "${pkgs.vale}/bin/vale";
      #    options = [ "--config=${config}" ];
      #    includes = [ "*.md" ];
      #    # TODO: too much at once, fix piecemeal
      #    excludes = [
      #      "docs/*"
      #      "clanModules/*"
      #      "pkgs/*"
      #    ];
      #  };
    };
}
