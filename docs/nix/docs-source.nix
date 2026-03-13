{
  module-docs,
  clan-cli-docs,
  runCommand,
  python314,
}:
runCommand "docs-source"
  {
    nativeBuildInputs = [ python314 ];
  }
  ''
    mkdir $out
    mkdir -p $out/reference/cli
    mkdir -p $out/services

    cp -LR ${../.}/site/* $out
    cp -LR ${module-docs}/services/* $out/services
    cp -LR ${module-docs}/reference/* $out/reference
    cp -LR ${clan-cli-docs}/* $out/reference/cli

    chmod -R +w $out
    python3 ${../.}/migrate.py $out
  ''
