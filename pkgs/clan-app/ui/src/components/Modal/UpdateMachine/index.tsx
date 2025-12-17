import {
  createStepper,
  getStepStore,
  StepperProvider,
  useStepper,
} from "@/src/components/Steps/stepper";
import { Component, createSignal, onCleanup, Show, Suspense } from "solid-js";
import { Dynamic } from "solid-js/web";
import {
  ConfigureAddress,
  ConfigureData,
} from "../InstallMachine/steps/installSteps";

import { InstallStoreType } from "../InstallMachine";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import Icon from "@/src/components/Icon/Icon";
import { LoadingBar } from "@/src/components/LoadingBar/LoadingBar";
import usbLogo from "@/logos/usb-stick-min.png?url";
import TitledModal from "../components/TitledModal";
import {
  MachineContextProvider,
  Modal,
  useMachineContext,
  useUIContext,
} from "@/src/models";
import { createAsync } from "@solidjs/router";
import { UpdateMachineProgress } from "@/src/models/machine/machine";

const UpdateMachine = () => {
  const [ui] = useUIContext();
  const modal = ui.modal as Extract<Modal, { type: "UpdateMachine" }>;
  const stepper = createStepper({ steps }, { initialStep: "update:address" });

  return (
    <TitledModal title="Update machine">
      <MachineContextProvider value={() => modal.machine}>
        <StepperProvider stepper={stepper}>
          <UpdateStepper />
        </StepperProvider>
      </MachineContextProvider>
    </TitledModal>
  );
};
export default UpdateMachine;

const UpdateStepper: Component = () => {
  const stepSignal = useStepper<UpdateSteps>();

  return <Dynamic component={stepSignal.currentStep().content} />;
};

const UpdateDone = () => {
  const [, { closeModal }] = useUIContext();
  const [, { updateMachine }] = useMachineContext();
  const stepSignal = useStepper<UpdateSteps>();
  const [store] = getStepStore<InstallStoreType>(stepSignal);
  const [progress, setProgress] = createSignal<
    UpdateMachineProgress | undefined
  >();

  const controller = new AbortController();
  const done = createAsync(async () => {
    await updateMachine({
      signal: controller.signal,
      ssh: {
        address: store.install.targetHost!,
        port: store.install.port ? parseInt(store.install.port, 10) : undefined,
        password: store.install.password,
      },
      onProgress: setProgress,
    });
    return true;
  });
  const handleCancel = async () => {
    controller.abort();
    stepSignal.previous();
  };
  onCleanup(() => {
    controller.abort();
  });

  return (
    <Suspense
      fallback={
        <div class="relative flex h-72 w-svw max-w-[30rem] flex-col items-center justify-end bg-inv-4">
          <img src={usbLogo} alt="usb logo" class="absolute top-2 z-0" />
          <div class="z-10 mb-6 flex w-full max-w-md flex-col items-center gap-2 fg-inv-1">
            <Typography hierarchy="title" weight="bold" color="inherit">
              Machine is being updated
            </Typography>
            <LoadingBar />
            <Typography hierarchy="label" color="secondary" inverted>
              Update {progress()}...
            </Typography>
            <Button
              hierarchy="primary"
              elasticity="fit"
              size="s"
              in="UpdateProgress"
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </div>
        </div>
      }
    >
      <Show when={done()}>
        <div class="flex h-72 w-svw max-w-[30rem] flex-col items-center justify-center bg-inv-4">
          <div class="flex w-full max-w-md flex-col items-center gap-3 py-6 fg-inv-1">
            <div class="rounded-full bg-semantic-success-4">
              <Icon icon="Checkmark" in="WorkflowPanelTitle" />
            </div>
            <Typography
              hierarchy="title"
              size="default"
              weight="bold"
              color="inherit"
            >
              Machine update finished!
            </Typography>
            <div class="mt-3 flex w-full justify-center">
              <Button
                hierarchy="primary"
                endIcon="Close"
                size="s"
                onClick={() => closeModal()}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      </Show>
    </Suspense>
  );
};

const steps = [
  {
    id: "update:address",
    content: () => <ConfigureAddress forUpdating={true} />,
  },
  {
    id: "update:data",
    content: () => <ConfigureData forUpdating={true} />,
  },
  {
    id: "update:done",
    content: UpdateDone,
  },
] as const;

type UpdateSteps = typeof steps;
