import { createSignal, Show } from "solid-js";
import { Button } from "@/src/components/Button/Button";
import { InstallModal } from "@/src/workflows/InstallMachine/InstallMachine";
import styles from "./SidebarSectionInstall.module.css";
import { Alert } from "../../Alert/Alert";
import { useMachineContext } from "@/src/components/Context/MachineContext";

export const SidebarSectionInstall = () => {
  const machine = useMachineContext()!;

  const [showInstall, setShowModal] = createSignal(false);

  return (
    <Show when={machine().status == "not_installed"}>
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
            machineName={machine().name}
            onClose={async () => {
              setShowModal(false);
            }}
          />
        </Show>
      </div>
    </Show>
  );
};
