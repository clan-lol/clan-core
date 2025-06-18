import { callApi, SuccessData } from "@/src/api";
import {
  createForm,
  getValue,
  getValues,
  setValue,
} from "@modular-forms/solid";
import { createSignal, Match, Switch } from "solid-js";
import { useClanContext } from "@/src/contexts/clan";
import { HWStep } from "../install/hardware-step";
import { DiskStep } from "../install/disk-step";
import { VarsStep } from "../install/vars-step";
import { SummaryStep } from "../install/summary-step";
import { InstallStepper } from "./InstallStepper";
import { InstallStepNavigation } from "./InstallStepNavigation";
import { InstallProgress } from "./InstallProgress";
import { DiskValues } from "../install/disk-step";
import { AllStepsValues } from "../types";
import { ResponseData } from "@modular-forms/solid";

type MachineData = SuccessData<"get_machine_details">;
type StepIdx = "1" | "2" | "3" | "4";

const INSTALL_STEPS = {
  HARDWARE: "1" as StepIdx,
  DISK: "2" as StepIdx,
  VARS: "3" as StepIdx,
  SUMMARY: "4" as StepIdx,
} as const;

const PROGRESS_DELAYS = {
  INITIAL: 10 * 1000,
  BUILD: 10 * 1000,
  FORMAT: 10 * 1000,
  COPY: 20 * 1000,
  REBOOT: 10 * 1000,
} as const;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

interface InstallMachineProps {
  name?: string;
  machine: MachineData;
}

export function InstallMachine(props: InstallMachineProps) {
  const { activeClanURI } = useClanContext();
  const curr = activeClanURI();
  const { name } = props;

  if (!curr || !name) {
    return <span>No Clan selected</span>;
  }

  const [formStore, { Form, Field }] = createForm<
    AllStepsValues,
    ResponseData
  >();
  const [isDone, setIsDone] = createSignal<boolean>(false);
  const [isInstalling, setIsInstalling] = createSignal<boolean>(false);
  const [progressText, setProgressText] = createSignal<string>();
  const [step, setStep] = createSignal<StepIdx>(INSTALL_STEPS.HARDWARE);

  const nextStep = () => {
    const currentStepNum = parseInt(step());
    const nextStepNum = Math.min(currentStepNum + 1, 4);
    setStep(nextStepNum.toString() as StepIdx);
  };

  const prevStep = () => {
    const currentStepNum = parseInt(step());
    const prevStepNum = Math.max(currentStepNum - 1, 1);
    setStep(prevStepNum.toString() as StepIdx);
  };

  const isFirstStep = () => step() === INSTALL_STEPS.HARDWARE;
  const isLastStep = () => step() === INSTALL_STEPS.SUMMARY;

  const handleInstall = async (values: AllStepsValues) => {
    const curr_uri = activeClanURI();
    const diskValues = values["2"];

    if (!curr_uri || !props.name) {
      console.error("Missing clan URI or machine name");
      return;
    }

    try {
      setIsInstalling(true);

      const shouldUpdateDisk =
        JSON.stringify(props.machine.disk_schema?.placeholders) !==
        JSON.stringify(diskValues.placeholders);

      if (shouldUpdateDisk) {
        setProgressText("Setting up disk ... (1/5)");
        await callApi("set_machine_disk_schema", {
          machine: {
            flake: { identifier: curr_uri },
            name: props.name,
          },
          placeholders: diskValues.placeholders,
          schema_name: diskValues.schema,
          force: true,
        }).promise;
      }

      setProgressText("Installing machine ... (2/5)");

      const targetHostResponse = await callApi("get_host", {
        field: "targetHost",
        flake: { identifier: curr_uri },
        name: props.name,
      }).promise;

      if (
        targetHostResponse.status === "error" ||
        !targetHostResponse.data?.data
      ) {
        throw new Error("No target host found for the machine");
      }

      const installPromise = callApi("install_machine", {
        opts: {
          machine: {
            name: props.name,
            flake: { identifier: curr_uri },
            private_key: values.sshKey?.name,
          },
        },
        target_host: targetHostResponse.data.data,
      });

      await sleep(PROGRESS_DELAYS.INITIAL);
      setProgressText("Building machine ... (3/5)");
      await sleep(PROGRESS_DELAYS.BUILD);
      setProgressText("Formatting remote disk ... (4/5)");
      await sleep(PROGRESS_DELAYS.FORMAT);
      setProgressText("Copying system ... (5/5)");
      await sleep(PROGRESS_DELAYS.COPY);
      setProgressText("Rebooting remote system ...");
      await sleep(PROGRESS_DELAYS.REBOOT);

      const installResponse = await installPromise;
      setIsDone(true);
    } catch (error) {
      console.error("Installation failed:", error);
      setIsInstalling(false);
    }
  };

  return (
    <Switch
      fallback={
        <div class="flex min-h-screen flex-col gap-0">
          <InstallStepper currentStep={step()} />
          <Switch fallback={<div>Step not found</div>}>
            <Match when={step() === INSTALL_STEPS.HARDWARE}>
              <HWStep
                machine_id={props.name || ""}
                dir={activeClanURI() || ""}
                handleNext={(data) => {
                  const prev = getValue(formStore, "1");
                  setValue(formStore, "1", { ...prev, ...data });
                  nextStep();
                }}
                initial={getValue(formStore, "1")}
                footer={
                  <InstallStepNavigation
                    currentStep={step()}
                    isFirstStep={isFirstStep()}
                    isLastStep={isLastStep()}
                    onPrevious={prevStep}
                  />
                }
              />
            </Match>

            <Match when={step() === INSTALL_STEPS.DISK}>
              <DiskStep
                machine_id={props.name || ""}
                dir={activeClanURI() || ""}
                footer={
                  <InstallStepNavigation
                    currentStep={step()}
                    isFirstStep={isFirstStep()}
                    isLastStep={isLastStep()}
                    onPrevious={prevStep}
                  />
                }
                handleNext={(data) => {
                  const prev = getValue(formStore, "2");
                  setValue(formStore, "2", { ...prev, ...data });
                  nextStep();
                }}
                initial={
                  {
                    placeholders: props.machine.disk_schema?.placeholders || {
                      mainDisk: "",
                    },
                    schema: props.machine.disk_schema?.schema_name || "",
                    schema_name: props.machine.disk_schema?.schema_name || "",
                    ...getValue(formStore, "2"),
                    initialized: !!props.machine.disk_schema,
                  } as DiskValues
                }
              />
            </Match>

            <Match when={step() === INSTALL_STEPS.VARS}>
              <VarsStep
                machine_id={props.name || ""}
                dir={activeClanURI() || ""}
                handleNext={(data) => {
                  const prev = getValue(formStore, "3");
                  setValue(formStore, "3", { ...prev, ...data });
                  nextStep();
                }}
                initial={getValue(formStore, "3") || {}}
                footer={
                  <InstallStepNavigation
                    currentStep={step()}
                    isFirstStep={isFirstStep()}
                    isLastStep={isLastStep()}
                    onPrevious={prevStep}
                  />
                }
              />
            </Match>

            <Match when={step() === INSTALL_STEPS.SUMMARY}>
              <SummaryStep
                machine_id={props.name || ""}
                dir={activeClanURI() || ""}
                handleNext={() => nextStep()}
                initial={getValues(formStore) as AllStepsValues}
                footer={
                  <InstallStepNavigation
                    currentStep={step()}
                    isFirstStep={isFirstStep()}
                    isLastStep={isLastStep()}
                    onPrevious={prevStep}
                    onInstall={() =>
                      handleInstall(getValues(formStore) as AllStepsValues)
                    }
                  />
                }
              />
            </Match>
          </Switch>
        </div>
      }
    >
      <Match when={isInstalling()}>
        <InstallProgress
          machineName={props.name || ""}
          progressText={progressText()}
          isDone={isDone()}
          onCancel={() => setIsInstalling(false)}
        />
      </Match>
    </Switch>
  );
}
