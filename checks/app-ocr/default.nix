{ self, pkgs, ... }:
{
  name = "app-ocr-smoke-test";

  enableOCR = true;

  nodes = {
    wayland =
      { modulesPath, ... }:
      {
        imports = [ (modulesPath + "/../tests/common/wayland-cage.nix") ];
        services.cage.program = "${self.packages.${pkgs.system}.clan-app}/bin/clan-app";
        virtualisation.memorySize = 2047;
        # TODO: get rid of this and fix debus-proxy error instead
        services.cage.environment.WEBKIT_DISABLE_SANDBOX_THIS_IS_DANGEROUS = "1";
      };
    xorg =
      { pkgs, modulesPath, ... }:
      {
        imports = [
          (modulesPath + "/../tests/common/user-account.nix")
          (modulesPath + "/../tests/common/x11.nix")
        ];
        virtualisation.memorySize = 2047;
        services.xserver.enable = true;
        services.xserver.displayManager.sessionCommands = "${
          self.packages.${pkgs.system}.clan-app
        }/bin/clan-app";
        test-support.displayManager.auto.user = "alice";
      };
  };
  testScript = ''
    start_all()

    wayland.wait_for_unit('graphical.target')
    xorg.wait_for_unit('graphical.target')

    wayland.wait_for_text('Welcome to Clan')
    xorg.wait_for_text('Welcome to Clan')
  '';
}
