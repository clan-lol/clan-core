import { RouteSectionProps, useNavigate } from "@solidjs/router";
import { SidebarPane } from "@/src/components/Sidebar/SidebarPane";
import { navigateToClan, useClanURI, useMachineName } from "@/src/hooks/clan";
import { createSignal, Show } from "solid-js";
import { SectionGeneral } from "./SectionGeneral";
import { InstallModal } from "@/src/workflows/Install/install";
import { Button } from "@/src/components/Button/Button";
import { Machine as MachineModel, useMachineQuery } from "@/src/hooks/queries";
import { SectionTags } from "@/src/routes/Machine/SectionTags";
import { callApi } from "@/src/hooks/api";

export const Machine = (props: RouteSectionProps) => {
  const navigate = useNavigate();
  const clanURI = useClanURI();

  const onClose = () => {
    // go back to clan route
    navigateToClan(navigate, clanURI);
  };

  const [showInstall, setShowModal] = createSignal(false);

  let container: Node;

  const sidebarPane = (machineName: string) => {
    const machineQuery = useMachineQuery(clanURI, machineName);

    // we have to update the whole machine model rather than just the sub fields that were changed
    // for that reason we pass in this common submit handler to each machine sub section
    const onSubmit = async (values: Partial<MachineModel>) => {
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
      <SidebarPane title={machineName} onClose={onClose}>
        <SectionGeneral {...sectionProps} />
        <SectionTags {...sectionProps} />
      </SidebarPane>
    );
  };

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
