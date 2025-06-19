import {
  Field,
  FormStore,
  ResponseData,
  FieldStore,
  FieldElementProps,
} from "@modular-forms/solid";
import { Typography } from "@/src/components/Typography";
import { InputLabel } from "@/src/components/inputBase";
import { FieldLayout } from "@/src/Form/fields/layout";
import Fieldset from "@/src/Form/fieldset";
import { SuccessData } from "@/src/api";

type MachineData = SuccessData<"get_machine_details">;

interface MachineHardwareInfoProps {
  formStore: FormStore<MachineData, ResponseData>;
}
export function MachineHardwareInfo(props: MachineHardwareInfoProps) {
  const { formStore } = props;

  return (
    <Typography hierarchy={"body"} size={"s"}>
      <Fieldset>
        <Field name="hw_config" of={formStore}>
          {(
            field: FieldStore<MachineData, "hw_config">,
            fieldProps: FieldElementProps<MachineData, "hw_config">,
          ) => (
            <FieldLayout
              label={<InputLabel>Hardware Configuration</InputLabel>}
              field={<span>{field.value || "None"}</span>}
            />
          )}
        </Field>
        <hr />
        <Field name="disk_schema.schema_name" of={formStore}>
          {(
            field: FieldStore<MachineData, "disk_schema.schema_name">,
            fieldProps: FieldElementProps<
              MachineData,
              "disk_schema.schema_name"
            >,
          ) => (
            <FieldLayout
              label={<InputLabel>Disk schema</InputLabel>}
              field={<span>{field.value || "None"}</span>}
            />
          )}
        </Field>
      </Fieldset>
    </Typography>
  );
}
