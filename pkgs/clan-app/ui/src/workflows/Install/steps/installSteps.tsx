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
import { getStepStore, useStepper } from "@/src/hooks/stepper";
import { InstallSteps, InstallStoreType, PromptValues } from "../install";
import { TextInput } from "@/src/components/Form/TextInput";
import { Alert } from "@/src/components/Alert/Alert";
import { For, onMount, Show } from "solid-js";
import { Divider } from "@/src/components/Divider/Divider";
import { Orienter } from "@/src/components/Form/Orienter";
import { Button } from "@/src/components/Button/Button";
import { Select } from "@/src/components/Select/Select";
import { LoadingBar } from "@/src/components/LoadingBar/LoadingBar";
import Icon from "@/src/components/Icon/Icon";
import {
  MachineGenerators,
  useMachineDiskSchemas,
  useMachineGenerators,
  useMachineHardwareSummary,
} from "@/src/hooks/queries";
import { useClanURI } from "@/src/hooks/clan";
import { useApiClient } from "@/src/hooks/ApiClient";

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
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<ConfigureAdressForm>({
    validate: valiForm(ConfigureAdressSchema),
    initialValues: {
      targetHost: store.install?.targetHost,
    },
  });

  const client = useApiClient();
  const clanUri = useClanURI();
  // TODO: push values to the parent form Store
  const handleSubmit: SubmitHandler<ConfigureAdressForm> = async (
    values,
    event,
  ) => {
    console.log("targetHost set", values);
    set("install", (s) => ({ ...s, targetHost: values.targetHost }));

    // Here you would typically trigger the ISO creation process
    stepSignal.next();
    console.log("Shit doesnt work", values);
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
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);
  const hardwareQuery = useMachineHardwareSummary(
    useClanURI(),
    store.install.machineName,
  );

  const handleNext = () => {
    stepSignal.next();
  };
  const clanUri = useClanURI();

  const client = useApiClient();

  const handleUpdateSummary = async () => {
    // TODO: Debounce
    const call = client.fetch("run_machine_hardware_info", {
      target_host: {
        address: store.install.targetHost,
      },
      opts: {
        machine: {
          flake: {
            identifier: clanUri,
          },
          name: store.install.machineName,
        },
      },
    });
    await call.result;
    hardwareQuery.refetch();
  };

  const reportExists = () => hardwareQuery?.data?.hardware_config !== "none";

  return (
    <StepLayout
      body={
        <div class="flex flex-col gap-2">
          <Fieldset>
            <Orienter orientation="horizontal">
              <Typography hierarchy="label" size="xs" weight="bold">
                Hardware Report
              </Typography>
              <Button
                hierarchy="secondary"
                startIcon="Report"
                onClick={handleUpdateSummary}
              >
                Update hardware report
              </Button>
            </Orienter>
            <Divider orientation="horizontal" />
            <Show when={hardwareQuery.isLoading}>Loading...</Show>
            <Show when={hardwareQuery.data}>
              {(d) => (
                <Alert
                  icon={reportExists() ? "Checkmark" : "Close"}
                  type={reportExists() ? "info" : "warning"}
                  title={
                    reportExists()
                      ? "Hardware report exists"
                      : "Hardware report not found"
                  }
                />
              )}
            </Show>
          </Fieldset>
        </div>
      }
      footer={
        <div class="flex justify-between">
          <BackButton />
          <NextButton
            type="button"
            onClick={handleNext}
            disabled={hardwareQuery.isLoading || !reportExists()}
          >
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
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<DiskForm>({
    validate: valiForm(DiskSchema),
    initialValues: {
      mainDisk: store.install?.mainDisk,
    },
  });

  const handleSubmit: SubmitHandler<DiskForm> = (values, event) => {
    console.log("disk submitted", values);

    set("install", (s) => ({ ...s, mainDisk: values.mainDisk }));
    stepSignal.next();
  };

  const diskSchemasQuery = useMachineDiskSchemas(
    useClanURI(),
    store.install.machineName,
  );

  return (
    <Form onSubmit={handleSubmit}>
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Fieldset>
              <Field name="mainDisk">
                {(field, props) => (
                  <Select
                    zIndex={100}
                    {...props}
                    value={field.value}
                    error={field.error}
                    required
                    label={{
                      label: "Main disk",
                      description: "Select the disk to install the system on",
                    }}
                    getOptions={async () => {
                      if (!diskSchemasQuery.data) {
                        await diskSchemasQuery.refetch();
                      }
                      const placeholders =
                        diskSchemasQuery.data?.["single-disk"].placeholders;
                      const mainDiskOptions = placeholders?.["mainDisk"];

                      return (
                        mainDiskOptions?.options?.map((disk) => ({
                          value: disk,
                          label: disk,
                        })) || []
                      );
                    }}
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

const ConfigureData = () => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);

  const generatorsQuery = useMachineGenerators(
    useClanURI(),
    store.install.machineName,
  );

  return (
    <>
      <Show when={generatorsQuery.isLoading}>
        Checking credentials & data...
      </Show>
      <Show when={generatorsQuery.data}>
        {(generators) => <PromptsFields generators={generators()} />}
      </Show>
    </>
  );
};

type PromptGroup = {
  name: string;
  fields: {
    prompt: Prompt;
    generator: string;
    value?: string | null;
  }[];
};

type Prompt = NonNullable<MachineGenerators[number]["prompts"]>[number];
type PromptForm = {
  promptValues: PromptValues;
};

interface PromptsFieldsProps {
  generators: MachineGenerators;
}
const PromptsFields = (props: PromptsFieldsProps) => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const groupsObj: Record<string, PromptGroup> = props.generators.reduce(
    (acc, generator) => {
      if (!generator.prompts) {
        return acc;
      }
      for (const prompt of generator.prompts) {
        const groupName = (
          prompt.display?.group || generator.name
        ).toUpperCase();

        if (!acc[groupName]) acc[groupName] = { fields: [], name: groupName };

        acc[groupName].fields.push({
          prompt,
          generator: generator.name,
          value: prompt.previous_value,
        });
      }
      return acc;
    },
    {} as Record<string, PromptGroup>,
  );
  const groups = Object.values(groupsObj);

  const [formStore, { Form, Field }] = createForm<PromptForm>({
    initialValues: {
      promptValues: store.install?.promptValues || {},
    },
  });

  console.log(groups);

  const handleSubmit: SubmitHandler<PromptForm> = (values, event) => {
    console.log("vars submitted", values);

    set("install", (s) => ({ ...s, promptValues: values.promptValues }));
    console.log("vars preloaded");
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  return (
    <Form onSubmit={handleSubmit}>
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <For each={groups}>
              {(group) => (
                <Fieldset legend={group.name}>
                  <For each={group.fields}>
                    {(fieldInfo) => (
                      <Field
                        name={`promptValues.${fieldInfo.generator}.${fieldInfo.prompt.name}`}
                      >
                        {(f, props) => (
                          <TextInput
                            {...f}
                            label={
                              fieldInfo.prompt.display?.label ||
                              fieldInfo.prompt.name
                            }
                            description={fieldInfo.prompt.description}
                            value={f.value || fieldInfo.value || ""}
                            required={fieldInfo.prompt.display?.required}
                            orientation="horizontal"
                            validationState={
                              getError(
                                formStore,
                                `promptValues.${fieldInfo.generator}.${fieldInfo.prompt.name}`,
                              )
                                ? "invalid"
                                : "valid"
                            }
                            input={{
                              type: fieldInfo.prompt.prompt_type.includes(
                                "hidden",
                              )
                                ? "password"
                                : "text",
                              ...props,
                            }}
                          />
                        )}
                      </Field>
                    )}
                  </For>
                </Fieldset>
              )}
            </For>
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
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const client = useApiClient();

  const clanUri = useClanURI();
  const handleInstall = async () => {
    // Here you would typically trigger the installation process
    console.log("Installation started");

    const setDisk = client.fetch("set_machine_disk_schema", {
      machine: {
        flake: {
          identifier: clanUri,
        },
        name: store.install.machineName,
      },
      schema_name: "single-disk",
      placeholders: {
        mainDisk: store.install.mainDisk,
      },
      force: true,
    });

    const diskResult = await setDisk.result; // Wait for the disk schema to be set
    if (diskResult.status === "error") {
      console.error("Error setting disk schema:", diskResult.errors);
      return;
    }

    const runGenerators = client.fetch("run_generators", {
      all_prompt_values: store.install.promptValues,
      base_dir: clanUri,
      machine_name: store.install.machineName,
    });
    stepSignal.setActiveStep("install:progress");

    await runGenerators.result; // Wait for the generators to run

    const runInstall = client.fetch("run_machine_install", {
      opts: {
        machine: {
          name: store.install.machineName,
          flake: {
            identifier: clanUri,
          },
        },
      },
      target_host: {
        address: store.install.targetHost,
      },
    });
    set("install", (s) => ({
      ...s,
      progress: runInstall,
    }));

    await runInstall.result; // Wait for the installation to finish

    stepSignal.setActiveStep("install:done");
  };
  return (
    <StepLayout
      body={
        <div class="flex flex-col gap-4">
          <Fieldset legend="Address Configuration">
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
              <Display label="Main Disk" value={store.install.mainDisk} />
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
  const stepSignal = useStepper<InstallSteps>();
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);

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
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);

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
            onClick={() => store.done()}
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
