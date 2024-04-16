{
  docs,
  pkgs,
  module-docs,
  ...
}:
pkgs.mkShell {
  inputsFrom = [ docs ];
  shellHook = ''
    mkdir -p ./site/reference
    cp -af ${module-docs}/* ./site/reference/
    chmod +w ./site/reference/*

    echo "Generated API documentation in './site/reference/' "
  '';
}
