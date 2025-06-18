import { FieldValues } from "@modular-forms/solid";
import { HardwareValues } from "./install/hardware-step";
import { DiskValues } from "./install/disk-step";
import { VarsValues } from "./install/vars-step";

export interface AllStepsValues extends FieldValues {
  "1": HardwareValues;
  "2": DiskValues;
  "3": VarsValues;
  "4": NonNullable<unknown>;
  sshKey?: File;
}
