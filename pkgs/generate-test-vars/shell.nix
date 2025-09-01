{ pkgs, generate-test-vars }:
pkgs.mkShell {
  inputsFrom = [
    generate-test-vars
  ];
  # packages = with pkgs; [ python3 ];
}
