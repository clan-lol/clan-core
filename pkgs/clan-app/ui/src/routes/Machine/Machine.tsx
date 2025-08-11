import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { SidebarPane } from "@/src/components/Sidebar/SidebarPane";
import { navigateToClan, useClanURI, useMachineName } from "@/src/hooks/clan";
import { createSignal, Show } from "solid-js";
import { SectionGeneral } from "./SectionGeneral";
import { InstallModal } from "@/src/workflows/Install/install";
import { Button } from "@/src/components/Button/Button";
import { useMachineQuery } from "@/src/hooks/queries";
import { SectionTags } from "@/src/routes/Machine/SectionTags";

export const Machine = (props: RouteSectionProps) => {
  const navigate = useNavigate();
  const clanURI = useClanURI();

  const onClose = () => {
    // go back to clan route
    navigateToClan(navigate, clanURI);
  };

  const [showInstall, setShowModal] = createSignal(false);
  const sidebarPane = (machineName: string) => {
    const machineQuery = useMachineQuery(clanURI, machineName);
    const sectionProps = { clanURI, machineName, machineQuery };

    return (
      <SidebarPane title={machineName} onClose={onClose}>
        <SectionGeneral {...sectionProps} />
        <SectionTags {...sectionProps} />
      </SidebarPane>
    );
  };

  let container: Node;
  return (
    <Show when={useMachineName()} keyed>
      <Button
        hierarchy="primary"
        onClick={() => setShowModal(true)}
        class="absolute right-0 top-0 m-4"
      >
        Install me!
      </Button>
      <Show when={showInstall()}>
        <div
          class="absolute left-0 top-0 z-50 flex size-full items-center justify-center bg-white/90"
          ref={(el) => (container = el)}
        >
          <InstallModal
            machineName={useMachineName()}
            mount={container!}
            onClose={() => setShowModal(false)}
          />
        </div>
      </Show>
      {sidebarPane(useMachineName())}
    </Show>
  );
};
