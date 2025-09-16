{ pkgs, ... }:
{
  clan.core.vars.generators.syncthing = {
    files.key = { };
    files.cert = { };
    files.api = { };
    files.id.secret = false;
    runtimeInputs = [
      pkgs.coreutils
      pkgs.gnugrep
      pkgs.syncthing
    ];
    script = ''
      export TMPDIR=/tmp
      TEMPORARY=$(mktemp -d)
      syncthing generate --config "$out" --data "$TEMPORARY"
      mv "$out"/key.pem "$out"/key
      mv "$out"/cert.pem "$out"/cert
      cat "$out"/config.xml | grep -oP '(?<=<device id=")[^"]+' | uniq > "$out"/id
      cat "$out"/config.xml | grep -oP '<apikey>\K[^<]+' | uniq > "$out"/api
    '';
  };
}
