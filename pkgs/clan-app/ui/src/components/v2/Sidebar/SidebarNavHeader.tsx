import "./SidebarNavHeader.css";
import Icon from "@/src/components/v2/Icon/Icon";
import { DropdownMenu } from "@kobalte/core/dropdown-menu";
import { useNavigate } from "@solidjs/router";
import { Typography } from "../Typography/Typography";
import { createSignal, For } from "solid-js";
import {
  ClanLinkProps,
  ClanProps,
} from "@/src/components/v2/Sidebar/SidebarNav";

export interface SidebarHeaderProps {
  clanDetail: ClanProps;
  clanLinks: ClanLinkProps[];
}

export const SidebarNavHeader = (props: SidebarHeaderProps) => {
  const navigate = useNavigate();

  const [open, setOpen] = createSignal(false);

  const firstChar = props.clanDetail.label.charAt(0);

  return (
    <div class="sidebar-header">
      <DropdownMenu open={open()} onOpenChange={setOpen} sameWidth={true}>
        <DropdownMenu.Trigger class="dropdown-trigger">
          <div class="title">
            <div class="clan-icon">
              <Typography
                hierarchy="label"
                size="s"
                weight="bold"
                inverted={true}
              >
                {firstChar.toUpperCase()}
              </Typography>
            </div>
            <Typography
              hierarchy="label"
              size="s"
              weight="bold"
              inverted={!open()}
            >
              {props.clanDetail.label}
            </Typography>
          </div>
          <DropdownMenu.Icon>
            <Icon icon={"CaretDown"} inverted={!open()} size="0.75rem" />
          </DropdownMenu.Icon>
        </DropdownMenu.Trigger>
        <DropdownMenu.Portal>
          <DropdownMenu.Content class="sidebar-dropdown-content">
            <DropdownMenu.Item
              class="dropdown-item"
              onSelect={() => navigate(props.clanDetail.settingsPath)}
            >
              <Icon
                icon="Settings"
                size="0.75rem"
                inverted={true}
                color="tertiary"
              />
              <Typography hierarchy="label" size="xs" weight="medium">
                Settings
              </Typography>
            </DropdownMenu.Item>
            <DropdownMenu.Group class="dropdown-group">
              <DropdownMenu.GroupLabel class="dropdown-group-label">
                <Typography
                  hierarchy="label"
                  family="mono"
                  size="xs"
                  color="tertiary"
                >
                  YOUR CLANS
                </Typography>
              </DropdownMenu.GroupLabel>
              <div class="dropdown-group-items">
                <For each={props.clanLinks}>
                  {(clan) => (
                    <DropdownMenu.Item
                      class="dropdown-item"
                      onSelect={() => navigate(clan.path)}
                    >
                      <Typography hierarchy="label" size="xs" weight="medium">
                        {clan.label}
                      </Typography>
                    </DropdownMenu.Item>
                  )}
                </For>
              </div>
            </DropdownMenu.Group>
          </DropdownMenu.Content>
        </DropdownMenu.Portal>
      </DropdownMenu>
    </div>
  );
};
