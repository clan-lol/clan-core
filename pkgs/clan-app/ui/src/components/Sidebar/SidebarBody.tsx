import "./SidebarBody.css";
import { A } from "@solidjs/router";
import { Accordion } from "@kobalte/core/accordion";
import Icon from "../Icon/Icon";
import { Typography } from "@/src/components/Typography/Typography";
import { For, Show } from "solid-js";
import { MachineStatus } from "@/src/components/MachineStatus/MachineStatus";
import {
  buildMachinePath,
  buildServicePath,
  useClanURI,
} from "@/src/hooks/clan";
import { useMachineStateQuery } from "@/src/hooks/queries";
import { SidebarProps } from "./Sidebar";
import { Button } from "../Button/Button";
import { useClanContext } from "@/src/routes/Clan/Clan";

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
    <Accordion.Item class="item" value="machines">
      <Accordion.Header class="header">
        <Accordion.Trigger class="trigger">
          <Typography
            class="section-title"
            hierarchy="label"
            family="mono"
            size="xs"
            inverted
            color="tertiary"
          >
            Your Machines
          </Typography>
          <Icon icon="CaretDown" color="tertiary" inverted size="0.75rem" />
        </Accordion.Trigger>
      </Accordion.Header>
      <Accordion.Content class="content">
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
                startIcon="Machine"
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
  machineName?: string;
  label: string;
  id: string;
  module: { input?: string | null | undefined; name: string };
}) => (
  <A href={buildServicePath(props)} replace={true}>
    <div class="flex w-full flex-col gap-2">
      <Typography
        hierarchy="label"
        size="s"
        weight="bold"
        color="primary"
        inverted
      >
        {props.label}
      </Typography>
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

    return Object.entries(ctx.serviceInstancesQuery.data).map(
      ([id, instance]) => {
        const moduleName = instance.module.name;

        const label = moduleName == id ? moduleName : `${moduleName} (${id})`;

        return { id, label, module: instance.module };
      },
    );
  };

  return (
    <Accordion.Item class="item" value="services">
      <Accordion.Header class="header">
        <Accordion.Trigger class="trigger">
          <Typography
            class="section-title"
            hierarchy="label"
            family="mono"
            size="xs"
            inverted
            color="tertiary"
          >
            Services
          </Typography>
          <Icon icon="CaretDown" color="tertiary" inverted size="0.75rem" />
        </Accordion.Trigger>
      </Accordion.Header>
      <Accordion.Content class="content">
        <nav>
          <For each={serviceInstances()}>
            {(instance) => <ServiceRoute clanURI={ctx.clanURI} {...instance} />}
          </For>
        </nav>
      </Accordion.Content>
    </Accordion.Item>
  );
};

export const SidebarBody = (props: SidebarProps) => {
  const clanURI = useClanURI();

  const ctx = useClanContext();

  const sectionLabels = (props.staticSections || []).map(
    (section) => section.title,
  );

  // controls which sections are open by default
  // we want them all to be open by default
  const defaultAccordionValues = ["machines", "services", ...sectionLabels];

  return (
    <div class="sidebar-body">
      <Accordion
        class="accordion"
        multiple
        defaultValue={defaultAccordionValues}
      >
        <Machines />
        <Services />

        <For each={props.staticSections}>
          {(section) => (
            <Accordion.Item class="item" value={section.title}>
              <Accordion.Header class="header">
                <Accordion.Trigger class="trigger">
                  <Typography
                    class="section-title"
                    hierarchy="label"
                    family="mono"
                    size="xs"
                    inverted
                    color="tertiary"
                  >
                    {section.title}
                  </Typography>
                  <Icon
                    icon="CaretDown"
                    color="tertiary"
                    inverted
                    size="0.75rem"
                  />
                </Accordion.Trigger>
              </Accordion.Header>
              <Accordion.Content class="content">
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
