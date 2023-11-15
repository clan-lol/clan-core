{ writeShellApplication
, bash
, curl
}:
writeShellApplication {
  name = "pending-reviews";
  runtimeInputs = [
    bash
    curl
  ];
  text = builtins.readFile ./script.sh;
}
