{
  imports = [ ./gui-installer/flake-module.nix ];
  perSystem =
    {
      self',
      inputs',
      lib,
      ...
    }:
    let
      pkgs = inputs'.nixpkgs.legacyPackages;

      images = {
        "ubuntu-22-04" = {
          image = import <nix/fetchurl.nix> {
            url = "https://app.vagrantup.com/generic/boxes/ubuntu2204/versions/4.1.12/providers/libvirt.box";
            hash = "sha256-HNll0Qikw/xGIcogni5lz01vUv+R3o8xowP2EtqjuUQ=";
          };
          rootDisk = "box.img";
          system = "x86_64-linux";
          package = self'.checks.package-gui-installer-deb;
          installCmd = "dpkg -i package/*.deb";
        };
      };

      makeTest =
        imageName: testName:
        let
          image = images.${imageName};
        in
        pkgs.runCommand "package-${testName}-install-test-${imageName}"
          {
            buildInputs = [
              pkgs.qemu_kvm
              pkgs.openssh
            ];
            image = image.image;
            postBoot = image.postBoot or "";
            installCmd = image.installCmd;
            package = image.package;
          }
          ''
            shopt -s nullglob

            echo "Unpacking Vagrant box $image..."
            tar xvf $image

            image_type=$(qemu-img info ${image.rootDisk} | sed 's/file format: \(.*\)/\1/; t; d')

            qemu-img create -b ./${image.rootDisk} -F "$image_type" -f qcow2 ./disk.qcow2

            extra_qemu_opts="${image.extraQemuOpts or ""}"

            # Add the config disk, required by the Ubuntu images.
            config_drive=$(echo *configdrive.vmdk || true)
            if [[ -n $config_drive ]]; then
              extra_qemu_opts+=" -drive id=disk2,file=$config_drive,if=virtio"
            fi

            echo "Starting qemu..."
            qemu-kvm -m 4096 -nographic \
              -drive id=disk1,file=./disk.qcow2,if=virtio \
              -netdev user,id=net0,restrict=yes,hostfwd=tcp::20022-:22 -device virtio-net-pci,netdev=net0 \
              $extra_qemu_opts &
            qemu_pid=$!
            trap "kill $qemu_pid" EXIT

            if ! [ -e ./vagrant_insecure_key ]; then
              cp ${./vagrant_insecure_key} vagrant_insecure_key
            fi

            chmod 0400 ./vagrant_insecure_key

            ssh_opts="-o StrictHostKeyChecking=no -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedKeyTypes=+ssh-rsa -i ./vagrant_insecure_key"
            ssh="ssh -p 20022 -q $ssh_opts vagrant@localhost"

            echo "Waiting for SSH..."
            for ((i = 0; i < 120; i++)); do
              echo "[ssh] Trying to connect..."
              if $ssh -- true; then
                echo "[ssh] Connected!"
                break
              fi
              if ! kill -0 $qemu_pid; then
                echo "qemu died unexpectedly"
                exit 1
              fi
              sleep 1
            done

            if [[ -n $postBoot ]]; then
              echo "Running post-boot commands..."
              $ssh "set -ex; $postBoot"
            fi

            echo "Copying package..."
            scp -r -P 20022 $ssh_opts $package vagrant@localhost:package

            echo "Installing Package..."
            $ssh "set -eux; $installScript"

            touch $out
          '';
    in
    {
      checks = lib.mapAttrs' (imageName: _image: {
        name = "package-gui-install-test-${imageName}";
        value = makeTest imageName "gui";
      }) images;
    };
}
