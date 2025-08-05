import { useStepper } from "@/src/hooks/stepper";
import { InstallSteps } from "../install";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import { Divider } from "@/src/components/Divider/Divider";

const InitialChoice = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <div class="flex flex-col gap-3">
      <div class="flex flex-col gap-6 rounded-md px-4 py-6 text-fg-def-1 bg-def-2">
        <div class="flex gap-2">
          <div class="flex flex-col gap-1 px-1">
            <Typography
              hierarchy="label"
              size="xs"
              weight="bold"
              color="primary"
            >
              Remote setup
            </Typography>
            <Typography
              hierarchy="body"
              size="xxs"
              weight="normal"
              color="secondary"
            >
              Is your machine currently online? Does it have an IP-address, can
              you SSH into it? And does it support Kexec?
            </Typography>
          </div>
          <Button
            type="button"
            ghost
            hierarchy="secondary"
            icon="CaretRight"
            onClick={() => stepSignal.setActiveStep("install:machine-0")}
          ></Button>
        </div>
        <Divider orientation="horizontal" class="bg-def-3" />

        <div class="flex items-center justify-between gap-2">
          <Typography hierarchy="label" size="xs" weight="bold">
            I don't have an installer, yet
          </Typography>
          <Button
            ghost
            hierarchy="secondary"
            endIcon="Flash"
            type="button"
            onClick={() => stepSignal.setActiveStep("create:iso-0")}
          >
            Create USB Installer
          </Button>
        </div>
      </div>
    </div>
  );
};

export const InitialStep = {
  id: "init",
  content: InitialChoice,
};
