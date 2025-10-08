{
  buildNpmPackage,
  importNpmLock,
  nodejs_latest,
  module-docs,
}:
buildNpmPackage {
  pname = "clan-site";
  version = "0.0.1";
  nodejs = nodejs_latest;
  src = ./.;

  npmDeps = importNpmLock {
    npmRoot = ./.;
  };

  npmConfigHook = importNpmLock.npmConfigHook;

  preBuild = ''
    # Copy generated reference docs
    mkdir -p src/routes/docs/reference
    cp -r ${module-docs}/reference/* src/routes/docs/reference

    mkdir -p src/routes/docs/services
    cp -r ${module-docs}/services/* src/routes/docs/services

    chmod +w -R src/routes/docs/reference

    mkdir -p static/icons
    cp -af ${../pkgs/clan-app/ui/icons}/* ./static/icons
    chmod +w -R static/icons
  '';
}
