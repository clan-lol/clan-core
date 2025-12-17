import { Typography } from "@/src/components/Typography/Typography";
import { BackButton, NextButton, StepLayout } from "@/src/components/Steps";
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
import { getStepStore, useStepper } from "@/src/components/Steps/stepper";
import { InstallSteps, InstallStoreType, PromptValues } from "..";
import { TextInput } from "@/src/components/Form/TextInput";
import { Alert, AlertProps } from "@/src/components/Alert/Alert";
import {
  batch,
  Component,
  createSignal,
  For,
  Match,
  onCleanup,
  Show,
  Suspense,
  Switch,
} from "solid-js";
import { Divider } from "@/src/components/Divider/Divider";
import { Orienter } from "@/src/components/Form/Orienter";
import { Button } from "@/src/components/Button/Button";
import { Select } from "@/src/components/Select/Select";
import { LoadingBar } from "@/src/components/LoadingBar/LoadingBar";
import Icon from "@/src/components/Icon/Icon";
import { Loader } from "@/src/components/Loader/Loader";
import { Button as KButton } from "@kobalte/core/button";
import usbLogo from "@/logos/usb-stick-min.png?url";
import {
  useMachineContext,
  useUIContext,
  MachineHardwareReport,
  MachineVarsPromptGroups,
  InstallMachineProgress,
} from "@/src/models";
import { createAsync } from "@solidjs/router";
import ModalHeading from "../../components/ModalHeading";

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
  const [machine, { isMachineSSHable }] = useMachineContext();
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<ConfigureAdressForm>({
    validate: valiForm(ConfigureAdressSchema),
    initialValues: {
      targetHost: store.install?.targetHost,
      port: store.install?.port,
    },
  });

  const [isReachable, setIsReachable] = createSignal(false);
  const [loading, setLoading] = createSignal<boolean>(false);
  // TODO: push values to the parent form Store
  const handleSubmit: SubmitHandler<ConfigureAdressForm> = async (
    values,
    event,
  ) => {
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
    await isMachineSSHable({
      address,
      port,
      password,
    });
    batch(() => {
      setLoading(false);
      setIsReachable(true);
    });
  };

  return (
    <Form
      onSubmit={handleSubmit}
      class="flex h-[30rem] w-svw max-w-3xl flex-col bg-white"
    >
      <ModalHeading text={`Installing: ${machine().id}`} />
      <div class="flex-1 p-4">
        <StepLayout
          body={
            <div class="flex flex-col gap-2">
              <Show when={props.alert}>
                {(alert) => <Alert {...alert()} />}
              </Show>
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
                when={!isReachable()}
                fallback={<NextButton type="submit">Next</NextButton>}
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
      </div>
    </Form>
  );
};

const CheckHardware = () => {
  const [machine, { getOrGenerateMachineHardwareReport }] = useMachineContext();
  const stepSignal = useStepper<InstallSteps>();
  const [store] = getStepStore<InstallStoreType>(stepSignal);

  const [machineHardwareReport, setMachineHardwareReport] = createSignal<
    MachineHardwareReport | null | undefined
  >();
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

    // TODO: Debounce
    const report = await getOrGenerateMachineHardwareReport({
      address: store.install.targetHost,
      port,
      password: store.install.password,
    });
    batch(() => {
      setUpdatingHardwareReport(false);
      setMachineHardwareReport(report);
    });
  };

  return (
    <div class="flex h-[30rem] w-svw max-w-3xl flex-col bg-white">
      <ModalHeading text={`Installing: ${machine().id}`} />
      <div class="flex-1 p-4">
        <StepLayout
          body={
            <div class="flex flex-col gap-2">
              <Fieldset>
                <Orienter orientation="horizontal">
                  <Typography hierarchy="label" size="xs" weight="bold">
                    Hardware Report
                  </Typography>
                  <Button
                    disabled={updatingHardwareReport()}
                    hierarchy="secondary"
                    icon="Report"
                    loading={updatingHardwareReport()}
                    in="CheckHardware"
                    onClick={handleUpdateSummary}
                  >
                    Update hardware report
                  </Button>
                </Orienter>

                <Show when={machineHardwareReport() !== undefined}>
                  <Divider orientation="horizontal" />
                  <Alert
                    size="s"
                    icon={machineHardwareReport() ? "Checkmark" : "Close"}
                    type={machineHardwareReport() ? "info" : "warning"}
                    title={
                      machineHardwareReport()
                        ? "Hardware report exists"
                        : "Hardware report not found"
                    }
                  />
                </Show>
              </Fieldset>
            </div>
          }
          footer={
            <div class="flex justify-between">
              <BackButton />
              <NextButton
                type="button"
                onClick={() => stepSignal.next()}
                disabled={!machineHardwareReport()}
              >
                Next
              </NextButton>
            </div>
          }
        />
      </div>
    </div>
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
  const [machine, { getMachineDiskTemplates }] = useMachineContext();
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<DiskForm>({
    validate: valiForm(DiskSchema),
    initialValues: {
      mainDisk: store.install?.mainDisk,
    },
  });

  const handleSubmit: SubmitHandler<DiskForm> = (values, event) => {
    set("install", (s) => ({ ...s, mainDisk: values.mainDisk }));
    stepSignal.next();
  };

  return (
    <Form
      onSubmit={handleSubmit}
      class="flex h-[30rem] w-svw max-w-3xl flex-col bg-white"
    >
      <ModalHeading text={`Installing: ${machine().id}`} />
      <div class="flex-1 p-4">
        <StepLayout
          body={
            <div class="flex flex-col gap-2">
              <Fieldset>
                <Field name="mainDisk">
                  {(field, props) => (
                    <Select
                      // TODO: this value has to be greater than a dialog/modal's
                      // z-index, other wise the dropdown list won't display in a
                      // model. Make this value static
                      zIndex={10000}
                      {...props}
                      value={field.value}
                      error={field.error}
                      required
                      label={{
                        label: "Main disk",
                        description: "Select the disk to install the system on",
                      }}
                      getOptions={async () => {
                        const templates = await getMachineDiskTemplates();
                        return templates.all[
                          "single-disk"
                        ].placeholders.mainDisk.values.map((value) => ({
                          value,
                          label: value,
                        }));
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
      </div>
    </Form>
  );
};

export const ConfigureData = () => {
  const [, { getMachineVarsPromptGroups }] = useMachineContext();
  const stepSignal = useStepper<InstallSteps>();
  const [, setStore] = getStepStore<InstallStoreType>(stepSignal);
  const groups = createAsync(async () => await getMachineVarsPromptGroups());

  return (
    <>
      <Suspense
        fallback={
          <div class="relative flex h-[30rem] w-svw max-w-3xl items-center justify-center bg-white">
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
        }
      >
        <Show when={groups()}>
          {(groups) => {
            if (Object.keys(groups().all).length === 0) {
              setStore("install", "promptValues", {});
              stepSignal.next();
              return;
            }
            return <PromptsFields varsPromptGroups={groups()} />;
          }}
        </Show>
      </Suspense>
    </>
  );
};

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

const PromptsFields: Component<{
  varsPromptGroups: MachineVarsPromptGroups;
}> = (props) => {
  const [machine] = useMachineContext();
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [formStore, { Form, Field }] = createForm<PromptForm>({
    initialValues: {
      promptValues: transformPromptValues(
        store.install?.promptValues || {},
        sanitize,
      ),
    },
  });

  const handleSubmit: SubmitHandler<PromptForm> = (values, event) => {
    const restoredValues: PromptValues = transformPromptValues(
      values.promptValues,
      restore,
    );

    set("install", (s) => ({ ...s, promptValues: restoredValues }));
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  return (
    <Form
      onSubmit={handleSubmit}
      class="flex h-[30rem] w-svw max-w-3xl flex-col bg-white"
    >
      <ModalHeading text={`Installing: ${machine().id}`} />
      <div class="flex-1 p-4">
        <StepLayout
          body={
            <div class="flex flex-col gap-2">
              <For each={props.varsPromptGroups.sorted}>
                {(group) => (
                  <Fieldset legend={group.id}>
                    <For each={group.prompts.sorted}>
                      {(prompt) => (
                        <Field
                          name={`promptValues.${prompt.generator}.${prompt.id}`}
                        >
                          {(f, props) => {
                            const inputType =
                              prompt.type === "hidden" ? "password" : "text";

                            const [isCleartext, setIsCleartext] =
                              createSignal(false);

                            const [value, setValue] = createSignal(
                              prompt.value,
                            );

                            return (
                              <TextInput
                                {...f}
                                label={prompt.name}
                                endComponent={(local) => (
                                  <Show when={inputType === "password"}>
                                    <KButton
                                      onClick={() => {
                                        setIsCleartext(!isCleartext());
                                      }}
                                    >
                                      <Icon
                                        icon={
                                          isCleartext() ? "EyeClose" : "EyeOpen"
                                        }
                                        color="quaternary"
                                        inverted={local.inverted}
                                      />
                                    </KButton>
                                  </Show>
                                )}
                                description={prompt.description}
                                value={value()}
                                onChange={setValue}
                                required={prompt.required}
                                orientation="horizontal"
                                validationState={
                                  getError(
                                    formStore,
                                    `promptValues.${prompt.generator}.${prompt.id}`,
                                  )
                                    ? "invalid"
                                    : "valid"
                                }
                                input={{
                                  type: isCleartext() ? "text" : inputType,
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
      </div>
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
  const [machine] = useMachineContext();
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const handleInstall = async () => {
    stepSignal.setActiveStep("install:done");
  };
  return (
    <div class="flex h-[30rem] w-svw max-w-3xl flex-col bg-white">
      <ModalHeading text="Summary" />
      <div class="flex-1 p-4">
        <StepLayout
          body={
            <div class="flex flex-col gap-4">
              <Fieldset legend="Machine">
                <Orienter orientation="horizontal">
                  <Display label="Name" value={machine().id} />
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
      </div>
    </div>
  );
};

const InstallDone = () => {
  const [, { closeModal }] = useUIContext();
  const [, { installMachine }] = useMachineContext();
  const stepSignal = useStepper<InstallSteps>();
  const [store] = getStepStore<InstallStoreType>(stepSignal);
  const [progress, setProgress] = createSignal<
    InstallMachineProgress | undefined
  >();

  const controller = new AbortController();
  const done = createAsync(async () => {
    await installMachine({
      signal: controller.signal,
      ssh: {
        address: store.install.targetHost!,
        port: store.install.port ? parseInt(store.install.port, 10) : undefined,
        password: store.install.password,
      },
      diskPath: store.install.mainDisk!,
      varsPromptValues: store.install.promptValues,
      onProgress: setProgress,
    });
    return true;
  });
  const handleCancel = async () => {
    controller.abort();
    stepSignal.previous();
  };

  onCleanup(() => {
    controller.abort();
  });

  return (
    <Suspense
      fallback={
        <div class="relative flex h-72 w-svw max-w-[30rem] flex-col items-center justify-end bg-inv-4">
          <img src={usbLogo} alt="usb logo" class="absolute top-2 z-0" />
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
            <Typography hierarchy="label" color="secondary" inverted>
              <Switch fallback={"Waiting for preparation to start..."}>
                <Match when={progress() === "disk"}>
                  Configuring disk schema ...
                </Match>
                <Match when={progress() === "varsPrompts"}>
                  Provisioning services ...
                </Match>
                <Match when={progress() === "generators"}>
                  Checking services ...
                </Match>
                <Match when={progress() === "upload-secrets"}>
                  Uploading Credentials ...
                </Match>
                <Match when={progress() === "nixos-anywhere"}>
                  Running nixos-anywhere ...
                </Match>
                <Match when={progress() === "formatting"}>Formatting ...</Match>
                <Match when={progress() === "installing"}>Installing ...</Match>
                <Match when={progress() === "rebooting"}>Rebooting ...</Match>
              </Switch>
            </Typography>
            <Button
              hierarchy="primary"
              elasticity="fit"
              size="s"
              in="InstallProgress"
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </div>
        </div>
      }
    >
      <Show when={done()}>
        <div class="flex size-full h-72 w-svw max-w-[30rem] flex-col items-center justify-center bg-inv-4">
          <div class="flex w-full max-w-md flex-col items-center gap-3 py-6 fg-inv-1">
            <div class="rounded-full bg-semantic-success-4">
              <Icon icon="Checkmark" in="WorkflowPanelTitle" />
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
                onClick={() => closeModal()}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      </Show>
    </Suspense>
  );
};

export const installSteps = [
  {
    id: "install:address",
    content: ConfigureAddress,
  },
  {
    id: "install:check-hardware",
    content: CheckHardware,
  },
  {
    id: "install:disk",
    content: ConfigureDisk,
  },
  {
    id: "install:data",
    content: ConfigureData,
  },
  {
    id: "install:summary",
    content: InstallSummary,
  },
  {
    id: "install:done",
    content: InstallDone,
    isSplash: true,
    class: "max-w-[30rem] h-[18rem]",
  },
] as const;
