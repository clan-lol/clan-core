{
  stdenv,
  makeWrapper,
  python3,
  bash,
  coreutils,
  git,
  lib,
  nix,
  openssh,
  tea,
  tea-create-pr,
  ...
}:
stdenv.mkDerivation {
  pname = "merge-after-ci";
  version = "0.1.0";

  src = ./.;

  nativeBuildInputs = [ makeWrapper ];

  buildInputs = [ python3 ];

  installPhase = ''
    runHook preInstall

    mkdir -p $out/bin
    cp merge-after-ci.py $out/bin/merge-after-ci
    chmod +x $out/bin/merge-after-ci

    wrapProgram $out/bin/merge-after-ci \
      --prefix PATH : ${
        lib.makeBinPath [
          bash
          coreutils
          git
          nix
          openssh
          tea
          tea-create-pr
          python3
        ]
      }

    runHook postInstall
  '';
}
