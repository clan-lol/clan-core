import { SidebarPane } from "@/src/components/Sidebar/SidebarPane";
import { SectionGeneral } from "./SectionGeneral";
import { SectionTags } from "@/src/components/Sidebar/SidebarMachine/SectionTags";
import { SidebarSectionInstall } from "@/src/components/Sidebar/SidebarMachine/SidebarSectionInstall";

import styles from "./SidebarMachine.module.css";
import { SectionServices } from "@/src/components/Sidebar/SidebarMachine/SectionServices";
import { SidebarSectionUpdate } from "@/src/components/Sidebar/SidebarMachine/SidebarSectionUpdate";
import { useMachineContext } from "@/src/models";

export default function SidebarMachine() {
  const [machine, { deactivateMachine }] = useMachineContext();
  const onClose = () => deactivateMachine();

  return (
    <div class={styles.sidebarPaneContainer}>
      <SidebarPane title={machine().id} onClose={onClose}>
        {/* TODO: merge the following two components */}
        <SidebarSectionInstall />
        <SidebarSectionUpdate />
        <SectionGeneral />
        <SectionTags />
        <SectionServices />
      </SidebarPane>
    </div>
  );
}
