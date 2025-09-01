import { BackButton, StepLayout } from "@/src/workflows/Steps";
import * as v from "valibot";
import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  createForm,
  setValue,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import {
  AddMachineSteps,
  AddMachineStoreType,
} from "@/src/workflows/AddMachine/AddMachine";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { MachineTags } from "@/src/components/Form/MachineTags";
import { Button } from "@/src/components/Button/Button";
import { useApiClient } from "@/src/hooks/ApiClient";
import { useClanURI } from "@/src/hooks/clan";

const TagsSchema = v.object({
  tags: v.array(v.string()),
});

type TagsForm = v.InferInput<typeof TagsSchema>;

export const StepTags = (props: { onDone: () => void }) => {
  const stepSignal = useStepper<AddMachineSteps>();
  const [store, set] = getStepStore<AddMachineStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<TagsForm>({
    validate: valiForm(TagsSchema),
    initialValues: store.tags,
  });

  const apiClient = useApiClient();
  const clanURI = useClanURI();

  const handleSubmit: SubmitHandler<TagsForm> = async (values, event) => {
    set("tags", (s) => ({
      ...s,
      ...values,
    }));

    const call = apiClient.fetch("create_machine", {
      opts: {
        clan_dir: {
          identifier: clanURI,
        },
        machine: {
          ...store.general,
          ...store.tags,
          deploy: store.deploy,
        },
      },
    });

    stepSignal.next();

    const result = await call.result;

    if (result.status == "error") {
      // setError(result.errors[0].message);
    }

    if (result.status == "success") {
      console.log("Machine creation was successful");
      if (store.general) {
        store.onCreated(store.general.name);
      }
    }
    props.onDone();
  };

  return (
    <Form onSubmit={handleSubmit} class="h-full">
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Fieldset>
              <Field name="tags" type="string[]">
                {(field, input) => (
                  <MachineTags
                    {...field}
                    required
                    orientation="horizontal"
                    defaultValue={field.value || []}
                    defaultOptions={[]}
                    onChange={(newVal) => {
                      // Workaround for now, until we manage to use native events
                      setValue(formStore, field.name, newVal);
                    }}
                  />
                )}
              </Field>
            </Fieldset>
          </div>
        }
        footer={
          <div class="flex justify-between">
            <BackButton />
            <Button hierarchy="primary" type="submit" endIcon="Flash">
              Create Machine
            </Button>
          </div>
        }
      />
    </Form>
  );
};
