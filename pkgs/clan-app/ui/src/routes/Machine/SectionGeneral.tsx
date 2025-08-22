import * as v from "valibot";
import { TextInput } from "@/src/components/Form/TextInput";
import { Divider } from "@/src/components/Divider/Divider";
import { TextArea } from "@/src/components/Form/TextArea";
import { Show, splitProps } from "solid-js";
import { MachineDetail } from "@/src/hooks/queries";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import { pick } from "@/src/util";
import { UseQueryResult } from "@tanstack/solid-query";
import { tooltipText } from "@/src/components/Form";

const schema = v.object({
  name: v.pipe(v.optional(v.string()), v.readonly()),
  description: v.nullish(v.string()),
  machineClass: v.pipe(
    v.optional(v.picklist(["nixos", "darwin"])),
    v.readonly(),
  ),
});

type FieldNames = "name" | "description" | "machineClass";

type FormValues = v.InferInput<typeof schema>;

export interface SectionGeneralProps {
  clanURI: string;
  machineName: string;
  onSubmit: (values: FormValues) => Promise<void>;
  machineQuery: UseQueryResult<MachineDetail>;
}

export const SectionGeneral = (props: SectionGeneralProps) => {
  const machineQuery = props.machineQuery;

  const initialValues = () => {
    if (!machineQuery.isSuccess) {
      return {};
    }

    return pick(machineQuery.data.machine, [
      "name",
      "description",
      "machineClass",
    ]) satisfies FormValues;
  };

  const fieldsSchema = () => {
    if (!machineQuery.isSuccess) {
      return undefined;
    }

    return machineQuery.data.fieldsSchema;
  };

  const readOnly = (editing: boolean, name: FieldNames) => {
    if (!editing) {
      return true;
    }

    return fieldsSchema()?.[name]?.readonly ?? false;
  };

  return (
    <Show when={machineQuery.isSuccess}>
      <SidebarSectionForm
        title="General"
        schema={schema}
        onSubmit={props.onSubmit}
        initialValues={initialValues()}
      >
        {({ editing, Field }) => (
          <div class="flex flex-col gap-3">
            <Field name="name">
              {(field, input) => (
                <TextInput
                  {...field}
                  value={field.value}
                  size="s"
                  inverted
                  label="Name"
                  labelWeight="normal"
                  required
                  readOnly={readOnly(editing, "name")}
                  orientation="horizontal"
                  input={input}
                  tooltip={tooltipText(
                    "name",
                    fieldsSchema()!,
                    "A unique identifier for this machine",
                  )}
                />
              )}
            </Field>
            <Divider inverted />
            <Field name="machineClass">
              {(field, input) => (
                <TextInput
                  {...field}
                  value={field.value}
                  size="s"
                  inverted
                  label="Platform"
                  labelWeight="normal"
                  required
                  readOnly={readOnly(editing, "machineClass")}
                  orientation="horizontal"
                  input={input}
                  tooltip={tooltipText(
                    "machineClass",
                    fieldsSchema()!,
                    "The target platform for this machine",
                  )}
                />
              )}
            </Field>
            <Divider inverted />
            <Field name="description">
              {(field, input) => (
                <TextArea
                  {...splitProps(field, ["value"])[1]}
                  defaultValue={field.value ?? ""}
                  size="s"
                  label="Description"
                  labelWeight="normal"
                  inverted
                  readOnly={readOnly(editing, "description")}
                  tooltip={tooltipText("description", fieldsSchema()!)}
                  orientation="horizontal"
                  input={{
                    ...input,
                    autoResize: true,
                    minRows: 2,
                    maxRows: 4,
                    placeholder: "No description",
                  }}
                />
              )}
            </Field>
          </div>
        )}
      </SidebarSectionForm>
    </Show>
  );
};
