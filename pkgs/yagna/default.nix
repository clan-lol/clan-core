{
  stdenv,
  fetchurl,
  fetchzip,
  makeWrapper,
}:
let
  ya-runtime-vm = fetchzip {
    url = "https://github.com/golemfactory/ya-runtime-vm/releases/download/pre-rel-v0.4.0-ITL-rc21/ya-runtime-vm-linux-pre-rel-v0.4.0-ITL-rc21.tar.gz";
    sha256 = "sha256-z9dr5cr9j89AWdIFYVzdDZX6+nqLeIccioUvkSXn+7U=";
  };
in

stdenv.mkDerivation (finalAttrs: {

  name = "yagna";
  version = "pre-rel-v0.16.0-preview.deposits.3";
  src = fetchurl {
    url = "https://github.com/golemfactory/yagna/releases/download/${finalAttrs.version}/golem-provider-linux-${finalAttrs.version}.tar.gz";
    sha256 = "sha256-RbNqzNjppGa0zK3cmpt8X13CpUO3fuRzrjttl4cwsGM=2";
  };

  nativeBuildInputs = [ makeWrapper ];
  dontBuild = true;
  installPhase = ''
    mkdir -p $out/bin
    mv * $out/bin
    # wrap all executables under $out/bin using wrapProgram
    for bin in $(find $out/bin -type f); do
      wrapProgram $bin --prefix PATH : $out/bin
    done

    cp -r ${ya-runtime-vm}/* $out/bin/plugins/
  '';
})
