import { Show } from "solid-js";
import { Button } from "@/components/Button/Button";
import styles from "./SidebarSectionInstall.module.css";
import { useMachineContext, useUIContext } from "@/models";

export const SidebarSectionUpdate = () => {
  const [, { showModal }] = useUIContext();
  const [machine] = useMachineContext();

  return (
    <Show when={machine().status !== "not_installed"}>
      <div class={styles.install}>
        <Button
          hierarchy="primary"
          size="s"
          onClick={() =>
            showModal({ type: "UpdateMachine", machine: machine() })
          }
        >
          Update machine
        </Button>
      </div>
    </Show>
  );
};
