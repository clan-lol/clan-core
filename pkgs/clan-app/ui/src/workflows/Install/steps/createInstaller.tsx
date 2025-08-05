import { useStepper } from "@/src/hooks/stepper";
import {
  createForm,
  getError,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import * as v from "valibot";
import { InstallSteps } from "../install";
import { callApi } from "@/src/hooks/api";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { HostFileInput } from "@/src/components/Form/HostFileInput";
import { Select } from "@/src/components/Select/Select";
import { BackButton, NextButton, StepFooter, StepLayout } from "../../Steps";
import { Typography } from "@/src/components/Typography/Typography";
import { Alert } from "@/src/components/Alert/Alert";
import { LoadingBar } from "@/src/components/LoadingBar/LoadingBar";
import { Button } from "@/src/components/Button/Button";
import Icon from "@/src/components/Icon/Icon";

const Prose = () => (
  <StepLayout
    body={
      <>
        <div class="flex h-36 w-full flex-col justify-center gap-3 rounded-md px-4 py-6 text-fg-inv-1 outline-2 outline-bg-def-acc-3 bg-inv-4">
          <div class="flex flex-col gap-3">
            <Typography
              hierarchy="label"
              size="xs"
              weight="medium"
              color="quaternary"
              family="mono"
              inverted
            >
              Create a portable installer
            </Typography>
            <Typography
              hierarchy="headline"
              size="default"
              weight="bold"
              color="inherit"
              class="text-balance"
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
            Create a portable installer tool that can turn any machine into a
            fully configured Clan machine.
          </Typography>
        </div>
      </>
    }
    footer={<StepFooter />}
  />
);

const CreateHeader = (props: { machineName: string }) => {
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

const ConfigureImageSchema = v.object({
  ssh_key: v.pipe(
    v.string("Please select a key."),
    v.nonEmpty("Please select a key."),
  ),
  language: v.pipe(v.string(), v.nonEmpty("Please choose a language.")),
  keymap: v.pipe(v.string(), v.nonEmpty("Please select a keyboard layout.")),
});

type ConfigureImageForm = v.InferInput<typeof ConfigureImageSchema>;

const ConfigureImage = () => {
  const [formStore, { Form, Field }] = createForm<ConfigureImageForm>({
    validate: valiForm(ConfigureImageSchema),
  });
  const stepSignal = useStepper<InstallSteps>();

  // TODO: push values to the parent form Store
  const handleSubmit: SubmitHandler<ConfigureImageForm> = (values, event) => {
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

const ChooseDiskSchema = v.object({
  disk: v.pipe(
    v.string("Please select a disk."),
    v.nonEmpty("Please select a disk."),
  ),
});

type ChooseDiskForm = v.InferInput<typeof ChooseDiskSchema>;

const ChooseDisk = () => {
  const stepSignal = useStepper<InstallSteps>();

  const [formStore, { Form, Field }] = createForm<ChooseDiskForm>({
    validate: valiForm(ChooseDiskSchema),
  });

  const handleSubmit: SubmitHandler<ChooseDiskForm> = (values, event) => {
    console.log("Disk selected", values);
    // Here you would typically trigger the disk selection process
    stepSignal.next();
  };
  return (
    <Form onSubmit={handleSubmit}>
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Fieldset>
              <Field name="disk">
                {(field, props) => (
                  <Select
                    {...props}
                    value={field.value}
                    error={field.error}
                    required
                    label={{
                      label: "Disk",
                      description: "Select a usb stick",
                    }}
                    options={[
                      { value: "1", label: "sda1" },
                      { value: "2", label: "sdb2" },
                    ]}
                    placeholder="Disk"
                    name={field.name}
                  />
                )}
              </Field>
              <Alert
                type="error"
                icon="Info"
                title="You're about to format this drive"
                description="It will erase all existing data on the target device"
              />
            </Fieldset>
          </div>
        }
        footer={
          <div class="flex justify-between">
            <BackButton />
            <NextButton endIcon="Flash">Flash USB Stick</NextButton>
          </div>
        }
      />
    </Form>
  );
};

const FlashProgress = () => {
  return (
    <div class="bg-inv-4 flex h-60 w-full flex-col items-center justify-end">
      <div class="flex flex-col gap-3 w-full max-w-md fg-inv-1 items-center mb-6">
        <Typography
          hierarchy="title"
          size="default"
          weight="bold"
          color="inherit"
        >
          USB stick is being flashed
        </Typography>
        <LoadingBar class="" />
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
    <div class="bg-inv-4 flex w-full flex-col items-center">
      <div class="flex flex-col gap-3 w-full max-w-md fg-inv-1 items-center py-6">
        <div class="rounded-full bg-semantic-success-4">
          <Icon icon="Checkmark" class="size-9" />
        </div>
        <Typography
          hierarchy="title"
          size="default"
          weight="bold"
          color="inherit"
        >
          Device has been successfully flashed!
        </Typography>
        <Alert
          type="warning"
          title="Plug the flashed device into the machine that you want to install."
          description=""
        />
        <div class="w-full flex justify-end mt-3">
          <Button
            hierarchy="primary"
            endIcon="ArrowRight"
            onClick={() => stepSignal.next()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
};

export const createInstallerSteps = [
  {
    id: "create:prose",
    content: Prose,
  },
  {
    id: "create:image",
    title: CreateHeader,
    content: ConfigureImage,
  },
  {
    id: "create:disk",
    title: CreateHeader,
    content: ChooseDisk,
  },
  {
    id: "create:progress",
    content: FlashProgress,
    isSplash: true,
  },
  {
    id: "create:done",
    content: FlashDone,
    isSplash: true,
  },
] as const;
