import * as v from "valibot";
import { Show, splitProps } from "solid-js";
import { Machine } from "@/src/hooks/queries";
import { callApi } from "@/src/hooks/api";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import { pick } from "@/src/util";
import { UseQueryResult } from "@tanstack/solid-query";
import { MachineTags } from "@/src/components/Form/MachineTags";

const schema = v.object({
  tags: v.pipe(v.optional(v.array(v.string()))),
});

type FormValues = v.InferInput<typeof schema>;

export interface SectionTags {
  clanURI: string;
  machineName: string;
  machineQuery: UseQueryResult<Machine>;
}

export const SectionTags = (props: SectionTags) => {
  const machineQuery = props.machineQuery;

  const initialValues = () => {
    if (!machineQuery.isSuccess) {
      return {};
    }

    return pick(machineQuery.data, ["tags"]) satisfies FormValues;
  };

  const onSubmit = async (values: FormValues) => {
    console.log("submitting tags", values);
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
        title="Tags"
        schema={schema}
        onSubmit={onSubmit}
        initialValues={initialValues()}
      >
        {({ editing, Field }) => (
          <div class="flex flex-col gap-3">
            <Field name="tags" type="string[]">
              {(field, input) => (
                <MachineTags
                  {...splitProps(field, ["value"])[1]}
                  size="s"
                  inverted
                  required
                  readOnly={!editing}
                  orientation="horizontal"
                  defaultValue={field.value}
                  input={input}
                />
              )}
            </Field>
          </div>
        )}
      </SidebarSectionForm>
    </Show>
  );
};
