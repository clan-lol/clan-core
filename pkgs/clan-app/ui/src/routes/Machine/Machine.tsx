import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { SidebarPane } from "@/src/components/Sidebar/SidebarPane";
import { navigateToClan, useClanURI, useMachineID } from "@/src/hooks/clan";

export const Machine = (props: RouteSectionProps) => {
  const navigate = useNavigate();
  const clanURI = useClanURI();

  const onClose = () => {
    // go back to clan route
    navigateToClan(navigate, clanURI);
  };

  return (
    <SidebarPane title={useMachineID()} onClose={onClose}>
      <h1>Hello world</h1>
    </SidebarPane>
  );
};
