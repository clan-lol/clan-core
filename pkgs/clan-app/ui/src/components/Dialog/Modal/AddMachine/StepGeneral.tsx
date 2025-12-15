import { NextButton, StepLayout } from "@/src/components/Dialog/Steps";
import * as v from "valibot";
import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  clearError,
  createForm,
  FieldValues,
  getError,
  getErrors,
  setError,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import styles from "./AddMachine.module.css";
import { AddMachineSteps, AddMachineStoreType } from ".";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { TextInput } from "@/src/components/Form/TextInput";
import { Divider } from "@/src/components/Divider/Divider";
import { TextArea } from "@/src/components/Form/TextArea";
import { Select } from "@/src/components/Select/Select";
import { Show } from "solid-js";
import { Alert } from "@/src/components/Alert/Alert";
import { useMachinesContext } from "@/src/models";
import { ModalHeading } from "..";

const PlatformOptions = [
  { label: "NixOS", value: "nixos" },
  { label: "Darwin", value: "darwin" },
];

const GeneralSchema = v.object({
  id: v.pipe(
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

export interface GeneralForm extends FieldValues {
  machineClass: "nixos" | "darwin";
  id: string;
  description?: string;
}

export const StepGeneral = () => {
  const [machines] = useMachinesContext();
  const stepSignal = useStepper<AddMachineSteps>();
  const [store, set] = getStepStore<AddMachineStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<GeneralForm>({
    validate: valiForm(GeneralSchema),
    initialValues: { ...store.general, machineClass: "nixos" },
  });

  const handleSubmit: SubmitHandler<GeneralForm> = (values, event) => {
    if (values.id in machines().all) {
      setError(
        formStore,
        "name",
        `A machine named '${values.id}' already exists. Please choose a different one.`,
      );
      return;
    }

    clearError(formStore, "id");

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
    <Form onSubmit={handleSubmit}>
      <ModalHeading text="General" />
      <div class={styles.content}>
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
                <Field name="id">
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
                        getError(formStore, "id") ? "invalid" : "valid"
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
      </div>
    </Form>
  );
};
