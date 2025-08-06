import {
  Accessor,
  createContext,
  createSignal,
  JSX,
  Setter,
  useContext,
} from "solid-js";

export interface StepBase {
  id: string;
}

export type Step<ExtraFields = unknown> = StepBase & ExtraFields;

export interface StepOptions<Id> {
  initialStep: Id;
}

export function createStepper<
  T extends readonly Step<Extra>[],
  StepId extends T[number]["id"],
  Extra = unknown,
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

export interface StepperReturn<
  T extends readonly Step[],
  StepId = T[number]["id"],
> {
  activeStep: Accessor<StepId>;
  setActiveStep: Setter<StepId>;
  currentStep: () => T[number];
  next: () => void;
  previous: () => void;
  hasPrevious: () => boolean;
  hasNext: () => boolean;
}

const StepperContext = createContext<unknown>(); // Concrete type will be provided by the provider

// Default assignment to "never" forces users to specify the type when using the hook, otherwise the return type will be `never`.
export function useStepper<T extends readonly Step[] = never>() {
  const ctx = useContext(StepperContext);
  if (!ctx) throw new Error("useStepper must be used inside StepperProvider");
  return ctx as T extends never ? never : StepperReturn<T, T[number]["id"]>; // type casting required due to context limitations
}

interface ProviderProps<T extends readonly Step[], StepId> {
  stepper: StepperReturn<T, StepId>;
  children: JSX.Element;
}

interface ProviderProps<
  T extends readonly Step[],
  StepId extends T[number]["id"],
> {
  stepper: StepperReturn<T, StepId>;
  children: JSX.Element;
}

export function StepperProvider<
  T extends readonly Step[],
  StepId extends T[number]["id"],
>(props: ProviderProps<T, StepId>) {
  return (
    <StepperContext.Provider value={props.stepper}>
      {props.children}
    </StepperContext.Provider>
  );
}

/**
 * Helper function to define steps in a type-safe manner.
 */
export function defineSteps<T extends readonly StepBase[]>(steps: T) {
  return steps;
}
