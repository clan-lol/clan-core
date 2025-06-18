import { Button } from "@/src/components/Button/Button";
import Icon from "@/src/components/icon";
import { Typography } from "@/src/components/Typography";

const LoadingBar = () => (
  <div
    class="h-3 w-80 overflow-hidden rounded-[3px] border-2 border-def-1"
    style={{
      background: `repeating-linear-gradient(
    45deg,
    #ccc,
    #ccc 8px,
    #eee 8px,
    #eee 16px
  )`,
      animation: "slide 25s linear infinite",
      "background-size": "200% 100%",
    }}
  ></div>
);

interface InstallProgressProps {
  machineName: string;
  progressText?: string;
  isDone: boolean;
  onCancel: () => void;
}

export function InstallProgress(props: InstallProgressProps) {
  return (
    <div class="flex h-96 w-[40rem] flex-col fg-inv-1">
      <div class="flex w-full gap-1 p-4 bg-inv-4">
        <Typography
          color="inherit"
          hierarchy="label"
          size="default"
          weight="medium"
        >
          Install:
        </Typography>
        <Typography
          color="inherit"
          hierarchy="label"
          size="default"
          weight="bold"
        >
          {props.machineName}
        </Typography>
      </div>
      <div class="flex h-full flex-col items-center gap-3 px-4 py-8 bg-inv-4 fg-inv-1">
        <Icon icon="ClanIcon" viewBox="0 0 72 89" class="size-20" />
        {props.isDone && <LoadingBar />}
        <Typography
          hierarchy="label"
          size="default"
          weight="medium"
          color="inherit"
        >
          {props.progressText}
        </Typography>
        <Button onClick={props.onCancel}>Cancel</Button>
      </div>
    </div>
  );
}
