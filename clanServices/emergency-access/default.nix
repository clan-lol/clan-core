{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/emergency-access";
  manifest.description = "Set recovery password for emergency access to machine to debug boot issues";
  manifest.categories = [ "System" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {
    description = "Placeholder role to apply the emergency-access service";
    perInstance = {
      nixosModule =
        { config, pkgs, ... }:
        {
          boot.initrd.systemd.emergencyAccess =
            config.clan.core.vars.generators.emergency-access.files.password-hash.value;

          clan.core.vars.generators.emergency-access = {
            runtimeInputs = [
              pkgs.coreutils
              pkgs.mkpasswd
              pkgs.xkcdpass
            ];
            files.password.deploy = false;
            files.password-hash.secret = false;

            script = ''
              xkcdpass --numwords 4 --delimiter - --count 1 | tr -d "\n" > $out/password
              mkpasswd -s -m sha-512 < $out/password | tr -d "\n" > $out/password-hash
            '';
          };
        };
    };
  };
}
