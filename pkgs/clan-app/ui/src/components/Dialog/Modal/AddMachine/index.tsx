import {
  createStepper,
  defineSteps,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { GeneralForm, StepGeneral } from "./StepGeneral";
import { Component } from "solid-js";
import { StepHost } from "./StepHost";
import { StepTags } from "./StepTags";
import { StepProgress } from "./StepProgress";
import { Dynamic } from "solid-js/web";
import { ModalConfig } from "..";

const AddMachine: Component = () => {
  const stepper = createStepper(
    {
      steps,
    },
    {
      initialStep: "general",
    },
  );

  return (
    <StepperProvider stepper={stepper}>
      <AddMachineStepper />
    </StepperProvider>
  );
};
export default AddMachine;

export const config: ModalConfig = {
  title: "Add Machine",
};

const AddMachineStepper: Component = () => {
  const stepSignal = useStepper<AddMachineSteps>();

  return <Dynamic component={stepSignal.currentStep().content} />;
};

export interface AddMachineStoreType {
  general: GeneralForm;
  deploy: {
    targetHost?: string;
  };
  tags: {
    tags: string[];
  };
  error?: string;
}

const steps = defineSteps([
  {
    id: "general",
    content: StepGeneral,
  },
  {
    id: "host",
    content: StepHost,
  },
  {
    id: "tags",
    content: StepTags,
  },
  {
    id: "progress",
    content: StepProgress,
  },
] as const);

export type AddMachineSteps = typeof steps;
