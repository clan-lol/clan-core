import * as v from "valibot";
import { TextInput } from "@/src/components/Form/TextInput";
import { Divider } from "@/src/components/Divider/Divider";
import { TextArea } from "@/src/components/Form/TextArea";
import { splitProps } from "solid-js";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import { tooltipText } from "@/src/components/Form";
import { useMachineContext } from "@/src/contexts/MachineContext";
import { MachineData } from "@/src/api/clan";

const schema = v.object({
  name: v.pipe(v.string(), v.readonly()),
  description: v.optional(v.string()),
  machineClass: v.pipe(v.picklist(["nixos", "darwin"]), v.readonly()),
});

type FieldNames = "name" | "description" | "machineClass";

export const SectionGeneral = () => {
  const machine = useMachineContext()!;

  const readOnly = (editing: boolean, name: FieldNames) => {
    if (!editing) {
      return true;
    }

    return machine.schema[name]?.readonly;
  };

  async function onSubmit(values: Partial<MachineData>): Promise<void> {
    // TODO: once the backend supports partial update, only pass in changed data
    await machine.updateData({ ...machine.data, ...values });
  }

  return (
    <SidebarSectionForm
      title="General"
      schema={schema}
      onSubmit={onSubmit}
      // FIXME: name is not editable, data shouldn't contain name
      // Make the name field just pure text
      initialValues={machine.data as MachineData & { name: string }}
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
                  machine.schema,
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
                  machine.schema,
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
                tooltip={tooltipText("description", machine.schema)}
                orientation="horizontal"
                autoResize={true}
                minRows={2}
                maxRows={4}
                input={{
                  ...input,
                  placeholder: "No description",
                }}
              />
            )}
          </Field>
        </div>
      )}
    </SidebarSectionForm>
  );
};
