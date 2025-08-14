import styles from "./SidebarMachineStatus.module.css";
import { Typography } from "@/src/components/Typography/Typography";
import { useMachineStateQuery } from "@/src/hooks/queries";
import { MachineStatus } from "@/src/components/MachineStatus/MachineStatus";

export interface SidebarMachineStatusProps {
  class?: string;
  clanURI: string;
  machineName: string;
}

export const SidebarMachineStatus = (props: SidebarMachineStatusProps) => {
  const query = useMachineStateQuery(props.clanURI, props.machineName);

  return (
    <div class={styles.machineStatus}>
      <div class={styles.summary}>
        <Typography
          hierarchy="body"
          size="xs"
          weight="medium"
          inverted={true}
          color="tertiary"
        >
          Status
        </Typography>
        <MachineStatus
          label
          status={query.isSuccess ? query.data.status : undefined}
        />
      </div>
    </div>
  );
};
