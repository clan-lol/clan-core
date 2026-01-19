import { SidebarPane } from "@/components/Sidebar/SidebarPane";
import { SectionGeneral } from "./SectionGeneral";
import { SectionTags } from "@/components/Sidebar/SidebarMachine/SectionTags";
import { SidebarSectionInstall } from "@/components/Sidebar/SidebarMachine/SidebarSectionInstall";

import styles from "./SidebarMachine.module.css";
import { SectionServices } from "@/components/Sidebar/SidebarMachine/SectionServices";
import { SidebarSectionUpdate } from "@/components/Sidebar/SidebarMachine/SidebarSectionUpdate";
import { useMachineContext } from "@/models";

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
