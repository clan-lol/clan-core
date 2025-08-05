import { Typography } from "@/src/components/Typography/Typography";
import { BackButton, NextButton, StepLayout } from "../../Steps";
import {
  createForm,
  getError,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import { Fieldset } from "@/src/components/Form/Fieldset";
import * as v from "valibot";
import { useStepper } from "@/src/hooks/stepper";
import { InstallSteps } from "../install";
import { TextInput } from "@/src/components/Form/TextInput";
import { Alert } from "@/src/components/Alert/Alert";
import { createSignal, Show } from "solid-js";
import { Divider } from "@/src/components/Divider/Divider";
import { Orienter } from "@/src/components/Form/Orienter";
import { Button } from "@/src/components/Button/Button";

export const InstallHeader = (props: { machineName: string }) => {
  return (
    <Typography hierarchy="label" size="default" class="px-6">
      Installing: {props.machineName}
    </Typography>
  );
};

const ConfigureAdressSchema = v.object({
  targetHost: v.pipe(
    v.string("Please set a target host."),
    v.nonEmpty("Please set a target host."),
  ),
});

type ConfigureAdressForm = v.InferInput<typeof ConfigureAdressSchema>;

const ConfigureAddress = () => {
  const [formStore, { Form, Field }] = createForm<ConfigureAdressForm>({
    validate: valiForm(ConfigureAdressSchema),
  });
  const stepSignal = useStepper<InstallSteps>();

  // TODO: push values to the parent form Store
  const handleSubmit: SubmitHandler<ConfigureAdressForm> = (values, event) => {
    console.log("ISO creation submitted", values);
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  return (
    <Form onSubmit={handleSubmit}>
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Fieldset>
              <Field name="targetHost">
                {(field, props) => (
                  <TextInput
                    {...field}
                    label="IP Address"
                    description="Hostname of the installation target"
                    value={field.value}
                    required
                    orientation="horizontal"
                    validationState={
                      getError(formStore, "targetHost") ? "invalid" : "valid"
                    }
                    input={{
                      ...props,
                      placeholder: "i.e. flash-installer.local",
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
            <NextButton type="submit">Next</NextButton>
          </div>
        }
      />
    </Form>
  );
};

const CheckHardware = () => {
  const stepSignal = useStepper<InstallSteps>();
  // TODO: Hook this up with api
  const [report, setReport] = createSignal<boolean>(true);

  const handleNext = () => {
    stepSignal.next();
  };

  return (
    <StepLayout
      body={
        <div class="flex flex-col gap-2">
          <Fieldset>
            <Orienter orientation="horizontal">
              <Typography hierarchy="label" size="xs" weight="bold">
                Check hardware
              </Typography>
              <Button hierarchy="secondary" startIcon="Report">
                Run hardware report
              </Button>
            </Orienter>
            <Divider orientation="horizontal" />
            <Show when={report()}>
              <Alert
                icon="Checkmark"
                type="info"
                title="Hardware report exists"
              />
            </Show>
          </Fieldset>
        </div>
      }
      footer={
        <div class="flex justify-between">
          <BackButton />
          <NextButton onClick={handleNext}>Next</NextButton>
        </div>
      }
    />
  );
};

export const installSteps = [
  {
    id: "install:address",
    title: InstallHeader,
    content: ConfigureAddress,
  },
  {
    id: "install:check-hardware",
    title: InstallHeader,
    content: CheckHardware,
  },
  {
    id: "install:confirm",
    title: InstallHeader,
    content: (props: { machineName: string }) => (
      <div>
        Confirm the installation of {props.machineName}
        <NextButton />
      </div>
    ),
  },
  {
    id: "install:progress",
    title: InstallHeader,
    content: () => (
      <div>
        <p>Installation in progress...</p>
        <p>Please wait while we set up your machine.</p>
      </div>
    ),
  },
] as const;
