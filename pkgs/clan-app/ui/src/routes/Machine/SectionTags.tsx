import * as v from "valibot";
import { Show, splitProps } from "solid-js";
import { MachineDetail } from "@/src/hooks/queries";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import { pick } from "@/src/util";
import { UseQueryResult } from "@tanstack/solid-query";
import { MachineTags } from "@/src/components/Form/MachineTags";
import { setValue } from "@modular-forms/solid";

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

  const options = () => {
    if (!machineQuery.isSuccess) {
      return [];
    }

    // these are static values or values which have been configured in nix and
    // cannot be modified in the UI
    const readonlyOptions =
      machineQuery.data.fieldsSchema.tags?.readonly_members || [];

    // filter out the read-only options from the superset of clan-wide options
    const readonlySet = new Set(readonlyOptions);

    const defaultOptions = (machineQuery.data.tags.options || []).filter(
      (tag) => !readonlySet.has(tag),
    );

    return [defaultOptions, readonlyOptions];
  };

  return (
    <Show when={machineQuery.isSuccess}>
      <SidebarSectionForm
        title="Tags"
        schema={schema}
        onSubmit={props.onSubmit}
        initialValues={initialValues()}
      >
        {({ editing, Field, formStore }) => (
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
                  defaultOptions={options()[0]}
                  readonlyOptions={options()[1]}
                  onChange={(newVal) => {
                    // Workaround for now, until we manage to use native events
                    setValue(formStore, field.name, newVal);
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
