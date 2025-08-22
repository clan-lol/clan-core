import { defineSteps, useStepper } from "@/src/hooks/stepper";
import { InstallSteps } from "../install";
import { Typography } from "@/src/components/Typography/Typography";
import { Button } from "@/src/components/Button/Button";
import { StepLayout } from "../../Steps";
import { NavSection } from "@/src/components/NavSection/NavSection";

const ChoiceLocalOrRemote = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <div class="flex size-full flex-col gap-3">
      <NavSection
        label="I have physical access to the machine"
        onClick={() => stepSignal.setActiveStep("local:choice")}
      />
      <NavSection
        label="The Machine is remote and i have ssh access to it"
        onClick={() => stepSignal.setActiveStep("install:address")}
      />
    </div>
  );
};

const ChoiceLocalInstaller = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <StepLayout
      body={
        <div class="flex flex-col gap-3">
          <NavSection
            label="I have an installer"
            onClick={() => stepSignal.setActiveStep("install:address")}
          />
          <NavSection
            label="I don't have an installer, yet"
            onClick={() => stepSignal.setActiveStep("create:prose")}
          />
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
