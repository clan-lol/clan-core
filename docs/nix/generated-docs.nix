{
  module-docs,
  clan-cli-docs,
  runCommand,
}:
runCommand "generated-docs" { } ''
  mkdir -p $out

  cp -R ${module-docs}/services $out/services
  cp -R ${module-docs}/reference $out/reference
  chmod +w $out/reference
  cp -R ${clan-cli-docs} $out/reference/cli
''
