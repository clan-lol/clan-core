import styles from "./SidebarBody.module.css";
import { Accordion } from "@kobalte/core/accordion";
import Icon from "../Icon/Icon";
import { Typography } from "@/src/components/Typography/Typography";
import { Component, For, Show } from "solid-js";
import MachineStatusComponent from "@/src/components/MachineStatus";
import { Button } from "../Button/Button";
import {
  MachineContextProvider,
  ServiceInstanceContextProvider,
  useClanContext,
  useMachineContext,
  useMachinesContext,
  useServiceInstanceContext,
  useUIContext,
} from "@/src/models";

const SidebarBody: Component = () => {
  return (
    <div class={styles.sidebarBody}>
      <Accordion
        class={styles.accordion}
        multiple
        defaultValue={["machines", "services"]}
      >
        <MachinesSection />
        <ServicesSection />
      </Accordion>
    </div>
  );
};
export default SidebarBody;

const MachinesSection: Component = () => {
  const [, { showModal }] = useUIContext();
  const [machines] = useMachinesContext();

  return (
    <Accordion.Item class={styles.accordionItem} value="machines">
      <Accordion.Header class={styles.accordionHeader}>
        <Accordion.Trigger class={styles.accordionTrigger}>
          <Typography
            hierarchy="label"
            family="mono"
            size="xs"
            inverted
            color="tertiary"
            transform="uppercase"
          >
            Your Machines
          </Typography>
          <Icon
            icon="CaretDown"
            color="tertiary"
            inverted
            size="0.75rem"
            in="SidebarBody-AccordionTrigger"
          />
        </Accordion.Trigger>
      </Accordion.Header>
      <Accordion.Content class={styles.accordionContent}>
        <Show
          when={Object.keys(machines().all).length !== 0}
          fallback={
            <div class="flex w-full flex-col items-center justify-center gap-2.5">
              <Typography hierarchy="body" size="s" weight="medium" inverted>
                No machines yet
              </Typography>
              <Button
                hierarchy="primary"
                size="s"
                icon="Machine"
                onClick={() =>
                  showModal({ type: "AddMachine", position: [0, 0] })
                }
              >
                Add machine
              </Button>
            </div>
          }
        >
          <nav>
            <For each={machines().sorted}>
              {(machine) => (
                <MachineContextProvider value={() => machine}>
                  <MachineSection />
                </MachineContextProvider>
              )}
            </For>
          </nav>
        </Show>
      </Accordion.Content>
    </Accordion.Item>
  );
};

const MachineSection: Component = () => {
  const [machine, { activateMachine }] = useMachineContext();
  return (
    <a
      href="#"
      onClick={(ev) => {
        ev.preventDefault();
        activateMachine();
      }}
    >
      <div class="flex w-full flex-col gap-2">
        <div class="flex flex-row items-center justify-between">
          <Typography
            hierarchy="label"
            size="xs"
            weight="bold"
            color="primary"
            inverted
          >
            {machine().id}
          </Typography>
          <MachineStatusComponent status={machine().status} />
        </div>
        <div class="flex w-full flex-row items-center gap-1">
          <Icon icon="Flash" size="0.75rem" inverted color="tertiary" />
          <Typography
            hierarchy="label"
            family="mono"
            size="s"
            inverted
            color="primary"
          >
            {machine().serviceInstances.length}
          </Typography>
        </div>
      </div>
    </a>
  );
};

const ServicesSection: Component = () => {
  const [clan] = useClanContext();

  return (
    <Accordion.Item class={styles.accordionItem} value="services">
      <Accordion.Header class={styles.accordionHeader}>
        <Accordion.Trigger class={styles.accordionTrigger}>
          <Typography
            hierarchy="label"
            family="mono"
            size="xs"
            inverted
            color="tertiary"
            transform="uppercase"
          >
            Services
          </Typography>
          <Icon
            icon="CaretDown"
            color="tertiary"
            inverted
            size="0.75rem"
            in="SidebarBody-AccordionTrigger"
          />
        </Accordion.Trigger>
      </Accordion.Header>
      <Accordion.Content class={styles.accordionContent}>
        <nav>
          <For each={clan().serviceInstances.sorted}>
            {(instance) => (
              <ServiceInstanceContextProvider value={() => instance}>
                <ServiceInstanceEntry />
              </ServiceInstanceContextProvider>
            )}
          </For>
        </nav>
      </Accordion.Content>
    </Accordion.Item>
  );
};

export const ServiceInstanceEntry: Component = () => {
  const [instance, { activateServiceInstance }] = useServiceInstanceContext();
  return (
    <a
      href="#"
      onClick={(ev) => {
        ev.preventDefault();
        activateServiceInstance();
      }}
    >
      <div class="flex w-full flex-col gap-2">
        <div class="flex flex-row items-center justify-between">
          <Typography
            hierarchy="label"
            size="xs"
            weight="bold"
            color="primary"
            inverted
          >
            {instance().data.name == instance().service.id
              ? instance().data.name
              : `${instance().service.id} (${instance().data.name})`}
          </Typography>
          <Icon icon="Code" size="0.75rem" inverted color="tertiary" />
        </div>
      </div>
    </a>
  );
};
