import { SidebarSection } from "@/src/components/Sidebar/SidebarSection";
import { useClanContext } from "@/src/routes/Clan/Clan";
import { For, Show } from "solid-js";
import { useMachineName } from "@/src/hooks/clan";
import { ServiceRoute } from "@/src/components/Sidebar/SidebarBody";
import styles from "./SectionServices.module.css";

export const SectionServices = () => {
  const ctx = useClanContext();

  const services = () => {
    if (!(ctx.machinesQuery.isSuccess && ctx.serviceInstancesQuery.isSuccess)) {
      return [];
    }

    const machineName = useMachineName();
    if (!ctx.machinesQuery.data[machineName]) {
      return [];
    }

    return (ctx.machinesQuery.data[machineName].instance_refs ?? []).map(
      (id) => {
        const module = ctx.serviceInstancesQuery.data?.[id].module;
        if (!module) {
          throw new Error(`Service instance ${id} has no module`);
        }

        return {
          id,
          module,
          label: module.name == id ? module.name : `${module.name} (${id})`,
        };
      },
    );
  };

  return (
    <Show when={ctx.serviceInstancesQuery.isSuccess}>
      <SidebarSection title="Services">
        <div class={styles.sectionServices}>
          <nav>
            <For each={services()}>
              {(instance) => (
                <ServiceRoute
                  clanURI={ctx.clanURI}
                  machineName={useMachineName()}
                  {...instance}
                />
              )}
            </For>
          </nav>
        </div>
      </SidebarSection>
    </Show>
  );
};
