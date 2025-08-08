import { Modal } from "@/src/components/Modal/Modal";
import {
  createStepper,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { createForm, FieldValues, SubmitHandler } from "@modular-forms/solid";
import { Show } from "solid-js";
import { Dynamic } from "solid-js/web";
import { initialSteps } from "./steps/Initial";
import { createInstallerSteps } from "./steps/createInstaller";
import { installSteps } from "./steps/installSteps";

interface InstallForm extends FieldValues {
  data_from_step_1: string;
  data_from_step_2?: string;
  data_from_step_3?: string;
}

const InstallStepper = () => {
  const stepSignal = useStepper<InstallSteps>();

  const [formStore, { Form, Field, FieldArray }] = createForm<InstallForm>();

  const handleSubmit: SubmitHandler<InstallForm> = (values, event) => {
    console.log("Installation started (submit)", values);
    stepSignal.setActiveStep("install:progress");
  };
  return (
    <Form onSubmit={handleSubmit}>
      <div class="gap-6">
        <Dynamic
          component={stepSignal.currentStep().content}
          machineName={"karl"}
        />
      </div>
    </Form>
  );
};

export interface InstallModalProps {
  machineName: string;
  initialStep?: InstallSteps[number]["id"];
  mount?: Node;
  onClose?: () => void;
}

const steps = [
  ...initialSteps,
  ...createInstallerSteps,
  ...installSteps,
] as const;

export type InstallSteps = typeof steps;
export interface InstallStoreType {
  flash: {
    language: string;
    keymap: string;
    ssh_file: string;
    device: string;
  };
}

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

  return (
    <StepperProvider stepper={stepper}>
      <Modal
        mount={props.mount}
        title="Install machine"
        onClose={() => {
          console.log("Install modal closed");
          props.onClose?.();
        }}
        // @ts-expect-error some steps might not have
        metaHeader={stepper.currentStep()?.title ? <MetaHeader /> : undefined}
        // @ts-expect-error some steps might not have
        disablePadding={stepper.currentStep()?.isSplash}
      >
        {(ctx) => <InstallStepper />}
      </Modal>
    </StepperProvider>
  );
};
