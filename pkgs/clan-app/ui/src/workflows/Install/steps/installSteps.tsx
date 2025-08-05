import { Typography } from "@/src/components/Typography/Typography";
import { NextButton } from "../../Steps";

export const InstallHeader = (props: { machineName: string }) => {
  return (
    <Typography hierarchy="label" size="default">
      Installing: {props.machineName}
    </Typography>
  );
};

export const installSteps = [
  {
    id: "install:machine-0",
    title: InstallHeader,
    content: () => (
      <div>
        Enter the targetHost
        <NextButton />
      </div>
    ),
  },
  {
    id: "install:confirm",
    title: InstallHeader,
    content: (props: { machineName: string }) => (
      <div>
        Confirm the installation of {props.machineName}
        <NextButton />
      </div>
    ),
  },
  {
    id: "install:progress",
    title: InstallHeader,
    content: () => (
      <div>
        <p>Installation in progress...</p>
        <p>Please wait while we set up your machine.</p>
      </div>
    ),
  },
] as const;
