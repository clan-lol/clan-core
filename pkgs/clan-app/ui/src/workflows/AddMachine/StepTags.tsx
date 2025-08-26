import { BackButton, NextButton, StepLayout } from "@/src/workflows/Steps";
import * as v from "valibot";
import { getStepStore, useStepper } from "@/src/hooks/stepper";
import { createForm, SubmitHandler, valiForm } from "@modular-forms/solid";
import {
  AddMachineSteps,
  AddMachineStoreType,
} from "@/src/workflows/AddMachine/AddMachine";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { MachineTags } from "@/src/components/Form/MachineTags";
import { Button } from "@/src/components/Button/Button";

const TagsSchema = v.object({
  tags: v.array(v.string()),
});

type TagsForm = v.InferInput<typeof TagsSchema>;

export const StepTags = () => {
  const stepSignal = useStepper<AddMachineSteps>();
  const [store, set] = getStepStore<AddMachineStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<TagsForm>({
    validate: valiForm(TagsSchema),
    initialValues: store.tags,
  });

  const handleSubmit: SubmitHandler<TagsForm> = (values, event) => {
    set("tags", (s) => ({
      ...s,
      ...values,
    }));

    stepSignal.next();
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
                    defaultValue={field.value}
                    defaultOptions={[]}
                    input={input}
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
