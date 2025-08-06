import { defineSteps, Step, StepBase, useStepper } from "@/src/hooks/stepper";
import { InstallSteps } from "../install";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import { Divider } from "@/src/components/Divider/Divider";
import { StepLayout } from "../../Steps";

const ChoiceLocalOrRemote = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <div class="flex flex-col gap-3">
      <div class="flex flex-col gap-6 rounded-md px-4 py-6 text-fg-def-1 bg-def-2">
        <div class="flex gap-2 justify-between">
          <div class="flex flex-col gap-1 px-1 justify-center">
            <Typography
              hierarchy="label"
              size="xs"
              weight="bold"
              color="primary"
            >
              I have physical access to the machine.
            </Typography>
          </div>
          <Button
            type="button"
            ghost
            hierarchy="secondary"
            icon="CaretRight"
            onClick={() => stepSignal.setActiveStep("local:choice")}
          />
        </div>
      </div>
      <div class="flex flex-col gap-6 rounded-md px-4 py-6 text-fg-def-1 bg-def-2">
        <div class="flex gap-2 justify-between">
          <div class="flex flex-col gap-1 px-1 justify-center">
            <Typography
              hierarchy="label"
              size="xs"
              weight="bold"
              color="primary"
            >
              The Machine is remote and i have ssh access to it.
            </Typography>
          </div>
          <Button
            type="button"
            ghost
            hierarchy="secondary"
            icon="CaretRight"
            onClick={() => stepSignal.setActiveStep("install:address")}
          />
        </div>
      </div>
    </div>
  );
};

const ChoiceLocalInstaller = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <StepLayout
      body={
        <div class="flex flex-col gap-3">
          <div class="flex flex-col gap-6 rounded-md px-4 py-6 text-fg-def-1 bg-def-2">
            <div class="flex gap-2 justify-between">
              <div class="flex flex-col gap-1 px-1 justify-center">
                <Typography
                  hierarchy="label"
                  size="xs"
                  weight="bold"
                  color="primary"
                >
                  I have an installer
                </Typography>
              </div>
              <Button
                type="button"
                ghost
                hierarchy="secondary"
                icon="CaretRight"
                onClick={() => stepSignal.setActiveStep("install:address")}
              />
            </div>
          </div>
          <div class="flex flex-col gap-6 rounded-md px-4 py-6 text-fg-def-1 bg-def-2">
            <div class="flex gap-2 justify-between">
              <div class="flex flex-col gap-1 px-1 justify-center">
                <Typography
                  hierarchy="label"
                  size="xs"
                  weight="bold"
                  color="primary"
                >
                  I don't have an installer, yet
                </Typography>
              </div>
              <Button
                type="button"
                ghost
                hierarchy="secondary"
                icon="CaretRight"
                onClick={() => stepSignal.setActiveStep("create:prose")}
              />
            </div>
          </div>
        </div>
      }
      footer={
        <div class="flex justify-start">
          <Button
            hierarchy="secondary"
            icon="ArrowLeft"
            onClick={() => stepSignal.previous()}
          />
        </div>
      }
    />
  );
};

export const initialSteps = defineSteps([
  {
    id: "init",
    content: ChoiceLocalOrRemote,
  },
  {
    id: "local:choice",
    content: ChoiceLocalInstaller,
  },
] as const);
