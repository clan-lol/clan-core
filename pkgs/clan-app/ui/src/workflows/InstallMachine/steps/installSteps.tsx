import { Typography } from "@/src/components/Typography/Typography";
import { BackButton, NextButton, StepLayout } from "../../Steps";
import {
  createForm,
  FieldValues,
  getError,
  getValue,
  SubmitHandler,
  valiForm,
} from "@modular-forms/solid";
import { Fieldset } from "@/src/components/Form/Fieldset";
import * as v from "valibot";
import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  InstallSteps,
  InstallStoreType,
  PromptValues,
} from "../InstallMachine";
import { TextInput } from "@/src/components/Form/TextInput";
import { Alert, AlertProps } from "@/src/components/Alert/Alert";
import { createSignal, For, Match, Show, Switch } from "solid-js";
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
import { ProcessMessage, useNotifyOrigin } from "@/src/hooks/notify";
import { Loader } from "@/src/components/Loader/Loader";
import { Button as KButton } from "@kobalte/core/button";

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
  port: v.optional(
    v.pipe(
      v.string(),
      v.transform((val) => (val === "" ? undefined : val)),
    ),
  ),
  password: v.optional(v.string()),
});

type ConfigureAdressForm = v.InferInput<typeof ConfigureAdressSchema>;

export const ConfigureAddress = (props: {
  next?: string;
  stepFinished: () => void;
  alert?: AlertProps;
}) => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<ConfigureAdressForm>({
    validate: valiForm(ConfigureAdressSchema),
    initialValues: {
      targetHost: store.install?.targetHost,
      port: store.install?.port,
    },
  });

  const [isReachable, setIsReachable] = createSignal<string | null>(null);
  const [loading, setLoading] = createSignal<boolean>(false);

  const client = useApiClient();
  // TODO: push values to the parent form Store
  const handleSubmit: SubmitHandler<ConfigureAdressForm> = async (
    values,
    event,
  ) => {
    console.log("targetHost set", values);
    set("install", (s) => ({
      ...s,
      targetHost: values.targetHost,
      port: values.port,
      password: values.password,
    }));

    stepSignal.next();
    props.stepFinished?.();
  };

  const tryReachable = async () => {
    const address = getValue(formStore, "targetHost");
    if (!address) {
      return;
    }

    const portValue = getValue(formStore, "port");
    const port = portValue ? parseInt(portValue, 10) : undefined;
    const password = getValue(formStore, "password") || undefined;

    setLoading(true);
    const call = client.fetch("check_machine_ssh_login", {
      remote: {
        address,
        ...(port && { port }),
        password: password,
        ssh_options: {
          StrictHostKeyChecking: "no",
          UserKnownHostsFile: "/dev/null",
        },
      },
    });
    const result = await call.result;
    setLoading(false);

    console.log("SSH login check result:", result);
    if (result.status === "success") {
      setIsReachable(address);
    }
  };

  return (
    <Form onSubmit={handleSubmit} class="h-full">
      <StepLayout
        body={
          <div class="flex flex-col gap-2">
            <Show when={props.alert}>{(alert) => <Alert {...alert()} />}</Show>
            <Fieldset>
              <Field name="targetHost">
                {(field, props) => (
                  <TextInput
                    {...field}
                    label="IP Address"
                    description="Hostname of the machine"
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
              <Field name="port">
                {(field, props) => (
                  <TextInput
                    {...field}
                    label="SSH Port"
                    description="SSH port (default: 22)"
                    value={field.value}
                    orientation="horizontal"
                    validationState={
                      getError(formStore, "port") ? "invalid" : "valid"
                    }
                    input={{
                      ...props,
                      placeholder: "22",
                      type: "number",
                    }}
                  />
                )}
              </Field>
              <Field name="password">
                {(field, props) => (
                  <TextInput
                    {...field}
                    label="Password"
                    description="SSH password (optional)"
                    value={field.value}
                    orientation="horizontal"
                    validationState={
                      getError(formStore, "port") ? "invalid" : "valid"
                    }
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

            <Show
              when={
                !isReachable() ||
                isReachable() !== getValue(formStore, "targetHost")
              }
              fallback={
                <NextButton type="submit">{props.next || "next"}</NextButton>
              }
            >
              <Button
                endIcon="ArrowRight"
                onClick={tryReachable}
                hierarchy="secondary"
                loading={loading()}
              >
                Test Connection
              </Button>
            </Show>
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

  const [updatingHardwareReport, setUpdatingHardwareReport] =
    createSignal(false);

  const handleUpdateSummary = async () => {
    if (!store.install.targetHost) {
      console.error(
        "Target host not set, this is required for updating hardware report",
      );
      setUpdatingHardwareReport(false);
      return;
    }

    setUpdatingHardwareReport(true);

    const port = store.install.port
      ? parseInt(store.install.port, 10)
      : undefined;

    try {
      // TODO: Debounce
      const call = client.fetch("run_machine_hardware_info", {
        target_host: {
          address: store.install.targetHost,
          port,
          password: store.install.password,
          ssh_options: {
            StrictHostKeyChecking: "no",
            UserKnownHostsFile: "/dev/null",
          },
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
      await hardwareQuery.refetch();
    } finally {
      setUpdatingHardwareReport(false);
    }
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
                disabled={hardwareQuery.isLoading || updatingHardwareReport()}
                hierarchy="secondary"
                startIcon="Report"
                onClick={handleUpdateSummary}
                class="flex gap-3"
                loading={hardwareQuery.isFetching || updatingHardwareReport()}
              >
                Update hardware report
              </Button>
            </Orienter>
            <Divider orientation="horizontal" />

            <Show when={hardwareQuery.data}>
              {(d) => (
                <Alert
                  size="s"
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
    <Form onSubmit={handleSubmit} class="h-full">
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

export const ConfigureData = () => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);

  const generatorsQuery = useMachineGenerators(
    useClanURI(),
    store.install.machineName,
  );

  return (
    <>
      <Show when={generatorsQuery.isLoading}>
        <div class="relative flex w-full flex-col items-center justify-end ">
          <div class="z-10 mb-6 flex w-full max-w-md flex-col items-center gap-2 pt-4">
            <Loader />
            <Typography
              hierarchy="title"
              size="default"
              weight="bold"
              color="inherit"
            >
              Credentials & Data
            </Typography>
            <Typography hierarchy="label" size="default" color="secondary">
              Loading Machine Generators ...
            </Typography>
          </div>
        </div>
      </Show>
      <Show when={generatorsQuery.data}>
        {(generators) => <PromptsFields generators={generators()} />}
      </Show>
    </>
  );
};

interface PromptGroup {
  name: string;
  fields: {
    prompt: Prompt;
    generator: string;
    value?: string | null;
  }[];
}

type Prompt = NonNullable<MachineGenerators[number]["prompts"]>[number];
interface PromptForm extends FieldValues {
  promptValues: PromptValues;
}

const sanitize = (name: string) => {
  return name.replace(".", "__dot__");
};
const restore = (name: string) => {
  return name.replace("__dot__", ".");
};

const transformPromptValues = (
  values: PromptValues,
  transform: (s: string) => string,
): PromptValues =>
  Object.fromEntries(
    Object.entries(values).map(([key, value]) => [
      transform(key),
      Object.fromEntries(
        Object.entries(value).map(([k, v]) => [transform(k), v]),
      ),
    ]),
  );
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
          prompt: {
            ...prompt,
            name: sanitize(prompt.name),
          },
          generator: sanitize(generator.name),
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
      promptValues: transformPromptValues(
        store.install?.promptValues || {},
        sanitize,
      ),
    },
  });

  console.log(groups);

  const handleSubmit: SubmitHandler<PromptForm> = (values, event) => {
    const restoredValues: PromptValues = transformPromptValues(
      values.promptValues,
      restore,
    );

    console.log("vars submitted", restoredValues);

    set("install", (s) => ({ ...s, promptValues: restoredValues }));
    console.log("vars preloaded");
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  return (
    <Form onSubmit={handleSubmit} class="h-full">
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
                        {(f, props) => {
                          const defaultInputType =
                            fieldInfo.prompt.prompt_type.includes("hidden")
                              ? "password"
                              : "text";

                          const [inputType, setInputType] =
                            createSignal(defaultInputType);

                          return (
                            <TextInput
                              {...f}
                              label={
                                fieldInfo.prompt.display?.label ||
                                fieldInfo.prompt.name
                              }
                              endComponent={(local) => (
                                <Show when={defaultInputType === "password"}>
                                  <KButton
                                    onClick={() => {
                                      setInputType((type) =>
                                        type === "password"
                                          ? "text"
                                          : "password",
                                      );
                                    }}
                                  >
                                    <Icon
                                      icon={
                                        inputType() == "password"
                                          ? "EyeClose"
                                          : "EyeOpen"
                                      }
                                      color="quaternary"
                                      inverted={local.inverted}
                                    />
                                  </KButton>
                                </Show>
                              )}
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
                                type: inputType(),
                                ...props,
                              }}
                            />
                          );
                        }}
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

const Display = (props: { value?: string; label: string }) => {
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
    if (!store.install.mainDisk) {
      console.error("Main disk not set");
      return;
    }

    if (!store.install.targetHost) {
      console.error("Target host not set, this is required for installing");
      return;
    }
    stepSignal.setActiveStep("install:progress");

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

    set("install", (s) => ({
      ...s,
      prepareStep: "disk",
    }));
    const diskResult = await setDisk.result; // Wait for the disk schema to be set
    if (diskResult.status === "error") {
      console.error("Error setting disk schema:", diskResult.errors);
      return;
    }

    // Extract generator names from prompt values
    // TODO: This is wrong. We need to extend run_generators to be able to compute
    //       a sane closure over a list of provided generators.
    const generators = Object.keys(store.install.promptValues || {});

    const runGenerators = client.fetch("run_generators", {
      generators: generators.length > 0 ? generators : undefined,
      prompt_values: store.install.promptValues,
      machines: [
        {
          name: store.install.machineName,
          flake: {
            identifier: clanUri,
          },
        },
      ],
    });

    set("install", (s) => ({
      ...s,
      prepareStep: "generators",
    }));
    await runGenerators.result; // Wait for the generators to run

    const port = store.install.port
      ? parseInt(store.install.port, 10)
      : undefined;

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
        port,
        password: store.install.password,
        ssh_options: {
          StrictHostKeyChecking: "no",
          UserKnownHostsFile: "/dev/null",
        },
      },
    });
    set("install", (s) => ({
      ...s,
      prepareStep: "install",
      progress: runInstall,
    }));

    await runInstall.result;

    stepSignal.setActiveStep("install:done");
  };
  return (
    <StepLayout
      body={
        <div class="flex flex-col gap-4">
          <Fieldset legend="Machine">
            <Orienter orientation="horizontal">
              <Display label="Name" value={store.install.machineName} />
            </Orienter>
            <Divider orientation="horizontal" />
            <Orienter orientation="horizontal">
              <Display label="Address" value={store.install.targetHost} />
            </Orienter>
            {store.install.port && (
              <>
                <Divider orientation="horizontal" />
                <Orienter orientation="horizontal">
                  <Display label="SSH Port" value={store.install.port} />
                </Orienter>
              </>
            )}
          </Fieldset>
          <Fieldset legend="Disk">
            <Orienter orientation="horizontal">
              <Display label="Disk Schema" value="Single" />
            </Orienter>
            <Divider orientation="horizontal" />
            <Orienter orientation="horizontal">
              <Display label="Main Disk" value={store.install?.mainDisk} />
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

type InstallTopic = [
  "generators",
  "upload-secrets",
  "nixos-anywhere",
  "formatting",
  "rebooting",
  "installing",
][number];

const InstallProgress = () => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);

  const handleCancel = async () => {
    const progress = store.install.progress;
    if (progress) {
      await progress.cancel();
    }
    stepSignal.previous();
  };
  const installState = useNotifyOrigin<ProcessMessage<unknown, InstallTopic>>(
    "run_machine_install",
  );

  return (
    <div class="relative flex size-full flex-col items-center justify-end bg-inv-4">
      <img
        src="/logos/usb-stick-min.png"
        alt="usb logo"
        class="absolute top-2 z-0"
      />
      <div class="z-10 mb-6 flex w-full max-w-md flex-col items-center gap-2 fg-inv-1">
        <Typography
          hierarchy="title"
          size="default"
          weight="bold"
          color="inherit"
        >
          Machine is being installed
        </Typography>
        <LoadingBar />
        <Typography
          hierarchy="label"
          size="default"
          class=""
          color="secondary"
          inverted
        >
          <Switch fallback={"Waiting for preparation to start..."}>
            <Match when={store.install.prepareStep === "disk"}>
              Configuring disk schema ...
            </Match>
            <Match when={store.install.prepareStep === "generators"}>
              Provisioning services ...
            </Match>
            <Match when={store.install.prepareStep === "install"}>
              {/* Progress after the run_machine_install api call */}
              <Switch fallback={"Waiting for installation to start..."}>
                <Match when={installState()?.topic === "generators"}>
                  Checking services ...
                </Match>
                <Match when={installState()?.topic === "upload-secrets"}>
                  Uploading Credentials ...
                </Match>
                <Match when={installState()?.topic === "nixos-anywhere"}>
                  Running nixos-anywhere ...
                </Match>
                <Match when={installState()?.topic === "formatting"}>
                  Formatting ...
                </Match>
                <Match when={installState()?.topic === "installing"}>
                  Installing ...
                </Match>
                <Match when={installState()?.topic === "rebooting"}>
                  Rebooting ...
                </Match>
              </Switch>
            </Match>
          </Switch>
        </Typography>
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

interface InstallDoneProps {
  onDone: () => void;
}
const InstallDone = (props: InstallDoneProps) => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);

  return (
    <div class="flex size-full flex-col items-center justify-center bg-inv-4">
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
            onClick={() => props.onDone()}
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
    class: "max-w-[30rem] h-[18rem]",
  },
  {
    id: "install:done",
    content: InstallDone,
    isSplash: true,
    class: "max-w-[30rem] h-[18rem]",
  },
] as const;
