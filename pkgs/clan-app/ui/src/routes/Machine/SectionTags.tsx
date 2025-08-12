import * as v from "valibot";
import { Show, splitProps } from "solid-js";
import { MachineDetail } from "@/src/hooks/queries";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import { pick } from "@/src/util";
import { UseQueryResult } from "@tanstack/solid-query";
import { MachineTag, MachineTags } from "@/src/components/Form/MachineTags";
import { machineNameParam } from "@/src/hooks/clan";

const schema = v.object({
  tags: v.pipe(v.optional(v.array(v.string()))),
});

type FormValues = v.InferInput<typeof schema>;

export interface SectionTags {
  clanURI: string;
  machineName: string;
  onSubmit: (values: FormValues) => Promise<void>;
  machineQuery: UseQueryResult<MachineDetail>;
}

export const SectionTags = (props: SectionTags) => {
  const machineQuery = props.machineQuery;

  const initialValues = () => {
    if (!machineQuery.isSuccess) {
      return {};
    }

    return pick(machineQuery.data.machine, ["tags"]) satisfies FormValues;
  };

  const readonlyOptions = () => {
    if (!machineQuery.isSuccess) {
      return [];
    }

    const result: string[] = ["all"];

    if (machineQuery.data.machine.machineClass) {
      result.push(machineQuery.data.machine.machineClass);
    }

    return result;
  };

  const defaultOptions = () => {
    if (!machineQuery.isSuccess) {
      return [];
    }

    return machineQuery.data.tags?.options ?? [];
  };

  return (
    <Show when={machineQuery.isSuccess}>
      <SidebarSectionForm
        title="Tags"
        schema={schema}
        onSubmit={props.onSubmit}
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
                  defaultOptions={defaultOptions()}
                  readonlyOptions={readonlyOptions()}
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
