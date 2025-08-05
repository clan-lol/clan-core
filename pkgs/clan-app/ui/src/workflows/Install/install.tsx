import { Button } from "@/src/components/Button/Button";
import { Divider } from "@/src/components/Divider/Divider";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { HostFileInput } from "@/src/components/Form/HostFileInput";
import { Modal } from "@/src/components/Modal/Modal";
import { Select } from "@/src/components/Select/Select";
import { Typography } from "@/src/components/Typography/Typography";
import { callApi } from "@/src/hooks/api";
import {
  createStepper,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import {
  createForm,
  FieldValues,
  getError,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import { JSX, Show } from "solid-js";
import { Dynamic } from "solid-js/web";
import * as v from "valibot";

const CreateFlashSchema = v.object({
  ssh_key: v.pipe(
    v.string("Please select a key."),
    v.nonEmpty("Please select a key."),
  ),
  language: v.pipe(v.string(), v.nonEmpty("Please choose a language.")),
  keymap: v.pipe(v.string(), v.nonEmpty("Please select a keyboard layout.")),
});

export const InstallHeader = (props: { machineName: string }) => {
  return (
    <Typography hierarchy="label" size="default">
      Installing: {props.machineName}
    </Typography>
  );
};

export const CreateHeader = (props: { machineName: string }) => {
  return (
    <div class="px-6 py-2">
      <Typography
        hierarchy="label"
        size="default"
        family="mono"
        weight="medium"
      >
        Create installer
      </Typography>
    </div>
  );
};

interface InstallForm extends FieldValues {
  data_from_step_1: string;
  data_from_step_2?: string;
  data_from_step_3?: string;
}

type NextButtonProps = JSX.ButtonHTMLAttributes<HTMLButtonElement> & {};

const NextButton = (props: NextButtonProps) => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <Button
      type="submit"
      hierarchy="primary"
      disabled={!stepSignal.hasNext()}
      endIcon="ArrowRight"
      {...props}
    >
      Next
    </Button>
  );
};

const InstallStepper = () => {
  const stepSignal = useStepper<InstallSteps>();

  const [formStore, { Form, Field, FieldArray }] = createForm<InstallForm>();

  const handleSubmit: SubmitHandler<InstallForm> = (values, event) => {
    console.log("Installation started (submit)", values);
    stepSignal.setActiveStep("install:progress");
  };
  return (
    <Form onSubmit={handleSubmit}>
      <div class="gap-6">
        <Dynamic
          component={stepSignal.currentStep().content}
          machineName={"karl"}
        />
      </div>
    </Form>
  );
};

export const BackButton = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <Button
      hierarchy="secondary"
      disabled={!stepSignal.hasPrevious()}
      startIcon="ArrowLeft"
      onClick={() => {
        stepSignal.previous();
      }}
    >
      Back
    </Button>
  );
};

export interface InstallModalProps {
  machineName: string;
  initialStep?: string;
}

const InitialChoice = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <div class="flex flex-col gap-3">
      <div class="flex flex-col gap-6 rounded-md px-4 py-6 text-fg-def-1 bg-def-2">
        <div class="flex gap-2">
          <div class="flex flex-col gap-1 px-1">
            <Typography
              hierarchy="label"
              size="xs"
              weight="bold"
              color="primary"
            >
              Remote setup
            </Typography>
            <Typography
              hierarchy="body"
              size="xxs"
              weight="normal"
              color="secondary"
            >
              Is your machine currently online? Does it have an IP-address, can
              you SSH into it? And does it support Kexec?
            </Typography>
          </div>
          <Button
            type="button"
            ghost
            hierarchy="secondary"
            icon="CaretRight"
            onClick={() => stepSignal.setActiveStep("install:machine-0")}
          ></Button>
        </div>
        <Divider orientation="horizontal" class="bg-def-3" />

        <div class="flex items-center justify-between gap-2">
          <Typography hierarchy="label" size="xs" weight="bold">
            I don't have an installer, yet
          </Typography>
          <Button
            ghost
            hierarchy="secondary"
            endIcon="Flash"
            type="button"
            onClick={() => stepSignal.setActiveStep("create:iso-0")}
          >
            Create USB Installer
          </Button>
        </div>
      </div>
    </div>
  );
};

type FlashFormType = v.InferInput<typeof CreateFlashSchema>;

const CreateIso = () => {
  const [formStore, { Form, Field }] = createForm<FlashFormType>({
    validate: valiForm(CreateFlashSchema),
  });
  const stepSignal = useStepper<InstallSteps>();

  // TODO: push values to the parent form Store
  const handleSubmit: SubmitHandler<FlashFormType> = (values, event) => {
    console.log("ISO creation submitted", values);
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  const onSelectFile = async () => {
    const req = callApi("get_system_file", {
      file_request: {
        mode: "select_folder",
        title: "Select a folder for you new Clan",
      },
    });

    const resp = await req.result;

    if (resp.status === "error") {
      // just throw the first error, I can't imagine why there would be multiple
      // errors for this call
      throw new Error(resp.errors[0].message);
    }

    if (resp.status === "success" && resp.data) {
      return resp.data[0];
    }

    throw new Error("No data returned from api call");
  };

  return (
    <Form onSubmit={handleSubmit}>
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Fieldset>
              <Field name="ssh_key">
                {(field, input) => (
                  <HostFileInput
                    description="Public Key for connecting to the machine"
                    onSelectFile={onSelectFile}
                    {...field}
                    value={field.value}
                    label="Select directory"
                    orientation="horizontal"
                    placeholder="Select SSH Key"
                    required={true}
                    validationState={
                      getError(formStore, "ssh_key") ? "invalid" : "valid"
                    }
                    input={input}
                  />
                )}
              </Field>
            </Fieldset>
            <Fieldset>
              <Field name="language">
                {(field, props) => (
                  <Select
                    {...props}
                    value={field.value}
                    error={field.error}
                    required
                    label={{
                      label: "Language",
                      description: "Select your preferred language",
                    }}
                    options={[
                      { value: "en", label: "English" },
                      { value: "fr", label: "Français" },
                    ]}
                    placeholder="Language"
                    name={field.name}
                  />
                )}
              </Field>
              <Field name="keymap">
                {(field, props) => (
                  <Select
                    {...props}
                    value={field.value}
                    error={field.error}
                    required
                    label={{
                      label: "Keymap",
                      description: "Select your keyboard layout",
                    }}
                    options={[
                      { value: "EN_US", label: "QWERTY" },
                      { value: "DE_DE", label: "QWERTZ" },
                    ]}
                    placeholder="Keymap"
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
            <NextButton type="submit" />
          </div>
        }
      />
    </Form>
  );
};

interface StepLayoutProps {
  body: JSX.Element;
  footer: JSX.Element;
}
const StepLayout = (props: StepLayoutProps) => {
  return (
    <div class="flex flex-col gap-6">
      {props.body}
      {props.footer}
    </div>
  );
};

const steps = [
  {
    id: "init",
    content: InitialChoice,
  },
  {
    id: "create:iso-0",
    content: () => (
      <StepLayout
        body={
          <>
            <div class="flex h-36 w-full flex-col justify-center gap-3 rounded-md px-4 py-6 text-fg-inv-1 outline-2 outline-bg-def-acc-3 bg-inv-4">
              <div class="flex flex-col gap-3">
                <Typography
                  hierarchy="label"
                  size="xs"
                  weight="medium"
                  color="inherit"
                >
                  Create a portable installer
                </Typography>
                <Typography
                  hierarchy="headline"
                  size="default"
                  weight="bold"
                  color="inherit"
                >
                  Grab a disposable USB stick and plug it in
                </Typography>
              </div>
            </div>
            <div class="flex flex-col gap-1">
              <Typography hierarchy="body" size="default" weight="bold">
                We will erase everything on it during this process
              </Typography>
              <Typography hierarchy="body" size="xs">
                Create a portable installer tool that can turn any machine into
                a fully configured Clan machine.
              </Typography>
            </div>
          </>
        }
        footer={<RegularFooter />}
      />
    ),
  },
  {
    id: "create:iso-1",
    title: CreateHeader,
    content: CreateIso,
  },
  {
    id: "install:machine-0",
    title: InstallHeader,
    content: () => (
      <div>
        Enter the targetHost
        <NextButton />
      </div>
    ),
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

const RegularFooter = () => {
  const stepper = useStepper<InstallSteps>();
  return (
    <div class="flex justify-between">
      <BackButton />
      <NextButton type="button" onClick={() => stepper.next()} />
    </div>
  );
};

export type InstallSteps = typeof steps;

export const InstallModal = (props: InstallModalProps) => {
  const stepper = createStepper(
    {
      steps,
    },
    { initialStep: "init" },
  );

  return (
    <StepperProvider stepper={stepper}>
      <Modal
        title="Install machine"
        onClose={() => {
          console.log("Install aborted");
        }}
        metaHeader={() => {
          // @ts-expect-error some steps might not have a title
          const HeaderComponent = stepper.currentStep()?.title;
          return (
            <Show when={HeaderComponent}>
              {(C) => (
                <Dynamic component={C()} machineName={props.machineName} />
              )}
            </Show>
          );
        }}
      >
        {(ctx) => <InstallStepper />}
      </Modal>
    </StepperProvider>
  );
};
