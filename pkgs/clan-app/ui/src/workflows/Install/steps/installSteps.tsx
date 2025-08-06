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
import { Select } from "@/src/components/Select/Select";
import { LoadingBar } from "@/src/components/LoadingBar/LoadingBar";
import Icon from "@/src/components/Icon/Icon";

export const InstallHeader = (props: { machineName: string }) => {
  return (
    <Typography hierarchy="label" size="default">
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
                Hardware Report
              </Typography>
              <Button hierarchy="secondary" startIcon="Report">
                Update hardware report
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
          <NextButton type="button" onClick={handleNext}>
            Next
          </NextButton>
        </div>
      }
    />
  );
};

const DiskSchema = v.object({
  mainDisk: v.pipe(
    v.string("Please select a disk"),
    v.nonEmpty("Please select a disk"),
  ),
});

type DiskForm = v.InferInput<typeof DiskSchema>;

const ConfigureDisk = () => {
  const [formStore, { Form, Field }] = createForm<DiskForm>({
    validate: valiForm(DiskSchema),
  });
  const stepSignal = useStepper<InstallSteps>();

  const handleSubmit: SubmitHandler<DiskForm> = (values, event) => {
    console.log("submitted", values);
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  return (
    <Form onSubmit={handleSubmit}>
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Fieldset>
              <Field name="mainDisk">
                {(field, props) => (
                  <Select
                    {...props}
                    value={field.value}
                    error={field.error}
                    required
                    label={{
                      label: "Main disk",
                      description: "Select the disk to install the system on",
                    }}
                    // TODO: Get from api
                    options={[{ value: "disk", label: "Disk0" }]}
                    placeholder="Select a disk"
                    name={field.name}
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

type DynamicForm = Record<string, string>;

const ConfigureData = () => {
  const [formStore, { Form, Field }] = createForm<DynamicForm>({
    // TODO: Dynamically validate fields
  });
  const stepSignal = useStepper<InstallSteps>();

  const handleSubmit: SubmitHandler<DynamicForm> = (values, event) => {
    console.log("vars submitted", values);
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  return (
    <Form onSubmit={handleSubmit}>
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Fieldset legend="Root password">
              <Field name="root-password">
                {(field, props) => (
                  <TextInput
                    {...field}
                    label="Root password"
                    description="Leave empty to generate automatically"
                    value={field.value}
                    required
                    orientation="horizontal"
                    validationState={
                      getError(formStore, "root-password") ? "invalid" : "valid"
                    }
                    icon="EyeClose"
                    input={{
                      ...props,
                      type: "password",
                    }}
                  />
                )}
              </Field>
            </Fieldset>
            <Fieldset legend="WIFI TU-YAN">
              <Field name="networkSSID">
                {(field, props) => (
                  <TextInput
                    {...field}
                    label="ssid"
                    description="Name of the wifi network"
                    value={field.value}
                    required
                    orientation="horizontal"
                    validationState={
                      getError(formStore, "wifi/password") ? "invalid" : "valid"
                    }
                    input={{
                      ...props,
                    }}
                  />
                )}
              </Field>
              <Field name="password">
                {(field, props) => (
                  <TextInput
                    {...field}
                    label="password"
                    description="Password for the wifi network"
                    value={field.value}
                    required
                    orientation="horizontal"
                    validationState={
                      getError(formStore, "wifi/password") ? "invalid" : "valid"
                    }
                    icon="EyeClose"
                    input={{
                      ...props,
                      type: "password",
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

const Display = (props: { value: string; label: string }) => {
  return (
    <>
      <Typography hierarchy="label" size="xs" color="primary" weight="bold">
        {props.label}
      </Typography>
      <Typography hierarchy="body" size="s" weight="medium">
        {props.value}
      </Typography>
    </>
  );
};

const InstallSummary = () => {
  const stepSignal = useStepper<InstallSteps>();

  const handleInstall = () => {
    // Here you would typically trigger the installation process
    console.log("Installation started");
    stepSignal.setActiveStep("install:progress");
  };
  return (
    <StepLayout
      body={
        <div class="flex flex-col gap-4">
          <Fieldset legend="Deploy to">
            <Orienter orientation="horizontal">
              {/* TOOD: Display the values emited from previous steps */}
              <Display label="Target" value="flash-installer.local" />
            </Orienter>
          </Fieldset>
          <Fieldset legend="Disk Configuration">
            <Orienter orientation="horizontal">
              <Display label="Disk Schema" value="Single" />
            </Orienter>
            <Divider orientation="horizontal" />
            <Orienter orientation="horizontal">
              <Display
                label="Main Disk"
                value="nvme-WD_PC_SN740_SDDQNQD-512G"
              />
            </Orienter>
          </Fieldset>
        </div>
      }
      footer={
        <div class="flex justify-between">
          <BackButton />
          <NextButton type="button" onClick={handleInstall} endIcon="Flash">
            Install
          </NextButton>
        </div>
      }
    />
  );
};

const InstallProgress = () => {
  return (
    <div class="flex h-60 w-full flex-col items-center justify-end bg-inv-4">
      <div class="mb-6 flex w-full max-w-md flex-col items-center gap-3 fg-inv-1">
        <Typography
          hierarchy="title"
          size="default"
          weight="bold"
          color="inherit"
        >
          Machine is beeing installed
        </Typography>
        <LoadingBar />
        <Button hierarchy="primary" class="w-fit" size="s">
          Cancel
        </Button>
      </div>
    </div>
  );
};

const FlashDone = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <div class="flex w-full flex-col items-center bg-inv-4">
      <div class="flex w-full max-w-md flex-col items-center gap-3 py-6 fg-inv-1">
        <div class="rounded-full bg-semantic-success-4">
          <Icon icon="Checkmark" class="size-9" />
        </div>
        <Typography
          hierarchy="title"
          size="default"
          weight="bold"
          color="inherit"
        >
          Machine installation finished!
        </Typography>
        <div class="mt-3 flex w-full justify-center">
          <Button
            hierarchy="primary"
            endIcon="Close"
            size="s"
            onClick={() => stepSignal.next()}
          >
            Close
          </Button>
        </div>
      </div>
    </div>
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
    id: "install:disk",
    title: InstallHeader,
    content: ConfigureDisk,
  },
  {
    id: "install:data",
    title: InstallHeader,
    content: ConfigureData,
  },
  {
    id: "install:summary",
    title: () => (
      <Typography hierarchy="label" size="default">
        Summary
      </Typography>
    ),
    content: InstallSummary,
  },
  {
    id: "install:progress",
    content: InstallProgress,
    isSplash: true,
  },
  {
    id: "install:done",
    content: FlashDone,
    isSplash: true,
  },
] as const;
