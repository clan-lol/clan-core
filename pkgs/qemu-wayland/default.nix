{ qemu_kvm, rutabaga-gfx-ffi, fetchurl }:
qemu_kvm.overrideAttrs (old: {
  src = fetchurl {
    url = "https://download.qemu.org/qemu-8.2.0.tar.xz";
    hash = "sha256-vwDS+hIBDfiwrekzcd71jmMssypr/cX1oP+Oah+xvzI=";
  };

  buildInputs = old.buildInputs ++ [ rutabaga-gfx-ffi ];
})
