import cx from "classnames";
import { Show } from "solid-js";
import styles from "./Sidebar.module.css";
import SidebarHeader from "@/src/components/Sidebar/SidebarHeader";
import SidebarBody from "@/src/components/Sidebar/SidebarBody";
import {
  MachineContextProvider,
  useMachinesContext,
} from "../Context/MachineContext";
import SidebarMachine from "./SidebarMachine";

export default function Sidebar() {
  const [machines] = useMachinesContext();
  return (
    <>
      <div
        class={cx(styles.sidebarContainer, {
          [styles.machineSelected]: machines().activeMachine,
        })}
      >
        <div class={styles.sidebar}>
          <SidebarHeader />
          <SidebarBody />
        </div>
      </div>
      <Show when={machines().activeMachine}>
        {(activeMachine) => (
          <MachineContextProvider machine={activeMachine}>
            <SidebarMachine />
          </MachineContextProvider>
        )}
      </Show>
    </>
  );
}
