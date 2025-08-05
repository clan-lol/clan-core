import { JSX } from "solid-js";
import { useStepper } from "../hooks/stepper";
import { Button } from "../components/Button/Button";
import { InstallSteps } from "./Install/install";

interface StepLayoutProps {
  body: JSX.Element;
  footer: JSX.Element;
}
export const StepLayout = (props: StepLayoutProps) => {
  return (
    <div class="flex flex-col gap-6">
      {props.body}
      {props.footer}
    </div>
  );
};

type NextButtonProps = JSX.ButtonHTMLAttributes<HTMLButtonElement> & {};

export const NextButton = (props: NextButtonProps) => {
  // TODO: Make this type generic
  const stepSignal = useStepper<InstallSteps>();
  return (
    <Button
      type="submit"
      hierarchy="primary"
      disabled={!stepSignal.hasNext()}
      endIcon="ArrowRight"
      {...props}
    >
      Next
    </Button>
  );
};

export const BackButton = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <Button
      hierarchy="secondary"
      disabled={!stepSignal.hasPrevious()}
      startIcon="ArrowLeft"
      onClick={() => {
        stepSignal.previous();
      }}
    >
      Back
    </Button>
  );
};

/**
 * Renders a footer with Back and Next buttons.
 * The Next button will trigger the next step in the stepper.
 * The Back button will go to the previous step.
 *
 * Does not trigger submission on any form
 *
 * Use this for overview steps where no form submission is required.
 */
export const StepFooter = () => {
  const stepper = useStepper<InstallSteps>();
  return (
    <div class="flex justify-between">
      <BackButton />
      <NextButton type="button" onClick={() => stepper.next()} />
    </div>
  );
};
