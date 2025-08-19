import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  createForm,
  getError,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import * as v from "valibot";
import { InstallSteps, InstallStoreType } from "../install";
import { Fieldset } from "@/src/components/Form/Fieldset";
import { HostFileInput } from "@/src/components/Form/HostFileInput";
import { Select } from "@/src/components/Select/Select";
import { BackButton, NextButton, StepFooter, StepLayout } from "../../Steps";
import { Typography } from "@/src/components/Typography/Typography";
import { Alert } from "@/src/components/Alert/Alert";
import { LoadingBar } from "@/src/components/LoadingBar/LoadingBar";
import { Button } from "@/src/components/Button/Button";
import Icon from "@/src/components/Icon/Icon";
import { useSystemStorageOptions } from "@/src/hooks/queries";
import { useApiClient } from "@/src/hooks/ApiClient";
import { onMount } from "solid-js";
import cx from "classnames";

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
              Local Setup
            </Typography>
            <Typography
              hierarchy="headline"
              size="default"
              weight="bold"
              color="inherit"
              class="text-balance"
            >
              Here's what you
              <br />
              need to do
            </Typography>
          </div>
        </div>
        <div class="flex flex-col gap-4 px-4">
          <div class="flex flex-col gap-1">
            <Typography hierarchy="body" size="default" weight="bold">
              Let's walk through it.
            </Typography>
            <Typography hierarchy="body" size="xs" weight="normal">
              In the following we will help you to write the clan installer
              software to a USB-stick. This USB-stick will then be used to set
              up the new machine. Get a USB-stick with at least 8GB of capacity,
              and plug it into the machine on which you read this text. Note,
              all data on the USB-Stick will be lost.
            </Typography>
          </div>
          <div class="flex flex-col gap-1">
            <Typography hierarchy="body" size="default" weight="bold">
              Why do you need to do this?
            </Typography>
            <Typography hierarchy="body" size="xs" weight="normal">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit.
              Suspendisse varius enim in eros elementum tristique. Duis cursus,
            </Typography>
          </div>
        </div>
      </>
    }
    footer={<StepFooter nextText="start" />}
  />
);

const CreateHeader = (props: { machineName: string }) => {
  return (
    <Typography hierarchy="label" size="default" family="mono" weight="medium">
      Create installer
    </Typography>
  );
};

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

  const client = useApiClient();
  const onSelectFile = async () => {
    const req = client.fetch("get_system_file", {
      file_request: {
        mode: "get_system_file",
        title: "Select a folder for you new Clan",
        initial_folder: "~/.ssh",
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

  let content: Node;

  return (
    <Form onSubmit={handleSubmit} class="h-full">
      <StepLayout
        body={
          <div
            class="flex flex-col gap-2"
            ref={(el) => {
              content = el;
            }}
          >
            <Fieldset>
              <Field name="ssh_key">
                {(field, input) => (
                  <HostFileInput
                    description="Public Key for connecting to the machine"
                    onSelectFile={onSelectFile}
                    {...field}
                    value={field.value}
                    label="Public Key"
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

const installMediaRegex = new RegExp("^(?<type>usb|mmc)-(?<name>.*)(-(.*))?$");

const ChooseDisk = () => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<ChooseDiskForm>({
    validate: valiForm(ChooseDiskSchema),
    initialValues: {
      disk: store.flash?.device,
    },
  });

  const client = useApiClient();
  const systemStorageQuery = useSystemStorageOptions();
  const handleSubmit: SubmitHandler<ChooseDiskForm> = (values, event) => {
    // Just for completeness, set the disk in the store
    console.log("Flashing", store.flash);
    set("flash", (s) => ({
      ...s,
      device: values.disk,
    }));
    const call = client.fetch("run_machine_flash", {
      system_config: {
        ssh_keys_path: [store.flash.ssh_file],
      },
      disks: [
        {
          name: "main",
          device: values.disk,
        },
      ],
    });

    set("flash", "progress", call);

    console.log("Flashing", store.flash);

    stepSignal.next();
  };

  const stripId = (s: string) => s.split("-")[1] ?? s;

  const getOptions = async () => {
    if (!systemStorageQuery.data) {
      await systemStorageQuery.refetch();
    }

    const blockDevices = systemStorageQuery.data?.blockdevices ?? [];

    return (
      blockDevices
        // we only want writeable block devices which are USB or MMC (SD cards)
        .filter(({ id_link, ro }) => !ro && installMediaRegex.test(id_link))
        // transform each entry into an option
        .map(({ id_link, size, path }) => {
          const match = id_link.match(installMediaRegex)!;
          const name = match.groups?.name || "";

          const truncatedName =
            name.length > 32 ? name.slice(0, 32) + "..." : name;

          return {
            value: path,
            label: `${truncatedName.replaceAll("_", " ")} (${size})`,
          };
        })
    );
  };

  return (
    <Form onSubmit={handleSubmit} class="h-full">
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
    </Form>
  );
};

const FlashProgress = () => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  onMount(async () => {
    const result = await store.flash.progress.result;
    if (result.status == "success") {
      console.log("Flashing Success");
    }
    stepSignal.next();
  });

  const handleCancel = async () => {
    if (store.flash) {
      const progress = store.flash.progress;
      if (progress) {
        await progress.cancel();
      }
    }
    stepSignal.previous();
  };

  return (
    <div
      class={cx(
        "relative flex size-full flex-col items-center justify-center bg-inv-4",
      )}
    >
      <img
        src="/logos/usb-stick-min.png"
        alt="usb logo"
        class="absolute top-2 z-0"
      />
      <div class="z-10 mb-6 flex w-full max-w-md flex-col items-center gap-3 fg-inv-1">
        <Typography
          hierarchy="title"
          size="default"
          weight="bold"
          color="inherit"
        >
          USB stick is being flashed
        </Typography>
        <LoadingBar />
        <Button
          hierarchy="primary"
          class="mt-3 w-fit"
          size="s"
          onClick={handleCancel}
        >
          Cancel
        </Button>
      </div>
    </div>
  );
};
const FlashDone = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <div class="flex size-full flex-col items-center justify-between bg-inv-4">
      <div class="flex size-full max-w-md flex-col items-center justify-center gap-3 py-6 fg-inv-1">
        <div class="rounded-full bg-semantic-success-4">
          <Icon icon="Checkmark" class="size-9" />
        </div>
        <Typography
          hierarchy="title"
          size="default"
          weight="bold"
          color="inherit"
        >
          USB Stick is ready!
        </Typography>
        <Alert
          type="warning"
          title="Remove it and plug it into the machine that you want to install."
          description=""
        />
      </div>
      <div class="flex w-full justify-end p-6">
        <Button
          hierarchy="primary"
          endIcon="ArrowRight"
          onClick={() => stepSignal.next()}
        >
          Next
        </Button>
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
