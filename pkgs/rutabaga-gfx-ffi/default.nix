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
    rev = "a10c83864e1d6e47773ca06e47ada4f888b30d82";
    hash = "sha256-Dd0oCgCL5LNxDuOJ6hyCXeqGyKBP0AqKamQTKXqNcjk=";
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

  cargoHash = "sha256-oh49o/WjfT9xsQH4SUtFwNl6H3pX5Wio3FzKw+slJcQ=";

  nativeBuildInputs = [ pkg-config ];
  buildInputs = [ gfxstream aemu libdrm ];
}
