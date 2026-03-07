{
  module-docs,
  clan-cli-docs,
  runCommand,
  python314,
}:
runCommand "docs-markdowns"
  {
    nativeBuildInputs = [ python314 ];
  }
  ''
    mkdir $out
    cp -LR ${../.}/site/* $out
    chmod +w $out/static
    rm -r $out/{index.md,api.md,static}
    chmod +w $out/services
    cp -LR ${module-docs}/services/* $out/services
    chmod +w $out/reference
    cp -LR ${module-docs}/reference/* $out/reference
    mkdir -p $out/reference/cli
    cp -LR ${clan-cli-docs}/* $out/reference/cli
    chmod -R +w $out
    python3 ${../.}/migrate.py $out
  ''
