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
    rev = "9b11879d63ac02b0df59960f47063aefc1baf176";
    hash = "sha256-oK2fKxCSonWs87s7BRdLO8GRm5MCfQNaJE7AoaH6K/c=";
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
