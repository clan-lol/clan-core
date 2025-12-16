import {
  createStepper,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { Component } from "solid-js";
import { Dynamic } from "solid-js/web";
import { initialSteps } from "./steps/Initial";
import { createInstallerSteps } from "./steps/createInstaller";
import { installSteps } from "./steps/installSteps";
import { ApiCall } from "@/src/hooks/api";

import { ModalConfig } from "..";
import { MachineContextProvider, Modal, useUIContext } from "@/src/models";

const InstallMachine: Component = () => {
  const [ui] = useUIContext();
  const modal = ui.modal as Extract<Modal, { type: "InstallMachine" }>;
  const stepper = createStepper(
    {
      steps,
    },
    { initialStep: "init" },
  );

  return (
    <MachineContextProvider value={() => modal.machine}>
      <StepperProvider stepper={stepper}>
        <InstallStepper />
      </StepperProvider>
    </MachineContextProvider>
  );
};
export default InstallMachine;

export const config: ModalConfig = {
  title: "Install machine",
};

const InstallStepper: Component = () => {
  const stepSignal = useStepper<InstallSteps>();

  return <Dynamic component={stepSignal.currentStep().content} />;
};

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
    mainDisk?: string;
    // ...TODO Vars
    progress: AbortController;
    promptValues: PromptValues;
    prepareStep: "disk" | "generators" | "install";
  };
  done: () => void;
}
export type PromptValues = Record<string, Record<string, string>>;
