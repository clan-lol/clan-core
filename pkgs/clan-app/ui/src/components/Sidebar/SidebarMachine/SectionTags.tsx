import * as v from "valibot";
import { splitProps } from "solid-js";
import { SidebarSectionForm } from "@/src/components/Sidebar/SidebarSectionForm";
import { MachineTags } from "@/src/components/Form/MachineTags";
import { setValue } from "@modular-forms/solid";
import { MachineData } from "@/src/api/clan";
import { useMachineContext } from "@/src/contexts/MachineContext";

const schema = v.object({
  tags: v.pipe(v.optional(v.array(v.string()))),
});

export const SectionTags = () => {
  const machine = useMachineContext()!;

  // we have to update the whole machine model rather than just the sub fields that were changed
  // for that reason we pass in this common submit handler to each machine sub section
  const onSubmit = async (values: Partial<MachineData>) => {
    await machine.updateData({ ...machine.data, ...values });
  };

  const readonlyTags = () => machine.schema?.tags?.readonly_members || [];
  const defaultTags = () =>
    (machine.clan.tags()?.regular || []).filter(
      (tag) => !readonlyTags().includes(tag),
    );

  // TODO: this should be a form solely for tags
  return (
    <SidebarSectionForm
      title="Tags"
      schema={schema}
      onSubmit={onSubmit}
      initialValues={{
        tags: machine.data.tags,
      }}
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
                defaultOptions={defaultTags()}
                readonlyOptions={readonlyTags()}
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
  );
};
