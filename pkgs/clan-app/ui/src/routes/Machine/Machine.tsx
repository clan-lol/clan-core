import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { SidebarPane } from "@/src/components/Sidebar/SidebarPane";
import { navigateToClan, useClanURI, useMachineName } from "@/src/hooks/clan";
import { Show } from "solid-js";
import { SectionGeneral } from "./SectionGeneral";

export const Machine = (props: RouteSectionProps) => {
  const navigate = useNavigate();
  const clanURI = useClanURI();

  const onClose = () => {
    // go back to clan route
    navigateToClan(navigate, clanURI);
  };

  const machineName = useMachineName();

  return (
    <Show when={useMachineName()} keyed>
      <SidebarPane title={useMachineName()} onClose={onClose}>
        <SectionGeneral />
      </SidebarPane>
    </Show>
  );
};
