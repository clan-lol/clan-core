import {
  createStepper,
  StepperProvider,
  useStepper,
} from "@/src/components/Steps/stepper";
import { Component } from "solid-js";
import { Dynamic } from "solid-js/web";
import { initialSteps } from "./steps/Initial";
import { createInstallerSteps } from "./steps/createInstaller";
import { installSteps } from "./steps/installSteps";

import { MachineContextProvider, Modal, useUIContext } from "@/src/models";
import TitledModal from "../components/TitledModal";

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
    <TitledModal title="Install machine">
      <MachineContextProvider value={() => modal.machine}>
        <StepperProvider stepper={stepper}>
          <InstallStepper />
        </StepperProvider>
      </MachineContextProvider>
    </TitledModal>
  );
};
export default InstallMachine;

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
  };
  install: {
    targetHost?: string;
    port?: string;
    password?: string;
    mainDisk?: string;
    promptValues: PromptValues;
  };
  done: () => void;
}
export type PromptValues = Record<string, Record<string, string>>;
