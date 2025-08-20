import "./SidebarHeader.css";
import Icon from "@/src/components/Icon/Icon";
import { DropdownMenu } from "@kobalte/core/dropdown-menu";
import { useNavigate } from "@solidjs/router";
import { Typography } from "../Typography/Typography";
import { createSignal, For, Suspense } from "solid-js";
import { useClanListQuery } from "@/src/hooks/queries";
import { navigateToClan, useClanURI } from "@/src/hooks/clan";
import { clanURIs } from "@/src/stores/clan";
import { Button } from "../Button/Button";

export const SidebarHeader = () => {
  const navigate = useNavigate();

  const [open, setOpen] = createSignal(false);

  // get information about the current active clan
  const clanURI = useClanURI();
  const allClans = useClanListQuery(clanURIs());

  const activeClan = () => allClans.find(({ data }) => data?.uri === clanURI);

  return (
    <div class="sidebar-header">
      <Suspense fallback={"Loading..."}>
        <DropdownMenu open={open()} onOpenChange={setOpen} sameWidth={true}>
          <DropdownMenu.Trigger class="dropdown-trigger">
            <div class="clan-label">
              <div class="clan-icon">
                <Typography
                  hierarchy="label"
                  size="s"
                  weight="bold"
                  inverted={true}
                >
                  {activeClan()?.data?.name.charAt(0).toUpperCase()}
                </Typography>
              </div>
              <Typography
                hierarchy="label"
                size="s"
                weight="bold"
                inverted={!open()}
              >
                {activeClan()?.data?.name}
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
                onSelect={() => navigateToClan(navigate, clanURI)}
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
                    transform="uppercase"
                  >
                    Your Clans
                  </Typography>
                  <Button
                    hierarchy="secondary"
                    ghost
                    size="xs"
                    startIcon="Plus"
                    onClick={() => navigate("/?addClan=true")}
                  >
                    Add
                  </Button>
                </DropdownMenu.GroupLabel>
                <div class="dropdown-group-items">
                  <For each={allClans}>
                    {(clan) => (
                      <Suspense fallback={"Loading..."}>
                        <DropdownMenu.Item
                          class="dropdown-item"
                          onSelect={() =>
                            navigateToClan(navigate, clan.data!.uri)
                          }
                        >
                          <Typography
                            hierarchy="label"
                            size="xs"
                            weight="medium"
                          >
                            {clan.data?.name}
                          </Typography>
                        </DropdownMenu.Item>
                      </Suspense>
                    )}
                  </For>
                </div>
              </DropdownMenu.Group>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu>
      </Suspense>
    </div>
  );
};
