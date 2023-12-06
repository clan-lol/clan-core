{ qemu_kvm, rutabaga-gfx-ffi, fetchurl, lib, vulkan-loader }:
qemu_kvm.overrideAttrs (old: {
  src = fetchurl {
    url = "https://download.qemu.org/qemu-8.2.0-rc2.tar.xz";
    hash = "sha256-AbQozd8IQNDBsA6/zE98xQboh4dWSk0/V/IsflCju9g=";
  };

  postFixup = (old.postFixup or "") + ''
    for bin in $out/bin/qemu-system-*; do
      wrapProgram $bin \
        --prefix LD_LIBRARY_PATH ':' ${lib.getLib vulkan-loader}/lib
    done
  '';
  buildInputs = old.buildInputs ++ [ rutabaga-gfx-ffi ];
})
