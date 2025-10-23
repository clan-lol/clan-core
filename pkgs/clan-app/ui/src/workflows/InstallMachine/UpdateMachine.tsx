import { Modal } from "@/src/components/Modal/Modal";
import {
  createStepper,
  getStepStore,
  StepperProvider,
  useStepper,
} from "@/src/hooks/stepper";
import { createSignal, Show } from "solid-js";
import { Dynamic } from "solid-js/web";
import { ConfigureAddress, ConfigureData } from "./steps/installSteps";

import cx from "classnames";
import { InstallStoreType } from "./InstallMachine";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import Icon from "@/src/components/Icon/Icon";
import { ProcessMessage, useNotifyOrigin } from "@/src/hooks/notify";
import { LoadingBar } from "@/src/components/LoadingBar/LoadingBar";
import * as api from "@/src/api";
import { useClanURI } from "@/src/hooks/clan";
import { AlertProps } from "@/src/components/Alert/Alert";
import usbLogo from "@/logos/usb-stick-min.png?url";

// TODO: Deduplicate
interface UpdateStepperProps {
  onDone: () => void;
}
const UpdateStepper = (props: UpdateStepperProps) => {
  const stepSignal = useStepper<UpdateSteps>();

  const [store, set] = getStepStore<InstallStoreType>(stepSignal);

  const [alert, setAlert] = createSignal<AlertProps>();

  const clanURI = useClanURI();

  const handleUpdate = async () => {
    console.log("Starting update for", store.install.machineName);

    const targetHost = store.install.targetHost;
    if (!targetHost) {
      console.error("No target host specified, API requires it");
      return;
    }
    const port = store.install.port
      ? parseInt(store.install.port, 10)
      : undefined;

    const abortController = new AbortController();
    set("install", "progress", abortController);
    try {
      await api.clan.updateMachine({
        clan: clanURI,
        name: store.install.machineName,
        targetHost,
        port,
        password: store.install.password,
        signal: abortController.signal,
      });
    } catch (err) {
      if (abortController.signal.aborted) {
        return;
      }
      setAlert(() => ({
        type: "error",
        title: "Update failed",
        description: String(err),
      }));
      stepSignal.previous();
      return;
    }

    stepSignal.next();
  };

  return (
    <Dynamic
      component={stepSignal.currentStep().content}
      onDone={props.onDone}
      next="update"
      stepFinished={handleUpdate}
      alert={alert()}
    />
  );
};

interface UpdateModalProps {
  machineName: string;
  open: boolean;
  initialStep?: UpdateSteps[number]["id"];
  mount?: Node;
  onClose?: () => void;
}

const UpdateHeader = (props: { machineName: string }) => {
  return (
    <Typography hierarchy="label" size="default">
      Update: {props.machineName}
    </Typography>
  );
};

type UpdateTopic = [
  "generators",
  "upload-secrets",
  "nixos-anywhere",
  "formatting",
  "rebooting",
  "installing",
][number];

const UpdateProgress = () => {
  const stepSignal = useStepper<UpdateSteps>();
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);

  const handleCancel = async () => {
    store.install.progress.abort();
    stepSignal.previous();
  };
  const updateState =
    useNotifyOrigin<ProcessMessage<unknown, UpdateTopic>>("run_machine_update");

  return (
    <div class="relative flex size-full flex-col items-center justify-end bg-inv-4">
      <img src={usbLogo} alt="usb logo" class="absolute top-2 z-0" />
      <div class="z-10 mb-6 flex w-full max-w-md flex-col items-center gap-2 fg-inv-1">
        <Typography hierarchy="title" weight="bold" color="inherit">
          Machine is being updated
        </Typography>
        <LoadingBar />
        <Typography hierarchy="label" color="secondary" inverted>
          Update {updateState()?.topic}...
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
  );
};

interface UpdateDoneProps {
  onDone: () => void;
}
const UpdateDone = (props: UpdateDoneProps) => {
  const stepSignal = useStepper<UpdateSteps>();
  const [store, get] = getStepStore<InstallStoreType>(stepSignal);

  return (
    <div class="flex size-full flex-col items-center justify-center bg-inv-4">
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
            onClick={() => props.onDone()}
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};

const steps = [
  {
    id: "update:data",
    title: UpdateHeader,
    content: ConfigureData,
  },
  {
    id: "update:address",
    title: UpdateHeader,
    content: ConfigureAddress,
  },
  {
    id: "update:progress",
    content: UpdateProgress,
    isSplash: true,
    class: "max-w-[30rem] h-[18rem]",
  },
  {
    id: "update:done",
    content: UpdateDone,
    isSplash: true,
    class: "max-w-[30rem] h-[18rem]",
  },
] as const;

type UpdateSteps = typeof steps;
type PromptValues = Record<string, Record<string, string>>;

export const UpdateModal = (props: UpdateModalProps) => {
  const stepper = createStepper(
    {
      steps,
    },
    {
      initialStep: props.initialStep || "update:data",
      initialStoreData: {
        install: { machineName: props.machineName },
      } as Partial<InstallStoreType>,
    },
  );

  const MetaHeader = () => {
    // @ts-expect-error some steps might not provide a title
    const HeaderComponent = () => stepper.currentStep()?.title;
    return (
      <Show when={HeaderComponent()}>
        {(C) => <Dynamic component={C()} machineName={props.machineName} />}
      </Show>
    );
  };
  const [store, set] = getStepStore<InstallStoreType>(stepper);

  set("install", { machineName: props.machineName });

  // allows each step to adjust the size of the modal
  const sizeClasses = () => {
    const defaultClass = "max-w-3xl h-[30rem]";

    const currentStep = stepper.currentStep();
    if (!currentStep) {
      return defaultClass;
    }

    switch (currentStep.id) {
      case "update:progress":
      case "update:done":
        return currentStep.class;

      default:
        return defaultClass;
    }
  };

  const onClose = async () => {
    props.onClose?.();
  };

  return (
    <StepperProvider stepper={stepper}>
      <Modal
        class={cx("w-screen", sizeClasses())}
        title="Update machine"
        onClose={onClose}
        open={props.open}
        // @ts-expect-error some steps might not have
        metaHeader={stepper.currentStep()?.title ? <MetaHeader /> : undefined}
        // @ts-expect-error some steps might not have
        disablePadding={stepper.currentStep()?.isSplash}
      >
        <UpdateStepper onDone={onClose} />
      </Modal>
    </StepperProvider>
  );
};
