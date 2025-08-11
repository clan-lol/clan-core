{
  lib,
  rustPlatform,
  fetchFromGitHub,
}:

rustPlatform.buildRustPackage {
  pname = "zt-tcp-relay";
  version = "unstable-2025-07-03";

  src = fetchFromGitHub {
    owner = "alexander-akhmetov";
    repo = "zt-tcp-relay";
    rev = "f6300870efc63a4dd06ed9b40a61a389de606bf5";
    hash = "sha256-yXCSE0I1u34doQ5PJ8kK6BabopVp5404R5kiJ6lGRa4=";
  };

  cargoHash = "sha256-8RCiGi/w0Qjmfppe236q2ojVbYo/jWIa7j6Nrz8GRiQ=";

  meta = with lib; {
    description = "ZeroTier One TCP relay";
    homepage = "https://github.com/alexander-akhmetov/zt-tcp-relay";
    license = licenses.mit;
    maintainers = with maintainers; [ mic92 ];
    mainProgram = "zt-tcp-relay";
  };
}
