{
  perSystem = {
    lib,
    pkgs,
    self',
    ...
  }: {
    devShells.default = pkgs.mkShell {
      packages = [
        pkgs.tea
        self'.packages.tea-create-pr
      ];
    };
}
