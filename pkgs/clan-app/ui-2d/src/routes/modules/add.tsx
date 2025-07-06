import { BackButton } from "@/src/components/BackButton";
import { createModulesQuery, machinesQuery } from "@/src/queries";
import { useParams } from "@solidjs/router";
import { For, Match, Switch } from "solid-js";
import { ModuleInfo } from "./list";
import { createForm, FieldValues, SubmitHandler } from "@modular-forms/solid";
import { SelectInput } from "@/src/Form/fields/Select";
import { useClanContext } from "@/src/contexts/clan";

export const ModuleDetails = () => {
  const params = useParams();
  const { activeClanURI } = useClanContext();
  const modulesQuery = createModulesQuery(activeClanURI());

  return (
    <div class="p-1">
      <BackButton />
      <div class="p-2">
        <h3 class="text-2xl">{params.id}</h3>
        {/* <Switch>
          <Match when={modulesQuery.data?.find((i) => i[0] === params.id)}>
            {(d) => <AddModule data={d()[1]} id={d()[0]} />}
          </Match>
        </Switch> */}
      </div>
    </div>
  );
};

interface AddModuleProps {
  data: ModuleInfo;
  id: string;
}

const AddModule = (props: AddModuleProps) => {
  const { activeClanURI } = useClanContext();
  const machines = machinesQuery(activeClanURI());
  return (
    <div>
      <div>Add to your clan</div>
      <Switch fallback="loading">Removed</Switch>
    </div>
  );
};

interface RoleFormData extends FieldValues {
  machines: string[];
  tags: string[];
  test: string;
}

interface RoleFormProps {
  avilableTags: string[];
  availableMachines: string[];
}
const RoleForm = (props: RoleFormProps) => {
  const [formStore, { Field, Form }] = createForm<RoleFormData>({
    // initialValues: {
    //   machines: ["hugo", "bruno"],
    //   tags: ["network", "backup"],
    // },
  });

  const handleSubmit: SubmitHandler<RoleFormData> = (values) => {
    console.log(values);
  };
  return (
    <Form onSubmit={handleSubmit}>
      <Field name="machines" type="string[]">
        {(field, fieldProps) => (
          <SelectInput
            error={field.error}
            label={"Machines"}
            value={field.value || []}
            options={props.availableMachines.map((o) => ({
              value: o,
              label: o,
            }))}
            multiple
            selectProps={fieldProps}
          />
        )}
      </Field>
      <Field name="tags" type="string[]">
        {(field, fieldProps) => (
          <SelectInput
            error={field.error}
            label={"Tags"}
            value={field.value || []}
            options={props.avilableTags.map((o) => ({
              value: o,
              label: o,
            }))}
            multiple
            selectProps={fieldProps}
          />
        )}
      </Field>
    </Form>
  );
};
