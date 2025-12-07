import styles from "./SidebarBody.module.css";
import { Accordion } from "@kobalte/core/accordion";
import Icon from "../Icon/Icon";
import { Typography } from "@/src/components/Typography/Typography";
import { Component, For, Show } from "solid-js";
import { MachineStatus } from "@/src/components/MachineStatus/MachineStatus";
import { Button } from "../Button/Button";
import { Instance } from "@/src/workflows/Service/models";
import { useClanContext } from "../Context/ClanContext";
import {
  MachineContextProvider,
  useMachineContext,
  useMachinesContext,
} from "../Context/MachineContext";

const SidebarBody: Component = () => {
  return (
    <div class={styles.sidebarBody}>
      <Accordion
        class={styles.accordion}
        multiple
        defaultValue={["machines", "services"]}
      >
        <MachinesSection />
        {/* <ServicesSection /> */}
      </Accordion>
    </div>
  );
};
export default SidebarBody;

const MachinesSection: Component = () => {
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
          when={machines().all.length !== 0}
          fallback={
            <div class="flex w-full flex-col items-center justify-center gap-2.5">
              <Typography hierarchy="body" size="s" weight="medium" inverted>
                No machines yet
              </Typography>
              <Button
                hierarchy="primary"
                size="s"
                icon="Machine"
                onClick={() => ctx.setShowAddMachine(true)}
              >
                Add machine
              </Button>
            </div>
          }
        >
          <nav>
            <For each={machines().all}>
              {(machine) => (
                <MachineContextProvider machine={() => machine}>
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
  const [machine, { activateMachine }] = useMachineContext()!;
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
          <MachineStatus status={machine().status} />
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

export const ServiceRoute = (props: {
  clanURI: string;
  label: string;
  id: string;
  instance: Instance;
}) => (
  <div class="flex w-full flex-col gap-2">
    <div class="flex flex-row items-center justify-between">
      <Typography
        hierarchy="label"
        size="xs"
        weight="bold"
        color="primary"
        inverted
      >
        {props.label}
      </Typography>
      <Icon icon="Code" size="0.75rem" inverted color="tertiary" />
    </div>
    {/* Same subtitle as Machine */}
    {/* <div class="flex w-full flex-row items-center gap-1">
        <Icon icon="Code" size="0.75rem" inverted color="tertiary" />
        <Typography
          hierarchy="label"
          family="mono"
          size="s"
          inverted
          color="primary"
        >
          {props.instance.resolved.usage_ref.name}
        </Typography>
      </div> */}
  </div>
);

const Services = () => {
  const clan = useClanContext()!;

  const serviceInstances = () => {
    if (!ctx.serviceInstancesQuery.isSuccess) {
      return [];
    }

    return Object.entries(ctx.serviceInstancesQuery.data)
      .map(([id, instance]) => {
        const moduleName = instance.module.name;

        const label = moduleName == id ? moduleName : `${moduleName} (${id})`;
        return {
          id,
          label,
          instance: instance,
        };
      })
      .sort((a, b) => a.label.localeCompare(b.label));
  };

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
          <For each={serviceInstances()}>
            {(mapped) => (
              <ServiceRoute
                clanURI={ctx.clanURI}
                id={mapped.id}
                label={mapped.label}
                instance={mapped.instance}
              />
            )}
          </For>
        </nav>
      </Accordion.Content>
    </Accordion.Item>
  );
};
