{ aemu
, rustPlatform
, fetchFromGitHub
, pkg-config
, gfxstream
, libdrm
}:

rustPlatform.buildRustPackage {
  pname = "rutabaga_gfx_ffi";
  version = "unstable-2023-12-05";

  src = fetchFromGitHub {
    owner = "google";
    repo = "crosvm";
    rev = "65b30e2ecede8056fdbfe8adbe52e9ff51d2a4e2";
    hash = "sha256-9jzLFBqMGw3wYCL5006+7b9l/f1N2Jy3rw5rEzOr4M0=";
    fetchSubmodules = true;
  };

  patches = [
    ./0001-rutabaga_gfx-don-t-clone-wayland-memfd-file-descript.patch
    ./0002-rutabaga_gfx-super-ugly-workaround-to-get-private-ke.patch
  ];

  buildPhase = ''
    cd rutabaga_gfx/ffi
    make build
  '';

  installPhase = ''
    make install prefix=$out
  '';

  cargoHash = "sha256-jEhobp/ZNx5t20hBjisXR8SSn0776Jehy+RJZNSd2iA=";

  nativeBuildInputs = [ pkg-config ];
  buildInputs = [ gfxstream aemu libdrm ];
}
