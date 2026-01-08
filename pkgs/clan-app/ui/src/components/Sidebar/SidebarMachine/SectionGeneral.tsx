import * as v from "valibot";
import { TextInput } from "@/src/components/Form/TextInput";
import { Divider } from "@/src/components/Divider/Divider";
import { TextArea } from "@/src/components/Form/TextArea";
import { splitProps } from "solid-js";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import { tooltipText } from "@/src/components/Form";
import { MachineData, useMachineContext } from "@/src/models";

const schema = v.object({
  name: v.pipe(v.string(), v.readonly()),
  description: v.optional(v.union([v.string(), v.null()])),
  machineClass: v.pipe(v.picklist(["nixos", "darwin"]), v.readonly()),
});

type FieldNames = "name" | "description" | "machineClass";

export const SectionGeneral = () => {
  const [machine, { updateMachineData }] = useMachineContext();

  const readOnly = (editing: boolean, name: FieldNames) => {
    if (!editing) {
      return true;
    }

    return machine().dataSchema[name]?.readonly;
  };

  async function onSubmit(values: Partial<MachineData>): Promise<void> {
    await updateMachineData(values);
  }

  return (
    <SidebarSectionForm
      title="General"
      schema={schema}
      onSubmit={onSubmit}
      // FIXME: name is not editable, data shouldn't contain name
      // Make the name field just pure text
      initialValues={machine().data}
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
                  machine().dataSchema,
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
                  machine().dataSchema,
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
                tooltip={tooltipText("description", machine().dataSchema)}
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
