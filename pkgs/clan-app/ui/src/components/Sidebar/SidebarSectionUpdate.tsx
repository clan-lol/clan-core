import { createSignal, Show } from "solid-js";
import { Button } from "@/src/components/Button/Button";
import { useMachineName } from "@/src/hooks/clan";
import { useMachineStateQuery } from "@/src/hooks/queries";
import styles from "./SidebarSectionInstall.module.css";
import { UpdateModal } from "@/src/workflows/InstallMachine/UpdateMachine";

export interface SidebarSectionUpdateProps {
  clanURI: string;
  machineName: string;
}

export const SidebarSectionUpdate = (props: SidebarSectionUpdateProps) => {
  const query = useMachineStateQuery(props.clanURI, props.machineName);

  const [showUpdate, setShowUpdate] = createSignal(false);

  return (
    <Show when={query.isSuccess && query.data.status !== "not_installed"}>
      <div class={styles.install}>
        <Button
          hierarchy="primary"
          size="s"
          onClick={() => setShowUpdate(true)}
        >
          Update machine
        </Button>
        <Show when={showUpdate()}>
          <UpdateModal
            open={showUpdate()}
            machineName={useMachineName()}
            onClose={() => setShowUpdate(false)}
          />
        </Show>
      </div>
    </Show>
  );
};
