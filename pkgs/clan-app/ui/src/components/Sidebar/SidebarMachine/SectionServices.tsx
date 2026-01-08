import { SidebarSection } from "@/src/components/Sidebar/SidebarSection";
import { For } from "solid-js";
import { ServiceInstanceEntry } from "@/src/components/Sidebar/SidebarBody";
import styles from "./SectionServices.module.css";
import {
  ServiceInstanceContextProvider,
  useMachineContext,
} from "@/src/models";

export const SectionServices = () => {
  const [machine] = useMachineContext();

  return (
    <SidebarSection title="Services">
      <div class={styles.sectionServices}>
        <nav>
          <For each={machine().serviceInstances}>
            {(instance) => (
              <ServiceInstanceContextProvider value={() => instance}>
                <ServiceInstanceEntry />
              </ServiceInstanceContextProvider>
            )}
          </For>
        </nav>
      </div>
    </SidebarSection>
  );
};
