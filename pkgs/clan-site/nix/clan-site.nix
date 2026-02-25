{
  lib,
  nodejs_24,
  pnpm_10,
  fetchPnpmDeps,
  pnpmConfigHook,
  stdenv,
  jq,
  playwright,
  makeFontsConf,
  mona-sans,
  docs-markdowns,
  clan-site-assets,
  clan-site-cli,
}:
let
  RED = "\\033[1;31m";
  NC = "\\033[0m";
in
stdenv.mkDerivation (finalAttrs: {
  pname = "clan-site";
  version = "0.0.1";
  src = ../.;

  nativeBuildInputs = [
    nodejs_24
    pnpm_10
    pnpmConfigHook
    clan-site-cli
    jq
  ];

  pnpmDeps = fetchPnpmDeps {
    inherit (finalAttrs) pname version src;
    fetcherVersion = 3;
    hash = "sha256-CV6ygBJgQmlbO+MhXR7O0hAUwrW/Gdn/eH1XmobeQB4=";
  };

  env = {
    PLAYWRIGHT_BROWSERS_PATH = playwright.browsers.override {
      withFfmpeg = false;
      withFirefox = false;
      withWebkit = false;
      withChromium = false;
      withChromiumHeadlessShell = true;
    };
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = 1;
    # This is needed because mermaid needs a font to correctly render text
    FONTCONFIG_FILE = makeFontsConf {
      fontDirectories = [ mona-sans ];
    };
  };

  preBuild = ''
    mkdir -p src/docs src/lib/assets
    cp -r ${docs-markdowns}/* src/docs
    cp -r ${clan-site-assets}/* src/lib/assets

    playwright_ver=$(jq --raw-output .dependencies.playwright ${../packages/svelte-md/package.json})
    if [[ $playwright_ver != '${playwright.version}' ]]; then
      echo >&2 -en '${RED}'
      echo >&2 "Error: The npm package "playwright" is of a different version ($playwright_ver) than the one used in nixpkgs (${playwright.version})"
      echo >&2 "Run this command to update the former"
      echo >&2
      echo >&2 "  pnpm add -E --filter @clan.lol/svelte-md playwright@${playwright.version}"
      echo >&2
      echo >&2 -en '${NC}'
      exit 1
    fi
  '';
  buildPhase = ''
    runHook preBuild
    clan-site build
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    mv build $out
    runHook postInstall
  '';
  passthru = {
    devShellEnv = lib.removeAttrs finalAttrs.env [ "FONTCONFIG_FILE" ];
    tests = {
      "${finalAttrs.pname}-lint" = stdenv.mkDerivation {
        name = "${finalAttrs.pname}-lint";
        inherit (finalAttrs)
          src
          nativeBuildInputs
          pnpmDeps
          env
          preBuild
          ;
        buildPhase = ''
          runHook preBuild
          clan-site lint
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
