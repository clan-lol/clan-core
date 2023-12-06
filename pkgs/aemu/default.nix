{ clangStdenv
, fetchgit
, cmake
}:

clangStdenv.mkDerivation {
  pname = "aemu";
  version = "unstable-2023-11-10";
  src = fetchgit {
    url = "https://android.googlesource.com/platform/hardware/google/aemu";
    rev = "ed69e33fb47e6cbe1b1d07c63d4d293dabc770f6";
    hash = "sha256-HYwGT48fPC3foqYvhw+RUsnkoEHgQXfMFGQVSpDu4v4=";
  };
  cmakeFlags = [
    "-DAEMU_COMMON_GEN_PKGCONFIG=ON"
    "-DAEMU_COMMON_BUILD_CONFIG=gfxstream"
  ];
  nativeBuildInputs = [ cmake ];
}
