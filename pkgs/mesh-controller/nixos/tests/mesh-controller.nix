{ pkgs, zerotier-src }:

let
  # Trim the working copy to avoid copying build artifacts into the VM.
  src = pkgs.lib.cleanSourceWith {
    src = ../../.;
    filter =
      path: _type:
      let
        base = pkgs.lib.baseNameOf path;
      in
      !builtins.elem base [
        ".git"
        "target"
        "build"
        "result"
        ".direnv"
      ];
  };
in
pkgs.nixosTest {
  name = "mesh-controller-integration";

  nodes = {
    node =
      { ... }:
      {
        virtualisation = {
          memorySize = 2048;
          diskSize = 8192;
        };

        environment.systemPackages = with pkgs; [
          bashInteractive
          cmake
          pkg-config
          rustc
          cargo
          openssl
          git
          sudo
          iputils
        ];

        users.users.root.password = "";
        security.sudo.wheelNeedsPassword = false;
      };
  };

  testScript = ''
    start_all()
    node.wait_for_unit("multi-user.target")

    node.succeed("cp -r ${src} /root/mesh-controller")
    node.succeed("cd /root/mesh-controller && mkdir -p build && cd build && cmake .. -DSOURCE_DIR=${zerotier-src}")
    node.succeed("cd /root/mesh-controller/build && make -j$(nproc)")
    node.succeed("cd /root/mesh-controller/build && MESH_BIN=$PWD/meshd CARGO_TARGET_DIR=$PWD/rust sudo ctest -V -R integration_test")
  '';
}
