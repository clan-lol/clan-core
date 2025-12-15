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

const AddMachineModal: Component<{
  initialStep?: AddMachineSteps[number]["id"];
}> = (props) => {
  const stepper = createStepper(
    {
      steps,
    },
    {
      initialStep: props.initialStep || "progress",
    },
  );

  return (
    <StepperProvider stepper={stepper}>
      <AddMachineStepper />
    </StepperProvider>
  );
};
export default AddMachineModal;

export const title = "Add Machine";

const AddMachineStepper = () => {
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
