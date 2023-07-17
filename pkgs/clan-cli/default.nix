{ symlinkJoin
, writers
}:
symlinkJoin {
  name = "clan";
  paths = [
    (writers.writePython3Bin "clan" {} ./clan.py)
    (writers.writePython3Bin "clan-admin" { flakeIgnore = [ "E501" ]; } ./clan-admin.py)
  ];
}
