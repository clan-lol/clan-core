import { NextButton, StepLayout } from "@/src/workflows/Steps";
import * as v from "valibot";
import { value } from "valibot";
import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  clearError,
  createForm,
  getError,
  getErrors,
  setError,
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
import { Select } from "@/src/components/Select/Select";
import { Show } from "solid-js";
import { Alert } from "@/src/components/Alert/Alert";
import { useMachinesQuery } from "@/src/hooks/queries";
import { useClanURI } from "@/src/hooks/clan";

const PlatformOptions = [
  { label: "NixOS", value: "nixos" },
  { label: "Darwin", value: "darwin" },
];

const GeneralSchema = v.object({
  name: v.pipe(
    v.string("Name must be a string"),
    v.nonEmpty("Please enter a machine name"),
    v.regex(
      new RegExp(/^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$/),
      "Name must be a valid hostname e.g. alphanumeric characters and - only",
    ),
  ),
  description: v.optional(v.string("Description must be a string")),
  machineClass: v.pipe(v.string(), v.nonEmpty()),
});

type GeneralForm = v.InferInput<typeof GeneralSchema>;

export const StepGeneral = () => {
  const stepSignal = useStepper<AddMachineSteps>();
  const [store, set] = getStepStore<AddMachineStoreType>(stepSignal);

  const clanURI = useClanURI();
  const machines = useMachinesQuery(clanURI);

  const machineNames = () => {
    if (!machines.isSuccess) {
      return [];
    }

    return Object.keys(machines.data || {});
  }

  const [formStore, { Form, Field }] = createForm<GeneralForm>({
    validate: valiForm(GeneralSchema),
    initialValues: { machineClass: "nixos", ...store.general },
  });

  const handleSubmit: SubmitHandler<GeneralForm> = (values, event) => {
    if (machineNames().includes(values.name)) {
      setError(formStore, "name", `A machine named '${values.name}' already exists. Please choose a different one.`)
      return
    }

    clearError(formStore, "name");

    set("general", (s) => ({
      ...s,
      ...values,
    }));

    stepSignal.next();
  };

  const formError = () => {
    const errors = getErrors(formStore);
    return errors.name || errors.description || errors.machineClass;
  };

  return (
    <Form onSubmit={handleSubmit} class="h-full">
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Show when={formError()}>
              <Alert
                type="error"
                icon="WarningFilled"
                title="Error"
                description={formError()}
              />
            </Show>
            <Fieldset>
              <Field name="name">
                {(field, input) => (
                  <TextInput
                    {...field}
                    value={field.value}
                    label="Name"
                    required
                    orientation="horizontal"
                    input={{
                      ...input,
                      placeholder: "A unique machine name.",
                    }}
                    validationState={
                      getError(formStore, "name") ? "invalid" : "valid"
                    }
                  />
                )}
              </Field>
              <Divider />
              <Field name="description">
                {(field, input) => (
                  <TextArea
                    {...field}
                    value={field.value}
                    label="Description"
                    orientation="horizontal"
                    input={{
                      ...input,
                      placeholder: "A short description of the machine.",
                    }}
                    validationState={
                      getError(formStore, "description") ? "invalid" : "valid"
                    }
                  />
                )}
              </Field>
            </Fieldset>
            <Fieldset>
              <Field name="machineClass">
                {(field, props) => (
                  <Select
                    zIndex={100}
                    {...props}
                    value={field.value}
                    error={field.error}
                    required
                    label={{
                      label: "Platform",
                    }}
                    options={PlatformOptions}
                    name={field.name}
                  />
                )}
              </Field>
            </Fieldset>
          </div>
        }
        footer={
          <div class="flex justify-end">
            <NextButton type="submit" />
          </div>
        }
      />
    </Form>
  );
};
