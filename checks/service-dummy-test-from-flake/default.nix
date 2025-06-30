{
  pkgs,
  nixosLib,
  clan-core,
  ...
}:

nixosLib.runTest (
  { hostPkgs, config, ... }:
  {
    imports = [
      clan-core.modules.nixosTest.clanTest
    ];

    hostPkgs = pkgs;

    # This tests the compatibility of the inventory
    # With the test framework
    # - legacy-modules
    # - clan.service modules
    name = "service-dummy-test-from-flake";

    clan.test.fromFlake = ./.;

    extraPythonPackages = _p: [
      clan-core.legacyPackages.${hostPkgs.system}.setupNixInNixPythonPackage
    ];

    testScript =
      { nodes, ... }:
      ''
        from setup_nix_in_nix import setup_nix_in_nix # type: ignore[import-untyped]
        setup_nix_in_nix()

        def run_clan(cmd: list[str], **kwargs) -> str:
            import subprocess
            clan = "${clan-core.packages.${hostPkgs.system}.clan-cli}/bin/clan"
            clan_args = ["--flake", "${config.clan.test.flakeForSandbox}"]
            return subprocess.run(
                ["${hostPkgs.util-linux}/bin/unshare", "--user", "--map-user", "1000", "--map-group", "1000", clan, *cmd, *clan_args],
                **kwargs,
                check=True,
            ).stdout

        start_all()
        admin1.wait_for_unit("multi-user.target")
        peer1.wait_for_unit("multi-user.target")
        # Provided by the legacy module
        print(admin1.succeed("systemctl status dummy-service"))
        print(peer1.succeed("systemctl status dummy-service"))

        # peer1 should have the 'hello' file
        peer1.succeed("cat ${nodes.peer1.clan.core.vars.generators.new-service.files.not-a-secret.path}")

        ls_out = peer1.succeed("ls -la ${nodes.peer1.clan.core.vars.generators.new-service.files.a-secret.path}")
        # Check that the file is owned by 'nobody'
        assert "nobody" in ls_out, f"File is not owned by 'nobody': {ls_out}"
        # Check that the file is in the 'users' group
        assert "users" in ls_out, f"File is not in the 'users' group: {ls_out}"
        # Check that the file is in the '0644' mode
        assert "-rw-r--r--" in ls_out, f"File is not in the '0644' mode: {ls_out}"

        run_clan(["machines", "list"])
      '';
  }
)
