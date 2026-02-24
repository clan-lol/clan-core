{
  fetchPnpmDeps,
  pnpm_10,
  nodejs_24,
  pnpmConfigHook,
  stdenv,
  docs-markdowns,
  clan-site-assets,
}:
stdenv.mkDerivation (finalAttrs: {
  pname = "clan-site";
  version = "0.0.1";
  src = ./.;

  nativeBuildInputs = [
    nodejs_24
    pnpm_10
    pnpmConfigHook
  ];

  pnpmDeps = fetchPnpmDeps {
    inherit (finalAttrs) pname version src;
    fetcherVersion = 3;
    hash = "sha256-L+P9Ttdw1m9blSpJispUxPimZAXa7RZgQO/MpFjkGAE=";
  };

  preBuild = ''
    mkdir -p src/docs src/lib/assets
    cp -r ${docs-markdowns}/* src/docs
    cp -r ${clan-site-assets}/* src/lib/assets
  '';
  buildPhase = ''
    runHook preBuild
    pnpm run build
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    mv build $out
    runHook postInstall
  '';
  passthru = {
    tests = {
      "${finalAttrs.pname}-lint" = stdenv.mkDerivation {
        name = "${finalAttrs.pname}-lint";
        inherit (finalAttrs)
          src
          nativeBuildInputs
          pnpmDeps
          ;
        preBuild = finalAttrs.preBuild + ''
          pnpm run prepare
        '';
        buildPhase = ''
          runHook preBuild
          pnpm run lint
          runHook postBuild
        '';
        installPhase = ''
          runHook preInstall
          : >$out
          runHook postInstall
        '';
      };
    };
  };
})
