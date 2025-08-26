import { JSX } from "solid-js";
import { useStepper } from "../hooks/stepper";
import { Button, ButtonProps } from "../components/Button/Button";
import { InstallSteps } from "./Install/install";
import styles from "./Steps.module.css";

interface StepLayoutProps {
  body: JSX.Element;
  footer: JSX.Element;
}
export const StepLayout = (props: StepLayoutProps) => {
  return (
    <div class={styles.step}>
      {props.body}
      {props.footer}
    </div>
  );
};

type NextButtonProps = ButtonProps & {};

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
      {props.children || "Next"}
    </Button>
  );
};

export const BackButton = () => {
  const stepSignal = useStepper<InstallSteps>();
  return (
    <Button
      hierarchy="secondary"
      disabled={!stepSignal.hasPrevious()}
      icon="ArrowLeft"
      onClick={() => {
        stepSignal.previous();
      }}
    ></Button>
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
interface StepFooterProps {
  nextText?: string;
}
export const StepFooter = (props: StepFooterProps) => {
  const stepper = useStepper<InstallSteps>();
  return (
    <div class={styles.footer}>
      <BackButton />
      <NextButton type="button" onClick={() => stepper.next()}>
        {props.nextText || undefined}
      </NextButton>
    </div>
  );
};
