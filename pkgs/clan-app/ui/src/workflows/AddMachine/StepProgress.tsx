import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  AddMachineSteps,
  AddMachineStoreType,
} from "@/src/workflows/AddMachine/AddMachine";
import { Loader } from "@/src/components/Loader/Loader";
import { Typography } from "@/src/components/Typography/Typography";
import { Show } from "solid-js";
import { Alert } from "@/src/components/Alert/Alert";

interface StepProgressProps {
  onDone: () => void;
}

export const StepProgress = (props: StepProgressProps) => {
  const stepSignal = useStepper<AddMachineSteps>();
  const [store, set] = getStepStore<AddMachineStoreType>(stepSignal);

  return (
    <div class="flex flex-col items-center justify-center gap-2.5 px-6 pb-7 pt-4">
      <Show
        when={store.error}
        fallback={
          <>
            <Loader size="l" />
            <Typography hierarchy="body" size="s" weight="medium" family="mono">
              {store.general?.name} is being created
            </Typography>
          </>
        }
      >
        <Alert
          type="error"
          title="There was an error"
          description={store.error}
        />
      </Show>
    </div>
  );
};
