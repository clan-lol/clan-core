{
  module-docs,
  clan-cli-docs,
  runCommand,
}:
runCommand "docs-markdowns" { } ''
  mkdir $out
  cp -Lr ${../.}/site/* $out
  chmod +w $out/services
  cp -r ${module-docs}/services/* $out/services
  chmod +w $out/reference
  cp -r ${module-docs}/reference/* $out/reference
  chmod -R +w $out/reference/cli
  cp -r ${clan-cli-docs}/* $out/reference/cli
''
