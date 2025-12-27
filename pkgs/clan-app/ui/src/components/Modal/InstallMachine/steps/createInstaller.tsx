import { getStepStore, useStepper } from "@/src/components/Steps/stepper";
import { createForm, SubmitHandler, valiForm } from "@modular-forms/solid";
import * as v from "valibot";
import { InstallSteps, InstallStoreType } from "..";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { HostFileInput } from "@/src/components/Form/HostFileInput";
import { Select } from "@/src/components/Select/Select";
import {
  BackButton,
  NextButton,
  StepFooter,
  StepLayout,
} from "@/src/components/Steps";
import { Typography } from "@/src/components/Typography/Typography";
import { Alert } from "@/src/components/Alert/Alert";
import { LoadingBar } from "@/src/components/LoadingBar/LoadingBar";
import { Button } from "@/src/components/Button/Button";
import Icon from "@/src/components/Icon/Icon";
import { onCleanup, Show, Suspense } from "solid-js";
import cx from "classnames";
import usbLogo from "@/logos/usb-stick-min.png?url";
import { useSysContext } from "@/src/models";
import { createAsync } from "@solidjs/router";
import ModalHeading from "../../components/ModalHeading";

const Prose = () => (
  <div class="h-[30rem] w-svw max-w-3xl bg-white p-4">
    <StepLayout
      body={
        <div class="flex flex-col gap-4">
          <div class="flex h-36 w-full flex-col justify-center gap-3 rounded-md p-4 text-fg-inv-1 outline-2 outline-bg-def-acc-3 bg-inv-4">
            <div class="flex flex-col gap-3">
              <Typography
                hierarchy="label"
                size="xs"
                weight="medium"
                color="quaternary"
                family="mono"
                inverted
              >
                Local Setup
              </Typography>
              <div class="text-balance">
                <Typography hierarchy="headline" weight="bold" color="inherit">
                  Here's what you
                  <br />
                  need to do
                </Typography>
              </div>
            </div>
          </div>
          <div class="flex flex-col gap-4 px-4">
            <div class="flex flex-col gap-1">
              <Typography hierarchy="body" size="default" weight="bold">
                Let's walk through it.
              </Typography>
              <Typography hierarchy="body" size="xs" weight="normal">
                We will help you write the Clan Installer to a USB-stick or SD
                card, which will then be used to set up the new machine.
              </Typography>
              <Typography hierarchy="body" size="xs" weight="normal">
                Get a USB-stick or an SD card with at least 8GB of capacity, and
                plug it into this machine.
              </Typography>
            </div>
            <div class="flex flex-col gap-1">
              <Typography hierarchy="body" size="default" weight="bold">
                Why do you need to do this?
              </Typography>
              <Typography hierarchy="body" size="xs" weight="normal">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                Suspendisse varius enim in eros elementum tristique. Duis
                cursus,
              </Typography>
            </div>
          </div>
        </div>
      }
      footer={<StepFooter nextText="start" />}
    />
  </div>
);

const ConfigureImageSchema = v.object({
  ssh_key: v.pipe(
    v.string("Please select a key."),
    v.nonEmpty("Please select a key."),
  ),
});

type ConfigureImageForm = v.InferInput<typeof ConfigureImageSchema>;

const ConfigureImage = () => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<ConfigureImageForm>({
    validate: valiForm(ConfigureImageSchema),
    initialValues: {
      ssh_key: store.flash?.ssh_file,
    },
  });

  const handleSubmit: SubmitHandler<ConfigureImageForm> = (values, event) => {
    // Push values to the store
    set("flash", (s) => ({
      ...s,
      ssh_file: values.ssh_key,
    }));

    stepSignal.next();
  };

  return (
    <Form
      onSubmit={handleSubmit}
      class="flex h-[30rem] w-svw max-w-3xl flex-col bg-white"
    >
      <ModalHeading text="Create installer" />
      <div class="flex-1 p-4">
        <StepLayout
          body={
            <div class="flex flex-col gap-2">
              <Fieldset>
                <Field name="ssh_key">
                  {(field, props) => (
                    <HostFileInput
                      {...props}
                      description="Public Key for connecting to the machine"
                      label="Public Key"
                      orientation="horizontal"
                      placeholder="Select SSH Key"
                      initialFolder="~/.ssh"
                      required={true}
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
      </div>
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
  const [, { getFlashableDevices }] = useSysContext();
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<ChooseDiskForm>({
    validate: valiForm(ChooseDiskSchema),
    initialValues: {
      disk: store.flash?.device,
    },
  });

  const handleSubmit: SubmitHandler<ChooseDiskForm> = (values, event) => {
    set("flash", "device", values.disk);

    stepSignal.next();
  };

  const getOptions = async () => {
    const devices = await getFlashableDevices();

    return devices.map((device) => {
      let name =
        device.name.length > 32
          ? device.name.slice(0, 32) + "..."
          : device.name;
      name = name.replaceAll("_", " ");
      return {
        value: device.path,
        label: `${name} (${device.size})`,
      };
    });
  };

  return (
    <Form
      onSubmit={handleSubmit}
      class="flex h-[30rem] w-svw max-w-3xl flex-col bg-white"
    >
      <ModalHeading text="Create installer" />
      <div class="flex-1 p-4">
        <StepLayout
          body={
            <div class="flex flex-col gap-2">
              <Fieldset>
                <Field name="disk">
                  {(field, props) => (
                    <Select
                      zIndex={100}
                      {...props}
                      value={field.value}
                      error={field.error}
                      required
                      label={{
                        label: "Install Media",
                        description:
                          "Select a USB stick or SD card from the list",
                      }}
                      getOptions={getOptions}
                      placeholder="Choose Device"
                      noOptionsText="No devices found"
                      name={field.name}
                    />
                  )}
                </Field>
                <Alert
                  transparent
                  dense
                  size="s"
                  type="error"
                  icon="Info"
                  title="You're about to format this drive"
                  description="It will erase all existing data"
                />
              </Fieldset>
            </div>
          }
          footer={
            <div class="flex justify-between">
              <BackButton />
              <NextButton endIcon="Flash">Flash Installer</NextButton>
            </div>
          }
        />
      </div>
    </Form>
  );
};

const FlashDone = () => {
  const [, { flashInstaller }] = useSysContext();
  const stepSignal = useStepper<InstallSteps>();
  const [store] = getStepStore<InstallStoreType>(stepSignal);

  const controller = new AbortController();
  const done = createAsync(async () => {
    await flashInstaller({
      signal: controller.signal,
      sshKeysDir: store.flash.ssh_file,
      diskPath: store.flash.device,
    });
    return true;
  });

  const handleCancel = () => {
    controller.abort();
    stepSignal.previous();
  };

  onCleanup(() => {
    controller.abort();
  });

  return (
    <Suspense
      fallback={
        <div
          class={cx(
            "relative flex size-full h-[18rem] w-svw max-w-[30rem] flex-col items-center justify-end bg-inv-4",
          )}
        >
          <img src={usbLogo} alt="usb logo" class="absolute top-4 z-0" />
          <div class="z-10 mb-6 flex w-full max-w-md flex-col items-center gap-2 fg-inv-1">
            <Typography
              hierarchy="title"
              size="default"
              weight="bold"
              color="inherit"
            >
              Removable media is being flashed
            </Typography>
            <LoadingBar />
            <Button
              hierarchy="primary"
              elasticity="fit"
              size="s"
              in="FlashProgress"
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </div>
        </div>
      }
    >
      <Show when={done()}>
        <div class="flex size-full h-72 w-svw max-w-[30rem] flex-col items-center justify-end bg-inv-4">
          <div class="flex size-full max-w-md flex-col items-center justify-center gap-3 pt-6 fg-inv-1">
            <div class="rounded-full bg-semantic-success-4">
              <Icon icon="Checkmark" in="WorkflowPanelTitle" />
            </div>
            <Typography
              hierarchy="title"
              size="default"
              weight="bold"
              color="inherit"
            >
              Your device has been flashed!
            </Typography>
            <Alert
              type="warning"
              title="Remove it and plug it into the machine that you want to install."
              description=""
            />
          </div>
          <div class="flex w-full justify-end px-5 py-4">
            <Button
              hierarchy="primary"
              endIcon="ArrowRight"
              onClick={() => stepSignal.next()}
            >
              Next
            </Button>
          </div>
        </div>
      </Show>
    </Suspense>
  );
};

export const createInstallerSteps = [
  {
    id: "create:prose",
    content: Prose,
  },
  {
    id: "create:image",
    content: ConfigureImage,
  },
  {
    id: "create:disk",
    content: ChooseDisk,
  },
  {
    id: "create:done",
    content: FlashDone,
  },
] as const;
