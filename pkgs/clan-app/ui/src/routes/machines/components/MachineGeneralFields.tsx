import {
  Field,
  FieldValues,
  FormStore,
  ResponseData,
  FieldStore,
  FieldElementProps,
  FieldPath,
} from "@modular-forms/solid";
import { TextInput } from "@/src/Form/fields/TextInput";
import { Typography } from "@/src/components/Typography";
import { TagList } from "@/src/components/TagList/TagList";
import Fieldset from "@/src/Form/fieldset";
import { SuccessData } from "@/src/api";

type MachineData = SuccessData<"get_machine_details">;

interface MachineGeneralFieldsProps {
  formStore: FormStore<MachineData, ResponseData>;
}

export function MachineGeneralFields(props: MachineGeneralFieldsProps) {
  const { formStore } = props;

  return (
    <Fieldset legend="General">
      <Field name="machine.name" of={formStore}>
        {(
          field: FieldStore<MachineData, "machine.name">,
          fieldProps: FieldElementProps<MachineData, "machine.name">,
        ) => {
          return (
            <TextInput
              inputProps={fieldProps}
              label="Name"
              value={field.value ?? ""}
              error={field.error}
              class="col-span-2"
              required
            />
          );
        }}
      </Field>

      <Field name="machine.description" of={formStore}>
        {(
          field: FieldStore<MachineData, "machine.description">,
          fieldProps: FieldElementProps<MachineData, "machine.description">,
        ) => (
          <TextInput
            inputProps={fieldProps}
            label="Description"
            value={field.value ?? ""}
            error={field.error}
            class="col-span-2"
          />
        )}
      </Field>

      <Field name="machine.tags" of={formStore} type="string[]">
        {(
          field: FieldStore<MachineData, "machine.tags">,
          fieldProps: FieldElementProps<MachineData, "machine.tags">,
        ) => (
          <div class="grid grid-cols-10 items-center">
            <Typography
              hierarchy="label"
              size="default"
              weight="bold"
              class="col-span-5"
            >
              Tags{" "}
            </Typography>
            <div class="col-span-5 justify-self-end">
              <TagList values={[...(field.value || [])].sort()} />
            </div>
          </div>
        )}
      </Field>
    </Fieldset>
  );
}
