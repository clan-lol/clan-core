import { Show } from "solid-js";
import { getStepStore, useStepper } from "@/src/components/Steps/stepper";
import styles from "./AddMachine.module.css";
import { AddMachineSteps, AddMachineStoreType } from ".";
import { Loader } from "@/src/components/Loader/Loader";
import { Typography } from "@/src/components/Typography/Typography";
import { Alert } from "@/src/components/Alert/Alert";
import ModalHeading from "../components/ModalHeading";

export const StepProgress = () => {
  const stepSignal = useStepper<AddMachineSteps>();
  const [store] = getStepStore<AddMachineStoreType>(stepSignal);

  return (
    <div class={styles.container}>
      <ModalHeading text="Creating..." />
      <div class="flex flex-col items-center justify-center gap-2.5 px-6 pb-7 pt-4">
        <Show
          when={store.error}
          fallback={
            <>
              <Loader size="l" />
              <Typography
                hierarchy="body"
                size="s"
                weight="medium"
                family="mono"
              >
                {store.general?.id /* FIXME: is optional necessary? */} is being
                created
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
    </div>
  );
};
