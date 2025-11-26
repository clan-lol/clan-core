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

  // we have to update the whole machine model rather than just the sub fields that were changed
  // for that reason we pass in this common submit handler to each machine sub section
  const onSubmit = async (values: Partial<MachineModel>) => {
    console.log("saving tags", values);
    const call = callApi("set_machine", {
      machine: {
        name: machineName,
        flake: {
          identifier: clanURI,
        },
      },
      update: {
        ...machineQuery.data?.machine,
        ...values,
      },
    });

    const result = await call.result;
    if (result.status === "error") {
      throw new Error(result.errors[0].message);
    }

    // refresh the query
    await machineQuery.refetch();
  };

  return (
    <MachineContextProvider machine={props.machine}>
      <div class={styles.sidebarPaneContainer}>
        <SidebarPane
          title={props.machine.name}
          onClose={onClose}
          // the implementation of remote machine status in the backend needs more time to bake, so for now we remove it and
          // present the user with the ability to install or update a machines based on `installedAt` in the inventory.json
          //
          // subHeader={
          //   <Show when={useMachineName()} keyed>
          //     <SidebarMachineStatus
          //       clanURI={clanURI}
          //       machineName={useMachineName()}
          //     />
          //   </Show>
          // }
        >
          <SidebarSectionInstall />
          {/* <SidebarSectionUpdate
          clanURI={clanURI}
          machineName={useMachineName()}
        />
        <SectionGeneral {...sectionProps} />
        <SectionTags {...sectionProps} />
        <SectionServices /> */}
        </SidebarPane>
      </div>
    </MachineContextProvider>
  );
}
