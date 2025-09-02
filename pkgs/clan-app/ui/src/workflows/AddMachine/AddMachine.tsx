import {
  createStepper,
  defineSteps,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import {
  GeneralForm,
  StepGeneral,
} from "@/src/workflows/AddMachine/StepGeneral";
import { Modal } from "@/src/components/Modal/Modal";
import cx from "classnames";
import { Dynamic } from "solid-js/web";
import { Show } from "solid-js";
import { Typography } from "@/src/components/Typography/Typography";
import { StepHost } from "@/src/workflows/AddMachine/StepHost";
import { StepTags } from "@/src/workflows/AddMachine/StepTags";
import { StepProgress } from "./StepProgress";

interface AddMachineStepperProps {
  onDone: () => void;
}

const AddMachineStepper = (props: AddMachineStepperProps) => {
  const stepSignal = useStepper<AddMachineSteps>();

  return (
    <Dynamic
      component={stepSignal.currentStep().content}
      onDone={props.onDone}
    />
  );
};

export interface AddMachineProps {
  onClose: () => void;
  onCreated: (id: string) => void;
  initialStep?: AddMachineSteps[number]["id"];
}

export interface AddMachineStoreType {
  general: GeneralForm;
  deploy: {
    targetHost?: string;
  };
  tags: {
    tags: string[];
  };
  onCreated: (id: string) => void;
  error?: string;
}

const steps = defineSteps([
  {
    id: "general",
    title: "General",
    content: StepGeneral,
  },
  {
    id: "host",
    title: "Host",
    content: StepHost,
  },
  {
    id: "tags",
    title: "Tags",
    content: StepTags,
  },
  {
    id: "progress",
    title: "Creating...",
    content: StepProgress,
    isSplash: true,
  },
] as const);

export type AddMachineSteps = typeof steps;

export const AddMachine = (props: AddMachineProps) => {
  const stepper = createStepper(
    {
      steps,
    },
    {
      initialStep: props.initialStep || "general",
      initialStoreData: { onCreated: props.onCreated },
    },
  );

  const MetaHeader = () => {
    const title = stepper.currentStep().title;
    return (
      <Show when={title}>
        <Typography
          hierarchy="label"
          family="mono"
          size="default"
          weight="medium"
        >
          {title}
        </Typography>
      </Show>
    );
  };

  const sizeClasses = () => {
    const defaultClass = "max-w-3xl h-fit";

    const currentStep = stepper.currentStep();
    if (!currentStep) {
      return defaultClass;
    }

    switch (currentStep.id) {
      default:
        return defaultClass;
    }
  };

  return (
    <StepperProvider stepper={stepper}>
      <Modal
        class={cx("w-screen", sizeClasses())}
        title="Add Machine"
        onClose={props.onClose}
        open={true}
        // @ts-expect-error some steps might not have
        metaHeader={stepper.currentStep()?.title ? <MetaHeader /> : undefined}
        // @ts-expect-error some steps might not have
        disablePadding={stepper.currentStep()?.isSplash}
      >
        <AddMachineStepper onDone={() => props.onClose()} />
      </Modal>
    </StepperProvider>
  );
};
