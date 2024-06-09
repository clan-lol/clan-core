{ self, ... }:
{
  perSystem =
    { pkgs, ... }:
    let
      nfpmConfig = pkgs.writeText "clan-nfpm-config.yaml" (
        builtins.toJSON {
          name = "clan-gui-installer";
          version = "0.0.${self.lastModifiedDate}";
          maintainer = "clan core team";
          homepage = "https://clan.lol";
          description = "Peer-to-Peer self-hosting made easy for developers";
          license = "MIT";
          contents = [
            {
              src = "${./gui-installer.sh}";
              dst = "/usr/bin/clan-app";
            }
          ];
        }
      );
      installerFor =
        packager:
        pkgs.runCommand "gui-installer" { } ''
          mkdir build
          cd build
          ${pkgs.nfpm}/bin/nfpm package --config ${nfpmConfig} --packager ${packager}
          mkdir $out
          mv * $out/
        '';
    in
    {
      packages.gui-installer-apk = installerFor "apk";
      packages.gui-installer-archlinux = installerFor "archlinux";
      packages.gui-installer-deb = installerFor "deb";
      packages.gui-installer-rpm = installerFor "rpm";
    };
}
