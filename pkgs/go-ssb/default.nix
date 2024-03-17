{
  lib,
  buildGoModule,
  fetchFromGitHub,
}:
buildGoModule rec {
  pname = "go-ssb";
  version = "0.2.1";

  src = fetchFromGitHub {
    owner = "ssbc";
    repo = "go-ssb";
    #rev = "v${version}";
    rev = "d6db27d1852d5edff9c7e07d2a3419fe6b11a8db";
    hash = "sha256-SewaIDNVrODWGxdvJjIg4oTdfGy8THNMlgv48KX8okE=";
  };

  vendorHash = "sha256-ZytuWFre7Cz6Qt01tLQoPEuNzDIyoC938OkdIrU8nZo=";

  ldflags = [
    "-s"
    "-w"
  ];

  # take very long
  doCheck = false;

  meta = with lib; {
    description = "Go implementation of ssb (work in progress)";
    homepage = "https://github.com/ssbc/go-ssb";
    license = licenses.mit;
    maintainers = with maintainers; [ ];
  };
}
