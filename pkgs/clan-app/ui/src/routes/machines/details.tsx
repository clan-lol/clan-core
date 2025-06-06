import { callApi, SuccessData } from "@/src/api";
import {
  createForm,
  FieldValues,
  getValue,
  getValues,
  setValue,
} from "@modular-forms/solid";
import { useNavigate, useParams, useSearchParams } from "@solidjs/router";
import { createQuery, useQuery, useQueryClient } from "@tanstack/solid-query";
import { createEffect, createSignal, For, Match, Show, Switch } from "solid-js";

import { Button } from "../../components/Button/Button";
import Icon from "@/src/components/icon";
import { TextInput } from "@/src/Form/fields/TextInput";
import Accordion from "@/src/components/accordion";
import toast from "solid-toast";
import { MachineAvatar } from "./avatar";
import { Header } from "@/src/layout/header";
import { InputLabel } from "@/src/components/inputBase";
import { FieldLayout } from "@/src/Form/fields/layout";
import { Modal } from "@/src/components/modal";
import { Typography } from "@/src/components/Typography";
import { HardwareValues, HWStep } from "./install/hardware-step";
import { DiskStep, DiskValues } from "./install/disk-step";
import { SummaryStep } from "./install/summary-step";
import cx from "classnames";
import { VarsStep, VarsValues } from "./install/vars-step";
import Fieldset from "@/src/Form/fieldset";
import {
  type FileDialogOptions,
  FileSelectorField,
} from "@/src/components/fileSelect";
import { useClanContext } from "@/src/contexts/clan";
import { TagList } from "@/src/components/TagList/TagList";

type MachineFormInterface = MachineData & {
  sshKey?: File;
  disk?: string;
};

type MachineData = SuccessData<"get_machine_details">;

const steps: Record<StepIdx, string> = {
  "1": "Hardware detection",
  "2": "Disk schema",
  "3": "Credentials & Data",
  "4": "Installation",
};

type StepIdx = keyof AllStepsValues;

export interface AllStepsValues extends FieldValues {
  "1": HardwareValues;
  "2": DiskValues;
  "3": VarsValues;
  "4": NonNullable<unknown>;
  sshKey?: File;
}

const LoadingBar = () => (
  <div
    class="h-3 w-80 overflow-hidden rounded-[3px] border-2 border-def-1"
    style={{
      background: `repeating-linear-gradient(
    45deg,
    #ccc,
    #ccc 8px,
    #eee 8px,
    #eee 16px
  )`,
      animation: "slide 25s linear infinite",
      "background-size": "200% 100%",
    }}
  ></div>
);

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

interface InstallMachineProps {
  name?: string;
  machine: MachineData;
}

const InstallMachine = (props: InstallMachineProps) => {
  const { activeClanURI } = useClanContext();

  const curr = activeClanURI();
  const { name } = props;
  if (!curr || !name) {
    return <span>No Clan selected</span>;
  }

  const [formStore, { Form, Field }] = createForm<AllStepsValues>();

  const [isDone, setIsDone] = createSignal<boolean>(false);
  const [isInstalling, setIsInstalling] = createSignal<boolean>(false);
  const [progressText, setProgressText] = createSignal<string>();

  const handleInstall = async (values: AllStepsValues) => {
    console.log("Installing", values);
    const curr_uri = activeClanURI();

    const target = values["1"].target;
    const diskValues = values["2"];

    if (!curr_uri) {
      return;
    }
    if (!props.name) {
      return;
    }

    setIsInstalling(true);

    // props.machine.disk_
    const shouldRunDisk =
      JSON.stringify(props.machine.disk_schema?.placeholders) !==
      JSON.stringify(diskValues.placeholders);

    if (shouldRunDisk) {
      setProgressText("Setting up disk ... (1/5)");
      const disk_response = await callApi("set_machine_disk_schema", {
        machine: {
          flake: { identifier: curr_uri },
          name: props.name,
        },
        placeholders: diskValues.placeholders,
        schema_name: diskValues.schema,
        force: true,
      });
    }

    setProgressText("Installing machine ... (2/5)");

    const installPromise = callApi("install_machine", {
      opts: {
        machine: {
          name: props.name,
          flake: {
            identifier: curr_uri,
          },
          override_target_host: target,
          private_key: values.sshKey?.name,
        },
        password: "",
      },
    });

    // Next step
    await sleep(10 * 1000);
    setProgressText("Building machine ... (3/5)");
    await sleep(10 * 1000);
    setProgressText("Formatting remote disk ... (4/5)");
    await sleep(10 * 1000);
    setProgressText("Copying system ... (5/5)");
    await sleep(20 * 1000);
    setProgressText("Rebooting remote system ... ");
    await sleep(10 * 1000);

    const installResponse = await installPromise;
  };

  const [step, setStep] = createSignal<StepIdx>("1");

  const handleNext = () => {
    console.log("Next");
    setStep((c) => `${+c + 1}` as StepIdx);
  };
  const handlePrev = () => {
    console.log("Next");
    setStep((c) => `${+c - 1}` as StepIdx);
  };

  const Footer = () => (
    <div class="flex justify-between p-4">
      <Button
        startIcon={<Icon icon="ArrowLeft" />}
        variant="light"
        type="button"
        onClick={handlePrev}
        disabled={step() === "1"}
      >
        Previous
      </Button>
      <Button
        endIcon={<Icon icon="ArrowRight" />}
        type="submit"
        // IMPORTANT: The step itself will try to submit and call the next step
        // onClick={(e: Event) => handleNext()}
      >
        Next
      </Button>
    </div>
  );

  return (
    <Switch
      fallback={
        <Form
          onSubmit={handleInstall}
          class="relative top-0 flex h-full flex-col gap-0"
        >
          {/* Register each step as form field */}
          {/* @ts-expect-error: object type is not statically supported */}
          <Field name="1">{(field, fieldProps) => <></>}</Field>
          {/* @ts-expect-error: object type is not statically supported */}
          <Field name="2">{(field, fieldProps) => <></>}</Field>

          {/* Modal Header */}
          <div class="select-none px-6 py-2">
            <Typography hierarchy="label" size="default">
              Install:{" "}
            </Typography>
            <Typography hierarchy="label" size="default" weight="bold">
              {props.name}
            </Typography>
          </div>
          {/* Stepper header */}
          <div class="flex items-center justify-evenly gap-2 border py-3 bg-def-3 border-def-2">
            <For each={Object.entries(steps)}>
              {([idx, label]) => (
                <div class="flex flex-col items-center gap-3 fg-def-1">
                  <Typography
                    classList={{
                      [cx("bg-inv-4 fg-inv-1")]: idx === step(),
                      [cx("bg-def-4 fg-def-1")]: idx < step(),
                    }}
                    color="inherit"
                    hierarchy="label"
                    size="default"
                    weight="bold"
                    class="flex size-6 items-center justify-center rounded-full text-center align-middle bg-def-1"
                  >
                    <Show
                      when={idx >= step()}
                      fallback={<Icon icon="Checkmark" class="size-5" />}
                    >
                      {idx}
                    </Show>
                  </Typography>
                  <Typography
                    color="inherit"
                    hierarchy="label"
                    size="xs"
                    weight="medium"
                    class="text-center align-top fg-def-3"
                    classList={{
                      [cx("!fg-def-1")]: idx == step(),
                    }}
                  >
                    {label}
                  </Typography>
                </div>
              )}
            </For>
          </div>
          <Switch fallback={"Undefined content. This Step seems to not exist."}>
            <Match when={step() === "1"}>
              <HWStep
                // @ts-expect-error: This cannot be undefined in this context.
                machine_id={props.name}
                // @ts-expect-error: This cannot be undefined in this context.
                dir={activeClanURI()}
                handleNext={(data) => {
                  const prev = getValue(formStore, "1");
                  setValue(formStore, "1", { ...prev, ...data });
                  handleNext();
                }}
                initial={
                  getValue(formStore, "1") || {
                    target: props.machine.machine.deploy?.targetHost || "",
                    report: false,
                  }
                }
                footer={<Footer />}
              />
            </Match>
            <Match when={step() === "2"}>
              <DiskStep
                // @ts-expect-error: This cannot be undefined in this context.
                machine_id={props.name}
                // @ts-expect-error: This cannot be undefined in this context.
                dir={activeClanURI()}
                footer={<Footer />}
                handleNext={(data) => {
                  const prev = getValue(formStore, "2");
                  setValue(formStore, "2", { ...prev, ...data });
                  handleNext();
                }}
                // @ts-expect-error: The placeholder type is to wide
                initial={{
                  ...props.machine.disk_schema,
                  ...getValue(formStore, "2"),
                  initialized: !!props.machine.disk_schema,
                }}
              />
            </Match>
            <Match when={step() === "3"}>
              <VarsStep
                // @ts-expect-error: This cannot be undefined in this context.
                machine_id={props.name}
                // @ts-expect-error: This cannot be undefined in this context.
                dir={activeClanURI()}
                handleNext={(data) => {
                  const prev = getValue(formStore, "3");
                  setValue(formStore, "3", { ...prev, ...data });
                  handleNext();
                }}
                initial={getValue(formStore, "3") || {}}
                footer={<Footer />}
              />
            </Match>
            <Match when={step() === "4"}>
              <SummaryStep
                // @ts-expect-error: This cannot be undefined in this context.
                machine_id={props.name}
                // @ts-expect-error: This cannot be undefined in this context.
                dir={activeClanURI()}
                handleNext={() => handleNext()}
                // @ts-expect-error: This cannot be known.
                initial={getValues(formStore)}
                footer={
                  <div class="flex justify-between p-4">
                    <Button
                      startIcon={<Icon icon="ArrowLeft" />}
                      variant="light"
                      type="button"
                      onClick={handlePrev}
                      disabled={step() === "1"}
                    >
                      Previous
                    </Button>
                    <Button startIcon={<Icon icon="Flash" />}>Install</Button>
                  </div>
                }
              />
            </Match>
          </Switch>
        </Form>
      }
    >
      <Match when={isInstalling()}>
        <div class="flex h-96 w-[40rem] flex-col fg-inv-1">
          <div class="flex w-full gap-1 p-4 bg-inv-4">
            <Typography
              color="inherit"
              hierarchy="label"
              size="default"
              weight="medium"
            >
              Install:
            </Typography>
            <Typography
              color="inherit"
              hierarchy="label"
              size="default"
              weight="bold"
            >
              {props.name}
            </Typography>
          </div>
          <div class="flex h-full flex-col items-center gap-3 px-4 py-8 bg-inv-4 fg-inv-1">
            <Icon icon="ClanIcon" viewBox="0 0 72 89" class="size-20" />
            {isDone() && <LoadingBar />}
            <Typography
              hierarchy="label"
              size="default"
              weight="medium"
              color="inherit"
            >
              {progressText()}
            </Typography>
            <Button onClick={() => setIsInstalling(false)}>Cancel</Button>
          </div>
        </div>
      </Match>
    </Switch>
  );
};

interface MachineDetailsProps {
  initialData: MachineData;
}

const MachineForm = (props: MachineDetailsProps) => {
  const [formStore, { Form, Field }] =
    // TODO: retrieve the correct initial values from API
    createForm<MachineFormInterface>({
      initialValues: props.initialData,
    });

  const targetHost = () => getValue(formStore, "machine.deploy.targetHost");
  const machineName = () =>
    getValue(formStore, "machine.name") || props.initialData.machine.name;

  const [installModalOpen, setInstallModalOpen] = createSignal(false);

  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { activeClanURI } = useClanContext();

  const handleSubmit = async (values: MachineFormInterface) => {
    console.log("submitting", values);

    const curr_uri = activeClanURI();
    if (!curr_uri) {
      return;
    }

    const machine_response = await callApi("update_machine", {
      machine: {
        name: props.initialData.machine.name || "My machine",
        flake: {
          identifier: curr_uri,
        },
      },
      update: {
        ...values.machine,
        // TODO: Remove this workaround
        tags: Array.from(
          values.machine.tags || props.initialData.machine.tags || [],
        ),
      },
    });
    await queryClient.invalidateQueries({
      queryKey: [curr_uri, "machine", machineName(), "get_machine_details"],
    });

    return null;
  };

  const generatorsQuery = createQuery(() => ({
    queryKey: [activeClanURI(), machineName(), "generators"],
    queryFn: async () => {
      const machine_name = machineName();
      const base_dir = activeClanURI();
      if (!machine_name || !base_dir) {
        return [];
      }
      const result = await callApi("get_generators_closure", {
        base_dir: base_dir,
        machine_name: machine_name,
      });
      if (result.status === "error") throw new Error("Failed to fetch data");
      return result.data;
    },
  }));

  const handleUpdateButton = async () => {
    await generatorsQuery.refetch();

    if (
      generatorsQuery.data?.some((generator) => generator.prompts?.length !== 0)
    ) {
      navigate(`/machines/${machineName()}/vars?action=update`);
    } else {
      handleUpdate();
    }
  };

  const [isUpdating, setIsUpdating] = createSignal(false);

  const handleUpdate = async () => {
    if (isUpdating()) {
      return;
    }
    const curr_uri = activeClanURI();
    if (!curr_uri) {
      return;
    }
    const machine = machineName();
    if (!machine) {
      toast.error("Machine is required");
      return;
    }

    const target = targetHost();

    setIsUpdating(true);
    const r = await callApi("deploy_machine", {
      machine: {
        name: machine,
        flake: {
          identifier: curr_uri,
        },
        override_target_host: target,
      },
    });
  };

  createEffect(() => {
    const action = searchParams.action;
    console.log({ action });
    if (action === "update") {
      setSearchParams({ action: undefined });
      handleUpdate();
    }
  });

  return (
    <>
      <div class="flex flex-col gap-6">
        <div class="sticky top-0 flex items-center justify-end gap-2 border-b border-secondary-100 bg-secondary-50 px-4 py-2">
          <div class="flex items-center gap-3">
            <div class="w-fit" data-tip="Machine must be online">
              {/* <Button
                class="w-full"
                size="s"
                // disabled={!online()}
                onClick={() => {
                  setInstallModalOpen(true);
                }}
                endIcon={<Icon icon="Flash" />}
              >
                Install
              </Button> */}
            </div>
            {/* <Typography hierarchy="label" size="default">
              Installs the system for the first time. Used to bootstrap the
              remote device.
            </Typography> */}
          </div>
          <div class="flex items-center gap-3">
            <div class="button-group flex">
              <Button
                variant="light"
                class="w-full"
                size="s"
                onClick={() => {
                  setInstallModalOpen(true);
                }}
                endIcon={<Icon size={14} icon="Flash" />}
              >
                Install
              </Button>
              <Button
                variant="light"
                class="w-full"
                size="s"
                onClick={() => handleUpdateButton()}
                endIcon={<Icon size={12} icon="Update" />}
              >
                Update
              </Button>
              <Button
                variant="light"
                class="w-full"
                size="s"
                onClick={() => {
                  navigate(`/machines/${machineName()}/vars`);
                }}
                endIcon={<Icon size={12} icon="Folder" />}
              >
                Credentials
              </Button>
            </div>
            <div class=" w-fit" data-tip="Machine must be online"></div>
            {/* <Typography hierarchy="label" size="default">
              Update the system if changes should be synced after the
              installation process.
            </Typography> */}
          </div>
        </div>
        <div class="p-4">
          <span class="mb-2 flex w-full justify-center">
            <MachineAvatar name={machineName()} />
          </span>
          <Form
            onSubmit={handleSubmit}
            class="mx-auto flex w-full max-w-2xl flex-col gap-y-6"
          >
            <Fieldset legend="General">
              <Field name="machine.name">
                {(field, props) => (
                  <TextInput
                    inputProps={props}
                    label="Name"
                    value={field.value ?? ""}
                    error={field.error}
                    class="col-span-2"
                    required
                  />
                )}
              </Field>
              <Field name="machine.description">
                {(field, props) => (
                  <TextInput
                    inputProps={props}
                    label="Description"
                    value={field.value ?? ""}
                    error={field.error}
                    class="col-span-2"
                  />
                )}
              </Field>
              <Field name="machine.tags" type="string[]">
                {(field, props) => (
                  <div class="grid grid-cols-10 items-center">
                    <Typography
                      hierarchy="label"
                      size="default"
                      weight="bold"
                      class="col-span-5"
                    >
                      Tags{" "}
                    </Typography>
                    <div class="col-span-5 justify-self-end">
                      {/* alphabetically sort the tags */}
                      <TagList values={[...(field.value || [])].sort()} />
                    </div>
                  </div>
                )}
              </Field>
            </Fieldset>

            <Typography hierarchy={"body"} size={"s"}>
              <Fieldset legend="Hardware">
                <Field name="hw_config">
                  {(field, props) => (
                    <FieldLayout
                      label={<InputLabel>Hardware Configuration</InputLabel>}
                      field={<span>{field.value || "None"}</span>}
                    />
                  )}
                </Field>
                <hr />
                <Field name="disk_schema.schema_name">
                  {(field, props) => (
                    <>
                      <FieldLayout
                        label={<InputLabel>Disk schema</InputLabel>}
                        field={<span>{field.value || "None"}</span>}
                      />
                    </>
                  )}
                </Field>
              </Fieldset>
            </Typography>

            <Accordion title="Connection Settings">
              <Fieldset>
                <Field name="machine.deploy.targetHost">
                  {(field, props) => (
                    <TextInput
                      inputProps={props}
                      label="Target Host"
                      value={field.value ?? ""}
                      error={field.error}
                      class="col-span-2"
                      required
                    />
                  )}
                </Field>
                <FileSelectorField
                  Field={Field}
                  of={Array<File>}
                  multiple={true}
                  name="sshKeys" // Corresponds to FlashFormValues.sshKeys
                  label="SSH Private Key"
                  description="Provide your SSH private key for secure, passwordless connections."
                  fileDialogOptions={
                    {
                      title: "Select SSH Keys",
                      initial_folder: "~/.ssh",
                    } as FileDialogOptions
                  }
                  // You could add custom validation via modular-forms 'validate' prop on CustomFileField if needed
                  // e.g. validate={[required("At least one SSH key is required.")]}
                  // This would require CustomFileField to accept and pass `validate` to its internal `Field`.
                />
              </Fieldset>
            </Accordion>

            {
              <footer class="flex justify-end gap-y-3 border-t border-secondary-200 pt-5">
                <Button
                  type="submit"
                  disabled={formStore.submitting || !formStore.dirty}
                >
                  Update edits
                </Button>
              </footer>
            }
          </Form>
        </div>
      </div>

      <Modal
        title={`Install machine`}
        open={installModalOpen()}
        handleClose={() => setInstallModalOpen(false)}
        class="min-w-[600px]"
      >
        <InstallMachine name={machineName()} machine={props.initialData} />
      </Modal>
    </>
  );
};

export const MachineDetails = () => {
  const params = useParams();
  const { activeClanURI } = useClanContext();

  const genericQuery = useQuery(() => ({
    queryKey: [activeClanURI(), "machine", params.id, "get_machine_details"],
    queryFn: async () => {
      const curr = activeClanURI();
      if (curr) {
        const result = await callApi("get_machine_details", {
          machine: {
            flake: {
              identifier: curr,
            },
            name: params.id,
          },
        });
        if (result.status === "error") throw new Error("Failed to fetch data");
        return result.data;
      }
    },
  }));

  return (
    <>
      <Header title={`${params.id} machine`} showBack />
      <Show when={genericQuery.data} fallback={<span class=""></span>}>
        {(data) => (
          <>
            <MachineForm initialData={data()} />
          </>
        )}
      </Show>
    </>
  );
};
