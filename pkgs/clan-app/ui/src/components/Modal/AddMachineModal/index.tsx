import {
  createStepper,
  defineSteps,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { GeneralForm, StepGeneral } from "./StepGeneral";
import { Modal } from "@/src/components/Modal/Modal";
import cx from "classnames";
import { Dynamic } from "solid-js/web";
import { Component, Show } from "solid-js";
import { Typography } from "@/src/components/Typography/Typography";
import { StepHost } from "./StepHost";
import { StepTags } from "./StepTags";
import { StepProgress } from "./StepProgress";
import { useModalContext } from "@/src/models";

const AddMachineModal: Component<{
  initialStep?: AddMachineSteps[number]["id"];
}> = (props) => {
  const [, { cancelModal }] = useModalContext();
  const stepper = createStepper(
    {
      steps,
    },
    {
      initialStep: props.initialStep || "general",
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

    return defaultClass;
  };

  return (
    <StepperProvider stepper={stepper}>
      <Modal
        class={cx("w-screen", sizeClasses())}
        title="Add Machine"
        onClose={() => cancelModal()}
        open={true}
        // @ts-expect-error some steps might not have
        metaHeader={stepper.currentStep()?.title ? <MetaHeader /> : undefined}
        // @ts-expect-error some steps might not have
        disablePadding={stepper.currentStep()?.isSplash}
      >
        <AddMachineStepper />
      </Modal>
    </StepperProvider>
  );
};
export default AddMachineModal;

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
