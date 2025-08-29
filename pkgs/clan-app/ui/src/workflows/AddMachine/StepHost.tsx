import { BackButton, NextButton, StepLayout } from "@/src/workflows/Steps";
import * as v from "valibot";
import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  createForm,
  getError,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import {
  AddMachineSteps,
  AddMachineStoreType,
} from "@/src/workflows/AddMachine/AddMachine";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { TextInput } from "@/src/components/Form/TextInput";
import { Divider } from "@/src/components/Divider/Divider";
import { TextArea } from "@/src/components/Form/TextArea";

const HostSchema = v.object({
  targetHost: v.pipe(v.string("Name must be a string")),
});

type HostForm = v.InferInput<typeof HostSchema>;

export const StepHost = () => {
  const stepSignal = useStepper<AddMachineSteps>();
  const [store, set] = getStepStore<AddMachineStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<HostForm>({
    validate: valiForm(HostSchema),
    initialValues: store.deploy,
  });

  const handleSubmit: SubmitHandler<HostForm> = (values, event) => {
    set("deploy", (s) => ({
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
              <Field name="targetHost">
                {(field, input) => (
                  <TextInput
                    {...field}
                    value={field.value}
                    label="Target"
                    required
                    orientation="horizontal"
                    input={{
                      ...input,
                      placeholder: "root@flashinstaller.local",
                    }}
                    validationState={
                      getError(formStore, "targetHost") ? "invalid" : "valid"
                    }
                  />
                )}
              </Field>
            </Fieldset>
          </div>
        }
        footer={
          <div class="flex justify-between">
            <BackButton />
            <NextButton type="submit" />
          </div>
        }
      />
    </Form>
  );
};
