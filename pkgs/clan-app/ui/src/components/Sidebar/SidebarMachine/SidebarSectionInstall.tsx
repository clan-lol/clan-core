import { Show } from "solid-js";
import { Button } from "@/src/components/Button/Button";
import styles from "./SidebarSectionInstall.module.css";
import { Alert } from "../../Alert/Alert";
import { useMachineContext, useUIContext } from "@/src/models";

export const SidebarSectionInstall = () => {
  const [, { showModal }] = useUIContext();
  const [machine] = useMachineContext();

  return (
    <Show when={machine().status == "not_installed"}>
      <div class={styles.install}>
        <Alert
          type="warning"
          size="s"
          title="Your machine is not installed yet"
          description="Start the process by clicking the button below."
        ></Alert>
        <Button
          hierarchy="primary"
          size="s"
          onClick={() =>
            showModal({ type: "InstallMachine", machine: machine() })
          }
        >
          Install machine
        </Button>
      </div>
    </Show>
  );
};
