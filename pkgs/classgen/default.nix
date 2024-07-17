{ writers }: writers.writePython3Bin "classgen" { flakeIgnore = [ "E501" ]; } ./main.py
