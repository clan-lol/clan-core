import styles from "./SidebarBody.module.css";
import { A } from "@solidjs/router";
import { Accordion } from "@kobalte/core/accordion";
import Icon from "../Icon/Icon";
import { Typography } from "@/src/components/Typography/Typography";
import { For, Show } from "solid-js";
import { MachineStatus } from "@/src/components/MachineStatus/MachineStatus";
import { buildMachinePath, buildServicePath } from "@/src/hooks/clan";
import { useMachineStateQuery } from "@/src/hooks/queries";
import { SidebarProps } from "./Sidebar";
import { Button } from "../Button/Button";
import { useClanContext } from "@/src/routes/Clan/Clan";
import { Instance } from "@/src/workflows/Service/models";

interface MachineProps {
  clanURI: string;
  machineID: string;
  name: string;
  serviceCount: number;
}

const MachineRoute = (props: MachineProps) => {
  const statusQuery = useMachineStateQuery(props.clanURI, props.machineID);

  const status = () =>
    statusQuery.isSuccess ? statusQuery.data.status : undefined;

  return (
    <A href={buildMachinePath(props.clanURI, props.machineID)}>
      <div class="flex w-full flex-col gap-2">
        <div class="flex flex-row items-center justify-between">
          <Typography
            hierarchy="label"
            size="xs"
            weight="bold"
            color="primary"
            inverted
          >
            {props.name}
          </Typography>
          <MachineStatus status={status()} />
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
            {props.serviceCount}
          </Typography>
        </div>
      </div>
    </A>
  );
};

const Machines = () => {
  const ctx = useClanContext();
  if (!ctx) {
    throw new Error("ClanContext not found");
  }

  const clanURI = ctx.clanURI;

  const machines = () => {
    if (!ctx.machinesQuery.isSuccess) {
      return {};
    }

    const result = ctx.machinesQuery.data;
    return Object.keys(result).length > 0 ? result : undefined;
  };

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
          when={machines()}
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
            <For each={Object.entries(machines()!)}>
              {([id, machine]) => (
                <MachineRoute
                  clanURI={clanURI}
                  machineID={id}
                  name={machine.data.name || id}
                  serviceCount={machine?.instance_refs?.length ?? 0}
                />
              )}
            </For>
          </nav>
        </Show>
      </Accordion.Content>
    </Accordion.Item>
  );
};

export const ServiceRoute = (props: {
  clanURI: string;
  label: string;
  id: string;
  instance: Instance;
}) => (
  <A
    href={buildServicePath({
      clanURI: props.clanURI,
      id: props.id,
      module: props.instance.module,
    })}
    replace={true}
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
  </A>
);

const Services = () => {
  const ctx = useClanContext();
  if (!ctx) {
    throw new Error("ClanContext not found");
  }

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

export const SidebarBody = (props: SidebarProps) => {
  const sectionLabels = (props.staticSections || []).map(
    (section) => section.title,
  );

  // controls which sections are open by default
  // we want them all to be open by default
  const defaultAccordionValues = ["machines", "services", ...sectionLabels];

  return (
    <div class={styles.sidebarBody}>
      <Accordion
        class={styles.accordion}
        multiple
        defaultValue={defaultAccordionValues}
      >
        <Machines />
        <Services />

        <For each={props.staticSections}>
          {(section) => (
            <Accordion.Item class={styles.accordionItem} value={section.title}>
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
                    {section.title}
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
                  <For each={section.links || []}>
                    {(link) => (
                      <A href={link.path}>
                        <Typography
                          hierarchy="body"
                          size="xs"
                          weight="bold"
                          color="primary"
                          inverted
                        >
                          {link.label}
                        </Typography>
                      </A>
                    )}
                  </For>
                </nav>
              </Accordion.Content>
            </Accordion.Item>
          )}
        </For>
      </Accordion>
    </div>
  );
};
