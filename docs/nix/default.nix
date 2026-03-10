{
  pkgs,
  module-docs,
  clan-cli-docs,
  clan-lib-openapi,
  roboto,
  fira-code,
  ...
}:
pkgs.stdenv.mkDerivation {
  name = "clan-documentation";

  # Points to repository root.
  # so that we can access directories outside of docs to include code snippets
  src = pkgs.lib.fileset.toSource {
    root = ../..;
    fileset = pkgs.lib.fileset.unions [
      # Docs directory
      ../../docs
      # Icons needed for the build
      ../../pkgs/clan-app/ui/src/assets/icons
      # Any other directories that might be referenced for code snippets
      # Add them here as needed based on what mkdocs actually uses
    ];
  };

  nativeBuildInputs = [
    pkgs.python3
  ]
  ++ (with pkgs.python3Packages; [
    mkdocs
    mkdocs-material
    mkdocs-redoc-tag
    mkdocs-redirects
    mike
  ]);
  configurePhase = ''
    pushd docs

    mkdir -p ./site/reference/cli
    cp -af ${module-docs}/services/* ./site/services/
    cp -af ${module-docs}/reference/* ./site/reference/
    cp -af ${clan-cli-docs}/* ./site/reference/cli/

    cp -af ${clan-lib-openapi} ./site/openapi.json

    chmod -R +w ./site
    echo "Generated API documentation in './site/reference/' "

    # Link to fonts
    ln -snf ${roboto}/share/fonts/truetype/Roboto-Regular.ttf ./site/static/
    ln -snf ${fira-code}/share/fonts/truetype/FiraCode-VF.ttf ./site/static/

    # Copy icons into place
    cp -af ../pkgs/clan-app/ui/src/assets/icons ./site/static/
  '';

  buildPhase = ''
    mkdocs build --strict
    ls -la .
  '';

  installPhase = ''
    cp -a out/ $out/
  '';
}
