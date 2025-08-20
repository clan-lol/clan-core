import {
  Accessor,
  createContext,
  createSignal,
  JSX,
  Setter,
  useContext,
} from "solid-js";
import { createStore, SetStoreFunction, Store } from "solid-js/store";

export interface StepBase {
  id: string;
}

export type Step<ExtraFields = unknown> = StepBase & ExtraFields;

export interface StepOptions<Id, StoreType> {
  initialStep: Id;
  initialStoreData?: StoreType;
}

export function createStepper<
  T extends readonly Step<Extra>[],
  StepId extends T[number]["id"],
  Extra = unknown,
  StoreType extends Record<string, unknown> = Record<string, unknown>,
>(
  s: { steps: T },
  stepOpts: StepOptions<StepId, StoreType>,
): StepperReturn<T, T[number]["id"]> {
  const [history, setHistory] = createSignal<T[number]["id"][]>(["init"]);

  const activeStep = () => history()[history().length - 1];

  const setActiveStep = (id: T[number]["id"]) => {
    setHistory((prev) => [...prev, id]);
  };

  const store: StoreTuple<StoreType> = createStore<StoreType>(
    stepOpts.initialStoreData ?? ({} as StoreType),
  );

  /**
   * Hooks to manage the current step in the workflow.
   * It provides the active step and a function to set the active step.
   */
  return {
    /**
     * Usage store = getStepStore<MyStoreType>(stepper);
     *
     * TODO: Getting type inference working is tricky. Might fix this later.
     */
    _store: store as unknown as never,
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
      const hist = history();
      if (hist.length <= 1) {
        throw new Error("No previous step available");
      }

      setHistory((prev) => {
        const update = prev.slice(0, -1);
        setActiveStep(update[update.length - 1]);
        return update;
      });
    },
    hasPrevious: () => {
      return history().length > 1;
    },
    hasNext: () => {
      const currentIndex = s.steps.findIndex(
        (step) => step.id === activeStep(),
      );
      return currentIndex >= 0 && currentIndex < s.steps.length - 1;
    },
  };
}

type StoreTuple<T> = [get: Store<T>, set: SetStoreFunction<T>];
export interface StepperReturn<
  T extends readonly Step[],
  StepId = T[number]["id"],
> {
  _store: never;
  activeStep: Accessor<StepId>;
  setActiveStep: (id: StepId) => void;
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

interface getStepStoreArg {
  _store: never;
}
export function getStepStore<StoreType>(stepper: getStepStoreArg) {
  return stepper._store as StoreTuple<StoreType>;
}
