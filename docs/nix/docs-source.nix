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
    mkdir docs
    pushd docs

    cp -r ${../site} ./site
    chmod -R +w ./site

    cp -r ${../code-examples} ./code-examples
    chmod -R +w ./code-examples

    cp -af ${module-docs}/services/* ./site/services/

    mkdir -p ./site/reference/cli
    cp -af ${module-docs}/reference/* ./site/reference/
    cp -af ${clan-cli-docs}/* ./site/reference/cli/

    mkdir -p $out
    cp -r . $out
    chmod -R +w $out
  ''
