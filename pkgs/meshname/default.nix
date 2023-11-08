{ lib
, buildGoModule
, fetchFromGitHub
}:

buildGoModule {
  pname = "meshname";
  version = "unstable-2023-11-08";

  src = fetchFromGitHub {
    owner = "Mic92";
    repo = "meshname";
    rev = "b3c0ec1cafcb91ae7801b139777ff5ffad4c8fed";
    hash = "sha256-uPon66nc5vw2QbbrNPXcCkO7T0l0foYovyR1adL9JBg=";
  };

  subPackages = [ "cmd/meshnamed" ];

  vendorHash = "sha256-kiNxB2R3Z6Z/Resr3r4jKCImVhyoOY55dEiV+JRUjDk=";

  ldflags = [ "-s" "-w" ];

  meta = with lib; {
    description = "Meshname, a universal naming system for all IPv6-based mesh networks, including CJDNS and Yggdrasil";
    homepage = "https://github.com/Mic92/meshname";
    license = licenses.mit;
    maintainers = with maintainers; [ mic92 ];
    mainProgram = "meshnamed";
  };
}
