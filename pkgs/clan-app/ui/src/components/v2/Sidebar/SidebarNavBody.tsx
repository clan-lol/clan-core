import "./SidebarNavBody.css";
import { A } from "@solidjs/router";
import { Accordion } from "@kobalte/core/accordion";
import Icon from "../Icon/Icon";
import { Typography } from "@/src/components/v2/Typography/Typography";
import {
  MachineProps,
  SidebarNavProps,
} from "@/src/components/v2/Sidebar/SidebarNav";
import { For } from "solid-js";
import { MachineStatus } from "@/src/components/v2/MachineStatus/MachineStatus";

const MachineRoute = (props: MachineProps) => (
  <div class="flex w-full flex-col gap-2">
    <div class="flex flex-row items-center justify-between">
      <Typography
        hierarchy="label"
        size="xs"
        weight="bold"
        color="primary"
        inverted={true}
      >
        {props.label}
      </Typography>
      <MachineStatus status={props.status} />
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
);

export const SidebarNavBody = (props: SidebarNavProps) => {
  const sectionLabels = props.extraSections.map((section) => section.label);

  // controls which sections are open by default
  // we want them all to be open by default
  const defaultAccordionValues = ["your-machines", ...sectionLabels];

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
            <nav>
              <For each={props.clanDetail.machines}>
                {(machine) => (
                  <A href={machine.path}>
                    <MachineRoute {...machine} />
                  </A>
                )}
              </For>
            </nav>
          </Accordion.Content>
        </Accordion.Item>

        <For each={props.extraSections}>
          {(section) => (
            <Accordion.Item class="item" value={section.label}>
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
                    {section.label}
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
