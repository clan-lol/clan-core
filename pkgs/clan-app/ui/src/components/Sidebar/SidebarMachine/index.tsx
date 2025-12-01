import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { SidebarPane } from "@/src/components/Sidebar/SidebarPane";
import { navigateToClan, useClanURI, useMachineName } from "@/src/hooks/clan";
import { Show } from "solid-js";
import { SectionGeneral } from "./SectionGeneral";
import { Machine as MachineModel, useMachineQuery } from "@/src/hooks/queries";
import { SectionTags } from "@/src/components/Sidebar/SidebarMachine/SectionTags";
import { callApi } from "@/src/hooks/api";
import { SidebarSectionInstall } from "@/src/components/Sidebar/SidebarMachine/SidebarSectionInstall";

import styles from "./SidebarMachine.module.css";
import { SectionServices } from "@/src/components/Sidebar/SidebarMachine/SectionServices";
import { SidebarSectionUpdate } from "@/src/components/Sidebar/SidebarMachine/SidebarSectionUpdate";
import { useClanContext } from "@/src/contexts/ClanContext";
import { Machine } from "@/src/contexts/ClanContext/Machine";
import { MachineContextProvider } from "@/src/contexts/MachineContext";

export default function SidebarMachine(props: { machine: Machine }) {
  const onClose = () => {
    props.machine.deactivate();
  };

  return (
    <MachineContextProvider machine={props.machine}>
      <div class={styles.sidebarPaneContainer}>
        <SidebarPane title={props.machine.name} onClose={onClose}>
          {/* TODO: merge the following two components */}
          <SidebarSectionInstall />
          <SidebarSectionUpdate />
          <SectionGeneral />
          <SectionTags />
          {/* <SectionServices /> */}
        </SidebarPane>
      </div>
    </MachineContextProvider>
  );
}
