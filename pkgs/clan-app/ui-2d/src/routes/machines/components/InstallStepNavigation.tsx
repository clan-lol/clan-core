import { Button } from "@/src/components/Button/Button";
import Icon from "@/src/components/icon";

interface InstallStepNavigationProps {
  currentStep: string;
  isFirstStep: boolean;
  isLastStep: boolean;
  onPrevious: () => void;
  onNext?: () => void;
  onInstall?: () => void;
}

export function InstallStepNavigation(props: InstallStepNavigationProps) {
  return (
    <div class="flex justify-between p-4">
      <Button
        startIcon={<Icon icon="ArrowLeft" />}
        variant="light"
        type="button"
        onClick={props.onPrevious}
        disabled={props.isFirstStep}
      >
        Previous
      </Button>

      {props.isLastStep ? (
        <Button startIcon={<Icon icon="Flash" />} onClick={props.onInstall}>
          Install
        </Button>
      ) : (
        <Button endIcon={<Icon icon="ArrowRight" />} type="submit">
          Next
        </Button>
      )}
    </div>
  );
}
