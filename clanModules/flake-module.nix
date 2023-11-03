{ self, lib, ... }: {
  flake.clanModules = {
    diskLayouts = lib.mapAttrs'
      (name: _: lib.nameValuePair (lib.removeSuffix ".nix" name) {
        imports = [
          self.inputs.disko.nixosModules.disko
          ./diskLayouts/${name}
        ];
      })
      (builtins.readDir ./diskLayouts);
    deltachat = ./deltachat.nix;
    xfce = ./xfce.nix;
  };
}
