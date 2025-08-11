import * as v from "valibot";
import { TextInput } from "@/src/components/Form/TextInput";
import { Divider } from "@/src/components/Divider/Divider";
import { TextArea } from "@/src/components/Form/TextArea";
import { Show, splitProps } from "solid-js";
import { Machine } from "@/src/hooks/queries";
import { callApi } from "@/src/hooks/api";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import { pick } from "@/src/util";
import { UseQueryResult } from "@tanstack/solid-query";

const schema = v.object({
  name: v.pipe(v.optional(v.string()), v.readonly()),
  description: v.nullish(v.string()),
  machineClass: v.optional(v.picklist(["nixos", "darwin"])),
});

type FormValues = v.InferInput<typeof schema>;

export interface SectionGeneralProps {
  clanURI: string;
  machineName: string;
  machineQuery: UseQueryResult<Machine>;
}

export const SectionGeneral = (props: SectionGeneralProps) => {
  const machineQuery = props.machineQuery;

  const initialValues = () => {
    if (!machineQuery.isSuccess) {
      return {};
    }

    return pick(machineQuery.data, [
      "name",
      "description",
      "machineClass",
    ]) satisfies FormValues;
  };

  const onSubmit = async (values: FormValues) => {
    const call = callApi("set_machine", {
      machine: {
        name: props.machineName,
        flake: {
          identifier: props.clanURI,
        },
      },
      update: {
        ...machineQuery.data,
        ...values,
      },
    });

    const result = await call.result;
    if (result.status === "error") {
      throw new Error(result.errors[0].message);
    }

    // refresh the query
    await machineQuery.refetch();
  };

  return (
    <Show when={machineQuery.isSuccess}>
      <SidebarSectionForm
        title="General"
        schema={schema}
        onSubmit={onSubmit}
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
                  required
                  readOnly
                  orientation="horizontal"
                  input={input}
                  tooltip={
                    "A unique identifier for this machine. It cannot be changed."
                  }
                />
              )}
            </Field>
            <Divider />
            <Field name="machineClass">
              {(field, input) => (
                <TextInput
                  {...field}
                  value={field.value}
                  size="s"
                  inverted
                  label="Platform"
                  required
                  readOnly
                  orientation="horizontal"
                  input={input}
                  tooltip={
                    "The target platform for this machine. It cannot be changed. It is set in the installer."
                  }
                />
              )}
            </Field>
            <Divider />
            <Field name="description">
              {(field, input) => (
                <TextArea
                  {...splitProps(field, ["value"])[1]}
                  defaultValue={field.value ?? ""}
                  size="s"
                  label="Description"
                  inverted
                  readOnly={!editing}
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
