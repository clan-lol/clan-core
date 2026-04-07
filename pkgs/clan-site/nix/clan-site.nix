{
  lib,
  nodejs_24,
  pnpm_10,
  fetchPnpmDeps,
  pnpmConfigHook,
  stdenv,
  jq,
  git,
  playwright,
  makeFontsConf,
  mona-sans,
  clan-site-assets,
  clan-site-cli,
  generated-docs,
}:
let
  RED = "\\033[1;31m";
  NC = "\\033[0m";
in
stdenv.mkDerivation (
  finalAttrs:
  let
    fodArgs = {
      inherit (finalAttrs) src version;
      sourceRoot = "${finalAttrs.src.name}/${finalAttrs.pnpmRoot}";
      fetcherVersion = 3;
    };
    fodAttrs = fodArgs // {
      pname = builtins.hashString "md5" (builtins.toJSON fodArgs);
    };
  in
  {
    pname = "clan-site";
    version = "0.0.1";

    pnpmRoot = "pkgs/clan-site";
    src = lib.fileset.toSource {
      root = ../../../.;
      fileset = lib.fileset.unions [
        ../../../VERSION
        ../../../docs
        ../../../${finalAttrs.pnpmRoot}
      ];
    };

    nativeBuildInputs = [
      nodejs_24
      pnpm_10
      pnpmConfigHook
      clan-site-cli
      jq
      git
    ];

    pnpmDeps = fetchPnpmDeps (
      fodAttrs
      // {
        hash = "sha256-Ih7fWCSycmcPMHJsl7V34VAXioUlTA9F0BbdL4SvJTA=";
      }
    );

    env = {
      GENERATED_DOCS = generated-docs;
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

    buildPhase = ''
      runHook preBuild
      cd ${finalAttrs.pnpmRoot}
      ${finalAttrs.passthru.devShellHook}
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
      devShellHook = ''
        mkdir -p src/lib/assets
        cp -R ${clan-site-assets}/* src/lib/assets
        chmod -R +w src/lib/assets

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
      tests = {
        "${finalAttrs.pname}-lint" = stdenv.mkDerivation {
          name = "${finalAttrs.pname}-lint";
          inherit (finalAttrs)
            pnpmRoot
            src
            nativeBuildInputs
            pnpmDeps
            env
            ;
          buildPhase = ''
            runHook preBuild
            cd ${finalAttrs.pnpmRoot}
            ${finalAttrs.passthru.devShellHook}
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
  }
)
