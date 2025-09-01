import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { SidebarPane } from "@/src/components/Sidebar/SidebarPane";
import { navigateToClan, useClanURI, useMachineName } from "@/src/hooks/clan";
import { Show } from "solid-js";
import { SectionGeneral } from "./SectionGeneral";
import { Machine as MachineModel, useMachineQuery } from "@/src/hooks/queries";
import { SectionTags } from "@/src/routes/Machine/SectionTags";
import { callApi } from "@/src/hooks/api";
import { SidebarMachineStatus } from "@/src/components/Sidebar/SidebarMachineStatus";
import { SidebarSectionInstall } from "@/src/components/Sidebar/SidebarSectionInstall";

import styles from "./Machine.module.css";

export const Machine = (props: RouteSectionProps) => {
  const navigate = useNavigate();
  const clanURI = useClanURI();

  const onClose = () => {
    // go back to clan route
    navigateToClan(navigate, clanURI);
  };

  const Sections = () => {
    const machineName = useMachineName();
    const machineQuery = useMachineQuery(clanURI, machineName);

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

    const sectionProps = { clanURI, machineName, onSubmit, machineQuery };

    return (
      <>
        <SidebarSectionInstall
          clanURI={clanURI}
          machineName={useMachineName()}
        />
        <SectionGeneral {...sectionProps} />
        <SectionTags {...sectionProps} />
      </>
    );
  };

  return (
    <Show when={useMachineName()}>
      <div class={styles.sidebarPaneContainer}>
        <SidebarPane
          title={useMachineName()}
          onClose={onClose}
          subHeader={
            <Show when={useMachineName()} keyed>
              <SidebarMachineStatus
                clanURI={clanURI}
                machineName={useMachineName()}
              />
            </Show>
          }
        >
          <Sections />
        </SidebarPane>
      </div>
    </Show>
  );
};
