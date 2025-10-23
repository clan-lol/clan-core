import { createSignal, Show } from "solid-js";
import { Button } from "@/src/components/Button/Button";
import { InstallModal } from "@/src/workflows/InstallMachine/InstallMachine";
import { useMachineName } from "@/src/hooks/clan";
import { useMachineStateQuery } from "@/src/hooks/queries";
import styles from "./SidebarSectionInstall.module.css";
import { Alert } from "../Alert/Alert";
import { useClanContext } from "@/src/routes/Clan/Clan";

interface SidebarSectionInstallProps {
  clanURI: string;
  machineName: string;
}

export const SidebarSectionInstall = (props: SidebarSectionInstallProps) => {
  const ctx = useClanContext();
  const query = useMachineStateQuery(props.clanURI, props.machineName);
  const [showInstall, setShowModal] = createSignal(false);

  return (
    <Show when={query.isSuccess && query.data.status == "not_installed"}>
      <div class={styles.install}>
        <Alert
          type="warning"
          size="s"
          title="Your machine is not installed yet"
          description="Start the process by clicking the button below."
        ></Alert>
        <Button hierarchy="primary" size="s" onClick={() => setShowModal(true)}>
          Install machine
        </Button>
        <Show when={showInstall()}>
          <InstallModal
            open={showInstall()}
            machineName={useMachineName()}
            onClose={async () => {
              // refresh some queries
              ctx.machinesQuery.refetch();
              ctx.serviceInstancesQuery.refetch();
              setShowModal(false);
            }}
          />
        </Show>
      </div>
    </Show>
  );
};
