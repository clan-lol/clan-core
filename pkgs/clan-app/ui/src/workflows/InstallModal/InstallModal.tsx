import { Button } from "@/src/components/Button/Button";
import { Modal } from "@/src/components/Modal/Modal";
import { createForm, SubmitHandler } from "@modular-forms/solid";
import {
  Accessor,
  Component,
  createContext,
  createSignal,
  JSX,
  Setter,
  Show,
  useContext,
} from "solid-js";
import { Dynamic } from "solid-js/web";

export const InstallHeader = (props: {
  machineName: string;
  stepid: string;
}) => {
  return (
    <h2>
      Installing: {props.machineName} {props.stepid}
    </h2>
  );
};

type Step = {
  id: string;
  title: Component<{ machineName: string; stepid: string }>;
  content: Component;
};

type StepOptions<Id> = {
  initialStep: Id;
};

function createStepper<
  T extends readonly Step[],
  StepId extends T[number]["id"],
>(s: { steps: T }, stepOpts: StepOptions<StepId>): StepperReturn<T> {
  const [activeStep, setActiveStep] = createSignal<T[number]["id"]>(
    stepOpts.initialStep,
  );

  /**
   * Hooks to manage the current step in the workflow.
   * It provides the active step and a function to set the active step.
   */
  return {
    activeStep,
    setActiveStep,
    currentStep: () => {
      const curr = s.steps.find((step) => step.id === activeStep());
      if (!curr) {
        throw new Error(`Step with id ${activeStep()} not found`);
      }
      return curr;
    },
    next: () => {
      const currentIndex = s.steps.findIndex(
        (step) => step.id === activeStep(),
      );
      if (currentIndex === -1 || currentIndex === s.steps.length - 1) {
        throw new Error("No next step available");
      }
      setActiveStep(s.steps[currentIndex + 1].id);
    },
    previous: () => {
      const currentIndex = s.steps.findIndex(
        (step) => step.id === activeStep(),
      );
      if (currentIndex <= 0) {
        throw new Error("No previous step available");
      }
      setActiveStep(s.steps[currentIndex - 1].id);
    },
    hasPrevious: () => {
      const currentIndex = s.steps.findIndex(
        (step) => step.id === activeStep(),
      );
      return currentIndex > 0;
    },
    hasNext: () => {
      const currentIndex = s.steps.findIndex(
        (step) => step.id === activeStep(),
      );
      return currentIndex >= 0 && currentIndex < s.steps.length - 1;
    },
  };
}

type StepperReturn<T extends readonly Step[]> = {
  activeStep: Accessor<T[number]["id"]>;
  setActiveStep: Setter<T[number]["id"]>;
  currentStep: () => T[number];
  next: () => void;
  previous: () => void;
  hasPrevious: () => boolean;
  hasNext: () => boolean;
};

function createStepperContext<T extends readonly Step[]>() {
  return createContext<StepperReturn<T>>();
}
const StepperContext = createStepperContext();

export function StepperProvider<T extends readonly Step[]>(props: {
  stepper: StepperReturn<T>;
  children: JSX.Element;
}) {
  return (
    // @ts-expect-error: I dont have time for this shit
    <StepperContext.Provider value={props.stepper}>
      {props.children}
    </StepperContext.Provider>
  );
}

export function useStepper() {
  const ctx = useContext(StepperContext);
  if (!ctx) throw new Error("useStepper must be used inside StepperProvider");
  return ctx;
}

type InstallForm = {
  data_from_step_1: string;
  data_from_step_2?: string;
  data_from_step_3?: string;
};

const NextButton = () => {
  const stepSignal = useStepper();
  return (
    <Button
      type="submit"
      hierarchy="primary"
      disabled={!stepSignal.hasNext()}
      endIcon="ArrowRight"
      // Needs to be handled in the form submit handler
      // onClick={(e) => stepSignal.next();
    >
      Next
    </Button>
  );
};

const InstallStepper = () => {
  const stepSignal = useStepper();

  const [formStore, { Form, Field, FieldArray }] = createForm<InstallForm>({});

  const handleSubmit: SubmitHandler<InstallForm> = (values, event) => {
    console.log("Installation started (submit)", values);
    stepSignal.setActiveStep("install:progress");
  };
  return (
    <Form onSubmit={handleSubmit}>
      <div class="gap-6">
        <Dynamic component={stepSignal.currentStep().content} />
      </div>
    </Form>
  );
};

export const BackButton = () => {
  const stepSignal = useStepper();
  return (
    <Button
      hierarchy="secondary"
      disabled={!stepSignal.hasPrevious()}
      startIcon="ArrowLeft"
      onClick={() => {
        stepSignal.previous();
      }}
    >
      Back
    </Button>
  );
};

export interface InstallModalProps {
  machineName: string;
}

const InitialChoice = () => {
  const stepSignal = useStepper();
  return (
    <div>
      <p>Welcome to the installation wizard!</p>
      <p>Please choose how you want to install your machine.</p>

      <Button
        hierarchy="secondary"
        onClick={() => stepSignal.setActiveStep("install:machine-0")}
      >
        Direct install
      </Button>

      <Button
        hierarchy="secondary"
        onClick={() => stepSignal.setActiveStep("create:iso-0")}
      >
        Create installer
      </Button>
    </div>
  );
};

const CreateIso = () => {
  const [formStore, { Form, Field }] = createForm({});
  const stepSignal = useStepper();

  // TODO: push values to the parent form Store
  const handleSubmit: SubmitHandler<{}> = (values, event) => {
    console.log("ISO creation submitted", values);
    // Here you would typically trigger the ISO creation process
    stepSignal.next();
  };

  return (
    <Form onSubmit={handleSubmit}>
      <p>Creating an ISO 1nstaller</p>

      <div class="flex justify-between mt-4">
        <BackButton />
        <NextButton />
      </div>
    </Form>
  );
};

export const InstallModal = (props: InstallModalProps) => {
  const stepper = createStepper(
    {
      steps: [
        {
          id: "init",
          title: InstallHeader,
          content: InitialChoice,
        },
        {
          id: "create:iso-0",
          title: InstallHeader,
          content: CreateIso,
        },
        {
          id: "install:machine-0",
          title: InstallHeader,
          content: () => (
            <div>
              Enter the targetHost
              <NextButton />
            </div>
          ),
        },
        {
          id: "install:confirm",
          title: InstallHeader,
          content: () => (
            <div>
              Confirm the installation of {props.machineName}
              <NextButton />
            </div>
          ),
        },
        {
          id: "install:progress",
          title: InstallHeader,
          content: () => (
            <div>
              <p>Installation in progress...</p>
              <p>Please wait while we set up your machine.</p>
            </div>
          ),
        },
      ],
    },
    { initialStep: "init" },
  );

  return (
    <StepperProvider stepper={stepper}>
      <Modal
        title="Install machine"
        onClose={() => {
          console.log("Install aborted");
        }}
        metaHeader={() => {
          const HeaderComponent = stepper.currentStep()?.title;
          return (
            <HeaderComponent
              machineName={props.machineName}
              stepid={stepper.currentStep().id}
            />
          );
        }}
      >
        {(ctx) => <InstallStepper />}
      </Modal>
    </StepperProvider>
  );
};
