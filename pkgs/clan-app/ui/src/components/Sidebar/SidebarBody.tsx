import "./SidebarBody.css";
import { A } from "@solidjs/router";
import { Accordion } from "@kobalte/core/accordion";
import Icon from "../Icon/Icon";
import { Typography } from "@/src/components/Typography/Typography";
import { For, Show, useContext } from "solid-js";
import { MachineStatus } from "@/src/components/MachineStatus/MachineStatus";
import { buildMachinePath, useClanURI } from "@/src/hooks/clan";
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
            inverted={true}
          >
            {props.name}
          </Typography>
          <MachineStatus status={status()} />
        </div>
        <div class="flex w-full flex-row items-center gap-1">
          <Icon icon="Flash" size="0.75rem" inverted={true} color="tertiary" />
          <Typography
            hierarchy="label"
            family="mono"
            size="s"
            inverted={true}
            color="primary"
          >
            {props.serviceCount}
          </Typography>
        </div>
      </div>
    </A>
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
  const defaultAccordionValues = ["your-machines", ...sectionLabels];

  const machines = () => {
    if (!ctx.machinesQuery.isSuccess) {
      return {};
    }

    const result = ctx.machinesQuery.data;
    return Object.keys(result).length > 0 ? result : undefined;
  };

  return (
    <div class="sidebar-body">
      <Accordion
        class="accordion"
        multiple
        defaultValue={defaultAccordionValues}
      >
        <Accordion.Item class="item" value="your-machines">
          <Accordion.Header class="header">
            <Accordion.Trigger class="trigger">
              <Typography
                class="section-title"
                hierarchy="label"
                family="mono"
                size="xs"
                inverted={true}
                color="tertiary"
              >
                Your Machines
              </Typography>
              <Icon
                icon="CaretDown"
                color="tertiary"
                inverted={true}
                size="0.75rem"
              />
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content class="content">
            <Show
              when={machines()}
              fallback={
                <div class="flex w-full flex-col items-center justify-center gap-2.5">
                  <Typography
                    hierarchy="body"
                    size="s"
                    weight="medium"
                    inverted
                  >
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
                      name={machine.name || id}
                      serviceCount={0}
                    />
                  )}
                </For>
              </nav>
            </Show>
          </Accordion.Content>
        </Accordion.Item>

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
                    inverted={true}
                    color="tertiary"
                  >
                    {section.title}
                  </Typography>
                  <Icon
                    icon="CaretDown"
                    color="tertiary"
                    inverted={true}
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
                          inverted={true}
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
