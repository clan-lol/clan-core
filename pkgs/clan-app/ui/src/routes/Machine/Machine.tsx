import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { SidebarPane } from "@/src/components/Sidebar/SidebarPane";
import { navigateToClan, useClanURI, useMachineName } from "@/src/hooks/clan";
import { createSignal, Show } from "solid-js";
import { SectionGeneral } from "./SectionGeneral";
import { InstallModal } from "@/src/workflows/Install/install";
import { Button } from "@/src/components/Button/Button";

export const Machine = (props: RouteSectionProps) => {
  const navigate = useNavigate();
  const clanURI = useClanURI();

  const onClose = () => {
    // go back to clan route
    navigateToClan(navigate, clanURI);
  };

  const [showInstall, setShowModal] = createSignal(false);

  let container: Node;
  return (
    <Show when={useMachineName()} keyed>
      <Button
        hierarchy="primary"
        onClick={() => setShowModal(true)}
        class="absolute top-0 right-0 m-4"
      >
        Install me!
      </Button>
      <Show when={showInstall()}>
        <div
          class="absolute top-0 left-0 w-full h-full flex justify-center items-center z-50 bg-white/90"
          ref={(el) => (container = el)}
        >
          <InstallModal
            machineName={useMachineName()}
            mount={container!}
            onClose={() => setShowModal(false)}
          />
        </div>
      </Show>
      <SidebarPane title={useMachineName()} onClose={onClose}>
        <SectionGeneral />
      </SidebarPane>
    </Show>
  );
};
