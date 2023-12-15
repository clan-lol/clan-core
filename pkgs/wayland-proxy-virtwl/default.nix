{ wayland-proxy-virtwl, fetchFromGitHub, libdrm, ocaml-ng }:
let
  ocaml-wayland = ocaml-ng.ocamlPackages_5_0.wayland.overrideAttrs (_old: {
    src = fetchFromGitHub {
      owner = "Mic92";
      repo = "ocaml-wayland";
      rev = "f6910aa5b626fa582cc000d4fe7b50182d11b439";
      hash = "sha256-cg3HLezWTxWoYWSrirOV12gv1CRz1gMIOT7j3j3v5EA=";
    };
  });
in
wayland-proxy-virtwl.overrideAttrs (_old: {
  src = fetchFromGitHub {
    owner = "Mic92";
    repo = "wayland-proxy-virtwl";
    rev = "652fca9d4e006a2bdeba920dfaf53190c5373a7d";
    hash = "sha256-VgpqxjHgueK9eQSX987PF0KvscpzkScOzFkW3haYCOw=";
  };
  buildInputs = [ libdrm ] ++ (with ocaml-ng.ocamlPackages_5_0; [
    ocaml-wayland
    dune-configurator
    eio_main
    ppx_cstruct
    cmdliner
    logs
    ppx_cstruct
  ]);
})
