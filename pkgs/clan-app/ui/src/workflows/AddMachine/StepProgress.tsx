import { getStepStore, useStepper } from "@/src/hooks/stepper";
import {
  AddMachineSteps,
  AddMachineStoreType,
} from "@/src/workflows/AddMachine/AddMachine";
import { Loader } from "@/src/components/Loader/Loader";
import { Typography } from "@/src/components/Typography/Typography";
import { createSignal, onMount, Show } from "solid-js";
import { Alert } from "@/src/components/Alert/Alert";
import { useApiClient } from "@/src/hooks/ApiClient";
import { callApi } from "@/src/hooks/api";
import { useClanURI } from "@/src/hooks/clan";

export interface StepProgressProps {
  onDone: () => void;
}

export const StepProgress = (props: StepProgressProps) => {
  const stepSignal = useStepper<AddMachineSteps>();
  const [store, set] = getStepStore<AddMachineStoreType>(stepSignal);

  const clanURI = useClanURI();
  const [error, setError] = createSignal<string | undefined>(undefined);

  onMount(async () => {
    const call = callApi("create_machine", {
      opts: {
        clan_dir: {
          identifier: clanURI,
        },
        machine: {
          ...store.general,
          ...store.deploy,
          ...store.tags,
        },
      },
    });

    const result = await call.result;

    if (result.status == "error") {
      setError(result.errors[0].message);
    }

    if (result.status == "success") {
      console.log("Machine creation was successful");
      props.onDone();
    }
  });

  return (
    <div class="flex flex-col items-center justify-center gap-2.5 px-6 pb-7 pt-4">
      <Show
        when={error()}
        fallback={
          <>
            <Loader class="size-8" />
            <Typography hierarchy="body" size="s" weight="medium" family="mono">
              Brian is being created
            </Typography>
          </>
        }
      >
        <Alert type="error" title="There was an error" description={error()} />
      </Show>
    </div>
  );
};
