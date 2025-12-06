import { createSignal, Show } from "solid-js";
import { Button } from "@/src/components/Button/Button";
import styles from "./SidebarSectionInstall.module.css";
import { UpdateModal } from "@/src/workflows/InstallMachine/UpdateMachine";
import { useMachineContext } from "@/src/components/Context/MachineContext";

export const SidebarSectionUpdate = () => {
  const [machine] = useMachineContext()!;

  const [showUpdate, setShowUpdate] = createSignal(false);

  return (
    <Show when={machine().status !== "not_installed"}>
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
            machineName={machine().id}
            onClose={async () => {
              setShowUpdate(false);
            }}
          />
        </Show>
      </div>
    </Show>
  );
};
