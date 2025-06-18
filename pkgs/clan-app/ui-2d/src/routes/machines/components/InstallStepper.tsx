import { For, Show } from "solid-js";
import cx from "classnames";
import Icon from "@/src/components/icon";
import { Typography } from "@/src/components/Typography";

const steps: Record<string, string> = {
  "1": "Hardware detection",
  "2": "Disk schema",
  "3": "Credentials & Data",
  "4": "Installation",
};

interface InstallStepperProps {
  currentStep: string;
}

export function InstallStepper(props: InstallStepperProps) {
  return (
    <div class="flex items-center justify-evenly gap-2 border py-3 bg-def-3 border-def-2">
      <For each={Object.entries(steps)}>
        {([idx, label]) => (
          <div class="flex flex-col items-center gap-3 fg-def-1">
            <Typography
              classList={{
                [cx("bg-inv-4 fg-inv-1")]: idx === props.currentStep,
                [cx("bg-def-4 fg-def-1")]: idx < props.currentStep,
              }}
              color="inherit"
              hierarchy="label"
              size="default"
              weight="bold"
              class="flex size-6 items-center justify-center rounded-full text-center align-middle bg-def-1"
            >
              <Show
                when={idx >= props.currentStep}
                fallback={<Icon icon="Checkmark" class="size-5" />}
              >
                {idx}
              </Show>
            </Typography>
            <Typography
              color="inherit"
              hierarchy="label"
              size="xs"
              weight="medium"
              class="text-center align-top fg-def-3"
              classList={{
                [cx("!fg-def-1")]: idx == props.currentStep,
              }}
            >
              {label}
            </Typography>
          </div>
        )}
      </For>
    </div>
  );
}
