{
  docs,
  pkgs,
  module-docs,
  clan-cli-docs,
  ...
}:
pkgs.mkShell {
  inputsFrom = [ docs ];
  shellHook = ''
    mkdir -p ./site/reference/cli
    cp -af ${module-docs}/* ./site/reference/
    cp -af ${clan-cli-docs}/* ./site/reference/cli/
    chmod +w ./site/reference/*

    echo "Generated API documentation in './site/reference/' "
  '';
}
