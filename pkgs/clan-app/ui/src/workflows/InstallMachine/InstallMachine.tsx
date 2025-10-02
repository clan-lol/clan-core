import { Modal } from "@/src/components/Modal/Modal";
import {
  createStepper,
  getStepStore,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { Show } from "solid-js";
import { Dynamic } from "solid-js/web";
import { initialSteps } from "./steps/Initial";
import { createInstallerSteps } from "./steps/createInstaller";
import { installSteps } from "./steps/installSteps";
import { ApiCall } from "@/src/hooks/api";

import cx from "classnames";

interface InstallStepperProps {
  onDone: () => void;
}
const InstallStepper = (props: InstallStepperProps) => {
  const stepSignal = useStepper<InstallSteps>();
  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  return (
    <Dynamic
      component={stepSignal.currentStep().content}
      onDone={props.onDone}
    />
  );
};

export interface InstallModalProps {
  machineName: string;
  initialStep?: InstallSteps[number]["id"];
  mount?: Node;
  onClose?: () => void;
  open: boolean;
}

const steps = [
  ...initialSteps,
  ...createInstallerSteps,
  ...installSteps,
] as const;

export type InstallSteps = typeof steps;
export interface InstallStoreType {
  flash: {
    ssh_file: string;
    device: string;
    progress: ApiCall<"run_machine_flash">;
  };
  install: {
    targetHost?: string;
    port?: string;
    password?: string;
    machineName: string;
    mainDisk?: string;
    // ...TODO Vars
    progress: AbortController;
    promptValues: PromptValues;
    prepareStep: "disk" | "generators" | "install";
  };
  done: () => void;
}
export type PromptValues = Record<string, Record<string, string>>;

export const InstallModal = (props: InstallModalProps) => {
  const stepper = createStepper(
    {
      steps,
    },
    { initialStep: props.initialStep || "init" },
  );

  const MetaHeader = () => {
    // @ts-expect-error some steps might not have
    const HeaderComponent = () => stepper.currentStep()?.title;
    return (
      <Show when={HeaderComponent()}>
        {(C) => <Dynamic component={C()} machineName={props.machineName} />}
      </Show>
    );
  };
  const [store, set] = getStepStore<InstallStoreType>(stepper);

  set("install", { machineName: props.machineName });

  // allows each step to adjust the size of the modal
  const sizeClasses = () => {
    const defaultClass = "max-w-3xl h-[30rem]";

    const currentStep = stepper.currentStep();
    if (!currentStep) {
      return defaultClass;
    }

    switch (currentStep.id) {
      case "create:progress":
      case "create:done":
      case "install:progress":
      case "install:done":
        return currentStep.class;

      default:
        return defaultClass;
    }
  };

  const onClose = async () => {
    props.onClose?.();
  };

  return (
    <StepperProvider stepper={stepper}>
      <Modal
        class={cx("w-screen", sizeClasses())}
        title="Install machine"
        onClose={onClose}
        open={props.open}
        // @ts-expect-error some steps might not have
        metaHeader={stepper.currentStep()?.title ? <MetaHeader /> : undefined}
        // @ts-expect-error some steps might not have
        disablePadding={stepper.currentStep()?.isSplash}
      >
        <InstallStepper onDone={onClose} />
      </Modal>
    </StepperProvider>
  );
};
